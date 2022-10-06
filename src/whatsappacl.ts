export interface WhatsAppACLConfig {
  allowAll: boolean
  canWrite: string[]
  canRead: string[]
  canReadWrite: string[]
}

export class NoAccessError extends Error {
  constructor (mode: string, chatId: string) {
    super(`No access to ${mode}: ${chatId}`)
    Object.setPrototypeOf(this, NoAccessError.prototype)
  }
}

const WhatsAppACLConfigDefault: WhatsAppACLConfig = {
  allowAll: false,
  canWrite: [],
  canRead: [],
  canReadWrite: []
}

export class WhatsAppACL {
  acl: WhatsAppACLConfig

  constructor (acl: Partial<WhatsAppACLConfig> = WhatsAppACLConfigDefault) {
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
}
