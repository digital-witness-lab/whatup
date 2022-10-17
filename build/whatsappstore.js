"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WhatsAppStore = void 0;
class WhatsAppStore {
    constructor(acl) {
        this._lastMessage = {};
        this._groupMetadata = {};
        this._contacts = {};
        this._chats = {};
        this.acl = acl;
    }
    bind(sock) {
        this.sock = sock;
        this.sock.ev.on('messages.upsert', this._messageUpsert.bind(this));
        this.sock.ev.on('messages.set', this._updateMessageHistory.bind(this));
        this.sock.ev.on('groups.upsert', this._upsertGroups.bind(this));
        this.sock.ev.on('groups.update', this._updateGroups.bind(this));
        // this.sock.ev.on('group-participants.update', ...)
        this.sock.ev.on('chats.set', this._updateChatHistory.bind(this));
        this.sock.ev.on('chats.upsert', this._upsertChat.bind(this));
        this.sock.ev.on('chats.update', this._updateChat.bind(this));
        this.sock.ev.on('chats.delete', this._deleteChat.bind(this));
        this.sock.ev.on('contacts.set', this._updateContactHistory.bind(this));
        this.sock.ev.on('contacts.upsert', this._upsertContact.bind(this));
        this.sock.ev.on('contacts.update', this._updateContact.bind(this));
    }
    //* ******** START PUBLIC METHODS ************//
    contacts() {
        return Object.values(this._contacts);
    }
    chats() {
        return Object.values(this._chats);
    }
    groups() {
        return Object.values(this._groupMetadata);
    }
    contact(cid) {
        return this._contacts[cid];
    }
    groupMetadata(chatId) {
        return __awaiter(this, void 0, void 0, function* () {
            let metadata = this._groupMetadata[chatId];
            if (metadata === undefined) {
                if (this.sock === undefined)
                    return undefined;
                metadata = yield this.sock.groupMetadata(chatId);
                this.setGroupMetadata(metadata);
            }
            return metadata;
        });
    }
    setChat(chat) {
        const id = chat.id;
        const prevChat = this._chats[id];
        this._chats[id] = chat;
        return prevChat;
    }
    setGroupMetadata(groupMetadata) {
        const chatId = groupMetadata.id;
        const prevMetadata = this._groupMetadata[chatId];
        this._groupMetadata[chatId] = groupMetadata;
        return prevMetadata;
    }
    lastMessage(chatId) {
        return this._lastMessage[chatId];
    }
    //* ******** END PUBLIC METHODS ************//
    //* ******** START Contact Events *************//
    _updateContactHistory(data) {
        data.contacts.map(this._setContact);
        console.log('update contact history:', this._contacts);
    }
    _upsertContact(contacts) {
        contacts.map(this._setContact);
        console.log('upsert contacts:', this._contacts);
    }
    _updateContact(contacts) {
        for (const contact of contacts) {
            const cid = contact.id;
            if (cid == null)
                return;
            if (this._contacts[cid] !== undefined) {
                Object.assign(this._contacts[cid], contact);
            }
        }
        console.log('update contacts:', this._contacts);
    }
    _setContact(contact) {
        const cid = contact.id;
        this._contacts[cid] = contact;
    }
    //* ******** END Contact Events *************//
    //* ******** START Message Events *************//
    _updateMessageHistory(data) {
        const { messages } = data;
        messages.map(this._setLatestMessage);
    }
    _messageUpsert(data) {
        for (const message of data.messages) {
            this._setLatestMessage(message);
        }
    }
    _setLatestMessage(message) {
        var _a;
        const chatId = (_a = message.key) === null || _a === void 0 ? void 0 : _a.remoteJid;
        if (chatId == null)
            return;
        if (!this.acl.canRead(chatId) && !this.acl.canWrite(chatId))
            return;
        const lastMessage = this._lastMessage[chatId];
        if (lastMessage == null || lastMessage.key.id == null || (message.key.id != null && lastMessage.key.id < message.key.id)) {
            this._lastMessage[chatId] = message;
        }
    }
    //* ******** END Message Events *************//
    //* ******** START Chat Events *************//
    _deleteChat(chatIds) {
        for (const chatId of chatIds) {
            // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
            delete this._chats[chatId];
        }
    }
    _updateChat(chats) {
        for (const chat of chats) {
            const cid = chat.id;
            if (cid == null)
                return;
            if (this._chats[cid] !== undefined) {
                Object.assign(this._chats[cid], chat);
            }
        }
        console.log('update contacts:', this._contacts);
    }
    _upsertChat(chats) {
        chats.map(this.setChat);
    }
    _updateChatHistory(data) {
        data.chats.map(this.setChat);
    }
    //* ******** END Chat Events *************//
    //* ******** START Contact Events *************//
    _upsertGroups(groupMetadatas) {
        groupMetadatas.map(this.setGroupMetadata);
    }
    _updateGroups(groupMetadatas) {
        for (const groupMetadata of groupMetadatas) {
            const gid = groupMetadata.id;
            if (gid == null)
                return;
            if (this._groupMetadata[gid] !== undefined) {
                Object.assign(this._groupMetadata[gid], groupMetadata);
            }
        }
        console.log('update contacts:', this._contacts);
    }
}
exports.WhatsAppStore = WhatsAppStore;
