import { Server, Socket } from 'socket.io'

import { WhatsAppSession } from './whatsappsession'

interface AuthenticateSessionParams {
  sessionAuth: string
  sharedConnection?: boolean
}

interface SharedSession {
  session: WhatsAppACLConfig
  name: string
  numListeners: number
}

const globalSessions: { [_: string]: SharedSession } = {}

module.exports = async (io: Server, socket: Socket) => {
  let session: WhatsAppSession = new WhatsAppSession({ acl: { allowAll: true } })
  let sharedSession: SharedSession | undefined

  const authenticateSession = async (payload: AuthenticateSessionParams): Promise<void> => {
    const { sessionAuth, sharedConnection } = payload
    const authData = JSON.parse(sessionAuth)
    if (authData.creds?.me?.id == null) {
      socket.emit('connection:auth', { error: 'Invalid Credentials: No self ID' })
      return
    }

    if (sharedConnection === true) {
      sharedSession = { name: authData.creds.me.id, numListeners: 1, session }
      if (sharedSession.name in globalSessions) {
        console.log('Using shared session')
        await session.close()
        sharedSession = globalSessions[sharedSession.name]
        sharedSession.numListeners += 1
        session = sharedSession.session
      } else {
        console.log('Creating new sharable session')
        globalSessions[sharedSession.name] = sharedSession
      }
    }

    session.once('ready', (data) => socket.emit('connection:ready', data))
    await session.init()
    socket.emit('connection:auth', { error: null })

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
    socket.on('read:messages:subscribe', async () => {
      const emitMessage = (data: any): void => {
        socket.emit('read:messages', data)
      }
      session.on('message', emitMessage)
      socket.on('read:messages:unsubscribe', async () => {
        session.off('message', emitMessage)
      })
    })

    socket.on('write:leaveGroup', async (chatId: string) => {
      try {
        const groupMetadata = await session.leaveGroup(chatId)
        socket.emit('write:leaveGroup', groupMetadata)
      } catch (e) {
        socket.emit('write:leaveGroup', { error: e })
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
    console.log('Disconnecting')
    if (sharedSession !== undefined) {
      sharedSession.numListeners -= 1
      if (sharedSession.numListeners === 0) {
        await sharedSession.session.close()
        // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
        delete globalSessions[sharedSession.name]
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
