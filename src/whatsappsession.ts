import makeWASocket, { Browsers, ConnectionState, DisconnectReason, GroupMetadata, MessageRetryMap, MessageUpsertType, useMultiFileAuthState, WAMessage, WASocket } from '@adiwajshing/baileys'
import { Boom } from '@hapi/boom'
import { EventEmitter } from 'events'

import { WhatsAppACLConfig, WhatsAppACL, NoAccessError } from './whatsappacl'
import { sleep } from './utils'

export interface GroupJoinResponse {metadata: GroupMetadata, response?: string }

export interface WhatsAppSessionInterface {
  init: () => Promise<void>
  qrCode: () => string | undefined
  sendMessage: (chatId: string, message: string, clearChatStatus: boolean, vampMaxSeconds: number | undefined) => Promise<void>
  markChatRead: (chatId: string) => Promise<void>
  joinGroup: (inviteCode: string) => Promise<GroupJoinResponse | null>
  groupMetadata: (chatId: string) => Promise<GroupMetadata | null>
}

export interface WhatsAppSessionConfig {
  acl?: WhatsAppACLConfig
  authString?: string
}

export class WhatsAppSession extends EventEmitter implements WhatsAppSessionInterface {
  protected sock?: WASocket = undefined
  protected config: WhatsAppSessionConfig = {}
  protected msgRetryCounterMap: MessageRetryMap = { }
  protected lastConnectionState: Partial<ConnectionState> = {}
  protected _lastMessage: { [_: string]: WAMessage } = {}

  protected acl: WhatsAppACL

  constructor (config: Partial<WhatsAppSessionConfig>) {
    super()
    this.config = config
    this.acl = new WhatsAppACL(config.acl)
  }

  async init (): Promise<void> {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
    this.sock = makeWASocket({
      browser: Browsers.macOS('Desktop'),
      auth: state
    })

    this.sock.ev.on('creds.update', saveCreds)
    this.sock.ev.on('connection.update', this._updateConnectionState.bind(this))
    this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this))
  }

  private async _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType }): Promise<void> {
    const { messages, type } = data
    for (const message of messages) {
      const chatId: string | null | undefined = message.key?.remoteJid
      if (chatId == null || !this.acl.canRead(chatId)) {
        continue
      }
      if (this._lastMessage[chatId] == null || this._lastMessage[chatId].key?.id < message.key?.id) {
        this._lastMessage[chatId] = message
      }
      if (message.key?.fromMe === false) {
        this.emit('message', { message, type })
        console.log(`Got message: ${JSON.stringify(message)}`)

        if (message.key?.remoteJid != null) {
          await this.sendMessage(message.key?.remoteJid, 'hello?')
        }
      }
    }
  }

  private async _updateConnectionState (data: Partial<ConnectionState>): Promise<void> {
    if (data.qr !== this.lastConnectionState.qr) {
      this.emit('qrCode', data)
    }
    if (data.connection === 'open') {
      this.emit('ready', data)
    } else if (data.connection !== undefined) {
      this.emit('closed', data)
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

  qrCode (): string | undefined {
    return this.lastConnectionState.qr
  }

  async sendMessage (chatId: string, message: string, clearChatStatus: boolean = true, vampMaxSeconds: number | undefined = 10): Promise<void> {
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
    await this.sock?.sendMessage(chatId, { text: message })
  }

  async markChatRead (chatId: string): Promise<void> {
    if (!this.acl.canWrite(chatId)) {
      throw new NoAccessError('write', chatId)
    }
    const msg: WAMessage | undefined = this._lastMessage[chatId]
    if ((msg?.key) != null) {
      await this.sock?.chatModify({ markRead: false, lastMessages: [msg] }, chatId)
    }
  }

  async joinGroup (inviteCode: string): Promise<GroupJoinResponse | null> {
    if (this.sock == null) return null
    const metadata = await this.sock.groupGetInviteInfo(inviteCode)
    if (!this.acl.canRead(metadata.id)) {
      throw new NoAccessError('read', metadata.id)
    }
    const response = await this.sock.groupAcceptInvite(inviteCode)
    return { metadata, response }
  }

  async groupMetadata (chatId: string): Promise<GroupMetadata | null> {
    if (this.sock == null) return null
    if (!this.acl.canRead(chatId)) {
      throw new NoAccessError('read', chatId)
    }
    return await this.sock.groupMetadata(chatId)
  }
}
