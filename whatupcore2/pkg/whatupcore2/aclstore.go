package whatupcore2

import (
	"database/sql"
	"errors"
	"fmt"
	"time"

	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow/types"
	waLog "go.mau.fi/whatsmeow/util/log"
	"google.golang.org/protobuf/types/known/timestamppb"
)

const (
    defaultJID = "DEFAULT"
)

type upgradeFunc func(*sql.Tx, *ACLStore) error

var Upgrades = [...]upgradeFunc{upgradeV1}

type ACLRow struct {
    JID string
    permission int32
    updatedAt time.Time
}

func NewACLRowFromGroupACL(groupACL *pb.GroupACL) *ACLRow {
    return &ACLRow{
        JID: ProtoToJID(groupACL.JID).String(),
        permission: int32(groupACL.Permission.Number()),
        updatedAt: groupACL.UpdatedAt.AsTime(),
    }
}

func (arow *ACLRow) Proto() (*pb.GroupACL, error) {
    var jid types.JID
    var err error
    if arow.JID == defaultJID {
        jid = types.EmptyJID
    } else {
        jid, err = types.ParseJID(arow.JID)
        if err != nil {
            return nil, err
        }
    }
    if _, ok := pb.GroupPermission_name[arow.permission]; !ok {
        return nil, fmt.Errorf("Unknown permission value: %d", arow.permission)
    }
    return &pb.GroupACL{
        JID: JIDToProto(jid),
        Permission: pb.GroupPermission(arow.permission),
        UpdatedAt: timestamppb.New(arow.updatedAt),
    }, nil
}

type ACLStore struct {
    db *sql.DB
    log waLog.Logger

    defaultACL *ACLRow
}

func NewACLStore(db *sql.DB, log waLog.Logger) *ACLStore {
    log.Debugf("Starting now ACLStore")
    acls := &ACLStore{db: db, log:log}
    acls.Upgrade()
    return acls
}

func (acls *ACLStore) getVersion() (int, error) {
	_, err := acls.db.Exec("CREATE TABLE IF NOT EXISTS aclstore_version (version INTEGER)")
	if err != nil {
		return -1, err
	}

	version := 0
	row := acls.db.QueryRow("SELECT version FROM aclstore_version LIMIT 1")
	if row != nil {
		_ = row.Scan(&version)
	}
	return version, nil
}

func (acls *ACLStore) setVersion(tx *sql.Tx, version int) error {
	_, err := tx.Exec("DELETE FROM aclstore_version")
	if err != nil {
		return err
	}
	_, err = tx.Exec("INSERT INTO aclstore_version (version) VALUES ($1)", version)
	return err
}

func (acls *ACLStore) Upgrade() error {
	version, err := acls.getVersion()
	if err != nil {
		return err
	}

	for ; version < len(Upgrades); version++ {
		var tx *sql.Tx
		tx, err = acls.db.Begin()
		if err != nil {
			return err
		}

		migrateFunc := Upgrades[version]
		acls.log.Infof("Upgrading database to v%d", version+1)
		err = migrateFunc(tx, acls)
		if err != nil {
			_ = tx.Rollback()
			return err
		}

		if err = acls.setVersion(tx, version+1); err != nil {
			return err
		}

		if err = tx.Commit(); err != nil {
			return err
		}
	}
	return nil
}

func upgradeV1(tx *sql.Tx, acls *ACLStore) error {
	_, err := tx.Exec(`CREATE TABLE aclstore_permissions (
		JID TEXT PRIMARY KEY,
        permission INT NOT NULL,
        updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )`)
	if err != nil {
		return err
	}
    return nil
}

func (acls *ACLStore) SetDefaultACL(permission *pb.GroupPermission) error {
    return acls.setACLByString(defaultJID, permission)
}

func (acls *ACLStore) SetACLByJID(jid *types.JID, permission *pb.GroupPermission) error {
    if jid.IsEmpty() {
        return errors.New("Cannot set ACL for empty JID")
    }
    jidStr := jid.ToNonAD().String()
    return acls.setACLByString(jidStr, permission)
}

func (acls *ACLStore) GetDefaultACL() (*pb.GroupACL, error) {
    groupACL, err := acls.GetACLbyJID(&types.EmptyJID)
    if err != nil {
        return nil, err
    }
    return groupACL, nil
}

func (acls *ACLStore) setACLByString(jidStr string, permission *pb.GroupPermission) error {
    _, err := acls.db.Exec(`REPLACE INTO
        aclstore_permissions (jid, permission, updatedAt)
        VALUES($1, $2, $3)`,
        jidStr,
        permission.Number(),
        time.Now().Unix(),
    )
    return err
}

func (acls *ACLStore) GetACLbyJID(jid *types.JID) (*pb.GroupACL, error) {
    var jidStr string
    permission := &ACLRow{}
    if jid.IsEmpty() {
        jidStr = defaultJID
    } else {
        jidStr = jid.ToNonAD().String()
    }
    err := acls.db.QueryRow(`
        SELECT
            JID, permission, updatedAt
        FROM aclstore_permissions
        WHERE jid = $1`,
        jidStr,
    ).Scan(&permission.JID, &permission.permission, &permission.updatedAt)
    if err != nil {
        acls.log.Errorf("Could not get ACL value: %s: %s", jid.String(), err)
        return nil, err
    }
    permissionProto, err := permission.Proto()
    if err != nil {
        return nil, err
    }
    return permissionProto, nil
}
