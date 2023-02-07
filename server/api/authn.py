"""Authentication module."""
from datetime import datetime, timedelta

from api.constants import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                           REFRESH_TOKEN_EXPIRE_MINUTES)
from api.db import UserModel
from fastapi import HTTPException, status
from jose import jwt
from jose.exceptions import JWTError
from kink import inject
from sqlalchemy.orm import Session


@inject
class AuthHelper:
    def __init__(self, session: Session, jwt_secret_key: str, jwt_refresh_secret_key: str):
        self.__session = session
        self.__jwt_secret_key = jwt_secret_key
        self.__jwt_refresh_secret_key = jwt_refresh_secret_key

    def authorize(self, authorization_header: str | None) -> UserModel | None:
        if not authorization_header:
            return None

        token = authorization_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token, self.__jwt_secret_key, algorithms=[ALGORITHM]
            )

            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = payload.get("sub")
        if email is None:
            return None
        return self.__session.query(UserModel).filter_by(email=email).first()

    def create_access_token(self, subject: str) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, str(self.__jwt_secret_key), ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, subject: str) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, str(self.__jwt_refresh_secret_key), ALGORITHM)
        return encoded_jwt
