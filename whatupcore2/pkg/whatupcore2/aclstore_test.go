package whatupcore2

import (
	"database/sql"
	"fmt"
	"testing"

	pb "github.com/digital-witness-lab/whatup/protos"
	"go.mau.fi/whatsmeow/types"
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
		err := acl.SetDefault(&permission)
		if err != nil {
			t.Fatalf("Could not set default acl: %s", err)
		}
		foundPermission, err := acl.GetDefault()
		if err != nil {
			t.Fatal(err)
		}
		foundPermissionNum := int32(foundPermission.Permission)
		if foundPermissionNum != permission_num {
			t.Fatalf("Mismatched default permission: %d: %d", foundPermissionNum, permission_num)
		}
	}
}

func TestJIDs(t *testing.T) {
	acl := createACL()

	var err error
	defaultPermission := pb.GroupPermission(2)
	permission := pb.GroupPermission(1)

	acl.SetDefault(&defaultPermission)

	err = acl.SetByJID(&types.EmptyJID, &permission)
	if err == nil {
		t.Fatalf("Should not be allowed to set empty JID ACL value")
	}

	adJID := types.NewADJID("useruser", 5, 5)
	nonAdJID := adJID.ToNonAD()
	err = acl.SetByJID(&adJID, &permission)
	if err != nil {
		t.Fatalf("Should not have errored: %s", err)
	}
	perm, err := acl.GetByJID(&nonAdJID)
	foundPerm := perm.Permission
	if foundPerm != int32(permission.Number()) {
		t.Fatalf("Should have seen the same permission: %d: %d", foundPerm, permission.Number())
	}

	uniqueJID := types.NewJID("uniqueJID", types.GroupServer)
	perm, err = acl.GetByJID(&uniqueJID)
	foundPerm = perm.Permission
	if foundPerm != int32(defaultPermission.Number()) {
		t.Fatalf("Did not correctly set default permission: %d: %d", foundPerm, defaultPermission.Number())
	}
}

func TestListACL(t *testing.T) {
	acl := createACL()

	aclValues, err := acl.GetAll()
	if err != nil {
		t.Fatalf("Error getting all ACLs: %s", err)
	}
	if L := len(aclValues); L != 0 {
		t.Fatalf("ACL Should be empty, found n_rows: %d", L)
	}

	permissions := make([]*pb.GroupPermission, 0)
	for _, permission_num := range pb.GroupPermission_value {
		permission := pb.GroupPermission(permission_num)
		permissions = append(permissions, &permission)
	}

	for i := 1; i < 100; i += 1 {
		uniqueJID := types.NewJID(fmt.Sprintf("user-%d", i), types.GroupServer)
		permission := permissions[i%len(permissions)]
		err := acl.SetByJID(&uniqueJID, permission)
		if err != nil {
			t.Fatalf("Error setting permission: %v: %v", uniqueJID, *permission)
		}

		aclValues, err := acl.GetAll()
		if err != nil {
			t.Fatalf("Error getting all ACLs: %s", err)
		}
		if L := len(aclValues); L != i {
			t.Fatalf("ACL doesn't have expected # rows: %d: %d", i, L)
		}
	}
}
