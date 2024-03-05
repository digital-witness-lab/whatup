from datetime import datetime


class UserState(dict):
    def connect(self, username, table):
        self.username = username
        self.table = table
        self.data = {}
        self.sync()

    def sync(self):
        super().update(self.table.find_one(username=self.username))

    def __setitem__(self, key, item):
        super().__setitem__(key, item)
        self.table.update(
            {key: item, "record_mtime": datetime.now(), "username": self.username},
            ["username"],
        )

    def update(self, **kwargs):
        super().update(kwargs)
        self.table.update(
            {**kwargs, "record_mtime": datetime.now(), "username": self.username},
            ["username"],
        )

    def clear(self):
        self.table.delete(username=self.username)
        super().clear()
