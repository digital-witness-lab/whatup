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
const SESSION_CLOSE_GRACE_TIME = 5000;
const globalSessions = {};
function assignBasicEvents(sharedSession, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        sharedSession.session.on(actions_1.ACTIONS.connectionQr, (qrCode) => {
            socket.emit(actions_1.ACTIONS.connectionQr, { qr: qrCode });
        });
        socket.on(actions_1.ACTIONS.connectionQr, (callback) => __awaiter(this, void 0, void 0, function* () {
            const qrCode = sharedSession === null || sharedSession === void 0 ? void 0 : sharedSession.session.qrCode();
            callback({ qr: qrCode });
        }));
        socket.on(actions_1.ACTIONS.connectionStatus, (callback) => {
            const connection = sharedSession === null || sharedSession === void 0 ? void 0 : sharedSession.session.connection();
            callback({ connection });
        });
        if (sharedSession.anonymous) {
            sharedSession.session.on(actions_1.ACTIONS.connectionReady, (data) => {
                socket.emit(actions_1.ACTIONS.connectionReady, data);
            });
        }
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
                console.log('Downloaded media message');
                callback(buffer);
            }
            catch (e) {
                console.log(`Exception downloading media message: ${String(e)}`);
                return callback && callback({ error: e.message });
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
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.writeMarkChatRead, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                yield session.markChatRead(chatId);
                callback({ error: null });
            }
            catch (e) {
                return callback && callback({ error: e.message });
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
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.readJoinGroup, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.joinGroup(chatId);
                callback(groupMetadata);
            }
            catch (e) {
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.readGroupMetadata, (chatId, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupMetadata = yield session.groupMetadata(chatId);
                callback(groupMetadata);
            }
            catch (e) {
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.readGroupInviteMetadata, (inviteCode, callback) => __awaiter(this, void 0, void 0, function* () {
            try {
                const groupInviteMetadata = yield session.groupInviteMetadata(inviteCode);
                callback(groupInviteMetadata);
            }
            catch (e) {
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.readListGroups, (callback) => {
            callback(session.groups());
        });
    });
}
function createSession(locator, io, socket, sharedConnection = true, anonymous = false) {
    return __awaiter(this, void 0, void 0, function* () {
        let sharedSession;
        let name = locator.sessionId;
        if (anonymous || !sharedConnection) {
            name = `private-${Math.floor(Math.random() * 10000000)}-${name}`;
        }
        if (name in globalSessions) {
            console.log(`Socket ${socket.id}: Found existing shared connection: ${name}`);
            sharedSession = globalSessions[name];
            sharedSession.numListeners += 1;
            yield assignBasicEvents(sharedSession, socket);
            if (sharedSession.session.isReady()) {
                // incase this event was already issued in the past, let's make sure the
                // client knows the connected session is ready
                socket.emit(actions_1.ACTIONS.connectionReady, {});
            }
        }
        else {
            const session = new whatsappsession_1.WhatsAppSession(locator);
            sharedSession = { name, session, numListeners: 1, anonymous };
            console.log(`Socket ${socket.id}: Creating new session: ${name}`);
            globalSessions[sharedSession.name] = sharedSession;
            yield assignBasicEvents(sharedSession, socket);
            yield session.init();
        }
        if (!anonymous) {
            yield assignAuthenticatedEvents(sharedSession, io, socket);
        }
        return sharedSession;
    });
}
function registerHandlers(io, socket) {
    return __awaiter(this, void 0, void 0, function* () {
        let sharedSession;
        socket.on('disconnect', () => __awaiter(this, void 0, void 0, function* () {
            console.log('Disconnecting');
            if (sharedSession !== undefined) {
                sharedSession.numListeners -= 1;
                yield (0, utils_1.sleep)(SESSION_CLOSE_GRACE_TIME);
                if (sharedSession.name in globalSessions && sharedSession.numListeners === 0) {
                    yield sharedSession.session.close();
                    // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
                    delete globalSessions[sharedSession.name];
                }
            }
        }));
        socket.on(actions_1.ACTIONS.connectionAuth, (payload, callback) => __awaiter(this, void 0, void 0, function* () {
            const { sharedConnection } = payload;
            payload.isNew = false;
            try {
                sharedSession = yield createSession(payload, io, socket, sharedConnection, false);
                return callback && callback(true);
            }
            catch (e) {
                return callback && callback({ error: e.message });
            }
        }));
        socket.on(actions_1.ACTIONS.connectionAuthAnonymous, (data, callback) => __awaiter(this, void 0, void 0, function* () {
            // TODO: create shared session here
            const { name } = data;
            const locator = whatsappsessionstorage_1.WhatsAppSessionStorage.createLocator(name);
            console.log(`${socket.id}: Initializing anonymous session: ${locator.sessionId}`);
            try {
                sharedSession = yield createSession(locator, io, socket, false, true);
            }
            catch (e) {
                console.log(e);
                return callback && callback({ error: e.message });
            }
            delete locator.isNew;
            socket.emit(actions_1.ACTIONS.connectionAuthLocator, locator);
            sharedSession.session.once(actions_1.ACTIONS.connectionReady, (0, utils_1.resolvePromiseSync)(() => __awaiter(this, void 0, void 0, function* () {
                yield assignAuthenticatedEvents(sharedSession, io, socket);
            })));
            yield sharedSession.session.init();
        }));
    });
}
exports.registerHandlers = registerHandlers;
