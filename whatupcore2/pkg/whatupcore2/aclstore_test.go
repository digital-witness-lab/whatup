package whatupcore2

import (
	"database/sql"
	"fmt"
	"testing"

	pb "github.com/digital-witness-lab/whatup/protos"
	_ "github.com/mattn/go-sqlite3"
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

func createACL(username string) *ACLStore {
	log := waLog.Stdout("acltest", "DEBUG", true)
	db := createDb()
	return NewACLStore(db, username, log)
}

func TestDefault(t *testing.T) {
	acl := createACL("username")

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

		if !foundPermission.IsDefault() {
			t.Fatalf("IsDefault is not set properly: %t", foundPermission.IsDefault())
		}
	}
}

func TestJIDs(t *testing.T) {
	acl := createACL("username")

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

func TestMutliUser(t *testing.T) {
	acl1 := createACL("user1")
	acl2 := createACL("user2")

	JID1 := types.NewJID("jid1", types.GroupServer)
	JID2 := types.NewJID("jid2", types.GroupServer)

	permission1 := pb.GroupPermission(1)
	permission2 := pb.GroupPermission(2)

	acl1.SetByJID(&JID1, &permission1)
	acl2.SetByJID(&JID1, &permission2)
	acl2.SetByJID(&JID2, &permission1)

	found_11, err := acl1.GetByJID(&JID1)
	if err != nil {
		t.Fatal(err)
	}
	found_12, err := acl1.GetByJID(&JID2)
	if err != nil {
		t.Fatal(err)
	}
	found_21, err := acl2.GetByJID(&JID1)
	if err != nil {
		t.Fatal(err)
	}
	found_22, err := acl2.GetByJID(&JID2)
	if err != nil {
		t.Fatal(err)
	}

	if found_11.Permission != 1 {
		t.Fatalf("Unexpected permission found user1/jid1: %d != %d", found_11.Permission, 1)
	}
	if found_12.Permission != 0 {
		t.Fatalf("Unexpected permission found user1/jid2: %d != %d", found_11.Permission, 0)
	}
	if found_21.Permission != 2 {
		t.Fatalf("Unexpected permission found user2/jid1: %d != %d", found_21.Permission, 2)
	}
	if found_22.Permission != 1 {
		t.Fatalf("Unexpected permission found user2/jid2: %d != %d", found_22.Permission, 1)
	}

	acl1All, err := acl1.GetAll()
	if err != nil {
		t.Fatal(err)
	}
	acl2All, err := acl2.GetAll()
	if err != nil {
		t.Fatal(err)
	}

	if len(acl1All) != 1 {
		t.Fatalf("Didn't find correct number of entries for ACL1: %d", len(acl1All))
	}
	if len(acl2All) != 2 {
		t.Fatalf("Didn't find correct number of entries for ACL2: %d", len(acl2All))
	}
}

func TestListACL(t *testing.T) {
	acl := createACL("username")

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
