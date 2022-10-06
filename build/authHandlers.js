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
    socket.on('connection:qr', () => {
        const qrCode = session.qrCode();
        socket.emit('connection:qr', { qrCode });
    });
    socket.on('connection:status', () => {
        const connection = session.connection();
        socket.emit('connection:status', { connection });
    });
    socket.on('connection:auth', authenticateSession);
});
