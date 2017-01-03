import json

def jsonKeys2str(x):
    if isinstance(x, dict):
        try:
            return {int(k):v for k,v in x.items()}
        except ValueError:
            return x
    return x

class GroupException(Exception):
    pass

class UserException(Exception):
    pass

class bot_database:
    group_whitelist = [-192014087, -1001084538434, -1001092224184 ]

    def __init__(self):
        self.db = {}
        self.file = ".db.json"
        try:
            self.reload()
        except FileNotFoundError:
            for g in bot_database.group_whitelist:
                self.db[g] = {}

    def getGroup(self, group_id):
        if self.db.get(group_id) == None:
            raise GroupException('Group not in whitelist')
        else:
            return self.db[group_id]

    def getGroupOption(self, group_id, option):
        g = self.getGroup(group_id)
        if g.get(option) != None:
            return g[option]
        else:
            raise GroupException('Option not found')

    def setGroupOption(self, group_id, option, value):
        g = self.getGroup(group_id)
        g[option] = value
        self.commit()

    def getGroupWhitelist(self, group_id):
        g = self.getGroup(group_id)
        if g.get('whitelist') == None:
            g['whitelist'] = []
        return g['whitelist']

    def addToWhitelist(self, group_id, user):
        gwl = self.getGroupWhitelist(group_id)
        if user['username'] and user['id']:
            gwl.append(user)
            self.commit()
        else:
            raise GroupException("User object malformed")

    def removeFromWhitelist(self, group_id, user):
        gwl = self.getGroupWhitelist(group_id)
        if user['username'] and user['id']:
            gwl.remove(user)
            self.commit()
        else:
            raise GroupException("User object malformed")

    def getGroupBanlist(self, group_id):
        g = self.getGroup(group_id)
        if g.get('banlist') == None:
            g['banlist'] = []
        return g['banlist']

    def addBanned(self, group_id, banned):
        gb = self.getGroupBanlist(group_id)
        if banned['username'] and banned['id']:
            gb.append(banned)
            self.commit()
        else:
            raise GroupException("Banned object malformed")

    def removeBanned(self, group_id, banned):
        gb = self.getGroupBanlist(group_id)
        if banned['username'] and banned['id']:
            gb.append(banned)
            self.commit()
        else:
            raise GroupException("Banned object malformed")

    def getUser(self, group_id, user_id):
        g = self.getGroup(group_id)
        if g.get(user_id) == None:
            g[user_id] = {}
            g[user_id]['counter'] = 0
            g[user_id]['old_ts'] = 0
            g[user_id]['last_msg'] = ''
        return g[user_id]

    def commit(self):
        # deep copy dict
        db = {}
        for g in self.db:
            db[g] = {}
            for child in self.db[g]:
                if type(child) != int:
                    db[g][child] = self.db[g][child]
        with open(self.file,'w') as f:
            f.write(json.dumps(db))

    def reload(self):
        with open(self.file,'r') as f:
            self.db = json.loads(f.read(), object_hook=jsonKeys2str)
