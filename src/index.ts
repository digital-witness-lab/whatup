import { App } from "uWebSockets.js";
import { Server } from "socket.io";


const registerAuthHandlers = require("./authHandlers");

// @ts-ignore: TS7009
const app = new App();
const io = new Server();
const port = 3000;

io.attachApp(app);

io.on("connection", async (socket) => {
  console.log(socket.id);
  await registerAuthHandlers(io, socket);
});

app.listen(3000, (token: any) => {
  if (!token) {
    console.warn("port already in use");
  }
  console.log(`Listening on port: ${port}`)
});
