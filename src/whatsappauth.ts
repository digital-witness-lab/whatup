import { proto, BufferJSON, initAuthCreds, AuthenticationState, AuthenticationCreds, SignalKeyStore, SignalDataSet, SignalDataTypeMap } from '@adiwajshing/baileys'
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

  id (): string | undefined {
    return this.state.creds?.me?.id
  }

  static fromString (data: string): WhatsAppAuth | undefined {
    try {
      const state = JSON.parse(data, BufferJSON.reviver)
      return new WhatsAppAuth(state)
    } catch (e) {
      return undefined
    }
  }

  toString (): string {
    return JSON.stringify(this.state, BufferJSON.replacer)
  }

  update (): void {
    this.emit('state:update', this.toString())
  }

  async get<T extends keyof SignalDataTypeMap>(type: T, ids: string[]): Awaitable<{ [id: string]: SignalDataTypeMap[T] }> {
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

  async set (data: SignalDataSet): Awaitable<void> {
    for (const key in data) {
      if (key === 'app-state-sync-key' && data[key] != null) {
        data[key] = data[key].toObject()
      }
      if (this.state.keys[key] === undefined) {
        this.state.keys[key] = {}
      }
      Object.assign(this.state.keys[key], data[key])
    }
    this.update()
  }
}
