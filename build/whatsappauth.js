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
    get(type, ids) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log("Auth get:", type, ids);
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
    setCreds(creds) {
        console.log("set creds", creds);
        this.state.creds = creds;
        this.emit('state:update', this.state);
    }
    set(data) {
        return __awaiter(this, void 0, void 0, function* () {
            console.log("auth set:", data);
            for (const key in data) {
                if (this.state.keys[key] === undefined) {
                    this.state.keys[key] = {};
                }
                Object.assign(this.state.keys[key], data[key]);
            }
            this.emit('state:update', this.state);
        });
    }
}
exports.WhatsAppAuth = WhatsAppAuth;
