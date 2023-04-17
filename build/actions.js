"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ACTIONS = void 0;
var ACTIONS;
(function (ACTIONS) {
    ACTIONS["writeMarkChatRead"] = "write_chat_markRead";
    ACTIONS["writeSendMessage"] = "write_messages_send";
    ACTIONS["writeLeaveGroup"] = "write_group_leave";
    ACTIONS["readMessagesSubscribe"] = "read_messages_subscribe";
    ACTIONS["readMessagesUnSubscribe"] = "read_messages_unsubscribe";
    ACTIONS["readMessages"] = "read_messages";
    ACTIONS["readDownloadMessage"] = "read_messages_downloadMedia";
    ACTIONS["readGroupInviteMetadata"] = "read_groups_inviteMetadata";
    ACTIONS["readGroupMetadata"] = "read_groups_metadata";
    ACTIONS["readJoinGroup"] = "read_groups_join";
    ACTIONS["readListGroups"] = "read_groups_list";
    ACTIONS["connectionAuthAnonymous"] = "connection_auth_anonymous";
    ACTIONS["connectionAuth"] = "connection_auth";
    ACTIONS["connectionAuthLocator"] = "connection_auth_locator";
    ACTIONS["connectionStatus"] = "connection_status";
    ACTIONS["connectionReady"] = "connection_ready";
    ACTIONS["connectionClosed"] = "connection_closed";
    ACTIONS["connectionQr"] = "connection_qr";
})(ACTIONS = exports.ACTIONS || (exports.ACTIONS = {}));
