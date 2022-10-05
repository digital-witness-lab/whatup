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
    };
    const getQR = () => {
        console.log(session.qrCode());
    };
    socket.once('auth', authenticateSession);
    socket.on('auth:qr', getQR);
});
