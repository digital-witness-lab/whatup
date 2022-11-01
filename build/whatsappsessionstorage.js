"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppSessionStorage = void 0;
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const crypto_1 = __importDefault(require("crypto"));
class WhatsAppSessionStorage {
    constructor(locator) {
        var _a, _b;
        this.sessionId = locator.sessionId;
        this.dataDir = ((_a = locator.dataDir) !== null && _a !== void 0 ? _a : './');
        this._sessionHash = crypto_1.default.createHash('sha256').update(this.sessionId).digest('hex');
        let keysSecret;
        if (this._hasKeys()) {
            keysSecret = this._loadKeys(locator);
        }
        else if ((_b = locator.createIfMissing) !== null && _b !== void 0 ? _b : true) {
            // The "?? true" effectively sets the default value of createIfMissing to true
            keysSecret = this._createKeys(locator);
        }
        else {
            throw Error(`Missing keys for session: ${this.sessionId}: ${this._sessionHash}`);
        }
        this.keys = { publicKey: keysSecret.publicKey };
        this._record = this._loadRecord(keysSecret);
    }
    createLocator(sessionId) {
        return {
            sessionId: sessionId !== null && sessionId !== void 0 ? sessionId : crypto_1.default.randomUUID(),
            passphrase: crypto_1.default.randomBytes(64).toString('hex')
        };
    }
    get record() {
        return this._record;
    }
    set record(r) {
        this._record = r;
    }
    _loadRecord(keys) {
        const contentEnc = this._loadBlob('record');
        return this._decrypt(contentEnc, keys);
    }
    _saveRecord(record, keys) {
        const contentEnc = this._encrypt(record, keys);
        this._saveBlob(contentEnc, 'record');
    }
    _hasKeys() {
        return fs_1.default.existsSync(this._blobPath('privKey')) && fs_1.default.existsSync(this._blobPath('pubKey'));
    }
    _loadKeys(locator) {
        const privateKey = crypto_1.default.createPrivateKey({
            key: this._loadBlob('privkey'),
            passphrase: locator.passphrase
        });
        const publicKey = crypto_1.default.createPublicKey({
            key: this._loadBlob('pubKey')
        });
        return { privateKey, publicKey };
    }
    _createKeys(locator) {
        const keys = crypto_1.default.generateKeyPairSync('ed25519', {});
        this._saveBlob(keys.privateKey.export({
            type: 'pkcs8',
            format: 'pem',
            cipher: 'aes-256-cbc',
            passphrase: locator.passphrase
        }), 'privKey');
        this._saveBlob(keys.publicKey.export({
            type: 'spki',
            format: 'pem'
        }), 'privKey');
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
    _saveBlob(blob, blobType) {
        const filepath = this._blobPath(blobType);
        if (!fs_1.default.existsSync(filepath)) {
            const fileparents = path_1.default.dirname(filepath);
            fs_1.default.mkdirSync(fileparents, { recursive: true });
        }
        fs_1.default.writeFileSync(filepath, blob);
    }
    _decrypt(contentEnc, keys) {
        if (keys.privateKey === undefined) {
            throw Error('Private key must be set to decrypt');
        }
        const contentDec = crypto_1.default.privateDecrypt(keys.privateKey, contentEnc);
        return JSON.parse(contentDec.toString('utf-8'));
    }
    _encrypt(record, keys) {
        const contentDec = Buffer.from(JSON.stringify(record));
        const contentEnc = crypto_1.default.publicEncrypt(keys.publicKey, contentDec);
        return contentEnc;
    }
}
exports.WhatsAppSessionStorage = WhatsAppSessionStorage;
