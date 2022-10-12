import makeWASocket, { fetchLatestBaileysVersion, Browsers, ConnectionState, Contact, Chat, DisconnectReason, GroupMetadata, MessageRetryMap, MessageUpsertType, useSingleFileAuthState, WAMessage, WASocket } from '@adiwajshing/baileys'
import { Boom } from '@hapi/boom'
import { EventEmitter } from 'events'

import { WhatsAppACLConfig, WhatsAppACL, NoAccessError } from './whatsappacl'
import { WhatsAppAuth, AuthenticationData } from './whatsappauth'
import { WhatsAppStore } from './whatsappstore'
import { sleep } from './utils'

export interface GroupJoinResponse {metadata: GroupMetadata, response?: string }

export interface WhatsAppSessionInterface {
  init: () => Promise<void>
  qrCode: () => string | undefined
  connection: () => string | undefined

  sendMessage: (chatId: string, message: string, clearChatStatus: boolean, vampMaxSeconds: number | undefined) => Promise<WAMessage | undefined>
  markChatRead: (chatId: string) => Promise<void>
  joinGroup: (inviteCode: string) => Promise<GroupJoinResponse | undefined | null>
  groupMetadata: (chatId: string) => Promise<GroupMetadata | undefined>
  groupInviteMetadata: (inviteCode: string) => Promise<GroupMetadata | undefined | null>
}

export interface WhatsAppSessionConfig {
  acl?: Partial<WhatsAppACLConfig>
  authData?: AuthenticationData
}

export class WhatsAppSession extends EventEmitter implements WhatsAppSessionInterface {
  public uid: string
  protected sock?: WASocket = undefined
  protected config: WhatsAppSessionConfig = {}
  protected msgRetryCounterMap: MessageRetryMap = { }
  protected lastConnectionState: Partial<ConnectionState> = {}

  protected acl: WhatsAppACL
  // @ts-expect-error: TS2564: this.auth is definitly initialized in
  //                   `constructor()` through the call to `this.setAuth`
  protected auth: WhatsAppAuth
  protected store: WhatsAppStore

  constructor (config: Partial<WhatsAppSessionConfig>) {
    super()
    this.uid = `WS-${Math.floor(Math.random() * 10000000)}`
    console.log(`${this.uid}: Constructing session`)
    this.config = config
    this.acl = new WhatsAppACL(config.acl)
    this.setAuth(new WhatsAppAuth(this.config.authData))
    this.store = new WhatsAppStore(this.acl)
  }

  setAuth (auth: WhatsAppAuth): void {
    this.auth = auth
    this.auth.on('state:update', (auth) => this.emit('connection:auth', auth))
  }

  async init (): Promise<void> {
    const { version } = await fetchLatestBaileysVersion()
    this.sock = makeWASocket({
      version,
      msgRetryCounterMap: this.msgRetryCounterMap,
      markOnlineOnConnect: false,
      auth: this.auth.getAuth(),

      browser: Browsers.macOS('Desktop'),
      downloadHistory: true,
      syncFullHistory: true
    })
    this.store.bind(this.sock)

    this.sock.ev.on('creds.update', () => {
      this.auth.update()
    })
    this.sock.ev.on('connection.update', this._updateConnectionState.bind(this))
    this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this))
  }

  async close (): Promise<void> {
    console.log(`${this.uid}: Closing session`)
    this.sock?.end(undefined)
  }

  private async _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType }): Promise<void> {
    const { messages, type } = data
    for (const message of messages) {
      console.log(`${this.uid}: got message`)
      const chatId: string | null | undefined = message.key?.remoteJid
      if (chatId == null || !this.acl.canRead(chatId)) {
        console.log(`${this.uid}: not can read`)
        continue
      }
      if (message.key?.fromMe === false) {
        this.emit('message', { message, type })
      }
    }
  }

  private async _updateConnectionState (data: Partial<ConnectionState>): Promise<void> {
    if (data.qr !== this.lastConnectionState.qr && data.qr != null) {
      this.emit('connection:qr', data)
    }
    if (data.connection === 'open') {
      this.emit('connection:ready', data)
    } else if (data.connection !== undefined) {
      this.emit('connection:closed', data)
      const { lastDisconnect } = data
      if (lastDisconnect != null) {
        const shouldReconnect = (lastDisconnect.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut
        if (shouldReconnect) {
          await this.init()
        }
      }
    }
    this.lastConnectionState = { ...this.lastConnectionState, ...data }
  }

  connection (): string | undefined {
    return this.lastConnectionState.connection
  }

  qrCode (): string | undefined {
    return this.lastConnectionState.qr
  }

  async sendMessage (chatId: string, message: string, clearChatStatus: boolean = true, vampMaxSeconds: number | undefined = 10): Promise<WAMessage | undefined> {
    if (!this.acl.canWrite(chatId)) {
      throw new NoAccessError('write', chatId)
    }
    if (clearChatStatus) {
      await this.markChatRead(chatId)
    }
    if (vampMaxSeconds > 0) {
      const nComposing: number = Math.floor(Math.random() * vampMaxSeconds)
      for (let i = 0; i < nComposing; i += 1) {
        await this.sock?.sendPresenceUpdate('composing', chatId)
        await sleep(Math.random() * 1000)
      }
      await this.sock?.sendPresenceUpdate('available', chatId)
    }
    return await this.sock?.sendMessage(chatId, { text: message })
  }

  async markChatRead (chatId: string): Promise<void> {
    if (!this.acl.canWrite(chatId)) {
      throw new NoAccessError('write', chatId)
    }
    const msg: WAMessage | undefined = this.store.lastMessage(chatId)
    if ((msg?.key) != null) {
      await this.sock?.chatModify({ markRead: false, lastMessages: [msg] }, chatId)
    }
  }

  async joinGroup (inviteCode: string): Promise<GroupJoinResponse | undefined | null> {
    if (this.sock == null) return null
    const metadata: GroupMetadata | undefined | null = await this.groupInviteMetadata(inviteCode)
    if (metadata == null) return undefined
    if (!this.acl.canRead(metadata?.id)) {
      throw new NoAccessError('read', metadata?.id)
    }
    this.store.setGroupMetadata(metadata)
    const response = await this.sock.groupAcceptInvite(inviteCode)
    return { metadata, response }
  }

  async leaveGroup (chatId: string): Promise<GroupMetadata | undefined | null > {
    if (this.sock == null) return null
    const groupMetadata: GroupMetadata | undefined = await this.store.groupMetadata(chatId)
    await this.sock.groupLeave(chatId)
    return groupMetadata
  }

  async groupInviteMetadata (inviteCode: string): Promise<GroupMetadata | undefined | null> {
    if (this.sock == null) return null
    const metadata: GroupMetadata = await this.sock.groupGetInviteInfo(inviteCode)
    return metadata
  }

  async groupMetadata (chatId: string): Promise<GroupMetadata | undefined> {
    if (!this.acl.canRead(chatId)) {
      throw new NoAccessError('read', chatId)
    }
    return await this.store.groupMetadata(chatId)
  }
}
