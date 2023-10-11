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

type ACLEntry struct {
	JID        string
	Permission int32
	UpdatedAt  time.Time
}

func NewACLEntryFromProto(groupACL *pb.GroupACL) *ACLEntry {
	return &ACLEntry{
		JID:        ProtoToJID(groupACL.JID).String(),
		Permission: int32(groupACL.Permission.Number()),
		UpdatedAt:  groupACL.UpdatedAt.AsTime(),
	}
}

func (aclEntry *ACLEntry) IsDefault() bool {
	return aclEntry.JID == defaultJID
}

func (aclEntry *ACLEntry) CanRead() bool {
	switch pb.GroupPermission(aclEntry.Permission) {
	case pb.GroupPermission_READONLY, pb.GroupPermission_READWRITE:
		return true
	default:
		return false
	}
}

func (aclEntry *ACLEntry) CanWrite() bool {
	switch pb.GroupPermission(aclEntry.Permission) {
	case pb.GroupPermission_WRITEONLY, pb.GroupPermission_READWRITE:
		return true
	default:
		return false
	}
}

func (aclEntry *ACLEntry) Proto() (*pb.GroupACL, error) {
	var jid types.JID
	var err error
	var isDefault bool
	if aclEntry.IsDefault() {
		jid = types.EmptyJID
		isDefault = true
	} else {
		isDefault = false
		jid, err = types.ParseJID(aclEntry.JID)
		if err != nil {
			return nil, err
		}
	}
	if _, ok := pb.GroupPermission_name[aclEntry.Permission]; !ok {
		return nil, fmt.Errorf("Unknown permission value: %d", aclEntry.Permission)
	}
	return &pb.GroupACL{
		JID:        JIDToProto(jid),
		Permission: pb.GroupPermission(aclEntry.Permission),
		UpdatedAt:  timestamppb.New(aclEntry.UpdatedAt),
		IsDefault:  isDefault,
	}, nil
}

type ACLStore struct {
	db  *sql.DB
	log waLog.Logger

	defaultACLEntry *ACLEntry
}

func NewACLStore(db *sql.DB, log waLog.Logger) *ACLStore {
	log.Debugf("Starting now ACLStore")
	acls := &ACLStore{db: db, log: log}
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

func (acls *ACLStore) SetDefault(permission *pb.GroupPermission) error {
	acls.defaultACLEntry = nil
	return acls.setByString(defaultJID, permission)
}

func (acls *ACLStore) SetByJID(jid *types.JID, permission *pb.GroupPermission) error {
	if jid.IsEmpty() {
		return errors.New("Cannot set ACL for empty JID")
	}
	jidStr := jid.ToNonAD().String()
	return acls.setByString(jidStr, permission)
}

func (acls *ACLStore) GetDefault() (*ACLEntry, error) {
	if acls.defaultACLEntry != nil {
		return acls.defaultACLEntry, nil
	}
	aclEntry, err := acls.GetByJID(&types.EmptyJID)
	if err != nil {
		return nil, err
	}
	acls.defaultACLEntry = aclEntry
	return aclEntry, nil
}

func (acls *ACLStore) setByString(jidStr string, permission *pb.GroupPermission) error {
	_, err := acls.db.Exec(`REPLACE INTO
        aclstore_permissions (jid, permission, updatedAt)
        VALUES($1, $2, $3)`,
		jidStr,
		permission.Number(),
		time.Now().Unix(),
	)
	return err
}

func (acls *ACLStore) GetByJID(jid *types.JID) (*ACLEntry, error) {
	var jidStr string
	permission := &ACLEntry{}
	if jid.IsEmpty() {
		jidStr = defaultJID
	} else {
		jidStr = jid.ToNonAD().String()
	}
	row := acls.db.QueryRow(`
        SELECT
            JID, permission, updatedAt
        FROM aclstore_permissions
        WHERE jid = $1`,
		jidStr,
	)
	if row.Err() != nil {
		return nil, row.Err()
	}

	err := row.Scan(&permission.JID, &permission.Permission, &permission.UpdatedAt)
	if err == sql.ErrNoRows {
		if jidStr == defaultJID {
			return &ACLEntry{}, nil
		}
		return acls.GetDefault()
	} else if err != nil {
		return nil, err
	}
	return permission, nil
}

func (acls *ACLStore) GetAll() ([]*ACLEntry, error) {
	aclEntries := make([]*ACLEntry, 0)
	query, err := acls.db.Query(`
        SELECT
            JID, permission, updatedAt
        FROM aclstore_permissions
        WHERE jid != $1
    `, defaultJID)
	if err != nil {
		return nil, err
	}
	defer query.Close()

	for query.Next() {
		row := &ACLEntry{}
		if err := query.Scan(&row.JID, &row.Permission, &row.UpdatedAt); err != nil {
			return nil, err
		}
		aclEntries = append(aclEntries, row)
	}
	return aclEntries, nil

}
