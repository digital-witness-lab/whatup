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
exports.registerHandlers = void 0;
const whatsappsession_1 = require("./whatsappsession");
const whatsappauth_1 = require("./whatsappauth");
const utils_1 = require("./utils");
const actions_1 = require("./actions");
const globalSessions = {};
function assignBasicEvents(session, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        session.on(actions_1.ACTIONS.connectionAuth, (state) => {
            socket.emit(actions_1.ACTIONS.connectionAuth, { sessionAuth: state, error: null });
        });
        session.on(actions_1.ACTIONS.connectionQr, (qrCode) => {
            socket.emit(actions_1.ACTIONS.connectionQr, { qr: qrCode.qr });
        });
        session.on(actions_1.ACTIONS.connectionReady, (data) => {
            socket.emit(actions_1.ACTIONS.connectionReady, data);
        });
    });
}
function assignAuthenticatedEvents(session, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        socket.on(actions_1.ACTIONS.writeSendMessage, (...args) => __awaiter(this, void 0, void 0, function* () {
            const callback = args.pop();
            try {
                // @ts-expect-error: TS2556: just let me use `...args` here pls.
                const sendMessage = yield session.sendMessage(...args);
                callback(sendMessage);
            }
            catch (e) {
                callback({ error: e });
            }
        }));
        socket.on(actions_1.ACTIONS.writeMarkChatRead, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                yield session.markChatRead(chatId);
                callback({ error: null });
            }
            catch (e) {
                callback({ error: e });
            }
        }));
        socket.on(actions_1.ACTIONS.readMessagesSubscribe, (callback) => __awaiter(this, void 0, void 0, function* () {
            // TODO: this unsubscribe functionality doesn't work using the callback
            // mechanism. I think a better route may be to create a new room when
            // message subscription happens and then put the client into it? this
            // gives the client the opportunity to "unsubscribe" by leaving the room
            // and the server can remove the event listener on that event.
            const emitMessage = (data) => {
                callback(data);
            };
            session.on(actions_1.ACTIONS.readMessages, emitMessage);
            socket.on(actions_1.ACTIONS.readMessages, () => __awaiter(this, void 0, void 0, function* () {
                session.off(actions_1.ACTIONS.readMessages, emitMessage);
            }));
        }));
        socket.on(actions_1.ACTIONS.writeLeaveGroup, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.leaveGroup(chatId);
                callback(groupMetadata);
            }
            catch (e) {
                callback(e);
            }
        }));
        socket.on(actions_1.ACTIONS.readJoinGroup, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.joinGroup(chatId);
                callback(groupMetadata);
            }
            catch (e) {
                callback(e);
            }
        }));
        socket.on(actions_1.ACTIONS.readGroupMetadata, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.groupMetadata(chatId);
                callback(groupMetadata);
            }
            catch (e) {
                callback(e);
            }
        }));
        socket.on(actions_1.ACTIONS.readGroupInviteMetadata, (inviteCode, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupInviteMetadata = yield session.groupInviteMetadata(inviteCode);
                callback(groupInviteMetadata);
            }
            catch (e) {
                callback(e);
            }
        }));
        socket.on(actions_1.ACTIONS.readListGroups, (callback) => {
            callback(session.groups());
        });
    });
}
function getAuthedSession(session, auth, socket, sharedConnection = true) {
    return __awaiter(this, void 0, void 0, function* () {
        let sharedSession;
        let name = auth.id();
        if (name === undefined) {
            throw new Error('Invalid Auth: not authenticated');
        }
        if (sharedConnection === false) {
            name = `private-${Math.floor(Math.random() * 10000000)}-${name}`;
        }
        if (name in globalSessions) {
            console.log(`${session.uid}: Switching to shared session: ${globalSessions[name].session.uid}`);
            yield session.close();
            sharedSession = globalSessions[name];
            sharedSession.numListeners += 1;
            session = sharedSession.session;
            yield assignBasicEvents(session, socket);
        }
        else {
            sharedSession = { name, numListeners: 1, session };
            console.log(`${session.uid}: Creating new sharable session`);
            globalSessions[sharedSession.name] = sharedSession;
            session.setAuth(auth);
            yield session.init();
        }
        yield assignAuthenticatedEvents(session, socket);
        return sharedSession;
    });
}
function registerHandlers(socket) {
    return __awaiter(this, void 0, void 0, function* () {
        let session = new whatsappsession_1.WhatsAppSession({ acl: { allowAll: true } });
        let sharedSession;
        yield assignBasicEvents(session, socket);
        const authenticateSession = (payload, callback) => __awaiter(this, void 0, void 0, function* () {
            const { sessionAuth, sharedConnection } = payload;
            const auth = whatsappauth_1.WhatsAppAuth.fromString(sessionAuth);
            if (auth === undefined) {
                callback(new Error('Unparsable Session Auth'));
                return;
            }
            try {
                // TODO: only use sharedSession and get rid of references to bare
                // `session` object
                sharedSession = yield getAuthedSession(session, auth, socket, sharedConnection);
                session = sharedSession.session;
            }
            catch (e) {
                callback(e);
            }
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
        socket.on(actions_1.ACTIONS.connectionQr, (callback) => __awaiter(this, void 0, void 0, function* () {
            const qrCode = session.qrCode();
            callback({ qrCode });
        }));
        socket.on(actions_1.ACTIONS.connectionStatus, (callback) => {
            const connection = session.connection();
            callback({ connection });
        });
        socket.on(actions_1.ACTIONS.connectionAuth, authenticateSession);
        socket.on(actions_1.ACTIONS.connectionAuthAnonymous, () => __awaiter(this, void 0, void 0, function* () {
            console.log(`${session.uid}: Initializing empty session`);
            session.once(actions_1.ACTIONS.connectionReady, (0, utils_1.resolvePromiseSync)(() => __awaiter(this, void 0, void 0, function* () {
                yield assignAuthenticatedEvents(session, socket);
            })));
            yield session.init();
        }));
    });
}
exports.registerHandlers = registerHandlers;
