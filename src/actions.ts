export enum ACTIONS {
  writeMarkChatRead = 'write:chat:markRead',
  writeSendMessage = 'write:messages:send',
  writeLeaveGroup = 'write:group:leave',

  readMessagesSubscribe = 'read:messages:subscribe',
  readMessagesUnSubscribe = 'read:messages:unsubscribe',
  readMessages = 'read:messages',
  readDownloadMessage = 'read:messages:downloadMedia',

  readGroupInviteMetadata = 'read:groups:inviteMetadata',
  readGroupMetadata = 'read:groups:metadata',
  readJoinGroup = 'read:groups:join',
  readListGroups = 'read:groups:list',

  connectionAuthAnonymous = 'connection:auth:anonymous',
  connectionAuth = 'connection:auth',
  connectionAuthLocator = 'connection:auth:locator',
  connectionStatus = 'connection:status',
  connectionReady = 'connection:ready',
  connectionClosed = 'connection:closed',
  connectionQr = 'connection:qr',
}
