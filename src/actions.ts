export declare enum ACTIONS {
  writeMarkChatRead = 'write:markChatRead',
  writeSendMessage = 'write:sendMessage',
  writeLeaveGroup = 'write:leaveGroup',

  readMessagesSubscribe = 'read:messages:subscribe',
  readMessages = 'read:messages',
  readGroupInviteMetadata = 'read:groupInviteMetadata',
  readGroupMetadata = 'read:groupMetadata',
  readJoinGroup = 'read:joinGroup',
  readListGroups = 'read:listGroups',

  connectionAuthAnonymous = 'connection:auth:anonymous',
  connectionStatus = 'connection:status',
  connectionReady = 'connection:ready',
  connectionClosed = 'connection:closed',
  connectionQr = 'connection:qr',
  connectionAuth = 'connection:auth'
}
