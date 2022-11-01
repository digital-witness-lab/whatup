import { proto, BufferJSON, initAuthCreds, AuthenticationState, AuthenticationCreds, SignalKeyStore, SignalDataSet, SignalDataTypeMap } from '@adiwajshing/baileys'
import { EventEmitter } from 'events'

export interface AuthenticationData {
  creds: AuthenticationCreds
  keys: { [_: string]: any }
}

export class WhatsAppAuth extends EventEmitter implements SignalKeyStore {
  readonly state: AuthenticationData

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

  async get<T extends keyof SignalDataTypeMap>(type: T, ids: string[]): Promise<{ [id: string]: SignalDataTypeMap[T] }> {
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

  async set (data: SignalDataSet): Promise<void> {
    let key: keyof SignalDataTypeMap
    for (key in data) {
      if (this.state.keys[key] === undefined) {
        this.state.keys[key] = {}
      }
      Object.assign(this.state.keys[key], data[key])
    }
    this.emit('update')
  }
}
