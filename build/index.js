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
const uWebSockets_js_1 = require("uWebSockets.js");
const socket_io_1 = require("socket.io");
const handlers_1 = require("./handlers");
// @ts-expect-error: TS7009
const app = new uWebSockets_js_1.App();
const io = new socket_io_1.Server();
const port = 3000;
io.attachApp(app);
io.on('connection', (socket) => __awaiter(void 0, void 0, void 0, function* () {
    console.log(socket.id);
    yield (0, handlers_1.registerHandlers)(io, socket);
}));
app.listen(port, (token) => {
    if (token == null) {
        console.warn('port already in use');
    }
    console.log(`Listening on port: ${port}`);
});
