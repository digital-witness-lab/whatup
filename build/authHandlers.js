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
const globalSessions;
module.exports = (io, socket) => __awaiter(void 0, void 0, void 0, function* () {
    let session = new whatsappsession_1.WhatsAppSession({});
    let sharedSession;
    const authenticateSession = (payload) => __awaiter(void 0, void 0, void 0, function* () {
        var _a;
        const { sessionInfo, sharedConnection } = payload;
        const authData = JSON.parse(sessionInfo);
        if (((_a = authData.me) === null || _a === void 0 ? void 0 : _a.id) == null) {
            socket.emit('connection:auth', { error: 'Invalid Credentials: No self ID' });
            return;
        }
        if (sharedConnection === true) {
            sharedSession = { name: authData.creds.me, numListeners: 1, session };
            if (sharedSession.name in globalSessions) {
                yield session.close();
                sharedSession = globalSessions[sharedSession.name];
                session = sharedSession.session;
                sharedSession.numListeners += 1;
            }
            else {
                globalSessions[sharedSession.name] = sharedSession;
            }
        }
        else {
            const r = Math.floor(Math.random() * 100000);
            sharedSession.name = `${authData.creds.me}-${r}`;
            globalSessions[sharedSession.name] = sharedSession;
        }
        yield session.init();
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
                yield session.markChatRead(chatId);
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
        socket.on('read:groupInviteMetadata', (inviteCode) => __awaiter(void 0, void 0, void 0, function* () {
            try {
                const groupInviteMetadata = yield session.groupInviteMetadata(inviteCode);
                socket.emit('read:groupInviteMetadata', groupInviteMetadata);
            }
            catch (e) {
                socket.emit('read:groupInviteMetadata', { error: e });
            }
        }));
    });
    socket.on('disconnect', () => __awaiter(void 0, void 0, void 0, function* () {
        if (sessionName !== null) {
            sessions[sessionName].numListeners -= 1;
            if (sessions[sessionName].numListeners === 0) {
                yield sessions[sessionName].session.close();
                // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
                delete sessions[sessionName];
            }
        }
        else {
            yield session.close();
        }
    }));
    socket.on('connection:qr', () => __awaiter(void 0, void 0, void 0, function* () {
        const qrCode = session.qrCode();
        socket.emit('connection:qr', { qrCode });
    }));
    socket.on('connection:status', () => {
        const connection = session.connection();
        socket.emit('connection:status', { connection });
    });
    socket.on('connection:auth', authenticateSession);
});
