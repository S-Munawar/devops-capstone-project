"""
Module: factories
Factory Boy factories for generating test data
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyText
from service.models import Account


class AccountFactory(factory.Factory):
    """Creates fake Accounts for testing."""

    class Meta:
        model = Account

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    email = factory.LazyAttribute(
        lambda obj: f"{obj.name.lower().replace(' ', '.')}@example.com"
    )
    address = factory.Faker("address")
    phone_number = factory.Faker("phone_number")
