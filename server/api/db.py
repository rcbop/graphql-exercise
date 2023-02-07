"""DB ORM module."""
from passlib.context import CryptContext
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

Base = declarative_base()
passwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PersonModel(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    house_id = Column(Integer, ForeignKey("houses.id"))
    house = relationship("HouseModel", back_populates="persons")

    def __repr__(self):
        return f"Person(name={self.name}, age={self.age})"


class HouseModel(Base):
    __tablename__ = "houses"
    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    persons = relationship("PersonModel", back_populates="house")

    def __repr__(self):
        return f"House(street={self.street}, city={self.city})"


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    _password = Column("password", String(256), nullable=False)

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password: str):
        self._password = self.get_hash(password)

    @staticmethod
    def get_hash(password: str) -> str:
        return passwd_ctx.hash(password)

    def verify_password(self, password: str) -> bool:
        return passwd_ctx.verify(password, self._password)  # type: ignore

    def __repr__(self):
        return f"User(username={self.email})"


def init_db() -> Session:
    engine = create_engine("sqlite:///db.sqlite")
    SessionLocal: sessionmaker[Session] = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    Base.metadata.create_all(bind=engine)
    return session
