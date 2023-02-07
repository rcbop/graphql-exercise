""" Bootstrap the application """
import os

from api.authn import AuthHelper
from api.db import init_db
from api.dummy import DummyHelper
from kink import di
from sqlalchemy.orm import Session


def bootstrap_di():
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

    if JWT_SECRET_KEY is None or JWT_REFRESH_SECRET_KEY is None:
        raise ValueError("JWT_SECRET_KEY or JWT_REFRESH_SECRET_KEY not set")

    di["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    di["JWT_REFRESH_SECRET_KEY"] = JWT_REFRESH_SECRET_KEY
    di[Session] = bootstrap_db()
    di[AuthHelper] = AuthHelper(di[Session], JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY)


def bootstrap_db() -> Session:
    add_data = True
    if os.path.exists("db.sqlite"):
        add_data = False
        print("database is not empty, skipping adding data")

    session = init_db()
    if add_data:
        DummyHelper.add_dummy_data(session)
    return session