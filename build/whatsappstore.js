"use strict";
/*
import { WAMessage, GroupMetadata, Chat, BaileysEventEmitter } from '@adiwajshing/baileys'
import { WhatsAppACL } from './whatsappacl'


export class WhatsAppStore {
  protected ev: BaileysEventEmitter
  protected acl: WhatsAppACL
  protected _messages: { [_: string]: WAMessage } = {}
  protected _groupMetadata: { [_: string]: GroupMetadata } = {}
  protected _chats: { [_: string]: Chat } = {}

  constructor (ev: BaileysEventEmitter, acl: WhatsAppACL) {
    this.ev = ev
    this.acl = acl
  }

  bind (ev: BaileysEventEmitter): void {
    ev.on('messages.upsert', ({ messages, type }) => {
      switch (type) {
        case 'append':
        case 'notify':
          for (const message of messages) {
            const jid: string | null | undefined = message.key.remoteJid
            if (jid != null && this.acl.canRead(jid)) {
              if (this._messages[jid] == null || message.key.id > this._messages[jid].key.id) {
                this._messages[jid] = message
              }
            }
          }
      }
    })

    ev.on(
    )
  }
}
*/
