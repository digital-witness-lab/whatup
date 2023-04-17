"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppSessionStorage = void 0;
const baileys_1 = require("@adiwajshing/baileys");
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const crypto_1 = __importDefault(require("crypto"));
const DEFAULT_SESSION_STORAGE_OPTIONS = {
    datadir: './data/',
    loadRecord: true
};
const DEFAULT_DATA_RECORD = {
    authData: null,
    aclConfig: { allowAll: true } // TODO: pass default ACL through auth
};
class WhatsAppSessionStorage {
    constructor(locator, _options = {}) {
        var _a, _b;
        this.algo = 'aes-256-gcm';
        this._writeQueue = {};
        const options = Object.assign(_options, DEFAULT_SESSION_STORAGE_OPTIONS);
        (_a = locator.isNew) !== null && _a !== void 0 ? _a : (locator.isNew = false);
        this.sessionId = locator.sessionId;
        this.dataDir = options.datadir;
        this._sessionHash = crypto_1.default.createHash('sha256').update(this.sessionId).digest('hex');
        let keysSecret;
        const hasKeys = this._hasKeys();
        if (hasKeys && locator.isNew) {
            throw Error('Cannot set isNew for a locator with an existing sessionId');
        }
        else if (hasKeys) {
            console.log(`${this.sessionId}: Loading existing keys`);
            keysSecret = this._loadKeys(locator);
        }
        else if ((_b = locator.isNew) !== null && _b !== void 0 ? _b : false) {
            console.log(`${this.sessionId}: Creating new keys`);
            // The "?? true" effectively sets the default value of isNew to false
            keysSecret = this._createKeys(locator);
        }
        else {
            throw Error(`Missing keys for session: ${this.sessionId}: ${this._sessionHash}`);
        }
        this.keys = { publicKey: keysSecret.publicKey };
        if (options.loadRecord && !locator.isNew) {
            this._record = this._loadRecord(keysSecret);
        }
        else {
            this.record = DEFAULT_DATA_RECORD;
        }
    }
    static createLocator(name = undefined) {
        let sessionId;
        if (name === undefined || name === '') {
            sessionId = crypto_1.default.randomUUID();
        }
        else {
            sessionId = `${name}-${crypto_1.default.randomUUID()}`;
        }
        return {
            sessionId,
            passphrase: crypto_1.default.randomBytes(64).toString('hex'),
            isNew: true
        };
    }
    static isValid(locator) {
        try {
            const session = new this(Object.assign(Object.assign({}, locator), { isNew: false }), { loadRecord: false });
            console.log(`Created session storage for id: ${session.sessionId}`);
            return true;
        }
        catch (e) {
            return false;
        }
    }
    get record() {
        if (this._record === undefined) {
            throw new Error('Record uninitialized');
        }
        return this._record;
    }
    set record(r) {
        this._record = r;
        this._saveRecord(this._record, this.keys);
    }
    _loadRecord(keys) {
        const contentEnc = this._loadBlob('record');
        return this._decrypt(contentEnc, keys);
    }
    _saveRecord(record, keys) {
        const contentEnc = this._encrypt(record, keys);
        this._saveBlob(contentEnc, 'record', 2000);
    }
    _hasKeys() {
        return fs_1.default.existsSync(this._blobPath('privKey')) && fs_1.default.existsSync(this._blobPath('pubKey'));
    }
    _loadKeys(locator) {
        const privateKey = crypto_1.default.createPrivateKey({
            key: this._loadBlob('privKey'),
            passphrase: locator.passphrase
        });
        const publicKey = crypto_1.default.createPublicKey({
            key: this._loadBlob('pubKey')
        });
        return { privateKey, publicKey };
    }
    _createKeys(locator) {
        const keys = crypto_1.default.generateKeyPairSync('rsa', { modulusLength: 2048 });
        this._saveBlob(keys.privateKey.export({
            type: 'pkcs8',
            format: 'pem',
            cipher: 'aes-256-cbc',
            passphrase: locator.passphrase
        }), 'privKey');
        this._saveBlob(keys.publicKey.export({
            type: 'spki',
            format: 'pem'
        }), 'pubKey');
        return keys;
    }
    _blobPath(blobType) {
        const filename = `${this._sessionHash}_${blobType}.dat`;
        const fileNesting = this._sessionHash.substr(-5).split('').join('/');
        return path_1.default.join(this.dataDir, fileNesting, filename);
    }
    _loadBlob(blobType) {
        const filepath = this._blobPath(blobType);
        return fs_1.default.readFileSync(filepath);
    }
    _saveBlob(blob, blobType, queueTime = 0) {
        const filepath = this._blobPath(blobType);
        if (!fs_1.default.existsSync(filepath)) {
            const fileparents = path_1.default.dirname(filepath);
            fs_1.default.mkdirSync(fileparents, { recursive: true });
        }
        if (queueTime === 0) {
            fs_1.default.writeFileSync(filepath, blob);
        }
        else {
            if (filepath in this._writeQueue) {
                clearTimeout(this._writeQueue[filepath]);
            }
            const timerid = setTimeout(() => fs_1.default.writeFileSync(filepath, blob), queueTime);
            this._writeQueue[filepath] = timerid;
        }
    }
    _decrypt(contentEncMsg, keys) {
        if (keys.privateKey === undefined) {
            throw Error('Private key must be set to decrypt');
        }
        const keyEnc = contentEncMsg.slice(0, 256);
        const iv = contentEncMsg.slice(256, 256 + 16);
        const tag = contentEncMsg.slice(256 + 16, 256 + 16 + 16);
        const contentEnc = contentEncMsg.slice(256 + 16 + 16);
        const key = crypto_1.default.privateDecrypt(keys.privateKey, keyEnc);
        const decipher = crypto_1.default.createDecipheriv(this.algo, key, iv, { authTagLength: 16 });
        decipher.setAuthTag(tag);
        const contentDec = decipher.update(contentEnc);
        try {
            decipher.final();
        }
        catch (err) {
            throw new Error('Could not decrypt message! Authentication failed!');
        }
        return JSON.parse(contentDec.toString('utf-8'), baileys_1.BufferJSON.reviver);
    }
    _encrypt(record, keys) {
        const key = crypto_1.default.randomBytes(32);
        const iv = crypto_1.default.randomBytes(16);
        const cipher = crypto_1.default.createCipheriv(this.algo, key, iv, { authTagLength: 16 });
        const contentDec = Buffer.from(JSON.stringify(record, baileys_1.BufferJSON.replacer));
        const contentEnc = Buffer.concat([cipher.update(contentDec), cipher.final()]);
        const tag = cipher.getAuthTag();
        const keyEnc = crypto_1.default.publicEncrypt(keys.publicKey, key);
        const contentEncMsg = Buffer.concat([keyEnc, iv, tag, contentEnc]);
        return contentEncMsg;
    }
}
exports.WhatsAppSessionStorage = WhatsAppSessionStorage;
