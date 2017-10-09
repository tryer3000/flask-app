from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import AnonymousUserMixin, UserMixin
from .base import db, BaseModel


class User(BaseModel, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    phone_number = db.Column(db.String(32))
    disabled = db.Column(db.Boolean(), default=False, nullable=False)

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

    def __repr__(self):
        return '<User %r>' % self.username

    def _asdict(self):
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name != 'password'}
