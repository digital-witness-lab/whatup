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
exports.registerAuthHandlers = void 0;
const whatsappsession_1 = require("./whatsappsession");
const whatsappauth_1 = require("./whatsappauth");
const globalSessions = {};
function assignSocket(session, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        session.on('connection:auth', (state) => {
            socket.emit('connection:auth', { sessionAuth: state, error: null });
        });
        session.on('connection:qr', (qrCode) => {
            socket.emit('connection:qr', { qrCode });
        });
        session.on('connection:ready', (data) => socket.emit('connection:ready', data));
    });
}
function assignAuthenticatedEvents(session, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        socket.on('write:sendMessage', (...args) => __awaiter(this, void 0, void 0, function* () {
            try {
                // @ts-expect-error: TS2556: just let me use `...args` here pls.
                const sendMessage = yield session.sendMessage(...args);
                socket.emit('write:sendMessage', sendMessage);
            }
            catch (e) {
                socket.emit('write:sendMessage', { error: e });
            }
        }));
        socket.on('write:markChatRead', (chatId) => __awaiter(this, void 0, void 0, function* () {
            try {
                yield session.markChatRead(chatId);
                socket.emit('write:markChatRead', { error: null });
            }
            catch (e) {
                socket.emit('write:markChatRead', { error: e });
            }
        }));
        socket.on('read:messages:subscribe', () => __awaiter(this, void 0, void 0, function* () {
            const emitMessage = (data) => {
                socket.emit('read:messages', data);
            };
            session.on('message', emitMessage);
            socket.on('read:messages:unsubscribe', () => __awaiter(this, void 0, void 0, function* () {
                session.off('message', emitMessage);
            }));
        }));
        socket.on('write:leaveGroup', (chatId) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.leaveGroup(chatId);
                socket.emit('write:leaveGroup', groupMetadata);
            }
            catch (e) {
                socket.emit('write:leaveGroup', { error: e });
            }
        }));
        socket.on('read:joinGroup', (chatId) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.joinGroup(chatId);
                socket.emit('read:joinGroup', groupMetadata);
            }
            catch (e) {
                socket.emit('read:joinGroup', { error: e });
            }
        }));
        socket.on('read:groupMetadata', (chatId) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.groupMetadata(chatId);
                socket.emit('read:groupMetadata', groupMetadata);
            }
            catch (e) {
                socket.emit('read:groupMetadata', { error: e });
            }
        }));
        socket.on('read:groupInviteMetadata', (inviteCode) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupInviteMetadata = yield session.groupInviteMetadata(inviteCode);
                socket.emit('read:groupInviteMetadata', groupInviteMetadata);
            }
            catch (e) {
                socket.emit('read:groupInviteMetadata', { error: e });
            }
        }));
    });
}
function registerAuthHandlers(io, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        let session = new whatsappsession_1.WhatsAppSession({ acl: { allowAll: true } });
        let sharedSession;
        yield assignSocket(session, socket);
        const authenticateSession = (payload) => __awaiter(this, void 0, void 0, function* () {
            const { sessionAuth, sharedConnection } = payload;
            const auth = whatsappauth_1.WhatsAppAuth.fromString(sessionAuth);
            if (auth === undefined) {
                socket.emit('connection:auth', { error: 'Unparsable Session Auth' });
                return;
            }
            const name = auth.id();
            if (name === undefined) {
                socket.emit('connection:auth', { error: 'Invalid Auth: not authenticated' });
                return;
            }
            if (sharedConnection === true || sharedSession === undefined) {
                sharedSession = { name, numListeners: 1, session };
                if (sharedSession.name in globalSessions) {
                    console.log('Using shared session');
                    yield session.close();
                    sharedSession = globalSessions[sharedSession.name];
                    sharedSession.numListeners += 1;
                    session = sharedSession.session;
                    yield assignSocket(session, socket);
                }
                else {
                    console.log('Creating new sharable session');
                    globalSessions[sharedSession.name] = sharedSession;
                    session.setAuth(auth);
                    yield session.init();
                }
            }
            else {
                session.setAuth(auth);
                yield session.init();
            }
            yield assignAuthenticatedEvents(session, socket);
        });
        socket.on('disconnect', () => __awaiter(this, void 0, void 0, function* () {
            console.log('Disconnecting');
            if (sharedSession !== undefined) {
                sharedSession.numListeners -= 1;
                if (sharedSession.numListeners === 0) {
                    yield sharedSession.session.close();
                    // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
                    delete globalSessions[sharedSession.name];
                }
            }
            else {
                yield session.close();
            }
        }));
        socket.on('connection:qr', () => __awaiter(this, void 0, void 0, function* () {
            const qrCode = session.qrCode();
            socket.emit('connection:qr', { qrCode });
        }));
        socket.on('connection:status', () => {
            const connection = session.connection();
            socket.emit('connection:status', { connection });
        });
        socket.on('connection:auth', authenticateSession);
        socket.on('connection:auth:anonymous', () => __awaiter(this, void 0, void 0, function* () {
            console.log('Initializing empty session');
            yield session.init();
            session.once('connection:ready', () => __awaiter(this, void 0, void 0, function* () {
                yield assignAuthenticatedEvents(session, socket);
            }));
        }));
    });
}
exports.registerAuthHandlers = registerAuthHandlers;
