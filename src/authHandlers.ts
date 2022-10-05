import { Server, Socket } from 'socket.io'

import { WhatsAppSession } from './whatsappsession'

interface AuthenticateSessionParams {
  sessionInfo: string
  sharedConnection?: boolean
}

module.exports = async (io: Server, socket: Socket) => {
  const session = new WhatsAppSession({})
  await session.init()
  const authenticateSession = (payload: AuthenticateSessionParams) => {
    const { sessionInfo, sharedConnection } = payload
    console.log(`sessionInfo: ${sessionInfo}`)
    console.log(`sharedConnection: ${sharedConnection}`)
  }

  const getQR = () => {
    console.log(session.qrCode())
  }

  socket.once('auth', authenticateSession)
  socket.on('auth:qr', getQR)
}
