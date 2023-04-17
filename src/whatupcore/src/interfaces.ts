import crypto from 'crypto'

import { AuthenticationCreds, WASocket, WAMessage, GroupMetadata, Contact, Chat } from '@adiwajshing/baileys'

import { WhatsAppSession } from './whatsappsession'

export interface WhatsAppACLConfig {
  allowAll: boolean
  canWrite: string[]
  canRead: string[]
  canReadWrite: string[]
}

export interface AuthenticationData {
  creds: AuthenticationCreds
  keys: { [_: string]: any }
}

export interface WhatsAppSessionLocator {
  sessionId: string
  passphrase: string
  isNew?: boolean
}

export interface DataRecord {
  authData: AuthenticationData | null
  aclConfig: Partial<WhatsAppACLConfig>
}

export interface Keys {
  publicKey: crypto.KeyObject
  privateKey?: crypto.KeyObject
}

export interface SessionStorageOptions {
  datadir: string
  loadRecord: boolean
}

export interface SessionOptions {
  sharedConnection?: boolean
  sendMessageHistory?: boolean
}

export interface AuthenticateSessionParams {
  sessionLocator: WhatsAppSessionLocator
  sessionOptions?: SessionOptions
}

export interface SharedSession {
  session: WhatsAppSession
  name: string
  numListeners: number
  anonymous: boolean
  hasReadMessageHandler?: boolean
}

export interface WhatsAppStoreInterface {
  bind: (sock: WASocket) => void
  contacts: () => Contact[]
  chats: () => Chat[]
  groups: () => GroupMetadata[]
  contact: (cid: string) => Contact | undefined
  setChat: (chat: Chat) => Chat | undefined
  setGroupMetadata: (groupMetadata: GroupMetadata) => GroupMetadata | undefined
  lastMessage: (chatId: string) => WAMessage | undefined
  groupMetadata: (chatId: string) => Promise<GroupMetadata | undefined>
}

export interface GroupJoinResponse {metadata: GroupMetadata, response?: string }

export interface WhatsAppSessionInterface {
  init: () => Promise<void>
  qrCode: () => string | undefined
  connection: () => string | undefined

  emitMessageHistory: () => Promise<void>
  sendMessage: (chatId: string, message: string, clearChatStatus: boolean, vampMaxSeconds: number | undefined) => Promise<WAMessage | undefined>
  markChatRead: (chatId: string) => Promise<void>
  joinGroup: (inviteCode: string) => Promise<GroupJoinResponse | undefined | null>
  groupMetadata: (chatId: string) => Promise<GroupMetadata | undefined>
  groupInviteMetadata: (inviteCode: string) => Promise<GroupMetadata | undefined | null>
  groups: () => GroupMetadata[]
}

