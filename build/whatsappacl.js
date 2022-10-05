"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppACL = void 0;
const events_1 = require("events");
const WhatsAppACLConfigDefault = {
    allowAll: false,
    canWrite: [],
    canRead: [],
    canReadWrite: []
};
class WhatsAppACL extends events_1.EventEmitter {
    constructor(acl) {
        super();
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
    _process(events) {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            for (const event in events) {
                const data = events[event];
                const canRead = [data === null || data === void 0 ? void 0 : data.jid, (_a = data === null || data === void 0 ? void 0 : data.key) === null || _a === void 0 ? void 0 : _a.jid, (_b = data === null || data === void 0 ? void 0 : data.key) === null || _b === void 0 ? void 0 : _b.remoteJid, (_c = data === null || data === void 0 ? void 0 : data.key) === null || _c === void 0 ? void 0 : _c.id, data === null || data === void 0 ? void 0 : data.id].map((id) => {
                    if (id === null)
                        return false;
                    return this.canRead(id);
                }).some((b) => b);
                if (canRead) {
                    this.emit(event, data);
                }
            }
        });
    }
}
exports.WhatsAppACL = WhatsAppACL;
