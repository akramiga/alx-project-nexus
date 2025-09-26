from django.contrib import admin
from .models import Post, Comment, Interaction
# Register your models here.



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "content", "created_at", "likes_count", "comments_count", "shares_count")
    search_fields = ("content", "author__username")
    list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "content", "created_at")
    search_fields = ("content", "author__username")
    list_filter = ("created_at",)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("user__username", "post__content")
