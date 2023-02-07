""" Dummy data for testing purposes. """
from api.db import HouseModel, PersonModel, UserModel
from faker import Faker
from sqlalchemy.orm import Session


class DummyHelper:
    @staticmethod
    def add_dummy_data(session: Session, length=10):
        fake = Faker()

        for _ in range(length):
            persons = []
            for _ in range(5):
                person = PersonModel(
                    name=fake.name(), age=fake.random_int(min=0, max=100)) # type: ignore
                print("adding person:  ", person)
                persons.append(person)
            house = HouseModel(
                street=fake.street_address(),
                city=fake.city(),
                persons=persons
            )
            print("adding house: ", house)
            session.add(house)

        for _ in range(5):
            fakepassword = fake.password()
            user = UserModel(email=fake.email(), password=fakepassword)
            print("USER: ", user, "PASSWORD: ", fakepassword)
            session.add(user)
        session.commit()
        print("done adding data!")
