import { Server, Socket } from 'socket.io'

import { WhatsAppSessionConfig, WhatsAppSession } from './whatsappsession'
import { WhatsAppAuth } from './whatsappauth'

interface AuthenticateSessionParams {
  sessionAuth: string
  sharedConnection?: boolean
}

interface SharedSession {
  session: WhatsAppSession
  name: string
  numListeners: number
}

const globalSessions: { [_: string]: SharedSession } = {}

async function assignBasicEvents (session: WhatsAppSession, socket: Socket): Promise<void> {
  session.on('connection:auth', (state) => {
    socket.emit('connection:auth', { sessionAuth: state, error: null })
  })
  session.on('connection:qr', (qrCode) => {
    socket.emit('connection:qr', { qr: qrCode.qr })
  })
  session.on('connection:ready', (data) => socket.emit('connection:ready', data))
}

async function assignAuthenticatedEvents (session: WhatsAppSession, socket: Socket): Promise<void> {
  socket.on('write:sendMessage', async (...args: any[]) => {
    try {
      // @ts-expect-error: TS2556: just let me use `...args` here pls.
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

export async function registerAuthHandlers (io: Server, socket: Socket): Promise<void> {
  let session: WhatsAppSession = new WhatsAppSession({ acl: { allowAll: true } })
  let sharedSession: SharedSession | undefined
  await assignBasicEvents(session, socket)

  const authenticateSession = async (payload: AuthenticateSessionParams): Promise<void> => {
    const { sessionAuth, sharedConnection } = payload
    const auth: WhatsAppAuth | undefined = WhatsAppAuth.fromString(sessionAuth)
    if (auth === undefined) {
      socket.emit('connection:auth', { error: 'Unparsable Session Auth' })
      return
    }
    const name = auth.id()
    if (name === undefined) {
      socket.emit('connection:auth', { error: 'Invalid Auth: not authenticated' })
      return
    }

    if (sharedConnection === true || sharedSession === undefined) {
      sharedSession = { name, numListeners: 1, session }
      if (sharedSession.name in globalSessions) {
        console.log(`${session.uid}: Switching to shared session: ${globalSessions[sharedSession.name].session.uid}`)
        await session.close()
        sharedSession = globalSessions[sharedSession.name]
        sharedSession.numListeners += 1
        session = sharedSession.session
        await assignBasicEvents(session, socket)
      } else {
        console.log(`${session.uid}: Creating new sharable session`)
        globalSessions[sharedSession.name] = sharedSession
        session.setAuth(auth)
        await session.init()
      }
    } else {
      session.setAuth(auth)
      await session.init()
    }
    await assignAuthenticatedEvents(session, socket)
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
  socket.on('connection:auth:anonymous', async () => {
    console.log(`${session.uid}: Initializing empty session`)
    session.once('connection:ready', async (): Promise<void> => {
      await assignAuthenticatedEvents(session, socket)
    })
    await session.init()
  })
}
