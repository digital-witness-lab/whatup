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
const whatsappsessionstorage_1 = require("./whatsappsessionstorage");
const whatsappsession_1 = require("./whatsappsession");
const utils_1 = require("./utils");
const actions_1 = require("./actions");
const globalSessions = {};
function assignBasicEvents(session, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        session.on(actions_1.ACTIONS.connectionQr, (qrCode) => {
            socket.emit(actions_1.ACTIONS.connectionQr, { qr: qrCode.qr });
        });
        session.on(actions_1.ACTIONS.connectionReady, (data) => {
            socket.emit(actions_1.ACTIONS.connectionReady, data);
        });
    });
}
function assignAuthenticatedEvents(sharedSession, io, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        const session = sharedSession.session;
        if (sharedSession.hasReadMessageHandler == null || !sharedSession.hasReadMessageHandler) {
            session.on(actions_1.ACTIONS.readMessages, (msg) => {
                console.log(`sharing message with room: ${sharedSession.name}`);
                io.to(sharedSession.name).emit(actions_1.ACTIONS.readMessages, msg);
            });
            sharedSession.hasReadMessageHandler = true;
        }
        socket.on(actions_1.ACTIONS.readDownloadMessage, (message, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const buffer = yield sharedSession.session.downloadMessageMedia(message);
                console.log("Downloaded media message");
                callback(buffer);
            }
            catch (e) {
                console.log(`Exception downloading media message: ${String(e)}`);
                callback(e);
            }
        }));
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
        socket.on(actions_1.ACTIONS.readMessagesSubscribe, () => __awaiter(this, void 0, void 0, function* () {
            console.log(`joining room: ${sharedSession.name}`);
            yield socket.join(sharedSession.name);
        }));
        socket.on(actions_1.ACTIONS.readMessagesUnSubscribe, () => __awaiter(this, void 0, void 0, function* () {
            console.log(`leaving room: ${sharedSession.name}`);
            yield socket.leave(sharedSession.name);
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
function getAuthedSession(session, locator, io, socket, sharedConnection = true) {
    var _a;
    return __awaiter(this, void 0, void 0, function* () {
        let sharedSession;
        if (locator === null && session.id() === undefined) {
            throw new Error('No additional auth provided and current session has not been authenticated');
        }
        let name = (_a = locator === null || locator === void 0 ? void 0 : locator.sessionId) !== null && _a !== void 0 ? _a : session.id();
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
            if (session.isReady()) {
                socket.emit(actions_1.ACTIONS.connectionReady, {});
            }
        }
        else {
            sharedSession = { name, numListeners: 1, session };
            console.log(`${session.uid}: Creating new sharable session`);
            globalSessions[sharedSession.name] = sharedSession;
            if (locator !== null)
                session.setStorage(locator);
            yield session.init();
        }
        yield assignAuthenticatedEvents(sharedSession, io, socket);
        return sharedSession;
    });
}
function registerHandlers(io, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        let session = new whatsappsession_1.WhatsAppSession({ acl: { allowAll: true } });
        let sharedSession;
        yield assignBasicEvents(session, socket);
        const authenticateSession = (payload, callback) => __awaiter(this, void 0, void 0, function* () {
            const { sharedConnection } = payload;
            if (!whatsappsessionstorage_1.WhatsAppSessionStorage.isValidateLocator(payload)) {
                callback(new Error('Invalid authentication'));
                return;
            }
            try {
                // TODO: only use sharedSession and get rid of references to bare
                // `session` object
                sharedSession = yield getAuthedSession(session, payload, io, socket, sharedConnection);
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
                yield (0, utils_1.sleep)(5000);
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
        socket.on(actions_1.ACTIONS.connectionAuthAnonymous, (data, callback) => __awaiter(this, void 0, void 0, function* () {
            let { sharedConnection } = data;
            if (sharedConnection == null)
                sharedConnection = false;
            console.log(`${session.uid}: Initializing empty session`);
            session.once(actions_1.ACTIONS.connectionReady, (0, utils_1.resolvePromiseSync)(() => __awaiter(this, void 0, void 0, function* () {
                try {
                    // TODO: only use sharedSession and get rid of references to bare
                    // `session` object
                    sharedSession = yield getAuthedSession(session, null, io, socket, sharedConnection);
                    session = sharedSession.session;
                }
                catch (e) {
                    callback(e);
                }
            })));
            yield session.init();
        }));
    });
}
exports.registerHandlers = registerHandlers;
