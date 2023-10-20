class CredentialsListener:
    async def listen(self, device_manager):
        raise NotImplementedError

    def mark_dead(self, username):
        raise NotImplementedError

    def unregister(self, username):
        raise NotImplementedError
