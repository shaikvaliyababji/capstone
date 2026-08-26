from app.database.base import Base
from app.database.connection import engine

from app.models.device import Device


def init_db():
    Base.metadata.create_all(bind=engine)