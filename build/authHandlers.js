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
const whatsappsession_1 = require("./whatsappsession");
module.exports = (io, socket) => __awaiter(void 0, void 0, void 0, function* () {
    const session = new whatsappsession_1.WhatsAppSession({});
    yield session.init();
    const authenticateSession = (payload) => {
        const { sessionInfo, sharedConnection } = payload;
        console.log(`sessionInfo: ${sessionInfo}`);
        console.log(`sharedConnection: ${sharedConnection}`);
        socket.on('write:sendMessage', (...args) => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const sendMessage = yield session.sendMessage(...args);
                socket.emit('write:sendMessage', sendMessage);
            }
            catch (e) {
                socket.emit('write:sendMessage', { error: e });
            }
        }));
        socket.on('write:markChatRead', (chatId) => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const markChatRead = yield session.markChatRead(chatId);
                socket.emit('write:markChatRead', { error: null });
            }
            catch (e) {
                socket.emit('write:markChatRead', { error: e });
            }
        }));
        socket.on('read:joinGroup', (chatId) => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.joinGroup(chatId);
                socket.emit('read:joinGroup', groupMetadata);
            }
            catch (e) {
                socket.emit('read:joinGroup', { error: e });
            }
        }));
        socket.on('read:groupMetadata', (chatId) => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.groupMetadata(chatId);
                socket.emit('read:groupMetadata', groupMetadata);
            }
            catch (e) {
                socket.emit('read:groupMetadata', { error: e });
            }
        }));
    };
    socket.on('connection:qr', () => __awaiter(void 0, void 0, void 0, function* () {
        const qrCode = session.qrCode();
        const QR = yield Promise.resolve().then(() => __importStar(require('qrcode-terminal')));
        QR === null || QR === void 0 ? void 0 : QR.generate(qrCode, { small: true });
        socket.emit('connection:qr', { qrCode });
    }));
    socket.on('connection:status', () => {
        const connection = session.connection();
        socket.emit('connection:status', { connection });
    });
    socket.on('connection:auth', authenticateSession);
});
