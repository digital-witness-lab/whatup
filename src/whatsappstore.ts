import { EventEmitter } from 'events'

import { WASocket, WAMessage, MessageUpsertType, GroupMetadata, Contact, Chat } from '@adiwajshing/baileys'

import { WhatsAppACL } from './whatsappacl'
import { WhatsAppStoreInterface } from './interfaces'

export class WhatsAppStore extends EventEmitter implements WhatsAppStoreInterface {
  protected sock: WASocket | undefined
  protected acl: WhatsAppACL

  protected _lastMessage: { [_: string]: WAMessage } = {}
  protected _messageHistory: { [_: string]: WAMessage[] } = {}
  protected _groupMetadata: { [_: string]: GroupMetadata } = {}
  protected _contacts: { [_: string]: Contact } = {}
  protected _chats: { [_: string]: Chat } = {}
  protected _saveMessageHistory: boolean = false

  constructor (acl: WhatsAppACL, saveMessageHistory: boolean = false) {
    super()
    this.acl = acl
    this._saveMessageHistory = saveMessageHistory
  }

  public bind (sock: WASocket): void {
    this.sock = sock

    this.sock.ev.on('messaging-history.set', (data: { chats: Chat[], contacts: Contact[], messages: WAMessage[], isLatest: boolean }) => {
      console.log(`Recieved history update: n_messages = ${data.messages.length}: n_chats = ${data.chats.length}: n_contacts = ${data.contacts.length}`)
      this._updateMessageHistory(data)
      this._updateChatHistory(data)
      this._updateContactHistory(data)
    })

    this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this))

    this.sock.ev.on('groups.upsert', this._upsertGroups.bind(this))
    this.sock.ev.on('groups.update', this._updateGroups.bind(this))
    // this.sock.ev.on('group-participants.update', ...)

    this.sock.ev.on('chats.upsert', this._upsertChat.bind(this))
    this.sock.ev.on('chats.update', this._updateChat.bind(this))
    this.sock.ev.on('chats.delete', this._deleteChat.bind(this))

    this.sock.ev.on('contacts.upsert', this._upsertContact.bind(this))
    this.sock.ev.on('contacts.update', this._updateContact.bind(this))
  }

  //* ******** START PUBLIC METHODS ************//
  public contacts (): Contact[] {
    return Object.values(this._contacts)
  }

  public chats (): Chat[] {
    return Object.values(this._chats)
  }

  public groups (): GroupMetadata[] {
    return Object.values(this._groupMetadata)
  }

  public contact (cid: string): Contact | undefined {
    return this._contacts[cid]
  }

  public async groupMetadata (chatId: string): Promise<GroupMetadata | undefined> {
    let metadata: GroupMetadata | undefined = this._groupMetadata[chatId]
    if (metadata === undefined) {
      if (this.sock === undefined) return undefined
      metadata = await this.sock.groupMetadata(chatId)
      this.setGroupMetadata(metadata)
    }
    return metadata
  }

  public setChat (chat: Chat): Chat | undefined {
    const id: string = chat.id
    const prevChat = this._chats[id]
    this._chats[id] = chat
    return prevChat
  }

  public setGroupMetadata (groupMetadata: GroupMetadata): GroupMetadata | undefined {
    const chatId: string = groupMetadata.id
    const prevMetadata = this._groupMetadata[chatId]
    this._groupMetadata[chatId] = groupMetadata
    return prevMetadata
  }

  public lastMessage (chatId: string): WAMessage | undefined {
    return this._lastMessage[chatId]
  }

  public messageHistory (): { [_: string]: WAMessage[] } {
    return this._messageHistory
  }

  public clearMessageHistory (): void {
    this._messageHistory = {}
    this._saveMessageHistory = false
  }

  //* ******** END PUBLIC METHODS ************//

  //* ******** START Contact Events *************//
  private _updateContactHistory (data: { contacts: Contact[], isLatest: boolean }): void {
    console.log(`Updating contact history: ${data.contacts.length}`)
    data.contacts.map(this._setContact.bind(this))
  }

  private _upsertContact (contacts: Contact[]): void {
    console.log(`Upserting contacts: ${contacts.length}`)
    contacts.map(this._setContact.bind(this))
  }

  private _updateContact (contacts: Array<Partial<Contact>>): void {
    console.log(`Updating contacts: ${contacts.length}`)
    for (const contact of contacts) {
      const cid: string | undefined = contact.id
      if (cid == null) return
      if (this._contacts[cid] !== undefined) {
        Object.assign(this._contacts[cid], contact)
      }
    }
  }

  private _setContact (contact: Contact): void {
    const cid: string = contact.id
    this._contacts[cid] = contact
  }
  //* ******** END Contact Events *************//

  //* ******** START Message Events *************//
  private _updateMessageHistory (data: { messages: WAMessage[], isLatest: boolean }): void {
    const { messages } = data
    console.log(`Recieved update message history: ${messages.length}`)
    messages.map(this._setLatestMessage.bind(this))
    messages.map(this._setMessageHistory.bind(this))
  }

  private _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType }): void {
    console.log(`Recieved upsert message history: ${data.messages.length}`)
    for (const message of data.messages) {
      this._setLatestMessage(message)
      this._setMessageHistory(message)
    }
  }

  private canAccessMessage (chatId: string | null | undefined): boolean {
    if (chatId == null) return false
    if (!this.acl.canRead(chatId) && !this.acl.canWrite(chatId)) return false
    return true
  }

  private _setMessageHistory (message: WAMessage): void {
    if (!this._saveMessageHistory) return
    const chatId: string | null | undefined = message.key?.remoteJid
    if (chatId == null || !this.canAccessMessage(chatId)) return
    if (this._messageHistory[chatId] === undefined) this._messageHistory[chatId] = []
    this._messageHistory[chatId].push(message)
    this._messageHistory[chatId].sort((a, b) => (((a.messageTimestamp ?? 0) as number) - ((b.messageTimestamp ?? 0) as number)))
    this.emit('messageHistory.update', message)
  }

  private _setLatestMessage (message: WAMessage): void {
    const chatId: string | null | undefined = message.key?.remoteJid
    if (chatId == null || !this.canAccessMessage(chatId)) return
    const lastMessage: WAMessage | undefined = this._lastMessage[chatId]
    if (lastMessage == null || lastMessage.key.id == null || (message.key.id != null && lastMessage.key.id < message.key.id)) {
      this._lastMessage[chatId] = message
    }
  }
  //* ******** END Message Events *************//

  //* ******** START Chat Events *************//
  private _deleteChat (chatIds: string[]): void {
    for (const chatId of chatIds) {
      // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
      delete this._chats[chatId]
    }
  }

  private _updateChat (chats: Array<Partial<Chat>>): void {
    console.log(`Updating chats: ${chats.length}`)
    for (const chat of chats) {
      const cid: string | undefined = chat.id
      if (cid == null) return
      if (this._chats[cid] !== undefined) {
        Object.assign(this._chats[cid], chat)
      }
    }
  }

  private _upsertChat (chats: Chat[]): void {
    chats.map(this.setChat.bind(this))
  }

  private _updateChatHistory (data: { chats: Chat[], isLatest: boolean }): void {
    data.chats.map(this.setChat.bind(this))
  }
  //* ******** END Chat Events *************//

  //* ******** START Contact Events *************//
  protected _upsertGroups (groupMetadatas: GroupMetadata[]): void {
    groupMetadatas.map(this.setGroupMetadata.bind(this))
  }

  protected _updateGroups (groupMetadatas: Array<Partial<GroupMetadata>>): void {
    console.log(`Updating groups: ${groupMetadatas.length}`)
    for (const groupMetadata of groupMetadatas) {
      const gid: string | undefined = groupMetadata.id
      if (gid == null) return
      if (this._groupMetadata[gid] !== undefined) {
        Object.assign(this._groupMetadata[gid], groupMetadata)
      }
    }
  }
  //* ******** END Contact Events *************//
}
