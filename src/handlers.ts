import { Socket } from 'socket.io'

import { WhatsAppSession } from './whatsappsession'
import { WhatsAppAuth } from './whatsappauth'
import { resolvePromiseSync } from './utils'
import { ACTIONS } from './actions'

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
  session.on(ACTIONS.connectionAuth, (state) => {
    socket.emit(ACTIONS.connectionAuth, { sessionAuth: state, error: null })
  })
  session.on(ACTIONS.connectionQr, (qrCode) => {
    socket.emit(ACTIONS.connectionQr, { qr: qrCode.qr })
  })
  session.on(ACTIONS.connectionReady, (data) => socket.emit(ACTIONS.connectionReady, data))
}

async function assignAuthenticatedEvents (session: WhatsAppSession, socket: Socket): Promise<void> {
  socket.on(ACTIONS.writeSendMessage, async (...args: any[]) => {
    try {
      // @ts-expect-error: TS2556: just let me use `...args` here pls.
      const sendMessage = await session.sendMessage(...args)
      socket.emit(ACTIONS.writeSendMessage, sendMessage)
    } catch (e) {
      socket.emit(ACTIONS.writeSendMessage, { error: e })
    }
  })
  socket.on(ACTIONS.writeMarkChatRead, async (chatId: string) => {
    try {
      await session.markChatRead(chatId)
      socket.emit(ACTIONS.writeMarkChatRead, { error: null })
    } catch (e) {
      socket.emit(ACTIONS.writeMarkChatRead, { error: e })
    }
  })
  socket.on(ACTIONS.readMessagesSubscribe, async () => {
    const emitMessage = (data: any): void => {
      socket.emit(ACTIONS.readMessages, data)
    }
    session.on(ACTIONS.readMessages, emitMessage)
    socket.on(ACTIONS.readMessages, async () => {
      session.off(ACTIONS.readMessages, emitMessage)
    })
  })

  socket.on(ACTIONS.writeLeaveGroup, async (chatId: string) => {
    try {
      const groupMetadata = await session.leaveGroup(chatId)
      socket.emit(ACTIONS.writeLeaveGroup, groupMetadata)
    } catch (e) {
      socket.emit(ACTIONS.writeLeaveGroup, { error: e })
    }
  })
  socket.on(ACTIONS.readJoinGroup, async (chatId: string) => {
    try {
      const groupMetadata = await session.joinGroup(chatId)
      socket.emit(ACTIONS.readJoinGroup, groupMetadata)
    } catch (e) {
      socket.emit(ACTIONS.readJoinGroup, { error: e })
    }
  })
  socket.on(ACTIONS.readGroupMetadata, async (chatId: string) => {
    try {
      const groupMetadata = await session.groupMetadata(chatId)
      socket.emit(ACTIONS.readGroupMetadata, groupMetadata)
    } catch (e) {
      socket.emit(ACTIONS.readGroupMetadata, { error: e })
    }
  })
  socket.on(ACTIONS.readGroupInviteMetadata, async (inviteCode: string) => {
    try {
      const groupInviteMetadata = await session.groupInviteMetadata(inviteCode)
      socket.emit(ACTIONS.readGroupInviteMetadata, groupInviteMetadata)
    } catch (e) {
      socket.emit(ACTIONS.readGroupInviteMetadata, { error: e })
    }
  })
}

export async function registerHandlers (socket: Socket): Promise<void> {
  let session: WhatsAppSession = new WhatsAppSession({ acl: { allowAll: true } })
  let sharedSession: SharedSession | undefined
  await assignBasicEvents(session, socket)

  const authenticateSession = async (payload: AuthenticateSessionParams): Promise<void> => {
    const { sessionAuth, sharedConnection } = payload
    const auth: WhatsAppAuth | undefined = WhatsAppAuth.fromString(sessionAuth)
    if (auth === undefined) {
      socket.emit(ACTIONS.connectionAuth, { error: 'Unparsable Session Auth' })
      return
    }
    const name = auth.id()
    if (name === undefined) {
      socket.emit(ACTIONS.connectionAuth, { error: 'Invalid Auth: not authenticated' })
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
  socket.on(ACTIONS.connectionQr, async () => {
    const qrCode = session.qrCode()
    socket.emit(ACTIONS.connectionQr, { qrCode })
  })
  socket.on(ACTIONS.connectionStatus, () => {
    const connection = session.connection()
    socket.emit(ACTIONS.connectionStatus, { connection })
  })
  socket.on(ACTIONS.connectionAuth, authenticateSession)
  socket.on(ACTIONS.connectionAuthAnonymous, async () => {
    console.log(`${session.uid}: Initializing empty session`)
    session.once(ACTIONS.connectionReady, resolvePromiseSync(async (): Promise<void> => {
      await assignAuthenticatedEvents(session, socket)
    }))
    await session.init()
  })
}
