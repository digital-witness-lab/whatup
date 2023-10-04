package whatupcore2

import (
	"database/sql"
	"testing"

	pb "github.com/digital-witness-lab/whatup/protos"
	waLog "go.mau.fi/whatsmeow/util/log"
)

func createDb() *sql.DB {
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        panic(err)
    }
    return db
}

func createACL() *ACLStore {
    log := waLog.Stdout("acltest", "DEBUG", true)
    db := createDb()
    return NewACLStore(db, log)
}

func TestDefault(t *testing.T) {
    acl := createACL()

    for _, permission_num := range pb.GroupPermission_value {
        permission := pb.GroupPermission(permission_num)
        err := acl.SetDefaultACL(&permission)
        if err != nil {
            t.Fatalf("Could not set default acl: %s", err)
        }
        foundPermission, err := acl.GetDefaultACL()
        if err != nil {
            t.Fatal(err)
        }
        foundPermissionNum := int32(foundPermission.Permission.Number())
        if  foundPermissionNum != permission_num {
            t.Fatalf("Mismatched default permission: %d: %d", foundPermissionNum, permission_num)
        }
    }
}
