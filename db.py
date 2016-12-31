class GroupException(Exception):
    pass

class UserException(Exception):
    pass

class bot_db:
    group_whitelist = [-192014087, -1001084538434 ]

    def __init__(self):
        self.db = {}
        for g in bot_db.group_whitelist:
            self.db[g] = {}

    def getGroup(self, group_id):
        if self.db.get(group_id) == None:
            raise GroupException('Group not in whitelist')
        else:
            return self.db[group_id]

    def getGroupOption(self, group_id, option):
        raise GroupException('TODO')

    def setGroupOption(self, group_id, option):
        raise GroupException('TODO')

    def getGroupWhitelist(self, group_id):
        g = getGroup(group_id)
        if g.get('whitelist') == None:
            raise GroupException('Group does not have a whitelist')
        else:
            return g['whitelist']

    def getGroupBanlist(self, group_id):
        g = getGroup(group_id)
        if g.get('banlist') == None:
            raise GroupException('Group does not have a banlist')
        else:
            return g['banlist']

    def getUser(self, group_id, user_id):
        g = getGroup(group_id)
        if g.get(user_id) == None:
            raise UserException('User not in memory')
        else:
            return g[user_id]
