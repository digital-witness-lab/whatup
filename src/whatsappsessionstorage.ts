import { WhatsAppACLConfig } from './whatsappacl'
import { AuthenticationData } from './whatsappauth'

import path from 'path'
import fs from 'fs'
import crypto from 'crypto'

export interface WhatsAppSessionLocator {
  sessionId: string
  passphrase: string
  dataDir?: string
  createIfMissing?: boolean
}

interface DataRecord {
  authData: AuthenticationData
  aclConfig: WhatsAppACLConfig
}

interface Keys {
  publicKey: crypto.KeyObject
  privateKey?: crypto.KeyObject
}

export class WhatsAppSessionStorage {
  public sessionId: string
  protected dataDir: string
  protected keys: Keys
  protected _sessionHash: string
  protected _record: DataRecord

  constructor (locator: WhatsAppSessionLocator) {
    this.sessionId = locator.sessionId
    this.dataDir = (locator.dataDir ?? './')
    this._sessionHash = crypto.createHash('sha256').update(this.sessionId).digest('hex')

    let keysSecret: Keys
    if (this._hasKeys()) {
      keysSecret = this._loadKeys(locator)
    } else if (locator.createIfMissing ?? true) {
      // The "?? true" effectively sets the default value of createIfMissing to true
      keysSecret = this._createKeys(locator)
    } else {
      throw Error(`Missing keys for session: ${this.sessionId}: ${this._sessionHash}`)
    }
    this.keys = { publicKey: keysSecret.publicKey }
    this._record = this._loadRecord(keysSecret)
  }

  public createLocator (sessionId: string | undefined): WhatsAppSessionLocator {
    return {
      sessionId: sessionId ?? crypto.randomUUID(),
      passphrase: crypto.randomBytes(64).toString('hex')
    }
  }

  public get record (): DataRecord {
    return this._record
  }

  public set record (r: DataRecord) {
    this._record = r
  }

  protected _loadRecord (keys: Keys): DataRecord {
    const contentEnc = this._loadBlob('record')
    return this._decrypt(contentEnc, keys)
  }

  protected _saveRecord (record: DataRecord, keys: Keys): void {
    const contentEnc = this._encrypt(record, keys)
    this._saveBlob(contentEnc, 'record')
  }

  protected _hasKeys (): boolean {
    return fs.existsSync(this._blobPath('privKey')) && fs.existsSync(this._blobPath('pubKey'))
  }

  protected _loadKeys (locator: WhatsAppSessionLocator): Keys {
    const privateKey = crypto.createPrivateKey({
      key: this._loadBlob('privkey'),
      passphrase: locator.passphrase
    })
    const publicKey = crypto.createPublicKey({
      key: this._loadBlob('pubKey')
    })
    return { privateKey, publicKey }
  }

  protected _createKeys (locator: WhatsAppSessionLocator): Keys {
    const keys = crypto.generateKeyPairSync('ed25519', { })
    this._saveBlob(keys.privateKey.export({
      type: 'pkcs8',
      format: 'pem',
      cipher: 'aes-256-cbc',
      passphrase: locator.passphrase
    }), 'privKey')
    this._saveBlob(keys.publicKey.export({
      type: 'spki',
      format: 'pem'
    }), 'privKey')
    return keys
  }

  private _blobPath (blobType: string): string {
    const filename = `${this._sessionHash}_${blobType}.dat`
    const fileNesting = this._sessionHash.substr(-5).split('').join('/')
    return path.join(this.dataDir, fileNesting, filename)
  }

  private _loadBlob (blobType: string): Buffer {
    const filepath = this._blobPath(blobType)
    return fs.readFileSync(filepath)
  }

  private _saveBlob (blob: Buffer | string, blobType: string): void {
    const filepath = this._blobPath(blobType)
    if (!fs.existsSync(filepath)) {
      const fileparents = path.dirname(filepath)
      fs.mkdirSync(fileparents, { recursive: true })
    }
    fs.writeFileSync(filepath, blob)
  }

  protected _decrypt (contentEnc: Buffer, keys: Keys): DataRecord {
    if (keys.privateKey === undefined) {
      throw Error('Private key must be set to decrypt')
    }
    const contentDec = crypto.privateDecrypt(keys.privateKey, contentEnc)
    return JSON.parse(contentDec.toString('utf-8'))
  }

  protected _encrypt (record: DataRecord, keys: Keys): Buffer {
    const contentDec = Buffer.from(JSON.stringify(record))
    const contentEnc = crypto.publicEncrypt(keys.publicKey, contentDec)
    return contentEnc
  }
}
