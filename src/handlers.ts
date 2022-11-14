import { WAMessage } from '@adiwajshing/baileys'
import { Server, Socket } from 'socket.io'

import { WhatsAppSessionLocator, WhatsAppSessionStorage } from './whatsappsessionstorage'
import { WhatsAppSession } from './whatsappsession'
import { sleep, resolvePromiseSync } from './utils'
import { ACTIONS } from './actions'

const SESSION_CLOSE_GRACE_TIME = 5000

interface AuthenticateSessionParams {
  sessionLocator: WhatsAppSessionLocator
  sharedConnection?: boolean
}

interface SharedSession {
  session: WhatsAppSession
  name: string
  numListeners: number
  anonymous: boolean
  hasReadMessageHandler?: boolean
}

const globalSessions: { [_: string]: SharedSession } = {}

async function assignBasicEvents (sharedSession: SharedSession, socket: Socket): Promise<void> {
  sharedSession.session.on(ACTIONS.connectionQr, (qrCode) => {
    socket.emit(ACTIONS.connectionQr, { qr: qrCode })
  })
  socket.on(ACTIONS.connectionQr, async (callback: Function) => {
    const qrCode = sharedSession?.session.qrCode()
    callback({ qr: qrCode })
  })
  socket.on(ACTIONS.connectionStatus, (callback: Function) => {
    const connection = sharedSession?.session.connection()
    callback({ connection })
  })
  if (sharedSession.anonymous) {
    sharedSession.session.on(ACTIONS.connectionReady, (data) => {
      socket.emit(ACTIONS.connectionReady, data)
    })
  }
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

  socket.on(ACTIONS.readDownloadMessage, async (message: WAMessage, callback: Function) => {
    try {
      const buffer = await sharedSession.session.downloadMessageMedia(message)
      console.log('Downloaded media message')
      callback(buffer)
    } catch (e: any) {
      console.log(`Exception downloading media message: ${String(e)}`)
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.writeSendMessage, async (...args: any[]) => {
    const callback: Function = args.pop()
    try {
      // @ts-expect-error: TS2556: just let me use `...args` here pls.
      const sendMessage = await session.sendMessage(...args)
      callback(sendMessage)
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.writeMarkChatRead, async (chatId: string, callback: Function) => {
    try {
      await session.markChatRead(chatId)
      callback({ error: null })
    } catch (e: any) {
      return callback && callback({error: e.message})
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

  socket.on(ACTIONS.writeLeaveGroup, async (chatId: string, callback: Function) => {
    try {
      const groupMetadata = await session.leaveGroup(chatId)
      callback(groupMetadata)
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.readJoinGroup, async (chatId: string, callback: Function) => {
    try {
      const groupMetadata = await session.joinGroup(chatId)
      callback(groupMetadata)
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.readGroupMetadata, async (chatId: string, callback: Function) => {
    try {
      const groupMetadata = await session.groupMetadata(chatId)
      callback(groupMetadata)
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.readGroupInviteMetadata, async (inviteCode: string, callback: Function) => {
    try {
      const groupInviteMetadata = await session.groupInviteMetadata(inviteCode)
      callback(groupInviteMetadata)
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.readListGroups, (callback: Function) => {
    callback(session.groups())
  })
}

async function createSession (locator: WhatsAppSessionLocator, io: Server, socket: Socket, sharedConnection: boolean = true, anonymous: boolean = false): Promise<SharedSession> {
  let sharedSession: SharedSession
  let name: string = locator.sessionId
  if (anonymous || !sharedConnection) {
    name = `private-${Math.floor(Math.random() * 10000000)}-${name}`
  }
  if (name in globalSessions) {
    console.log(`Socket ${socket.id}: Found existing shared connection: ${name}`)
    sharedSession = globalSessions[name]
    sharedSession.numListeners += 1
    await assignBasicEvents(sharedSession, socket)
    if (sharedSession.session.isReady()) {
      // incase this event was already issued in the past, let's make sure the
      // client knows the connected session is ready
      socket.emit(ACTIONS.connectionReady, {})
    }
  } else {
    const session = new WhatsAppSession(locator)
    sharedSession = { name, session, numListeners: 1, anonymous }
    console.log(`Socket ${socket.id}: Creating new session: ${name}`)
    globalSessions[sharedSession.name] = sharedSession
    await assignBasicEvents(sharedSession, socket)
    await session.init()
  }
  if (!anonymous) {
    await assignAuthenticatedEvents(sharedSession, io, socket)
  }
  return sharedSession
}

export async function registerHandlers (io: Server, socket: Socket): Promise<void> {
  let sharedSession: SharedSession

  socket.on('disconnect', async () => {
    console.log('Disconnecting')
    if (sharedSession !== undefined) {
      sharedSession.numListeners -= 1
      await sleep(SESSION_CLOSE_GRACE_TIME)
      if (sharedSession.name in globalSessions && sharedSession.numListeners === 0) {
        await sharedSession.session.close()
        // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
        delete globalSessions[sharedSession.name]
      }
    }
  })

  socket.on(ACTIONS.connectionAuth, async (payload: AuthenticateSessionParams, callback: Function): Promise<void> => {
    const { sharedConnection, sessionLocator } = payload
    sessionLocator.isNew = false
    try {
      sharedSession = await createSession(sessionLocator, io, socket, sharedConnection, false)
      return callback && callback({error: null})
    } catch (e: any) {
      return callback && callback({error: e.message})
    }
  })
  socket.on(ACTIONS.connectionAuthAnonymous, async (data: { [_: string]: string }, callback: Function) => {
    // TODO: create shared session here
    const { name } = data
    const locator = WhatsAppSessionStorage.createLocator(name)
    console.log(`${socket.id}: Initializing anonymous session: ${locator.sessionId}`)
    try {
      sharedSession = await createSession(locator, io, socket, false, true)
    } catch (e: any) {
      console.log(e)
      return callback && callback({error: e.message})
    }
    delete locator.isNew
    socket.emit(ACTIONS.connectionAuthLocator, locator)
    sharedSession.session.once(ACTIONS.connectionReady, resolvePromiseSync(async (): Promise<void> => {
      await assignAuthenticatedEvents(sharedSession, io, socket)
    }))
    await sharedSession.session.init()
  })
}
