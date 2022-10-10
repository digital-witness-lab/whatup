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
        this._lastMessage = {};
        this._groupMetadata = {};
        this.config = config;
        this.acl = new whatsappacl_1.WhatsAppACL(config.acl);
    }
    init() {
        return __awaiter(this, void 0, void 0, function* () {
            const { version, isLatest } = yield (0, baileys_1.fetchLatestBaileysVersion)();
            const { state, saveState } = (0, baileys_1.useSingleFileAuthState)('single_auth');
            this.sock = (0, baileys_1.default)({
                version,
                browser: baileys_1.Browsers.macOS('Desktop'),
                markOnlineOnConnect: false,
                auth: state
                // downloadHistory: true,
                // syncFullHistory: true
            });
            this.sock.ev.on('creds.update', saveState);
            this.sock.ev.on('connection.update', this._updateConnectionState.bind(this));
            this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this));
            // this.sock.ev.on('messages.set', this._updateHistory.bind(this))
        });
    }
    close() {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            (_a = this.sock) === null || _a === void 0 ? void 0 : _a.end(undefined);
        });
    }
    _setMessageHistory(data) {
        var _a, _b, _c;
        const { messages } = data;
        for (const message of messages) {
            const chatId = (_a = message.key) === null || _a === void 0 ? void 0 : _a.remoteJid;
            if (chatId == null || !this.acl.canRead(chatId)) {
                continue;
            }
            if (this._lastMessage[chatId] == null || ((_b = this._lastMessage[chatId].key) === null || _b === void 0 ? void 0 : _b.id) < ((_c = message.key) === null || _c === void 0 ? void 0 : _c.id)) {
                this._lastMessage[chatId] = message;
            }
        }
    }
    _messageUpsert(data) {
        var _a, _b, _c, _d;
        return __awaiter(this, void 0, void 0, function* () {
            const { messages, type } = data;
            for (const message of messages) {
                console.log('got message');
                const chatId = (_a = message.key) === null || _a === void 0 ? void 0 : _a.remoteJid;
                if (chatId == null || !this.acl.canRead(chatId)) {
                    console.log('not can read');
                    continue;
                }
                if (this._lastMessage[chatId] == null || ((_b = this._lastMessage[chatId].key) === null || _b === void 0 ? void 0 : _b.id) < ((_c = message.key) === null || _c === void 0 ? void 0 : _c.id)) {
                    this._lastMessage[chatId] = message;
                }
                if (((_d = message.key) === null || _d === void 0 ? void 0 : _d.fromMe) === false) {
                    console.log('emitting');
                    this.emit('message', { message, type });
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
        });
    }
    connection() {
        return this.lastConnectionState.connection;
    }
    qrCode() {
        return this.lastConnectionState.qr;
    }
    sendMessage(chatId, message, clearChatStatus = true, vampMaxSeconds = 10) {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.acl.canWrite(chatId)) {
                throw new whatsappacl_1.NoAccessError('write', chatId);
            }
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
            return yield ((_c = this.sock) === null || _c === void 0 ? void 0 : _c.sendMessage(chatId, { text: message }));
        });
    }
    markChatRead(chatId) {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.acl.canWrite(chatId)) {
                throw new whatsappacl_1.NoAccessError('write', chatId);
            }
            const msg = this._lastMessage[chatId];
            if ((msg === null || msg === void 0 ? void 0 : msg.key) != null) {
                yield ((_a = this.sock) === null || _a === void 0 ? void 0 : _a.chatModify({ markRead: false, lastMessages: [msg] }, chatId));
            }
        });
    }
    joinGroup(inviteCode) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.sock == null)
                return null;
            const metadata = yield this.groupInviteMetadata(inviteCode);
            if (metadata == null)
                return null;
            if (!this.acl.canRead(metadata === null || metadata === void 0 ? void 0 : metadata.id)) {
                throw new whatsappacl_1.NoAccessError('read', metadata === null || metadata === void 0 ? void 0 : metadata.id);
            }
            this._groupMetadata[metadata.id] = metadata;
            const response = yield this.sock.groupAcceptInvite(inviteCode);
            return { metadata, response };
        });
    }
    leaveGroup(chatId) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.sock == null)
                return null;
            const groupMetadata = yield this.groupMetadata(chatId);
            yield this.sock.groupLeave(chatId);
            return groupMetadata;
        });
    }
    groupInviteMetadata(inviteCode) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.sock == null)
                return null;
            const metadata = yield this.sock.groupGetInviteInfo(inviteCode);
            return metadata;
        });
    }
    groupMetadata(chatId) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.acl.canRead(chatId)) {
                throw new whatsappacl_1.NoAccessError('read', chatId);
            }
            if (this._groupMetadata[chatId] != null) {
                return this._groupMetadata[chatId];
            }
            if (this.sock == null)
                return null;
            return yield this.sock.groupMetadata(chatId);
        });
    }
}
exports.WhatsAppSession = WhatsAppSession;
