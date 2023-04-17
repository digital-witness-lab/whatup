import { WhatsAppACLConfig } from './interfaces'

export class NoAccessError extends Error {
  constructor (mode: string, chatId: string | undefined) {
    super(`No access to ${mode}: ${chatId ?? 'no chatId'}`)
    Object.setPrototypeOf(this, NoAccessError.prototype)
  }
}

export const DefaultWhatsAppACLConfig: WhatsAppACLConfig = {
  allowAll: false,
  canWrite: [],
  canRead: [],
  canReadWrite: []
}

export class WhatsAppACL {
  readonly acl: WhatsAppACLConfig

  constructor (acl: Partial<WhatsAppACLConfig> = DefaultWhatsAppACLConfig) {
    this.acl = { ...DefaultWhatsAppACLConfig, ...acl }
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

  canReadWrite (chatId: string | null | undefined): boolean {
    return this.canRead(chatId) && this.canWrite(chatId)
  }

  canAccess (chatId: string | null | undefined): boolean {
    return this.canRead(chatId) || this.canWrite(chatId)
  }
}
