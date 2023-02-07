""" Request context for GraphQL API module. """
from functools import cached_property

from api.authn import AuthHelper
from api.db import UserModel
from kink import inject
from sqlalchemy.orm import Session
from strawberry.fastapi import BaseContext


@inject
class Context(BaseContext):
    def __init__(self, auth: AuthHelper, session: Session):
        self.auth = auth
        self._session = session
        super().__init__()

    @cached_property
    def user(self) -> UserModel | None:
        if not self.request:
            return None

        auth_header = self.request.headers.get("Authorization", None)
        return self.auth.authorize(auth_header)

    @cached_property
    def db_session(self) -> Session:
        return self._session
