package main

import (
	"fmt"
	"hash/fnv"
	"regexp"
	"strings"

	"github.com/nyaruka/phonenumbers"
)

const HASH_LEN = 4

type CleanerFunc func(string) string

func phoneNumberCleaner() CleanerFunc {
	phoneRegex := regexp.MustCompile(`\b[0-9]{11,15}\b`)

	return func(line string) string {
		return phoneRegex.ReplaceAllStringFunc(line, func(phoneNumber string) string {
			number, err := phonenumbers.Parse(phoneNumber, "IN")
			if err != nil || !phonenumbers.IsPossibleNumber(number) {
				return phoneNumber
			}

			// Compute FNV hash of the phone number
			hash := fnv.New32a()
			hash.Write([]byte(phoneNumber))
			hashValue := hash.Sum32()

			hashHex := fmt.Sprintf("%x", hashValue)[:HASH_LEN]
			return fmt.Sprintf("[TEL-%s]", hashHex)
		})
	}
}

func notifyAttribCleaner() CleanerFunc {
	notifyAttrib := regexp.MustCompile(`(notify|subject|display_name|companion_enc_static)="[^"]+"`)

	return func(line string) string {
		return notifyAttrib.ReplaceAllStringFunc(line, func(attribute string) string {
			// Compute FNV hash of the field
			hash := fnv.New32a()
			hash.Write([]byte(attribute))
			hashValue := hash.Sum32()

			attributeName := strings.SplitN(attribute, "=", 2)[0]
			hashHex := fmt.Sprintf("%x", hashValue)[:HASH_LEN]
			return fmt.Sprintf(`%s="[ATTRIB-%s]"`, attributeName, hashHex)
		})
	}
}

func notifyBodyCleaner() CleanerFunc {
	notifyBody := regexp.MustCompile(`(<notification.*>)([0-9a-f]{4})[0-9a-f]+<`)

	return func(line string) string {
		return notifyBody.ReplaceAllString(line, `$1[NBODY-$2]<`)
	}
}
