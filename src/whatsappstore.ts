import { WASocket, WAMessage, MessageUpsertType, GroupMetadata, Contact, Chat } from '@adiwajshing/baileys'

import { WhatsAppACL } from './whatsappacl'
import { keys } from './utils'

export class WhatsAppStore {
  protected sock: WASocket | undefined
  protected acl: WhatsAppACL

  protected _lastMessage: { [_: string]: WAMessage } = {}
  protected _groupMetadata: { [_: string]: GroupMetadata } = {}
  protected _contacts: { [_: string]: Contact } = {}
  protected _chats: { [_: string]: Chat } = {}

  constructor (acl: WhatsAppACL) {
    this.acl = acl
  }

  public bind (sock: WASocket): void {
    this.sock = sock

    this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this))
    this.sock.ev.on('messages.set', this._updateMessageHistory.bind(this))

    // this.sock.ev.on('groups.upsert', ...)
    // this.sock.ev.on('groups.update', ...)
    // this.sock.ev.on('group-participants.update', ...)

    this.sock.ev.on('chats.set', this._updateChatHistory.bind(this))
    this.sock.ev.on('chats.upsert', this._upsertChat.bind(this))
    this.sock.ev.on('chats.update', this._updateChat.bind(this))
    this.sock.ev.on('chats.delete', this._deleteChat.bind(this))

    this.sock.ev.on('contacts.set', this._updateContactHistory.bind(this))
    this.sock.ev.on('contacts.upsert', this._upsertContact.bind(this))
    this.sock.ev.on('contacts.update', this._updateContact.bind(this))
  }

  //* ******** START PUBLIC METHODS ************//
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
  //* ******** END PUBLIC METHODS ************//

  //* ******** START Contact Events *************//
  private _updateContactHistory (data: { contacts: Contact[], isLatest: boolean }): void {
    data.contacts.map(this._setContact)
    console.log('update contact history:', this._contacts)
  }

  private _upsertContact (contacts: Contact[]): void {
    contacts.map(this._setContact)
    console.log('upsert contacts:', this._contacts)
  }

  private _updateContact (contacts: Array<Partial<Contact>>): void {
    for (const contact of contacts) {
      const cid: string | undefined = contact.id
      if (cid == null) return
      if (this._contacts[cid] === undefined) return
      Object.assign(this._contacts[cid], contact)
    }
    console.log('update contacts:', this._contacts)
  }

  private _setContact (contact: Contact): void {
    const cid: string = contact.id
    this._contacts[cid] = contact
  }
  //* ******** END Contact Events *************//

  //* ******** START Message Events *************//
  private _updateMessageHistory (data: { messages: WAMessage[], isLatest: boolean }): void {
    const { messages } = data
    messages.map(this._setLatestMessage)
  }

  private _messageUpsert (data: { messages: WAMessage[], type: MessageUpsertType }): void {
    for (const message of data.messages) {
      this._setLatestMessage(message)
    }
  }

  private _setLatestMessage (message: WAMessage): void {
    const chatId: string | null | undefined = message.key?.remoteJid
    if (chatId == null) return
    if (!this.acl.canRead(chatId) && !this.acl.canWrite(chatId)) return
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
    for (const chat of chats) {
      const cid: string | undefined = chat.id
      if (cid == null) return
      if (this._chats[cid] === undefined) return
      Object.assign(this._chats[cid], chat)
    }
    console.log('update contacts:', this._contacts)
  }

  private _upsertChat (chats: Chat[]): void {
    chats.map(this.setChat)
  }

  private _updateChatHistory (data: { chats: Chat[], isLatest: boolean }): void {
    data.chats.map(this.setChat)
  }
  //* ******** END Chat Events *************//
}
