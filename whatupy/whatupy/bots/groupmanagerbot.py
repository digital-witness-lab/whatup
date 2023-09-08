from pathlib import Path
import itertools as IT
import csv
from datetime import datetime, timedelta
import typing as T
import random
import asyncio

import dataset

from ..protos import whatupcore_pb2 as wuc
from .. import NotRegisteredError, utils
from . import BaseBot, BotCommandArgs, MediaType


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
        resync_interval: timedelta = timedelta(minutes=10),
        *args,
        **kwargs,
    ):
        kwargs["mark_messages_read"] = True
        super().__init__(*args, **kwargs)
        self.group_join_replication = group_join_replication
        self.resync_interval = resync_interval
        self.db: dataset.Database = dataset.connect(database_url)
        self.init_database(self.db)

    def init_database(self, db):
        # TODO: ensure indicies here
        db["device_sync"]  # device name as PK
        db["device_groups"]  # jid as PK, device_name as index?
        db["group_metadata"]  # id as PK, jid as index
        return

    async def on_start(self, **kwargs):
        while True:
            self.logger.info("Triggering automatic re-syncing of groups")
            await self.sync_groups()
            dt = self.resync_interval.total_seconds() * random.uniform(0.9, 1.1)
            await asyncio.sleep(dt)

    async def sync_groups(self):
        now = datetime.now()
        db = self.db
        device_name = self.authenticator.username
        db["device_sync"].insert_ignore(
            {"device_name": device_name, "first_update": now}
        )
        current_group_infos = list(await self.core_client.GetJoinedGroups())
        current_group_jids: T.Set[str | None] = {
            utils.jid_to_str(gi.JID) for gi in current_group_infos
        }

        required_groups = db["device_groups"].find(device_name=device_name)
        required_groups_jids = {rg["jid"] for rg in required_groups}
        required_groups_valid_invites: T.Dict[str | None, str] = {
            rg["jid"]: rg["invite_link"] for rg in required_groups if rg["valid"]
        }

        if len(required_groups) > MAX_GROUPS_PER_BOT:
            raise TooManyGroupsRequested()

        groups_to_note = current_group_jids.difference(required_groups_jids)
        groups_to_join = set(required_groups_valid_invites.keys()) - current_group_jids

        results = {
            "groups_joined": [],
            "groups_joined_error": [],
            "groups_noted": [],
        }
        for jid in groups_to_join:
            self.logger.info("Joining group from sync: %s", jid)
            # TODO: handle expired invite url
            datum = {
                "record_joined": now,
                "device_name": device_name,
                "jid": jid,
                "last_checked": now,
            }
            link = required_groups_valid_invites[jid]
            try:
                await self.core_client.JoinGroup(wuc.InviteCode(link=link))
                results["groups_joined"].append(jid)
                self.db["device_groups"].update(
                    {**datum, "valid": True},
                    ["device_name", "jid"],
                )
            except InvalidInviteLink:
                results["groups_joined_error"].append(jid)
                self.logger.exception("Could not join group: %s: %s", jid, link)
                self.db["device_groups"].update(
                    {**datum, "valid": False},
                    ["device_name", "jid"],
                )

        for jid in groups_to_note:
            self.logger.info("Leaving group because of sync: %s", jid)
            datum = {
                "record_joined": now,
                "device_name": device_name,
                "jid": jid,
                "last_checked": now,
                "valid": False,
                "invite_link": None,
            }
            self.db["device_groups"].insert(datum)
            results["groups_noted"].append(jid)
            # TODO: leave groups?!?!

        db["device_sync"].update(
            {
                "device_name": device_name,
                "last_update": now,
                "last_sync_log": results,
            },
            ["device_name"],
        )
        return results

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
        N_devices = self.db["device_groups"].count(jid=chat_jid)
        group_join_replication = group_join_replication or self.group_join_replication
        self.db["device_groups"].update(
            {"invite_link": invite_link, "jid": chat_jid, "valid": False},
            ["chat_jid", "valid"],
        )

        if not force:
            if N_devices >= group_join_replication:
                # TODO add matching rows to exception
                raise GroupAlreadyJoined()
            group_join_replication -= N_devices

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

        join_group = sub_parser.add_parser(
            "join-group",
            description="Join a group given an invite link. Alternativvely, attach a valid CSV file for a column 'invite_link' to builk-join",
        )
        join_group.add_argument(
            "--N",
            type=int,
            default=None,
            help="Number of devices that should join this group (optional, default = server preference)",
        )
        join_group.add_argument(
            "--force",
            action="store_true",
            help="Whether to force joining the group even if existing devices have already joined",
        )
        join_group.add_argument("link", type=str, help="Valid invite link", nargs=-1)

        rebalance_groups = sub_parser.add_parser(
            "rebalance-groups",
            description="Rebalance which devices are in which groups in order to target desired redundancy in group membership",
        )
        rebalance_groups.add_argument(
            "--N",
            type=int,
            default=None,
            help="Number of devices that should join this group (optional, default = server preference)",
        )

        device_status = sub_parser.add_parser(
            "device-status",
            description="Status of devices",
        )
        groups_status = sub_parser.add_parser(
            "groups-status",
            description="Status of groupss",
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
            links = params.link
            if utils.media_message_filename(message):
                data_bytes = await self.download_message_media(message)
                data = list(csv.DictReader(data_bytes.decode("utf8").splitlines()))
            else:
                data = []

            link_meta_iter = IT.chain(
                IT.zip_longest(links, [{}], fillvalue={}),
                ((d.pop("invite_link"), d) for d in data),
            )

            statuses: T.List[str] = []
            for link, metadata in link_meta_iter:
                try:
                    result = await self.join_group(
                        link, group_join_replication=params.N, force=params.force
                    )
                    statuses.append(
                        "Group «{result['group_info'].groupName.name}» joined by the following devices:\n"
                        "\n".join(
                            list(self._format_device_membership(result["devices"]))
                        )
                    )
                    self.db["group_metadata"].insert(
                        {
                            "jid": result["group_info"].JID,
                            "invite_link": link,
                            "metadata": metadata,
                        }
                    )
                except InvalidInviteLink:
                    statuses.append(f"Invite code invalid: {link}")
            if len(statuses) < 5:
                await self.send_text_message(sender, "\n---\n".join(statuses))
            else:
                await self.send_media_message(
                    sender,
                    MediaType.MediaDocument,
                    content="\n---\n".join(statuses).encode("utf8"),
                    caption=f"Results of joining groups.",
                    mimetype="text/txt",
                    filename=f"group-join-result-{datetime.now().isoformat(timespec='minutes')}.csv",
                )
        elif params.command == "rebalance-groups":
            data: T.List[dict] = await self.rebalance_groups(
                group_join_replication=params.N
            )
            content = utils.dict_to_csv_bytes(data)
            n_no_invite = sum(d.get("error", "") == "no_invite_link" for d in data)
            summary = (
                f"{len(data)} groups affected, {n_no_invite} have no valid invite link."
            )
            await self.send_media_message(
                sender,
                MediaType.MediaDocument,
                content=content,
                caption=f"Results of group rebalancing. {summary}",
                mimetype="text/csv",
                filename=f"group-rebalancing-{datetime.now().isoformat(timespec='minutes')}.csv",
            )
        elif params.command == "device-status":
            data: T.List[dict] = list(self.db["device_sync"].all())
            content = utils.dict_to_csv_bytes(data)
            n_devices = len(set(d["device_name"] for d in data))
            oldest_sync, oldest_sync_name = min(
                (d["last_update"], d["device_name"]) for d in data
            )
            summary = f"{n_devices} devices synced. {oldest_sync_name} hasn't synced since {oldest_sync}"
            await self.send_media_message(
                sender,
                MediaType.MediaDocument,
                content=content,
                caption=f"Current device sync status. {summary}",
                mimetype="text/csv",
                filename=f"device-status-{datetime.now().isoformat(timespec='minutes')}.csv",
            )
        elif params.command == "groups-status":
            data: T.List[dict] = list(self.db["device_groups"].all())
            content = utils.dict_to_csv_bytes(data)
            n_devices = len(set(d["device_name"] for d in data))
            n_chats = len(set(d["jid"] for d in data))
            n_invalid = sum(not d["valid"] for d in data)
            summary = f"{n_devices} connected to {n_chats} groups (avg {n_chats/n_devices:0.2f} groups/device). {n_invalid} groups don't have a valid invite code"
            await self.send_media_message(
                sender,
                MediaType.MediaDocument,
                content=content,
                caption=f"Current device sync status. {summary}",
                mimetype="text/csv",
                filename=f"group-status-{datetime.now().isoformat(timespec='minutes')}.csv",
            )
