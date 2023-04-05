import { App } from 'uWebSockets.js'
import { Server } from 'socket.io'
import { registerHandlers } from './handlers'

// @ts-expect-error: TS7009
const app = new App()
const io = new Server()
const port = 3000

io.attachApp(app)

io.on('connection', async (socket) => {
  console.info(`New connection ${socket.id}`)
  await registerHandlers(io, socket)
})

app.listen(port, (token: any) => {
  if (token == null) {
    console.warn('port already in use')
  }
  console.log(`Listening on port: ${port}`)
})
