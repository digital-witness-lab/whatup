 # AUTOGENERATED BY actions.py. DO NOT MODIFY BY HAND
import json
import base64
import typing as T
source_hash='13d89cc20eea0fe307aae1f353ba9fd788c3cd8fd87823bf2ba285a08187dfda'
write_mark_chat_read = 'write_chat_markRead'
write_send_message = 'write_messages_send'
write_leave_group = 'write_group_leave'
read_messages_subscribe = 'read_messages_subscribe'
read_messages_un_subscribe = 'read_messages_unsubscribe'
read_messages = 'read_messages'
read_download_message = 'read_messages_downloadMedia'
read_group_invite_metadata = 'read_groups_inviteMetadata'
read_group_metadata = 'read_groups_metadata'
read_join_group = 'read_groups_join'
read_list_groups = 'read_groups_list'
connection_auth_anonymous = 'connection_auth_anonymous'
connection_auth = 'connection_auth'
connection_auth_locator = 'connection_auth_locator'
connection_status = 'connection_status'
connection_ready = 'connection_ready'
connection_closed = 'connection_closed'
connection_qr = 'connection_qr'
actions_enc=b'FCH7ESJ9EHILURB1E9LLUOR8C5Q5USJ5C5I24EH049RN4QBKCLFM6Q31EHFMQOBIDD96AOB448M208JNE9KN8PAVEDIMSP2VDLIN6SR1CTII4EH049RN4QBKCLFMQPBJEDGMEPBJBTPMARJ448M208JNE9KN8PAVDHIM2TJ5BTJN4RRLE0H3K812ETP6IT35BTJN4RRLE1FMOPB1EPII4B1049P6AOB4BTMMASRJC5JMASQVEDQM4SR3E9KM4P9278G24SJ5C5I5URB5EDPM2PR5EDFN6TB2EDHN4QB2CKH2O812E9IM2P2VDLIN6SR1CTIN6NRLDPFN6TB2EDHN4QB2CKH3K812E9IM2P2VDLIN6SR1CTIN6NRLDPPNAOJJCDP6IOJ548M208JICLGM8NRDCLPN6OB7CLPI4EH049P6AOB4BTMMASRJC5JMASP25GG24SJ5C5I5UP3FETN6ORR1CHFMQPBJEDGMEP9278G24SJ5C5I5URB5EDPM2PR5EDFM8RRNDPM6UOB49LIM8QB148M208JICLGM8NR7E9NNAS2VD5N7CQBKCLFMQPBKC5I62T3148T208JICLGM8NR7E9NNAS3JBTKMSTJ9EHIKQPBKC5I62T3148M208JICLGM8NR7E9NNAS2VDLIN8OB4C5Q628HQ40H74PB1CHFMESJFELO76NRDCLQ62P31EHGI4B1049P6AOB4BTL6UQBEBTJN4RRLE0H3K812E9IM2P2VCTP6UTBGEDFMKRR9DOH2O812E9IM2P2VDHKN6T2VCTP6UTBGECH3K812E9IM2P2VCTP6UTBGEDFMOQBJEGH2O812CDNMSRJ5CDQ6IRREBTGNAT38BTGMSRREF5MMUTBJ48T208J3DTN6SPB3EHKMURIVC5QN8Q2VC5N6URJPDLNNASP25GG24ORFDPN6AORKD5NMSNR1ELQ6G8HQ40H66RREDPIM6T39DTN5UOBLEHK24B1049HMURJECLHN8QBFDPFM2TBKD1FMORR3C5Q6USH278G24ORFDPN6AORKD5NMSNR1ELQ6GNRCDTHM2T3FE8H2O812CDNMSRJ5CDQ6IRREBTPN8OBKELPI4EH049HMURJECLHN8QBFDPFN6T31EHQN68HC40H66RREDPIM6T39DTN5USJ5C5I7I8HQ40H66RREDPIM6T39DTN5USJ5C5I7I8HC40H66RREDPIM6T39DTN5UORCDTPMAP1278G24ORFDPN6AORKD5NMSNR3DHNN6PB448M208J3DTN6SPB3EHKMURIVE5P24EH049HMURJECLHN8QBFDPFN2SH2FK======'
events_enc=b'FCH7ESJ9EHILUOR8C5Q5URB1E9LL4PB1CGH3K812ETP6IT35BTMM2SJBBTHMGOBKBTP6AOB448M208JNE9KN8PAVDLIN6SR1CTIN6NRJCLN688HQ40H7ESJ9EHILUSR5DPI5URB5EDPM2PR548M208JNE9KN8PAVCTP6UTBGBTM6AOBMCKH3K812ETP6IT35BTM6AOBMCLFMESJFELO24B1049P6AOB4BTMMASRJC5JMASQVEDQM4SR3E9KM4P9278G24SJ5C5I5URB5EDPM2PR5EDFN6TB2EDHN4QB2CKH2O812E9IM2P2VDLIN6SR1CTIN6NRLDPPNAOJJCDP6IOJ548T208JICLGM8NRDCLPN6OB7CLPLUTBEBTPNAOJJCDP6IOJ548M208JICLGM8NRDCLPN6OB7CLPI4EH049P6AOB4BTMMASRJC5JMASP25GG24SJ5C5I5URB5EDPM2PR5EDFM8RRNDPM6UOB49LIM8QB148T208JICLGM8NR4DTRMSR3FC5I5URB5EDPM2PR548M208JICLGM8NR7E9NNAS3JBTKMSTJ9EHIKQPBKC5I62T3148T208JICLGM8NR7E9NNAS2VD5N7CQBKCLFMQPBKC5I62T3148M208JICLGM8NR7E9NNAS3JBTMMAT31CHGN8O9278G24SJ5C5I5UPRIDTQN0NRDCLQ62P31EHGI4B1049P6AOB4BTJN4RRLE1PLUQJFD5N24EH049P6AOB4BTL6UQBEBTJN4RRLE0H2O812E9IM2P2VCTP6UTBGEDFMOQBJEGH3K812E9IM2P2VDHKN6T2VCTP6UTBGECH2O812CDNMSRJ5CDQ6IRREBTGNAT38BTGMSRREF5MMUTBJ48T208J3DTN6SPB3EHKMURIVC5QN8Q2VC5N6URJPDLNNASP25GG24ORFDPN6AORKD5NMSNR1ELQ6G8HQ40H66RREDPIM6T39DTN5UOBLEHK24B1049HMURJECLHN8QBFDPFM2TBKD1FMORR3C5Q6USH278G24ORFDPN6AORKD5NMSNR1ELQ6GNRCDTHM2T3FE8H2O812CDNMSRJ5CDQ6IRREBTPN8OBKELPI4EH049HMURJECLHN8QBFDPFN6T31EHQN68HC40H66RREDPIM6T39DTN5USJ5C5I7I8HQ40H66RREDPIM6T39DTN5USJ5C5I7I8HC40H66RREDPIM6T39DTN5UORCDTPMAP1278G24ORFDPN6AORKD5NMSNR3DHNN6PB448M208J3DTN6SPB3EHKMURIVE5P24EH049HMURJECLHN8QBFDPFN2SH2FK======'
ACTIONS: T.Dict[str, str] = json.loads(base64.b32hexdecode(actions_enc))
EVENTS: T.Dict[str, str] = json.loads(base64.b32hexdecode(events_enc))
