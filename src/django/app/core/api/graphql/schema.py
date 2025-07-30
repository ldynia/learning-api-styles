import random

from strawberry import Schema
from strawberry_django.optimizer import DjangoOptimizerExtension

from .queries import Query, CustomQuery
from .mutations import Mutation, CustomMutation

if random.randint(0, 1) == 0:
    query = Query
    mutation = Mutation
else:
    # Solution for GraphQL exercise no. 1
    query = CustomQuery
    mutation = CustomMutation

schema = Schema(
    query=query,
    mutation=mutation,
    extensions=[DjangoOptimizerExtension],
)
