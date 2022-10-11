import { proto, initAuthCreds, AuthenticationState, AuthenticationCreds, SignalKeyStore, SignalDataSet, SignalDataTypeMap } from '@adiwajshing/baileys'
import { EventEmitter } from 'events'

type Awaitable<T> = T | PromiseLike<T>

export interface AuthenticationData {
  creds: AuthenticationCreds
  keys: { [_: string]: any }
}

export class WhatsAppAuth implements SignalKeyStore extends EventEmitter {
  protected state: AuthenticationData

  constructor (state: AuthenticationData | null = null) {
    super()
    this.state = state !== null ? state : { creds: initAuthCreds(), keys: {} }
  }

  getAuth (): AuthenticationState {
    return {
      creds: this.state.creds,
      keys: this
    }
  }

  async get<T extends keyof SignalDataTypeMap>(type: T, ids: string[]): Awaitable<{ [id: string]: SignalDataTypeMap[T] }> {
    console.log("Auth get:", type, ids)
    return ids.reduce((dict: { [_: string]: any }, id: string): { [id: string]: SignalDataTypeMap[T] } => {
      let value = this.state.keys[type]?.[id]
      if (value != null) {
        if (type === 'app-state-sync-key') {
          value = proto.Message.AppStateSyncKeyData.fromObject(value)
        }
        dict[id] = value
      }
      return dict
    }, { })
  }

  setCreds (creds: AuthenticationCreds): void {
    console.log("set creds", creds)
    this.state.creds = creds
    this.emit('state:update', this.state)
  }

  async set (data: SignalDataSet): Awaitable<void> {
    console.log("auth set:", data)
    for (const key in data) {
      if (this.state.keys[key] === undefined) {
        this.state.keys[key] = {}
      }
      Object.assign(this.state.keys[key], data[key])
    }
    this.emit('state:update', this.state)
  }
}
