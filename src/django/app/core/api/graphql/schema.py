from strawberry import Schema
from strawberry_django.optimizer import DjangoOptimizerExtension

from .queries import Query
from .mutations import Mutation


schema = Schema(
    query=Query,
    mutation=Mutation,
    extensions=[DjangoOptimizerExtension],
)
