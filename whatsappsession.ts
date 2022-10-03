import makeWASocket, {useMultiFileAuthState, fetchLatestBaileysVersion, ConnectionState, WASocket, UserFacingSocketConfig, AuthenticationCreds, MessageRetryMap} from '@adiwajshing/baileys'
import { Boom } from '@hapi/boom'


export interface WhatsAppSessionConfig {
    authString?: string
}


export class WhatsAppSession {
    protected sock?: WASocket = undefined;
    protected config: WhatsAppSessionConfig = {};
    protected msgRetryCounterMap: MessageRetryMap = { };
    protected lastConnectionState: Partial<ConnectionState> = {};

    constructor(config: WhatsAppSessionConfig) {
        this.config = config;
    }

    async init() {
        const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys')
        this.sock = makeWASocket({
            auth: state 
        });
        this.sock.ev.on("connection.update", this._updateConnectionState);
    }

    private async _updateConnectionState(data: Partial<ConnectionState>) {
        this.lastConnectionState = {...this.lastConnectionState, ...data}
        console.log(`Updated State: ${JSON.stringify(this.lastConnectionState)}`)
    }

    qrCode() {
        return this.lastConnectionState.qr;
    }

}
