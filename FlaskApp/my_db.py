from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    user_id = db.Column(db.String(25))
    token = db.Column(db.String(255))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)
    write_access = db.Column(db.Integer)
    is_admin = db.Column(db.Integer)
    
    def __init__(self, name, user_id, token, login, read_access, write_access, is_admin):
        self.name = name
        self.user_id = user_id
        self.token = token
        self.login = login
        self.read_access = read_access
        self.write_access = write_access
        self.is_admin = is_admin
    
def delete_all():
    try:
        db.session.query(User).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        

def get_user_row_if_exists(user_to_find):
    get_user_row = User.query.filter_by(user_id=user_to_find).first()
    if get_user_row is not None:
        return get_user_row
    else:
        print("That user does not exist")
        return False
    
def add_user_and_login(name, user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 1
        db.session.commit()
    else:
        new_user = User(name, user_id, None, 1, 0, 0, 0)
        db.session.add(new_user)
        db.session.commit()
        
        
def user_logout(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.login = 0
        db.session.commit()
        
        
def add_token(user_id, token):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.token = token
        db.session.commit()
        
        
def get_token(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        return row.token
    else:
        print(f"User with id {user_id} doesn't exist")
        
        
def delete_revoked_token(user_id):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        row.token = None
        db.session.commit()
        
        
def view_all():
    all_rows = User.query.all()
    print_results(all_rows)
    
    
def print_results(all_rows):
    for i in range(0, len(all_rows)):
        print(f"{all_rows[i].id} | {all_rows[i].name} | {all_rows[i].token} | {all_rows[i].login} | {all_rows[i].read_access} | {all_rows[i].write_access}")
        
        
def get_all_logged_in_users():
    rows = User.query.filter_by(login=1).all()
    online_users = {"users":[]}
    for row in rows:
        if row.read_access == 0 and row.write_access ==0:
            read = "unchecked"
            write = "unchecked"
        elif row.read_access == 1 and row.write_access ==0:
            read = "checked"
            write = "unchecked"
        elif row.read_access == 0 and row.write_access ==1:
            read = "unchecked"
            write = "checked"
        else:
            read = "checked"
            write = "checked"
        online_users["users"].append([row.name, row.user_id, read, write])
    return online_users


def add_user_permission(user_id, read, write):
    row = get_user_row_if_exists(user_id)
    if row is not False:
        if read =="true":
            row.read_access = 1
        elif read =="false":
            row.read_access = 0
        elif write =="true":
            row.write_access = 1
        elif write =="false":
            row.write_access = 0
        db.session.commit()
        

def is_admin(user_id):
    row = get_user_row_if_exists(user_id)
    if row.is_admin ==1:
        return True
    else:
        return False
