from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import relationship
from flask_login import AnonymousUserMixin, UserMixin
from .base import db, BaseModel

user_role = db.Table('user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)


class Role(BaseModel):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    desc = db.Column(db.String(256))
    terms = relationship('Term', cascade="all")
    users = relationship('User', secondary=user_role, back_populates='roles')
    def has_permission(self, perm):
        return any([x.permission==perm for x in self.terms])


class Term(BaseModel):
    __tablename__ = 'term'
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
    permission = db.Column(db.String(64), primary_key=True)


class User(BaseModel, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    phone_number = db.Column(db.String(32))
    disabled = db.Column(db.Boolean(), default=False, nullable=False)
    roles = relationship('Role', secondary=user_role, back_populates='users')

    def populate(self, json_data):
        for k, v in json_data.items():
            if k == 'password':
                self.set_password(v)
            else:
                setattr(self, k, v)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    @property
    def is_root(self):
        return self.is_authenticated and self.username == 'root'

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id
    
    def has_role(self, role):
        return self.is_root or any([x.name==role for x in self.roles])
    
    def has_permission(self, perm):
        return self.is_root or any([x.has_permission(perm) for x in self.roles])

    def __repr__(self):
        return '<User %r>' % self.username

    def _asdict(self):
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name != 'password'}


root = User(id='0', username='root', password='Iwntellyou!!!')