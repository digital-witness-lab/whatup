export enum ACTIONS {
  writeMarkChatRead = 'write_chat_markRead',
  writeSendMessage = 'write_messages_send',
  writeLeaveGroup = 'write_group_leave',

  readMessagesSubscribe = 'read_messages_subscribe',
  readMessagesUnSubscribe = 'read_messages_unsubscribe',
  readMessages = 'read_messages',
  readDownloadMessage = 'read_messages_downloadMedia',

  readGroupInviteMetadata = 'read_groups_inviteMetadata',
  readGroupMetadata = 'read_groups_metadata',
  readJoinGroup = 'read_groups_join',
  readListGroups = 'read_groups_list',

  connectionAuthAnonymous = 'connection_auth_anonymous',
  connectionAuth = 'connection_auth',
  connectionAuthLocator = 'connection_auth_locator',
  connectionStatus = 'connection_status',
  connectionReady = 'connection_ready',
  connectionClosed = 'connection_closed',
  connectionQr = 'connection_qr',
}
