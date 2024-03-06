package whatupcore2

import (
	"database/sql"
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
}

func TestCache(t *testing.T) {
	acl := createACL("user1")

	JIDs := []types.JID{
		types.NewJID("jid1", types.GroupServer),
		types.NewJID("jid2", types.GroupServer),
		types.NewJID("asdf-jid3", types.GroupServer),
		types.NewJID("asdf-jid3", types.GroupServer),
	}

	permission := pb.GroupPermission(1)

	for _, jid := range JIDs {
		acl.SetByJID(&jid, &permission)
	}

	cache, err := acl.CachedLookup()
	if err != nil {
		t.Fatal(err)
	}

	for _, jid := range JIDs {
		entry, found := cache.GetByJID(&jid)
		if !found {
			t.Fatalf("Should have found cached ACL value: %s", jid.String())
		}
		if entry.Permission != 1 {
			t.Fatalf("Incorrect permission found in cache: %d != %d", entry.Permission, 1)
		}
	}

	unkJID := types.NewJID("sdfjaoifhasifhsadkjfs", types.DefaultUserServer)
	_, found := cache.GetByJID(&unkJID)
	if found {
		t.Fatalf("Should not have found unknown JID: %s", unkJID.String())
	}
}
