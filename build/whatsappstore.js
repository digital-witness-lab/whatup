"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppStore = void 0;
class WhatsAppStore {
    constructor(ev, acl) {
        this._messages = {};
        this._groupMetadata = {};
        this._chats = {};
        this.ev = ev;
        this.acl = acl;
    }
    bind(ev) {
        ev.on('messages.upsert', ({ messages, type }) => {
            switch (type) {
                case 'append':
                case 'notify':
                    for (const message of messages) {
                        const jid = message.key.remoteJid;
                        if (jid != null && this.acl.canRead(jid)) {
                            if (this._messages[jid] == null || message.key.id > this._messages[jid].key.id) {
                                this._messages[jid] = message;
                            }
                        }
                    }
            }
        });
        ev.on();
    }
}
exports.WhatsAppStore = WhatsAppStore;
