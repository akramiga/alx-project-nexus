import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model
from .models import User
import logging
import traceback
from django.db import transaction
import graphql_jwt
from graphql_jwt import ObtainJSONWebToken


UserModel = get_user_model()

class UserType(DjangoObjectType):
    id = graphene.String()
    class Meta:
        model = UserModel
        fields = (
            "id", 
            "email", 
            "username", 
            "full_name", 
            "bio", 
            "profile_image", 
            "date_of_birth"
        )

#  Queries 
class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required!")
        return user

#  Mutations 
logger = logging.getLogger(__name__)
class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, username, password):
        logger.info(f"=== DEBUGGING USER CREATION ===")
        logger.info(f"Input - Email: {email} (type: {type(email)})")
        logger.info(f"Input - Username: {username} (type: {type(username)})")
        logger.info(f"Input - Password length: {len(password) if password else 0}")
        
        try:
            # Test 1: Check if user already exists
            if User.objects.filter(email=email).exists():
                raise Exception("User with this email already exists")
            
            if User.objects.filter(username=username).exists():
                raise Exception("User with this username already exists")
            
            # Test 2: Try creating user step by step
            logger.info("Creating user...")
            
            # Method 1: Use transaction to catch database errors
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    #info=info,
                   # full_name=full_name
                )
                logger.info(f"User created successfully: {user.id}")
                return RegisterUser(user=user)
                
        except Exception as e:
            logger.error(f"Full error details:")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error module: {type(e).__module__}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Re-raise with more specific error
            raise Exception(f"User creation failed: {str(e)}")
    
class LoginUserBuiltIn(ObtainJSONWebToken):
    """
    Using the built-in ObtainJSONWebToken mutation
    """
    user = graphene.Field('users.schema.UserType')
    success = graphene.Boolean()
    message = graphene.String()
    token = graphene.String()
    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)   
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        # Call the parent mutation to handle JWT creation
        result = super().mutate(root, info, **kwargs)
        
        # If successful, add user info
        if hasattr(result, 'token') or not hasattr(result, 'errors'):
            user = info.context.user
            if user.is_authenticated:
                result.user = user
                result.success = True
                result.message = "Login successful!"
                result.token = result.token
        else:
            result.success = False
            result.message = "Invalid credentials"
            
        return result

# Logout mutation with cookie clearing
class LogoutUser(graphql_jwt.DeleteJSONWebTokenCookie):
    success = graphene.Boolean()
    message = graphene.String()
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        result = super().mutate(root, info, **kwargs)
        result.success = True
        result.message = "Logged out successfully!"
        return result

# Refresh token mutation
class RefreshToken(graphql_jwt.Refresh):
    success = graphene.Boolean()
    message = graphene.String()
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            result = super().mutate(root, info, **kwargs)
            result.success = True
            result.message = "Token refreshed successfully!"
            return result
        except Exception as e:
            return RefreshToken(
                success=False,
                message=f"Token refresh failed: {str(e)}"
            )

# Verify token mutation
class VerifyToken(graphql_jwt.Verify):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
    
    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            result = super().mutate(root, info, **kwargs)
            result.success = True
            result.message = "Token is valid!"
            if info.context.user.is_authenticated:
                result.user = info.context.user
            return result
        except Exception as e:
            return VerifyToken(
                success=False,
                message=f"Token verification failed: {str(e)}"
            )

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    logout_user = LogoutUser.Field()
    token_auth = LoginUserBuiltIn.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()