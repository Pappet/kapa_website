from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    User_ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(80), unique=True, nullable=False)
    Password = db.Column(db.String(120), nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Role_ID = db.Column(db.Integer, db.ForeignKey('role.Role_ID'))
    Team_ID = db.Column(db.Integer, db.ForeignKey('team.Team_ID'))
    CreatedAt = db.Column(db.DateTime)
    Role = db.relationship('Role', backref='users', foreign_keys=[Role_ID])
    Team = db.relationship('Team', backref='users', foreign_keys=[Team_ID])

    def set_password(self, password):
        self.Password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.Password, password)

    def serialize(self):
        return {
            'User_ID': self.User_ID,
            'Username': self.Username,
            'Email': self.Email,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'Role_ID': self.Role_ID,
            'Team_ID': self.Team_ID,
        }


class Team(db.Model):
    Team_ID = db.Column(db.Integer, primary_key=True)
    TeamName = db.Column(db.String(80), unique=True, nullable=False)
    TeamLeader_ID = db.Column(db.Integer, db.ForeignKey('user.User_ID'))
    CreatedAt = db.Column(db.DateTime)
    TeamLeader = db.relationship(
        'User', backref='led_teams', foreign_keys=[TeamLeader_ID])

    def serialize(self):
        return {
            'Team_ID': self.Team_ID,
            'TeamName': self.TeamName,
            'TeamLeader_ID': self.TeamLeader_ID,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None
        }


class Role(db.Model):
    Role_ID = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(80), unique=True, nullable=False)
    CreatedAt = db.Column(db.DateTime)
    Permissions = db.relationship('Permission', secondary='role_permissions',
                                  backref=db.backref('roles', lazy='dynamic'))


class Permission(db.Model):
    Permission_ID = db.Column(db.Integer, primary_key=True)
    PermissionName = db.Column(db.String(80), unique=True, nullable=False)
    Description = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime)
    Roles = db.relationship('Role', secondary='role_permissions',
                            backref=db.backref('permissions', lazy='dynamic'))


class RolePermissions(db.Model):
    Role_ID = db.Column(db.Integer, db.ForeignKey(
        'role.Role_ID'), primary_key=True)
    Permission_ID = db.Column(db.Integer, db.ForeignKey(
        'permission.Permission_ID'), primary_key=True)
