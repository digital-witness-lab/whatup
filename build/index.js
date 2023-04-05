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
const fs_1 = require("fs");
const http2_1 = require("http2");
const socket_io_1 = require("socket.io");
const handlers_1 = require("./handlers");
const port = 3000;
const httpServer = (0, http2_1.createSecureServer)({
    allowHTTP1: true,
    key: (0, fs_1.readFileSync)('static/key.pem'),
    cert: (0, fs_1.readFileSync)('static/cert.pem')
});
const io = new socket_io_1.Server(httpServer, {});
io.on('connection', (socket) => __awaiter(void 0, void 0, void 0, function* () {
    console.info(`New connection ${socket.id}`);
    yield (0, handlers_1.registerHandlers)(io, socket);
}));
console.log(`Listening on port: ${port}`);
httpServer.listen(port);
