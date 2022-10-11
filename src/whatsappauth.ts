import { initAuthCreds, AuthenticationState, AuthenticationCreds, SignalKeyStore, SignalDataSet, SignalDataTypeMap } from '@adiwajshing/baileys'

type Awaitable<T> = T | PromiseLike<T>

export interface AuthenticationData {
  creds: AuthenticationCreds
  [_: string]: any
}

export class WhatsAppAuth implements SignalKeyStore {
  protected state: AuthenticationData

  constructor (state: AuthenticationData | null = null) {
    this.state = state !== null ? state : { creds: initAuthCreds() }
  }

  protected _uniqueId (type: string, id: string): string {
    return `${type}.${id}`
  }

  getAuth (): AuthenticationState {
    return {
      creds: this.state.creds,
      keys: this
    }
  }

  async get<T extends keyof SignalDataTypeMap>(type: T, ids: string[]): Awaitable<{ [id: string]: SignalDataTypeMap[T] }> {
    const data: { [_: string]: SignalDataTypeMap[typeof type] } = { }
    for (const id of ids) {
      const key = this._uniqueId(type, id)
      const value = this.state.keys.get(key)
      data[id] = value
    }
    return data
  }

  setCreds (creds: AuthenticationCreds): void {
    this.state.creds = creds
  }

  async set (data: SignalDataSet): Awaitable<void> {
    for (const category in data) {
      for (const id in data[category]) {
        const key: string = this._uniqueId(category, id)
        const value = data[category][id]
        if (value != null) {
          this.state.keys.set(key, value)
        } else {
          delete this.state.keys[key]
        }
      }
    }
  }
}
