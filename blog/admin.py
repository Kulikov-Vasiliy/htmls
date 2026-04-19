from django.contrib import admin
from blog.models import Categories, Post, PostMedia, Comment

# Register your models here.
class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag', 'order', 'icon')
    list_editable = ('order', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'tag', 'is_published', 'viewed', 'created_at')
    list_filter = ('is_published', 'publish_status', 'tag', 'created_at')
    search_fields = ('title', 'content', 'author__nickname')
    readonly_fields = ('viewed', 'created_at', 'updated_at', 'published_at')
    inlines = [PostMediaInline]
    filter_horizontal = ('favorites',)  # Удобный выбор пользователей для ManyToMany

    fieldsets = (
        ('Основное', {'fields': ('title', 'author', 'tag', 'content', 'about_content')}),
        ('Статистика', {'fields': ('viewed', 'likes', 'dislikes', 'popularity', 'favorites')}),
        ('Публикация', {'fields': ('publish_status', 'is_published', 'scheduled_at', 'published_at')}),
        ('Техническое', {'fields': ('is_active', 'is_formatted', 'is_delete', 'is_deleted')}),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text', 'author__nickname', 'post__title')
    prepopulated_fields = {'slug': ('text',)}  # Осторожно, если текст длинный


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ('post',)
