# Group Invite Data

Sketch of commands to send to `debug-bot` when trying to get group invite data.

```python
from pathlib import Path
import time
import csv

data = [
    line.strip()
    for line in Path("/data-tmp/groups.txt").open()
]
group_data = {}

for i, invite in enumerate(data):
    if invite in group_data:
        continue
    invite = invite.replace("/invite", "")
    print(invite, i, len(data))
    try:
        invite_data = await c.GetGroupInfoInvite(wuc.InviteCode(link=invite))
        group_data[invite] = {
            "invite": invite,
            "name": invite_data.groupName.name,
            "topic": invite_data.groupTopic.topic
        }
    except Exception as e:
        group_data[invite] = {
            "invite": invite, 
            "error": "Invalid Link",
            "error_details": str(e)
        }
        print(e)
    time.sleep(10)

all_fields = set(
    k
    for item in group_data.values()
    for k in item.keys()
)
with open("/data-tmp/output.csv", "w+") as fd:
    writer = csv.DictWriter(fd, list(all_fields))
    writer.writeheader()
    for link, item in group_data.items():
        writer.writerow({
            k: item.get(k, '')
            for k in all_fields
        })
```
