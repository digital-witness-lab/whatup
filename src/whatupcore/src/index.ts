import { readFileSync } from 'fs'
import { createSecureServer } from 'http2'
import { Server } from 'socket.io'
import { registerHandlers } from './handlers'

const keydir = process.env.KEY_DIR || './static/'
const port = 3000
console.log(`Loading key:${keydir}/key.pem`)
console.log(`Loading cert:${keydir}/cert.pem`)
const httpServer = createSecureServer({
  allowHTTP1: true,
  key: readFileSync(`${keydir}/key.pem`),
  cert: readFileSync(`${keydir}/cert.pem`)
})

const io = new Server(httpServer, { })

io.on('connection', async (socket) => {
  console.info(`New connection ${socket.id}`)
  await registerHandlers(io, socket)
})

console.log(`Listening on port: ${port}`)
httpServer.listen(port)
