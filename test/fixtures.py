from uuid import uuid4

from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import BaseFuzzyAttribute, FuzzyText

from test import models


class FuzzyUuid(BaseFuzzyAttribute):
    def fuzz(self):
        return uuid4()


class Random(SQLAlchemyModelFactory):
    class Meta:
        model = models.Random

    uuid = FuzzyUuid()
    name = FuzzyText()
