import makeWASocket, { Browsers, ConnectionState, DisconnectReason, makeInMemoryStore, MessageRetryMap, MessageUpsertType, useMultiFileAuthState, WAMessage, WASocket } from '@adiwajshing/baileys'
import { Boom } from '@hapi/boom'
import { EventEmitter } from 'events'

import { WhatsAppACLConfig, WhatsAppACL } from './whatsappacl'
import { sleep } from './utils'


export interface WhatsAppSessionConfig {
  acl?: WhatsAppACLConfig
  authString?: string
}

export interface WhatsAppSessionInterface {
  init: () => void
  qrCode: () => string | undefined
}

export class WhatsAppSession extends EventEmitter implements WhatsAppSessionInterface {
  protected sock?: WASocket = undefined
  protected config: WhatsAppSessionConfig = {}
  protected msgRetryCounterMap: MessageRetryMap = { }
  protected lastConnectionState: Partial<ConnectionState> = {}
  protected _messages: WAMessage[] = []
  protected store

  constructor (config: Partial<WhatsAppSessionConfig>) {
    super()
    this.config = config
    this.acl = new WhatsAppACL(config.acl)
    this.store = makeInMemoryStore({})
  }

  async init (): Promise<void> {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
    this.sock = makeWASocket({
      browser: Browsers.macOS('Desktop'),
      auth: state
    })
    this.store.bind(this.sock.ev)
    this.sock.ev.on('creds.update', saveCreds)
    this.sock.ev.on('connection.update', this._updateConnectionState.bind(this))
    this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this))
  }

  async _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType }): Promise<void> {
    const { messages, type } = data
    for (const message of messages) {
      if (message.key?.fromMe === false) {
        this.emit('message', { message, type })
        console.log(`Got message: ${JSON.stringify(message)}`)
        this._messages.push(message)

        if (message.key?.remoteJid != null) {
          await this.sendMessage(message.key?.remoteJid, 'hello?')
        }
      }
    }
  }

  async _updateConnectionState (data: Partial<ConnectionState>): Promise<void> {
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
    console.log(`State: ${JSON.stringify(this.lastConnectionState)}`)
  }

  messages (): WAMessage[] {
    return this._messages
  }

  qrCode (): string | undefined {
    return this.lastConnectionState.qr
  }

  async sendMessage (chatId: string, message: string, clearChatStatus: boolean = true, vampMaxSeconds: number | undefined = 10): Promise<void> {
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
    const msg: WAMessage | undefined = await this.store.mostRecentMessage(chatId, undefined)
    if ((msg?.key) != null) {
      await this.sock?.chatModify({ markRead: false, lastMessages: [msg] }, chatId)
    }
  }
}
