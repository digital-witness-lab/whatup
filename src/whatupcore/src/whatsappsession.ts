import makeWASocket, { downloadMediaMessage, fetchLatestBaileysVersion, Browsers, ConnectionState, DisconnectReason, GroupMetadata, MessageRetryMap, MessageUpsertType, WAMessage, WASocket, S_WHATSAPP_NET } from '@adiwajshing/baileys'
import { debounce } from 'tadaaa'
import { Boom } from '@hapi/boom'
import P from 'pino'
import axios from 'axios'
import { EventEmitter } from 'events'

import { WhatsAppACL, NoAccessError } from './whatsappacl'
import { WhatsAppAuth } from './whatsappauth'
import { WhatsAppStore } from './whatsappstore'
import { WhatsAppSessionStorage } from './whatsappsessionstorage'
import { ACTIONS } from './actions'
import { sleep, resolvePromiseSync } from './utils'
import { SessionOptions, WhatsAppSessionLocator, GroupJoinResponse, WhatsAppSessionInterface } from './interfaces'

export class WhatsAppSession extends EventEmitter implements WhatsAppSessionInterface {
  public uid: string
  protected sock?: WASocket = undefined
  protected msgRetryCounterMap: MessageRetryMap = { }
  protected lastConnectionState: Partial<ConnectionState> = {}
  protected closing: boolean = false
  protected sessionOptions: SessionOptions = {}

  protected acl: WhatsAppACL
  protected auth!: WhatsAppAuth
  protected store: WhatsAppStore
  protected sessionStorage: WhatsAppSessionStorage

  constructor (locator: WhatsAppSessionLocator, sessionOptions: SessionOptions = {}) {
    super()
    this.uid = locator.sessionId
    console.log(`${this.uid}: Constructing session: ${JSON.stringify(sessionOptions)}`)
    this.sessionOptions = sessionOptions

    this.sessionStorage = new WhatsAppSessionStorage(locator)
    this.acl = new WhatsAppACL(this.sessionStorage.record.aclConfig)
    this.store = new WhatsAppStore(this.acl, this.sessionOptions.sendMessageHistory ?? false)
    this.auth = new WhatsAppAuth(this.sessionStorage.record.authData)
  }

  id (): string | undefined {
    return this.auth?.id()
  }

  async init (): Promise<void> {
    const { version } = await fetchLatestBaileysVersion()
    this.sock = makeWASocket({
      version,
      msgRetryCounterMap: this.msgRetryCounterMap,
      markOnlineOnConnect: false,
      auth: this.auth.getAuth(),
      logger: P({ level: 'error' }),

      browser: Browsers.macOS('Desktop'),
      syncFullHistory: this.sessionOptions.sendMessageHistory ?? false
    })
    this.store.bind(this.sock)

    this.sock.ev.on('creds.update', () => {
      this._updateSessionStorage()
    })
    this.sock.ev.on('connection.update', resolvePromiseSync(this._updateConnectionState.bind(this)))
    this.sock.ev.on('messages.upsert', resolvePromiseSync(this._messageUpsert.bind(this)))
    this.store.on('messageHistory.update', () => debounce(async (msg: WAMessage) => {
      await this.emitMessageHistory()
      if (this.sessionOptions.sharedConnection !== true) {
        this.store.clearMessageHistory()
      }
    }, { delay: 5000, onError: console.log }))
  }

  async close (): Promise<void> {
    this.closing = true
    console.log(`${this.uid}: Closing session`)
    this.sock?.end(undefined)
    this.removeAllListeners()
    delete this.sock
  }

  private _updateSessionStorage (): void {
    this.sessionStorage.record = {
      authData: this.auth.state,
      aclConfig: this.acl.acl
    }
  }

  private async _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType | 'history' }): Promise<void> {
    const { messages, type } = data
    for (const message of messages) {
      const messageAugmented = { type, ...message }
      console.log(`${this.uid}: got message`)
      const chatId: string | null | undefined = message.key?.remoteJid
      if (chatId == null || !this.acl.canRead(chatId)) {
        console.log(`${this.uid}: not can read`)
        continue
      }
      if (message.key?.fromMe === false) {
        this.emit(ACTIONS.readMessages, messageAugmented)
      }
    }
  }

  isReady (): boolean {
    return this.lastConnectionState?.connection === 'open'
  }

  private async _updateConnectionState (data: Partial<ConnectionState>): Promise<void> {
    if (data.qr !== this.lastConnectionState.qr && data.qr != null) {
      this.emit(ACTIONS.connectionQr, data.qr)
    }
    console.log(`connection state update: ${JSON.stringify(data)}`)
    if (data.connection === 'open') {
      this.emit(ACTIONS.connectionReady, data)
      // Note: In the multi-device version of WhatsApp -- if a desktop client
      // is active, WA doesn't send push notifications to the device. If you
      // would like to receive said notifications -- mark your Baileys client
      // offline using sock.sendPresenceUpdate('unavailable')
      await this.sock?.sendPresenceUpdate('unavailable')
    } else if (data.connection === 'close') {
      this.emit(ACTIONS.connectionClosed, data)
      const { lastDisconnect } = data
      if (lastDisconnect != null && !this.closing) {
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

  async downloadMessageMedia (message: WAMessage): Promise<Buffer> {
    const chatId = message.key.remoteJid
    if (chatId == null || !this.acl.canRead(message.key.remoteJid)) {
      throw new NoAccessError('read', chatId ?? 'undefined')
    }
    try {
      const buffer = await downloadMediaMessage(message, 'buffer', {})
      if (buffer instanceof Buffer) {
        return buffer
      }
      // This should never happen but the signature of downloadMediaMessage
      // doesn't fix the return type based on the `type` function parameter
      throw new Error(`downloadMediaMessage returned invalid type, expected buffer: ${typeof buffer}`)
    } catch (error) {
      if (axios.isAxiosError(error) && [410, 404].includes(error.response?.status ?? 0)) {
        await this.sock?.updateMediaMessage(message)
        return await this.downloadMessageMedia(message)
      }
      throw error
    }
  }

  async emitMessageHistory (): Promise<void> {
    const history = this.store.messageHistory()
    for (const chatId in history) {
      await this._messageUpsert({ messages: history[chatId], type: 'history' })
    }
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

  groups (): GroupMetadata[] {
    return this.store.groups()
  }
}
