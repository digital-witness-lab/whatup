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
exports.WhatsAppAuth = void 0;
const baileys_1 = require("@adiwajshing/baileys");
class WhatsAppAuth {
    constructor(state = null) {
        this.state = state !== null ? state : { creds: (0, baileys_1.initAuthCreds)() };
    }
    _uniqueId(type, id) {
        return `${type}.${id}`;
    }
    getAuth() {
        return {
            creds: this.state.creds,
            keys: this
        };
    }
    get(type, ids) {
        return __awaiter(this, void 0, void 0, function* () {
            const data = {};
            for (const id of ids) {
                const key = this._uniqueId(type, id);
                const value = this.state.keys.get(key);
                data[id] = value;
            }
            return data;
        });
    }
    setCreds(creds) {
        this.state.creds = creds;
    }
    set(data) {
        return __awaiter(this, void 0, void 0, function* () {
            for (const category in data) {
                for (const id in data[category]) {
                    const key = this._uniqueId(category, id);
                    const value = data[category][id];
                    if (value != null) {
                        this.state.keys.set(key, value);
                    }
                    else {
                        delete this.state.keys[key];
                    }
                }
            }
        });
    }
}
exports.WhatsAppAuth = WhatsAppAuth;
