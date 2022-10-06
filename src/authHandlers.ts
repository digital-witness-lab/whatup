import { Server, Socket } from 'socket.io'

import { WhatsAppSession } from './whatsappsession'

interface AuthenticateSessionParams {
  sessionInfo: string
  sharedConnection?: boolean
}

module.exports = async (io: Server, socket: Socket) => {
  const session: WhatsAppSession = new WhatsAppSession({})
  await session.init()

  const authenticateSession = (payload: AuthenticateSessionParams) => {
    const { sessionInfo, sharedConnection } = payload
    console.log(`sessionInfo: ${sessionInfo}`)
    console.log(`sharedConnection: ${sharedConnection}`)

    socket.on('write:sendMessage', async (...args: any[]) => {
      try {
        const sendMessage = await session.sendMessage(...args)
        socket.emit('write:sendMessage', sendMessage)
      } catch (e) {
        socket.emit('write:sendMessage', { error: e })
      }
    })
    socket.on('write:markChatRead', async (chatId: string) => {
      try {
        const markChatRead = await session.markChatRead(chatId)
        socket.emit('write:markChatRead', { error: null })
      } catch (e) {
        socket.emit('write:markChatRead', { error: e })
      }
    })

    socket.on('read:joinGroup', async (chatId: string) => {
      try {
        const groupMetadata = await session.joinGroup(chatId)
        socket.emit('read:joinGroup', groupMetadata)
      } catch (e) {
        socket.emit('read:joinGroup', { error: e })
      }
    })
    socket.on('read:groupMetadata', async (chatId: string) => {
      try {
        const groupMetadata = await session.groupMetadata(chatId)
        socket.emit('read:groupMetadata', groupMetadata)
      } catch (e) {
        socket.emit('read:groupMetadata', { error: e })
      }
    })
  }

  socket.on('connection:qr', async () => {
    const qrCode = session.qrCode()
    const QR = await import('qrcode-terminal')
    QR?.generate(qrCode, { small: true })
    socket.emit('connection:qr', { qrCode })
  })
  socket.on('connection:status', () => {
    const connection = session.connection()
    socket.emit('connection:status', { connection })
  })
  socket.on('connection:auth', authenticateSession)
}
