from .base import db, BaseModel


class Role(BaseModel):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
