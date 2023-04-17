import { readFileSync } from 'fs'
import { createSecureServer } from 'http2'
import { Server } from 'socket.io'
import { registerHandlers } from './handlers'

const port = 3000
const httpServer = createSecureServer({
  allowHTTP1: true,
  key: readFileSync('static/key.pem'),
  cert: readFileSync('static/cert.pem')
})

const io = new Server(httpServer, { })

io.on('connection', async (socket) => {
  console.info(`New connection ${socket.id}`)
  await registerHandlers(io, socket)
})

console.log(`Listening on port: ${port}`)
httpServer.listen(port)
