import { WAMessage } from '@adiwajshing/baileys'
import { Server, Socket } from 'socket.io'

import { WhatsAppSessionLocator, WhatsAppSessionStorage } from './whatsappsessionstorage'
import { WhatsAppSession } from './whatsappsession'
import { WhatsAppAuth } from './whatsappauth'
import { sleep, resolvePromiseSync } from './utils'
import { ACTIONS } from './actions'

interface AuthenticateSessionParams extends WhatsAppSessionLocator {
  sharedConnection?: boolean
}

interface SharedSession {
  session: WhatsAppSession
  name: string
  numListeners: number
  hasReadMessageHandler?: boolean
}

const globalSessions: { [_: string]: SharedSession } = {}

async function assignBasicEvents (session: WhatsAppSession, socket: Socket): Promise<void> {
  session.on(ACTIONS.connectionQr, (qrCode) => {
    socket.emit(ACTIONS.connectionQr, { qr: qrCode.qr })
  })
  session.on(ACTIONS.connectionReady, (data) => {
    socket.emit(ACTIONS.connectionReady, data)
  })
}

async function assignAuthenticatedEvents (sharedSession: SharedSession, io: Server, socket: Socket): Promise<void> {
  const session: WhatsAppSession = sharedSession.session
  if (sharedSession.hasReadMessageHandler == null || !sharedSession.hasReadMessageHandler) {
    session.on(ACTIONS.readMessages, (msg: any): void => {
      console.log(`sharing message with room: ${sharedSession.name}`)
      io.to(sharedSession.name).emit(ACTIONS.readMessages, msg)
    })
    sharedSession.hasReadMessageHandler = true
  }

  socket.on(ACTIONS.readDownloadMessage, async (message: WAMessage, callback: any) => {
    try {
      const buffer = await sharedSession.session.downloadMessageMedia(message)
      console.log("Downloaded media message")
      callback(buffer)
    } catch (e) {
      console.log(`Exception downloading media message: ${String(e)}`)
      callback(e)
    }
  })
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

  socket.on(ACTIONS.readMessagesSubscribe, async () => {
    console.log(`joining room: ${sharedSession.name}`)
    await socket.join(sharedSession.name)
  })

  socket.on(ACTIONS.readMessagesUnSubscribe, async () => {
    console.log(`leaving room: ${sharedSession.name}`)
    await socket.leave(sharedSession.name)
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

async function getAuthedSession (session: WhatsAppSession, locator: WhatsAppSessionLocator | null, io: Server, socket: Socket, sharedConnection: Boolean = true): Promise<SharedSession> {
  let sharedSession: SharedSession
  if (locator === null && session.id() === undefined) {
    throw new Error('No additional auth provided and current session has not been authenticated')
  }
  let name = locator?.sessionId ?? session.id()
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
    if (session.isReady()) {
      socket.emit(ACTIONS.connectionReady, {})
    }
  } else {
    sharedSession = { name, numListeners: 1, session }
    console.log(`${session.uid}: Creating new sharable session`)
    globalSessions[sharedSession.name] = sharedSession
    if (locator !== null) session.setStorage(locator)
    await session.init()
  }
  await assignAuthenticatedEvents(sharedSession, io, socket)
  return sharedSession
}

export async function registerHandlers (io: Server, socket: Socket): Promise<void> {
  let session: WhatsAppSession = new WhatsAppSession({ acl: { allowAll: true } })
  let sharedSession: SharedSession | undefined
  await assignBasicEvents(session, socket)

  const authenticateSession = async (payload: AuthenticateSessionParams, callback: any): Promise<void> => {
    const { sharedConnection } = payload
    if (!WhatsAppSessionStorage.isValidateLocator(payload)) {
      callback(new Error('Invalid authentication'))
      return
    }
    try {
      // TODO: only use sharedSession and get rid of references to bare
      // `session` object
      sharedSession = await getAuthedSession(session, payload, io, socket, sharedConnection)
      session = sharedSession.session
    } catch (e) {
      callback(e)
    }
  }

  socket.on('disconnect', async () => {
    console.log('Disconnecting')
    if (sharedSession !== undefined) {
      sharedSession.numListeners -= 1
      await sleep(5000)
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
  socket.on(ACTIONS.connectionAuthAnonymous, async (data: Partial<AuthenticateSessionParams>, callback: any) => {
    let { sharedConnection } = data
    if (sharedConnection == null) sharedConnection = false
    console.log(`${session.uid}: Initializing empty session`)
    session.once(ACTIONS.connectionReady, resolvePromiseSync(async (): Promise<void> => {
      try {
        // TODO: only use sharedSession and get rid of references to bare
        // `session` object
        sharedSession = await getAuthedSession(session, null, io, socket, sharedConnection)
        session = sharedSession.session
      } catch (e) {
        callback(e)
      }
    }))
    await session.init()
  })
}
