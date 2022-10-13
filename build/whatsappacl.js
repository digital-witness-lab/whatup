"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppACL = exports.NoAccessError = void 0;
class NoAccessError extends Error {
    constructor(mode, chatId) {
        super(`No access to ${mode}: ${chatId !== null && chatId !== void 0 ? chatId : 'no chatId'}`);
        Object.setPrototypeOf(this, NoAccessError.prototype);
    }
}
exports.NoAccessError = NoAccessError;
const WhatsAppACLConfigDefault = {
    allowAll: false,
    canWrite: [],
    canRead: [],
    canReadWrite: []
};
class WhatsAppACL {
    constructor(acl = WhatsAppACLConfigDefault) {
        this.acl = Object.assign(Object.assign({}, WhatsAppACLConfigDefault), acl);
    }
    canRead(chatId) {
        if (this.acl.allowAll)
            return true;
        if (chatId == null)
            return false;
        return (chatId in this.acl.canRead) || (chatId in this.acl.canReadWrite);
    }
    canWrite(chatId) {
        if (this.acl.allowAll)
            return true;
        if (chatId == null)
            return false;
        return (chatId in this.acl.canWrite) || (chatId in this.acl.canReadWrite);
    }
    canReadWrite(chatId) {
        return this.canRead(chatId) && this.canWrite(chatId);
    }
    canAccess(chatId) {
        return this.canRead(chatId) || this.canWrite(chatId);
    }
}
exports.WhatsAppACL = WhatsAppACL;
