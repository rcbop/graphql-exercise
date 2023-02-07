""" Graphql schema module. """
import strawberry
from api.authz import IsAuthenticated
from api.db import HouseModel, PersonModel, UserModel
from strawberry.types import Info


@strawberry.type
class LoginSuccess:
    access_token: str
    refresh_token: str


@strawberry.type
class LoginError:
    message: str


LoginResult = strawberry.union("LoginResult", (LoginSuccess, LoginError))


@strawberry.type
class User:
    email: str


@strawberry.type
class Mutation:

    @strawberry.mutation
    def signup(self, info: Info, email: str, password: str) -> str:
        user = info.context.db_session.query(
            UserModel).filter_by(email=email).first()
        if user is not None:
            raise Exception("User with this email already exist")
        user = UserModel(email=email, password=password)
        info.context.db_session.add(user)
        info.context.db_session.commit()
        return f"{email} user created"

    @strawberry.field
    def login(self, info: Info, email: str, password: str) -> "LoginResult":
        user = info.context.db_session.query(
            UserModel).filter_by(email=email).first()

        if user is None:
            return LoginError(message="User does not exist")

        if not user.verify_password(password):
            return LoginError(message="Wrong password")

        return LoginSuccess(access_token=info.context.auth.create_access_token(str(user.email)),
                            refresh_token=info.context.auth.create_refresh_token(str(user.email)))


@strawberry.type
class Person:
    name: str
    age: int


@strawberry.type
class House:
    street: str
    city: str
    persons: list[Person]


def person_model_to_person(person: PersonModel) -> Person:
    return Person(name=str(person.name), age=int(person.age))  # type: ignore


def house_model_to_house(house: HouseModel) -> House:
    return House(street=str(house.street), city=str(house.city), persons=[
        person_model_to_person(person) for person in house.persons
    ])


@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def houses(self, info: Info) -> list[House]:
        houses = info.context.db_session.query(HouseModel).all()
        return [house_model_to_house(house) for house in houses]

    @strawberry.field(permission_classes=[IsAuthenticated])
    def persons(self, info: Info) -> list[Person]:
        persons: list[PersonModel] = info.context.db_session.query(
            PersonModel).all()
        return [person_model_to_person(person) for person in persons]

    @strawberry.field(permission_classes=[IsAuthenticated])
    def users(self, info: Info) -> list[User]:
        users: list[UserModel] = info.context.db_session.query(UserModel).all()
        return [User(email=str(user.email)) for user in users]

    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_authenticated_user(self, info: Info) -> User | None:
        return info.context.user


class SchemaHelper:
    @classmethod
    def get_schema(cls) -> strawberry.Schema:
        return strawberry.Schema(query=Query, mutation=Mutation)
