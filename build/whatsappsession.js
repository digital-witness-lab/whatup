"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
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
exports.WhatsAppSession = void 0;
const baileys_1 = __importStar(require("@adiwajshing/baileys"));
const events_1 = require("events");
const whatsappacl_1 = require("./whatsappacl");
const utils_1 = require("./utils");
class WhatsAppSession extends events_1.EventEmitter {
    constructor(config) {
        super();
        this.sock = undefined;
        this.config = {};
        this.msgRetryCounterMap = {};
        this.lastConnectionState = {};
        this._messages = [];
        this.config = config;
        this.acl = new whatsappacl_1.WhatsAppACL(config.acl);
        this.store = (0, baileys_1.makeInMemoryStore)({});
    }
    init() {
        return __awaiter(this, void 0, void 0, function* () {
            const { state, saveCreds } = yield (0, baileys_1.useMultiFileAuthState)('auth_info_baileys');
            this.sock = (0, baileys_1.default)({
                browser: baileys_1.Browsers.macOS('Desktop'),
                auth: state
            });
            this.store.bind(this.sock.ev);
            this.sock.ev.on('creds.update', saveCreds);
            this.sock.ev.on('connection.update', this._updateConnectionState.bind(this));
            this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this));
        });
    }
    _messageUpsert(data) {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            const { messages, type } = data;
            for (const message of messages) {
                if (((_a = message.key) === null || _a === void 0 ? void 0 : _a.fromMe) === false) {
                    this.emit('message', { message, type });
                    console.log(`Got message: ${JSON.stringify(message)}`);
                    this._messages.push(message);
                    if (((_b = message.key) === null || _b === void 0 ? void 0 : _b.remoteJid) != null) {
                        yield this.sendMessage((_c = message.key) === null || _c === void 0 ? void 0 : _c.remoteJid, 'hello?');
                    }
                }
            }
        });
    }
    _updateConnectionState(data) {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function* () {
            if (data.qr !== this.lastConnectionState.qr) {
                this.emit('qrCode', data);
            }
            if (data.connection === 'open') {
                this.emit('ready', data);
            }
            else if (data.connection !== undefined) {
                this.emit('closed', data);
                const { lastDisconnect } = data;
                if (lastDisconnect != null) {
                    const shouldReconnect = ((_b = (_a = lastDisconnect.error) === null || _a === void 0 ? void 0 : _a.output) === null || _b === void 0 ? void 0 : _b.statusCode) !== baileys_1.DisconnectReason.loggedOut;
                    if (shouldReconnect) {
                        yield this.init();
                    }
                }
            }
            this.lastConnectionState = Object.assign(Object.assign({}, this.lastConnectionState), data);
            console.log(`State: ${JSON.stringify(this.lastConnectionState)}`);
        });
    }
    messages() {
        return this._messages;
    }
    qrCode() {
        return this.lastConnectionState.qr;
    }
    sendMessage(chatId, message, clearChatStatus = true, vampMaxSeconds = 10) {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            if (clearChatStatus) {
                yield this.markChatRead(chatId);
            }
            if (vampMaxSeconds > 0) {
                const nComposing = Math.floor(Math.random() * vampMaxSeconds);
                for (let i = 0; i < nComposing; i += 1) {
                    yield ((_a = this.sock) === null || _a === void 0 ? void 0 : _a.sendPresenceUpdate('composing', chatId));
                    yield (0, utils_1.sleep)(Math.random() * 1000);
                }
                yield ((_b = this.sock) === null || _b === void 0 ? void 0 : _b.sendPresenceUpdate('available', chatId));
            }
            yield ((_c = this.sock) === null || _c === void 0 ? void 0 : _c.sendMessage(chatId, { text: message }));
        });
    }
    markChatRead(chatId) {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            const msg = yield this.store.mostRecentMessage(chatId, undefined);
            if ((msg === null || msg === void 0 ? void 0 : msg.key) != null) {
                yield ((_a = this.sock) === null || _a === void 0 ? void 0 : _a.chatModify({ markRead: false, lastMessages: [msg] }, chatId));
            }
        });
    }
}
exports.WhatsAppSession = WhatsAppSession;
