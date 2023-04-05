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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppSession = void 0;
const baileys_1 = __importStar(require("@adiwajshing/baileys"));
const pino_1 = __importDefault(require("pino"));
const axios_1 = __importDefault(require("axios"));
const events_1 = require("events");
const whatsappacl_1 = require("./whatsappacl");
const whatsappauth_1 = require("./whatsappauth");
const whatsappstore_1 = require("./whatsappstore");
const whatsappsessionstorage_1 = require("./whatsappsessionstorage");
const actions_1 = require("./actions");
const utils_1 = require("./utils");
class WhatsAppSession extends events_1.EventEmitter {
    constructor(locator) {
        super();
        this.sock = undefined;
        this.msgRetryCounterMap = {};
        this.lastConnectionState = {};
        this.closing = false;
        this.uid = locator.sessionId;
        console.log(`${this.uid}: Constructing session`);
        this.sessionStorage = new whatsappsessionstorage_1.WhatsAppSessionStorage(locator);
        this.acl = new whatsappacl_1.WhatsAppACL(this.sessionStorage.record.aclConfig);
        this.store = new whatsappstore_1.WhatsAppStore(this.acl);
        this.auth = new whatsappauth_1.WhatsAppAuth(this.sessionStorage.record.authData);
    }
    id() {
        var _a;
        return (_a = this.auth) === null || _a === void 0 ? void 0 : _a.id();
    }
    init() {
        return __awaiter(this, void 0, void 0, function* () {
            const { version } = yield (0, baileys_1.fetchLatestBaileysVersion)();
            this.sock = (0, baileys_1.default)({
                version,
                msgRetryCounterMap: this.msgRetryCounterMap,
                markOnlineOnConnect: false,
                auth: this.auth.getAuth(),
                logger: (0, pino_1.default)({ level: 'error' }),
                browser: baileys_1.Browsers.macOS('Desktop')
                // downloadHistory: true,
                // syncFullHistory: true
            });
            this.store.bind(this.sock);
            this.sock.ev.on('creds.update', () => {
                this._updateSessionStorage();
            });
            this.sock.ev.on('connection.update', (0, utils_1.resolvePromiseSync)(this._updateConnectionState.bind(this)));
            this.sock.ev.on('messages.upsert', (0, utils_1.resolvePromiseSync)(this._messageUpsert.bind(this)));
        });
    }
    close() {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            this.closing = true;
            console.log(`${this.uid}: Closing session`);
            (_a = this.sock) === null || _a === void 0 ? void 0 : _a.end(undefined);
            this.removeAllListeners();
            delete this.sock;
        });
    }
    _updateSessionStorage() {
        this.sessionStorage.record = {
            authData: this.auth.state,
            aclConfig: this.acl.acl
        };
    }
    _messageUpsert(data) {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function* () {
            const { messages } = data;
            for (const message of messages) {
                console.log(`${this.uid}: got message`);
                const chatId = (_a = message.key) === null || _a === void 0 ? void 0 : _a.remoteJid;
                if (chatId == null || !this.acl.canRead(chatId)) {
                    console.log(`${this.uid}: not can read`);
                    continue;
                }
                if (((_b = message.key) === null || _b === void 0 ? void 0 : _b.fromMe) === false) {
                    this.emit(actions_1.ACTIONS.readMessages, message);
                }
            }
        });
    }
    isReady() {
        var _a;
        return ((_a = this.lastConnectionState) === null || _a === void 0 ? void 0 : _a.connection) === 'open';
    }
    _updateConnectionState(data) {
        var _a, _b;
        return __awaiter(this, void 0, void 0, function* () {
            if (data.qr !== this.lastConnectionState.qr && data.qr != null) {
                this.emit(actions_1.ACTIONS.connectionQr, data.qr);
            }
            console.log(`connection state update: ${JSON.stringify(data)}`);
            if (data.connection === 'open') {
                this.emit(actions_1.ACTIONS.connectionReady, data);
            }
            else if (data.connection === 'close') {
                this.emit(actions_1.ACTIONS.connectionClosed, data);
                const { lastDisconnect } = data;
                if (lastDisconnect != null && !this.closing) {
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
    downloadMessageMedia(message) {
        var _a, _b, _c;
        return __awaiter(this, void 0, void 0, function* () {
            const chatId = message.key.remoteJid;
            if (chatId == null || !this.acl.canRead(message.key.remoteJid)) {
                throw new whatsappacl_1.NoAccessError('read', chatId !== null && chatId !== void 0 ? chatId : 'undefined');
            }
            try {
                const buffer = yield (0, baileys_1.downloadMediaMessage)(message, 'buffer', {});
                if (buffer instanceof Buffer) {
                    return buffer;
                }
                // This should never happen but the signature of downloadMediaMessage
                // doesn't fix the return type based on the `type` function parameter
                throw new Error(`downloadMediaMessage returned invalid type, expected buffer: ${typeof buffer}`);
            }
            catch (error) {
                if (axios_1.default.isAxiosError(error) && [410, 404].includes((_b = (_a = error.response) === null || _a === void 0 ? void 0 : _a.status) !== null && _b !== void 0 ? _b : 0)) {
                    yield ((_c = this.sock) === null || _c === void 0 ? void 0 : _c.updateMediaMessage(message));
                    return yield this.downloadMessageMedia(message);
                }
                throw error;
            }
        });
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
            const msg = this.store.lastMessage(chatId);
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
                return undefined;
            if (!this.acl.canRead(metadata === null || metadata === void 0 ? void 0 : metadata.id)) {
                throw new whatsappacl_1.NoAccessError('read', metadata === null || metadata === void 0 ? void 0 : metadata.id);
            }
            this.store.setGroupMetadata(metadata);
            const response = yield this.sock.groupAcceptInvite(inviteCode);
            return { metadata, response };
        });
    }
    leaveGroup(chatId) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.sock == null)
                return null;
            const groupMetadata = yield this.store.groupMetadata(chatId);
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
            return yield this.store.groupMetadata(chatId);
        });
    }
    groups() {
        return this.store.groups();
    }
}
exports.WhatsAppSession = WhatsAppSession;
