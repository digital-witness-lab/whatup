import { Server, Socket } from 'socket.io'

import { WhatsAppSession } from './whatsappsession'

interface AuthenticateSessionParams {
  sessionInfo: string
  sharedConnection?: boolean
}

interface SharedSession {
  session: WhatsAppACLConfig
  name: string
  numListeners: number
}

const globalSessions: { [_: string]: SharedSession }

module.exports = async (io: Server, socket: Socket) => {
  let session: WhatsAppSession = new WhatsAppSession({})
  let sharedSession: SharedSession

  const authenticateSession = async (payload: AuthenticateSessionParams) => {
    const { sessionInfo, sharedConnection } = payload
    const authData = JSON.parse(sessionInfo)
    if (authData.me?.id == null) {
      socket.emit('connection:auth', { error: 'Invalid Credentials: No self ID' })
      return
    }
    if (sharedConnection === true) {
      sharedSession = { name: authData.creds.me, numListeners: 1, session }
      if (sharedSession.name in globalSessions) {
        await session.close()
        sharedSession = globalSessions[sharedSession.name]
        session = sharedSession.session
        sharedSession.numListeners += 1
      } else {
        globalSessions[sharedSession.name] = sharedSession
      }
    } else {
      const r = Math.floor(Math.random() * 100000)
      sharedSession.name = `${authData.creds.me}-${r}`
      globalSessions[sharedSession.name] = sharedSession
    }

    await session.init()
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
        await session.markChatRead(chatId)
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
    socket.on('read:groupInviteMetadata', async (inviteCode: string) => {
      try {
        const groupInviteMetadata = await session.groupInviteMetadata(inviteCode)
        socket.emit('read:groupInviteMetadata', groupInviteMetadata)
      } catch (e) {
        socket.emit('read:groupInviteMetadata', { error: e })
      }
    })
  }

  socket.on('disconnect', async () => {
    if (sessionName !== null) {
      sessions[sessionName].numListeners -= 1
      if (sessions[sessionName].numListeners === 0) {
        await sessions[sessionName].session.close()
        // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
        delete sessions[sessionName]
      }
    } else {
      await session.close()
    }
  })
  socket.on('connection:qr', async () => {
    const qrCode = session.qrCode()
    socket.emit('connection:qr', { qrCode })
  })
  socket.on('connection:status', () => {
    const connection = session.connection()
    socket.emit('connection:status', { connection })
  })
  socket.on('connection:auth', authenticateSession)
}
