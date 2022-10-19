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
  session.on(ACTIONS.connectionReady, (data) => {
    socket.emit(ACTIONS.connectionReady, data)
  })
}

async function assignAuthenticatedEvents (session: WhatsAppSession, socket: Socket): Promise<void> {
  socket.on(ACTIONS.writeSendMessage, async (...args: any[]) => {
    const callback: any = args.pop()
    try {
      // @ts-expect-error: TS2556: just let me use `...args` here pls.
      const sendMessage = await session.sendMessage(...args)
      callback(sendMessage)
    } catch (e) {
      callback({ error: e })
    }
  })
  socket.on(ACTIONS.writeMarkChatRead, async (chatId: string, callback: any) => {
    try {
      await session.markChatRead(chatId)
      callback({ error: null })
    } catch (e) {
      callback({ error: e })
    }
  })
  socket.on(ACTIONS.readMessagesSubscribe, async (callback: any) => {
    // TODO: this unsubscribe functionality doesn't work using the callback
    // mechanism. I think a better route may be to create a new room when
    // message subscription happens and then put the client into it? this
    // gives the client the opportunity to "unsubscribe" by leaving the room
    // and the server can remove the event listener on that event.
    const emitMessage = (data: any): void => {
      callback(data)
    }
    session.on(ACTIONS.readMessages, emitMessage)
    socket.on(ACTIONS.readMessages, async () => {
      session.off(ACTIONS.readMessages, emitMessage)
    })
  })

  socket.on(ACTIONS.writeLeaveGroup, async (chatId: string, callback: any) => {
    try {
      const groupMetadata = await session.leaveGroup(chatId)
      callback(groupMetadata)
    } catch (e) {
      callback(e)
    }
  })
  socket.on(ACTIONS.readJoinGroup, async (chatId: string, callback: any) => {
    try {
      const groupMetadata = await session.joinGroup(chatId)
      callback(groupMetadata)
    } catch (e) {
      callback(e)
    }
  })
  socket.on(ACTIONS.readGroupMetadata, async (chatId: string, callback: any) => {
    try {
      const groupMetadata = await session.groupMetadata(chatId)
      callback(groupMetadata)
    } catch (e) {
      callback(e)
    }
  })
  socket.on(ACTIONS.readGroupInviteMetadata, async (inviteCode: string, callback: any) => {
    try {
      const groupInviteMetadata = await session.groupInviteMetadata(inviteCode)
      callback(groupInviteMetadata)
    } catch (e) {
      callback(e)
    }
  })
  socket.on(ACTIONS.readListGroups, (callback: any) => {
    callback(session.groups())
  })
}

async function getAuthedSession (session: WhatsAppSession, auth: WhatsAppAuth, socket: Socket, sharedConnection: Boolean = true): Promise<SharedSession> {
  let sharedSession: SharedSession
  let name = auth.id()
  if (name === undefined) {
    throw new Error('Invalid Auth: not authenticated')
  }
  if (sharedConnection === false) {
    name = `private-${Math.floor(Math.random() * 10000000)}-${name}`
  }
  if (name in globalSessions) {
    console.log(`${session.uid}: Switching to shared session: ${globalSessions[name].session.uid}`)
    await session.close()
    sharedSession = globalSessions[name]
    sharedSession.numListeners += 1
    session = sharedSession.session
    await assignBasicEvents(session, socket)
  } else {
    sharedSession = { name, numListeners: 1, session }
    console.log(`${session.uid}: Creating new sharable session`)
    globalSessions[sharedSession.name] = sharedSession
    session.setAuth(auth)
    await session.init()
  }
  await assignAuthenticatedEvents(session, socket)
  return sharedSession
}

export async function registerHandlers (socket: Socket): Promise<void> {
  let session: WhatsAppSession = new WhatsAppSession({ acl: { allowAll: true } })
  let sharedSession: SharedSession | undefined
  await assignBasicEvents(session, socket)

  const authenticateSession = async (payload: AuthenticateSessionParams, callback: any): Promise<void> => {
    const { sessionAuth, sharedConnection } = payload
    const auth: WhatsAppAuth | undefined = WhatsAppAuth.fromString(sessionAuth)
    if (auth === undefined) {
      callback(new Error('Unparsable Session Auth'))
      return
    }
    try {
      // TODO: only use sharedSession and get rid of references to bare
      // `session` object
      sharedSession = await getAuthedSession(session, auth, socket, sharedConnection)
      session = sharedSession.session
    } catch (e) {
      callback(e)
    }
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
  socket.on(ACTIONS.connectionQr, async (callback: any) => {
    const qrCode = session.qrCode()
    callback({ qrCode })
  })
  socket.on(ACTIONS.connectionStatus, (callback: any) => {
    const connection = session.connection()
    callback({ connection })
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
