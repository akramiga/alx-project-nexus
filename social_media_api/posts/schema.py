import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql_relay.node.node import from_global_id, to_global_id
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from .models import Post, Interaction, Comment
from django.db.models import Count, Q
from django.db.models import Prefetch

User = get_user_model()


class UserSummaryType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "profile_image")


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        interfaces = (relay.Node,)
        # enable some common filters
        filter_fields = {
            "content": ["icontains"],
            "author__username": ["exact"],
            "created_at": ["lt", "gt"],
        }
        fields = (
            "id",
            "content",
            "author",
            "created_at",
            "updated_at",
            "likes_count",
            "comments_count",
            "shares_count",
        )

class CommentNode(DjangoObjectType):
    class Meta:
        model = Comment
        interfaces = (relay.Node,)
        filter_fields = {
            "post__id": ["exact"],
            "author__username": ["exact"],
        }
        fields = ("id", "content", "author", "post", "created_at")


class InteractionNode(DjangoObjectType):
    class Meta:
        model = Interaction
        interfaces = (relay.Node,)
        filter_fields = {
            "post__id": ["exact"],
            "user__username": ["exact"],
            "type": ["exact"],
        }
        fields = ("id", "type", "user", "post", "created_at")

# ---------------- Mutations ----------------
class CreatePost(graphene.Mutation):
    post = graphene.Field(PostNode)

    class Arguments:
        content = graphene.String(required=True)

    def mutate(self, info, content):
        user = info.context.user
        if not getattr(user, "is_authenticated", False):
            raise Exception("Authentication required")
        post = Post.objects.create(author=user, content=content)
        return CreatePost(post=post)

class AddComment(graphene.Mutation):
    comment = graphene.Field(CommentNode)

    class Arguments:
        post_id = graphene.ID(required=True)
        content = graphene.String(required=True)

    def mutate(self, info, post_id, content):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        
        # Handle Relay Node ID
        try:
            node_type, raw_post_id = from_global_id(post_id)
            if node_type != "PostNode":
                raise Exception("Invalid post ID")
        except Exception:
            raise Exception("Invalid post ID format")
            
        post = Post.objects.get(pk=raw_post_id)
        comment = Comment.objects.create(post=post, author=user, content=content)
        # Update denormalized counter
        post.comments_count = post.comments.count()
        post.save(update_fields=["comments_count"])
        return AddComment(comment=comment)


class InteractWithPost(graphene.Mutation):
    interaction = graphene.Field(InteractionNode)

    class Arguments:
        post_id = graphene.ID(required=True)
        type = graphene.String(required=True)  # "like" or "share"

    def mutate(self, info, post_id, type):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required")

        if type not in ["like", "share"]:
            raise Exception("Invalid interaction type")

        # Handle Relay Node ID decoding
        try:
            # Decode the Relay Node ID
            node_type, raw_post_id = from_global_id(post_id)
            print(f"Decoded - Type: {node_type}, ID: {raw_post_id}")  # Debug info
            
            # Validate it's a PostNode
            if node_type != "PostNode":
                raise Exception(f"Expected PostNode, got {node_type}")
                
        except ValueError as e:
            print(f"ValueError decoding Node ID: {e}")
            raise Exception("Invalid Node ID format")
        except Exception as e:
            print(f"Error decoding Node ID: {e}")
            raise Exception(f"Failed to decode Node ID: {str(e)}")

        try:
            post = Post.objects.get(pk=raw_post_id)
        except Post.DoesNotExist:
            raise Exception(f"Post with ID {raw_post_id} not found")
        except Exception as e:
            raise Exception(f"Error finding post: {str(e)}")

        interaction, created = Interaction.objects.get_or_create(
            post=post, user=user, type=type
        )

        # Fetch like/share counts in a single query
        counts = post.interactions.aggregate(
            likes=Count('id', filter=Q(type='like')),
            shares=Count('id', filter=Q(type='share'))
        )
        post.likes_count = counts['likes']
        post.shares_count = counts['shares']
        post.save(update_fields=["likes_count", "shares_count"])

        return InteractWithPost(interaction=interaction)
    


# ---------------- Queries ----------------
class Query(graphene.ObjectType):
    post = relay.Node.Field(PostNode)
    posts = DjangoFilterConnectionField(PostNode)
    comment = relay.Node.Field(CommentNode)
    comments = DjangoFilterConnectionField(CommentNode)
    interaction = relay.Node.Field(InteractionNode)
    interactions = DjangoFilterConnectionField(InteractionNode)

    def resolve_posts(self, info, **kwargs):
        # Efficiently fetch author, comments, and interactions
        return Post.objects.select_related("author").prefetch_related(
            Prefetch("comments", queryset=Comment.objects.select_related("author")),
            Prefetch("interactions", queryset=Interaction.objects.select_related("user"))
        ).all()

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
    add_comment = AddComment.Field()
    interact_with_post = InteractWithPost.Field()

