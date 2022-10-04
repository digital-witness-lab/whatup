import makeWASocket, {Browsers, useMultiFileAuthState, makeInMemoryStore, ConnectionState, WASocket, WAMessage, MessageUpsertType, MessageRetryMap, DisconnectReason} from '@adiwajshing/baileys'
import { Boom } from '@hapi/boom'
import {EventEmitter} from 'events';


function sleep(ms: number) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
}

export interface WhatsAppSessionChatAccess {
    canWrite: string[],
    canRead: string[],
    canReadWrite: string[]
}


export interface WhatsAppSessionConfig {
    groupChats?: string[],
    authString?: string
}


export interface WhatsAppSessionInterface {
    init(): void;
    qrCode(): string | undefined;
}


export class WhatsAppSession extends EventEmitter implements WhatsAppSessionInterface {
    protected sock?: WASocket = undefined;
    protected config: WhatsAppSessionConfig = {};
    protected msgRetryCounterMap: MessageRetryMap = { };
    protected lastConnectionState: Partial<ConnectionState> = {};
    protected _messages: WAMessage[] = [];
    protected store;

    constructor(config: Partial<WhatsAppSessionConfig>) {
        super();
        this.config = config;
        this.store = makeInMemoryStore({});
    }

    async init() {
        const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
        this.sock = makeWASocket({
            browser: Browsers.macOS('Desktop'),
            auth: state 
        });
        this.store.bind(this.sock.ev)
        this.sock.ev.on ('creds.update', saveCreds)
        this.sock.ev.on("connection.update", this._updateConnectionState.bind(this));
        this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this));
    }

    async _messageUpsert(data: {messages: WAMessage[], type: MessageUpsertType}) {
        const {messages, type} = data;
        for (let message of messages) {
            if (!message.key.fromMe) {
                this.emit('message', {message, type});
                console.log(`Got message: ${JSON.stringify(message)}`);
                this._messages.push(message)

                if (message.key.remoteJid) {
                    await this.sendMessage(message.key.remoteJid, "hello?");
                }
            }
        }
    }

    async _updateConnectionState(data: Partial<ConnectionState>) {
        if (data.qr && data.qr !== this.lastConnectionState.qr) {
            this.emit('qrCode', data);
        }
        if (data.connection === 'open') {
            this.emit('ready', data);
        } else if (data.connection) {
            this.emit('closed', data);
            const { lastDisconnect } = data;
            if (lastDisconnect) {
                const shouldReconnect = (lastDisconnect.error as Boom)?.output?.statusCode !== DisconnectReason.loggedOut
                if(shouldReconnect) {
                    await this.init()
                }
            }
        }
        this.lastConnectionState = {...this.lastConnectionState, ...data}
        console.log(`State: ${JSON.stringify(this.lastConnectionState)}`)
    }

    messages(): WAMessage[] {
        return this._messages;
    }

    qrCode(): string | undefined {
        return this.lastConnectionState.qr;
    }

    async sendMessage(chatId: string, message: string, clearChatStatus: boolean = true, vampMaxSeconds: number | undefined = 10) {
        if (clearChatStatus === true) {
            await this.markChatRead(chatId)
        }
        if (vampMaxSeconds > 0) {
            const nComposing: number = Math.floor(Math.random() * vampMaxSeconds);
            for (let i=0; i < nComposing; i+=1) {
                await this.sock?.sendPresenceUpdate('composing', chatId) 
                await sleep(Math.random() * 1000);
            }
            await this.sock?.sendPresenceUpdate('available', chatId) 
        }
        await this.sock?.sendMessage(chatId, {text: message})
    }

    async markChatRead(chatId: string) {
        const msg: WAMessage | undefined = await this.store.mostRecentMessage(chatId, undefined);
        if (msg?.key) {
            await this.sock?.chatModify({ markRead: false, lastMessages: [msg] }, chatId)
        }
    }
}
