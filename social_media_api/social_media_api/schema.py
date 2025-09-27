import graphene
import graphql_jwt
import users.schema
import posts.schema
from users.schema import LoginUserBuiltIn
class Query(users.schema.Query, posts.schema.Query, graphene.ObjectType):
    pass

class Mutation(users.schema.Mutation, posts.schema.Mutation, graphene.ObjectType):
    # JWT mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    login_user = LoginUserBuiltIn.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)