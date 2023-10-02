package whatupcore2

import (
	"database/sql"

	pb "github.com/digital-witness-lab/whatup/protos"
	waLog "go.mau.fi/whatsmeow/util/log"
)

type ACLStore struct {
    db *sql.DB
    log waLog.Logger
}

func NewACLStore(db *sql.DB, log waLog.Logger) *ACLStore {
    log.Debugf("Starting now ACLStore")
    acls := &ACLStore{db: db, log:log}
    acls.Upgrade()
}

func (acls *ACLStore) Upgrade() error {
    _, err := // CREATE THE NEEDED TABLES HERE + TABLE TO STORE ACL VERSION TO TRACK ANY NECISSARY UPGRADES
}

func (acls *ACLStore) SetDefaultACL(permission *pb.GroupPermission) *pb.GroupPermission {
    pb.GroupPermission
    return nil
}
