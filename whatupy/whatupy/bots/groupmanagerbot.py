from pathlib import Path
from datetime import datetime
import typing as T

import dataset

from ..protos import whatupcore_pb2 as wuc
from .. import NotRegisteredError, utils
from . import BaseBot, BotCommandArgs


MAX_GROUPS_PER_BOT = 256


class TooManyGroupsRequested(LookupError):
    pass


class GroupAlreadyJoined(Exception):
    pass


class InvalidInviteLink(ValueError):
    pass


class GroupManagerBot(BaseBot):
    def __init__(
        self,
        database_url: str,
        group_join_replication: int = 2,
        *args,
        **kwargs,
    ):
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)
        self.group_join_replication = group_join_replication
        self.db: dataset.Database = dataset.connect(database_url)
        self.init_database(self.db)

    def init_database(self, db):
        db["device_sync"]
        db["device_groups"]
        return

    async def sync_groups(self):
        now = datetime.now()
        db = self.db
        device_name = self.authenticator.username
        db["device_sync"].insert_ignore(
            {"device_name": device_name, "first_update": now}
        )
        db["device_sync"].update(
            {
                "device_name": device_name,
                "last_update": now,
            },
            ["device_name"],
        )
        current_group_infos = list(await self.core_client.GetJoinedGroups())
        current_group_jids: T.Set[str | None] = {
            utils.jid_to_str(gi.JID) for gi in current_group_infos
        }

        required_groups = db["device_groups"].find(device_name=device_name, valid=True)
        required_group_jids: T.Dict[str | None, str] = {
            rg["jid"]: rg["invite_link"] for rg in required_groups
        }

        if len(required_groups) > MAX_GROUPS_PER_BOT:
            raise TooManyGroupsRequested()

        groups_to_leave = current_group_jids.difference(required_group_jids.keys())
        groups_to_join = set(required_group_jids.keys()) - current_group_jids

        results = {
            "groups_joined": [],
            "groups_joined_error": [],
            "groups_left": [],
            "groups_left_error": [],
        }
        for jid in groups_to_join:
            self.logger.info("Joining group from sync: %s", jid)
            # TODO: handle expired invite url
            datum = (
                {
                    "record_joined": now,
                    "device_name": device_name,
                    "jid": jid,
                    "last_checked": now,
                },
            )
            try:
                await self.core_client.JoinGroup(
                    wuc.InviteCode(link=required_group_jids[jid])
                )
                results["groups_joined"].append(jid)
                self.db["device_groups"].update(
                    {**datum, "valid": True},
                    ["device_name", "jid"],
                )
            except:
                results["groups_joined_error"].append(jid)
                self.logger.exception(
                    "Could not join group: %s: %s", jid, required_group_jids[jid]
                )
                self.db["device_groups"].update(
                    {**datum, "valid": False},
                    ["device_name", "jid"],
                )

        for jid in groups_to_leave:
            self.logger.info("Leaving group because of sync: %s", jid)
            results["groups_left"].append(jid)
            # TODO: leave groups?!?!

    async def join_group(self, invite_link, group_join_replication=None, force=False):
        now = datetime.now()
        try:
            group_info: wuc.GroupInfo = await self.core_client.GetGroupInfoInvite(
                invite_link
            )
        except Exception:
            self.logger.exception(
                "Could not get group metadata from invite: %s", invite_link
            )
            raise InvalidInviteLink()

        chat_jid = utils.jid_to_str(group_info.JID)

        if not force and self.db["device_groups"].find_one(jid=chat_jid) is not None:
            # TODO add matching rows to exception
            raise GroupAlreadyJoined()

        group_join_replication = group_join_replication or self.group_join_replication
        query = f"""
            SELECT
                device_name, count
            FROM (
                SELECT
                    device_name,
                    count(*) AS count,
                    ARRAY_AGG(jid) AS groups
                FROM device_groups
                GROUP BY device_name
            ) AS data
            WHERE '{chat_jid}' != ANY (groups)
            ORDER BY count
            LIMIT {group_join_replication}
        """
        rows = list(self.db.query(query))
        for row in rows:
            self.db["device_groups"].insert(
                {
                    "device_name": row["device_name"],
                    "jid": chat_jid,
                    "record_added": now,
                    "invite_link": invite_link,
                    "valid": True,
                    "last_checked": now,
                }
            )
        return {"group_info": group_info, "devices": rows}

    async def rebalance_groups(self, group_join_replication=None):
        group_join_replication = group_join_replication or self.group_join_replication
        query = f"""
            SELECT *
            FROM (
                SELECT jid, count(DISTINCT device_name) AS count
                FROM device_groups
                GROUP BY jid
            ) AS data
            ORDER BY count
            WHERE count != {group_join_replication}
        """
        results = []
        for row in self.db.query(query):
            chat_jid = row["chat_jid"]
            n_devices = row["count"]
            if n_devices > group_join_replication:
                results.append(
                    {
                        "jid": chat_jid,
                        "n_devices": n_devices,
                        "error_desc": "We should leave this group because it is over-subscribed... but should we really?",
                        "error": "should_leave",
                    }
                )
            else:
                invite_row = self.db["device_groups"].find_one(
                    jid=chat_jid, valid=True, order_by=["-last_checked"]
                )
                if invite_row is None:
                    results.append(
                        {
                            "jid": chat_jid,
                            "n_devices": n_devices,
                            "error_desc": "No valid invite link",
                            "error": "no_invite_link",
                        }
                    )
                else:
                    # TODO: try _all_ invite links?
                    invite_link = invite_row["invite_link"]
                    try:
                        N = group_join_replication - n_devices
                        join_data = await self.join_group(
                            invite_link,
                            force=True,
                            group_join_replication=N,
                        )
                        self.db["device_groups"].update(
                            {
                                "valid": True,
                                "last_checked": now,
                                "jid": chat_jid,
                                "invite_link": invite_link,
                            },
                            ["jid"],
                        )
                        results.append(
                            {
                                "jid": chat_jid,
                                "n_devices": n_devices,
                                "new_devices": join_data["devices"],
                            }
                        )
                    except InvalidInviteLink:
                        self.db["device_groups"].update(
                            {"valid": False, "last_checked": now, "jid": chat_jid},
                            ["jid"],
                        )
                        results.append(
                            {
                                "jid": chat_jid,
                                "n_devices": n_devices,
                                "error_desc": "No valid invite link",
                                "error": "no_invite_link",
                            }
                        )
        return results

    def setup_command_args(self):
        parser = BotCommandArgs(
            prog=self.__class__.__name__,
            description="Group Membership Manager. Responsible for distributing out group membership to bots",
        )
        sub_parser = parser.add_subparsers(dest="command")

        group_info = sub_parser.add_parser(
            "join-group",
            description="Join a group given an invite link",
        )
        group_info.add_argument(
            "--N",
            type=int,
            default=None,
            help="Number of devices that should join this group (optional, default = server preference)",
        )
        group_info.add_argument(
            "--force",
            action="store_true",
            help="Whether to force joining the group even if existing devices have already joined",
        )
        group_info.add_argument("link", type=str, help="Valid invite link")

        rebalance_groups = sub_parser.add_parser(
            "rebalance-groups",
            description="Rebalance which devices are in which groups in order to target desired redundancy in group membership",
        )

        return parser

    def _format_device_membership(self, device_counts):
        for dc in device_counts:
            yield f"{dc['device_name']} (part of {dc['count']} groups)"

    async def on_control(self, message):
        params = await self.parse_command(message)
        self.logger.info("Got command: %s", params)
        if params is None:
            return
        sender = message.info.source.sender

        if params.command == "join-group":
            link = params.link

            try:
                result = await self.join_group(
                    link, group_join_replication=params.N, force=params.force
                )
                msg = (
                    "Group «{result['group_info'].groupName.name}» joined by the following devices:\n"
                    "\n".join(list(self._format_device_membership(result["devices"])))
                )
                await self.send_text_message(sender, msg)

            except InvalidInviteLink:
                await self.send_text_message(
                    sender,
                    "The invite code you provided is invalid. Sorry, I can't join this group. :(",
                )
        elif params.command == "repalance-groups":
            pass
