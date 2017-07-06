import sqlite3 as lite    

def SetupSession():
    try:
        db = lite.connect("buster.db")
        cur = db.cursor()
    except lite.Error as e:
        print (e)
    return db, cur

def UserInDb(db,cur,userid):
    query = "SELECT * FROM users WHERE uid = (?)"
    try:
        cur.execute(query,[userid])
        if cur.fetchone():
            db.close()
            return True
        else:
            db.close()
            return False
    except lite.Error as e:
        print(e)

def AdminInDb(db,cur,userid,gid):
    query = "SELECT * FROM admins WHERE uid = (?) AND gid = (?)"
    try:
        cur.execute(query,(userid,gid))
        if cur.fetchone():
            db.close()
            return True
        else:
            db.close()
            return False
    except lite.Error as e:
        print(e)



def RegisterUser(db,cur,userid,username):
    if not UserInDb(db,cur,userid):
        try:
            query = "INSERT INTO users(uid,username) VALUES(?,?)"
            cur.execute(query,(userid,username))
            db.commit()
            db.close()
        except lite.Error as e:
            print(e)

def RegisterAdmin(db,cur,userid,gid):
    if not AdminInDb(db,cur,userid,gid):
        query = "INSERT INTO admins(uid,gid) VALUES(?,?)"
        cur.execute(query,(userid,gid))
        db.commit()
        db.close()
    else:
        print("utente già admin")

def  RemoveAdmin(db,cur,userid,gid):
    if AdminInDb(db,cur,userid,gid):
        query = "DELETE FROM admins WHERE uid = (?) AND gid = (?)"
        cur.execute(query,(userid,gid))
        db.commit()
        db.close()
    else:
        print("user not in db")
        db.close()

def UserInBanlist(db,cur,userid,gid):
    query = "SELECT * FROM banlist WHERE uid = (?) AND gid = (?)"
    cur.execute(query,(userid,gid))
    if cur.fetchone():
        return True
    else:
        return False

def BanUser(db,cur,userid,gid):
    if not UserInBanlist(db,cur,userid,gid):
        query = "INSERT INTO banlist(uid,gid) VALUES(?,?)"
        cur.execute(query,(userid,gid))
        db.commit()
        print("ban")
    else:
        return False

def UnbanUser(db,cur,userid,gid):
    if UserInBanlist(db,cur,userid,gid):
        query = "DELETE  FROM banlist WHERE uid = (?) AND gid = (?)"
        cur.execute(query,(userid,gid))
        db.commit()
        return True
    else:
        return False
