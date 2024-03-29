package main

import "testing"

type TestCase struct {
	name     string
	input    string
	expected string
}

func runTestCases(t *testing.T, cleaner CleanerFunc, cases []TestCase) {
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			output := cleaner(tc.input)
			if output != tc.expected {
				t.Errorf("Failed %s: Expected \n%s\ngot\n%s", tc.name, tc.expected, output)
			}
		})
	}
}

func TestPhoneNumberCleaner(t *testing.T) {
	cases := []TestCase{
		{
			name:     "No phone numbers",
			input:    "This is a test string without phone numbers.",
			expected: "This is a test string without phone numbers.",
		},
		{
			name:     "Log Example",
			input:    "[RPC/SM/test/WAC/WMC WARN] Error decrypting message from 918239472156:11@s.whatsapp.net in 914791823791-1579955702@g.us: failed to decrypt group message: no sender key for 918239472156:11 in 914791823791-1579955702@g.us",
			expected: "[RPC/SM/test/WAC/WMC WARN] Error decrypting message from [TEL-5fff]:11@s.whatsapp.net in [TEL-fb88]-1579955702@g.us: failed to decrypt group message: no sender key for [TEL-5fff]:11 in [TEL-fb88]-1579955702@g.us",
		},
		{
			name:     "Non-Phone group name",
			input:    "Updating group: 128329472347918238@g.us",
			expected: "Updating group: 128329472347918238@g.us",
		},
	}

	cleaner := phoneNumberCleaner()
	runTestCases(t, cleaner, cases)
}

func BenchmarkPhoneNumberCleaner(b *testing.B) {
	strings := []string{
		"This is a test string without phone numbers.",
		"[RPC/SM/test/WAC/WMC WARN] Error decrypting message from 918239472156:11@s.whatsapp.net in 914791823791-1579955702@g.us: failed to decrypt group message: no sender key for 918239472156:11 in 914791823791-1579955702@g.us",
		"Updating group: 128329472347918238@g.us",
	}
	cleaner := phoneNumberCleaner()
	for n := 0; n < b.N; n++ {
		cleaner(strings[n%len(strings)])
	}
}

func TestNotifyAttribCleaner(t *testing.T) {
	cases := []TestCase{
		{
			name:     "No notification",
			input:    "This is a test string without phone numbers.",
			expected: "This is a test string without phone numbers.",
		},
		{
			name:     "Simple Notification - Notify Field",
			input:    `<notification id="8937492381" notify="REDACT THIS 😊" offline="0" t="1823947234" type="picture"><set hash="09U/"/></notification>`,
			expected: `<notification id="8937492381" notify="[ATTRIB-da9b]" offline="0" t="1823947234" type="picture"><set hash="09U/"/></notification>`,
		},
		{
			name:     "Simple Notification - Subject Field",
			input:    `<iq from="g.us" id="148.54-3" type="result"><groups><group a_v_id="234234" addressing_mode="pn" creation="1699979993" creator="[TEL-d4c7]@s.whatsapp.net" id="111111111111111111" p_v_id="2222222222222222" s_o="[TEL-d4c7]@s.whatsapp.net" s_t="1699979993" subject="Blah blah">`,
			expected: `<iq from="g.us" id="148.54-3" type="result"><groups><group a_v_id="234234" addressing_mode="pn" creation="1699979993" creator="[TEL-d4c7]@s.whatsapp.net" id="111111111111111111" p_v_id="2222222222222222" s_o="[TEL-d4c7]@s.whatsapp.net" s_t="1699979993" subject="[ATTRIB-c751]">`,
		},
		{
			name:     "Simple Notification - Display Name",
			input:    `<success abprops="8" companion_enc_static="ifdsafdsafsd" creation="1234234233" display_name="+23948234287" lid="18234235214236:18@lid" location="vll" props="27" t="1711713012"/>`,
			expected: `<success abprops="8" companion_enc_static="[ATTRIB-be63]" creation="1234234233" display_name="[ATTRIB-fec2]" lid="18234235214236:18@lid" location="vll" props="27" t="1711713012"/>`,
		},
	}

	cleaner := notifyAttribCleaner()
	runTestCases(t, cleaner, cases)
}

func TestNotifyBodyCleaner(t *testing.T) {
	cases := []TestCase{
		{
			name:     "No notification",
			input:    "This is a test string without phone numbers.",
			expected: "This is a test string without phone numbers.",
		},
		{
			name:     "Simple Notification",
			input:    `<notification from="XXXXX@s.whatsapp.net"><add device_hash="XXXXX"><device><key-index-list>0a14088fea9e97011086c99ab006180122020001280012406fb7dd1289347234892358ac0b8714d4d2a750b70ed9a6a4f97fb102e95d3d37a5caabf4973d11635be8eeaa0a331170a710d</key-index-list></add></notification>`,
			expected: `<notification from="XXXXX@s.whatsapp.net"><add device_hash="XXXXX"><device><key-index-list>[NBODY-0a14]</key-index-list></add></notification>`,
		},
	}

	cleaner := notifyBodyCleaner()
	runTestCases(t, cleaner, cases)
}
