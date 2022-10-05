import { BaileysEventData, BaileysEventMap, BaileysEvent, WAMessageKey } from '@adiwajshing/baileys'
import { EventEmitter } from 'events'

export interface WhatsAppACLConfig {
  allowAll: boolean
  canWrite: string[]
  canRead: string[]
  canReadWrite: string[]
}

const WhatsAppACLConfigDefault: WhatsAppACLConfig = {
  allowAll: false,
  canWrite: [],
  canRead: [],
  canReadWrite: []
}

export class WhatsAppACL extends EventEmitter {
  acl: WhatsAppACLConfig

  constructor (acl: Partial<WhatsAppACLConfig>) {
    super()
    this.acl = { ...WhatsAppACLConfigDefault, ...acl }
  }

  canRead (chatId: string | null | undefined): boolean {
    if (this.acl.allowAll) return true
    if (chatId == null) return false
    return (chatId in this.acl.canRead) || (chatId in this.acl.canReadWrite)
  }

  canWrite (chatId: string | null | undefined): boolean {
    if (this.acl.allowAll) return true
    if (chatId == null) return false
    return (chatId in this.acl.canWrite) || (chatId in this.acl.canReadWrite)
  }

  protected async _process (events: BaileysEventData): Promise<void> {
    for (const event in events) {
      const data = events[event]
      const canRead: boolean = [data?.jid, data?.key?.jid, data?.key?.remoteJid, data?.key?.id, data?.id].map((id: string | null): boolean => {
        if (id === null) return false
        return this.canRead(id)
      }).some((b: boolean) => b)
      if (canRead) {
        this.emit(event, data)
      }
    }
  }
}
