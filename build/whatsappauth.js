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
const events_1 = require("events");
class WhatsAppAuth extends events_1.EventEmitter {
    constructor(state = null) {
        super();
        this.state = state !== null ? state : { creds: (0, baileys_1.initAuthCreds)(), keys: {} };
    }
    getAuth() {
        return {
            creds: this.state.creds,
            keys: this
        };
    }
    id() {
        var _a, _b;
        return (_b = (_a = this.state.creds) === null || _a === void 0 ? void 0 : _a.me) === null || _b === void 0 ? void 0 : _b.id;
    }
    static fromString(data) {
        try {
            const state = JSON.parse(data, baileys_1.BufferJSON.reviver);
            return new WhatsAppAuth(state);
        }
        catch (e) {
            return undefined;
        }
    }
    toString() {
        return JSON.stringify(this.state, baileys_1.BufferJSON.replacer);
    }
    update() {
        this.emit('state:update', this.toString());
    }
    get(type, ids) {
        return __awaiter(this, void 0, void 0, function* () {
            return ids.reduce((dict, id) => {
                var _a;
                let value = (_a = this.state.keys[type]) === null || _a === void 0 ? void 0 : _a[id];
                if (value != null) {
                    if (type === 'app-state-sync-key') {
                        value = baileys_1.proto.Message.AppStateSyncKeyData.fromObject(value);
                    }
                    dict[id] = value;
                }
                return dict;
            }, {});
        });
    }
    set(data) {
        return __awaiter(this, void 0, void 0, function* () {
            let key;
            for (key in data) {
                if (this.state.keys[key] === undefined) {
                    this.state.keys[key] = {};
                }
                Object.assign(this.state.keys[key], data[key]);
            }
            this.update();
        });
    }
}
exports.WhatsAppAuth = WhatsAppAuth;
