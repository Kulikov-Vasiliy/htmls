from django.contrib import admin
from users.models import User, UserActivity,  Subscription, Moderator

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'email', 'first_name', 'last_name', 'is_deleted', 'joined_at')
    list_filter = ('is_deleted', 'joined_at')
    search_fields = ('nickname', 'email', 'login', 'first_name', 'last_name')
    readonly_fields = ('joined_at', 'deleted_at')
    fieldsets = (
        ('Личные данные', {'fields': ('nickname', 'login', 'email', 'profile_img', 'about')}),
        ('ФИО', {'fields': ('first_name', 'last_name')}),
        ('Статус удаления', {'fields': ('is_deleted', 'deleted_at', 'is_delete')}),
    )


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__nickname', 'post__title')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    # Позволяет сразу видеть, кто на кого подписан и когда это случилось
    list_display = ('subscriber', 'author', 'is_subscribe', 'created_at')
    list_filter = ('is_subscribe', 'created_at')
    # Поиск по никам обоих участников связи
    search_fields = ('subscriber__nickname', 'author__nickname')
    date_hierarchy = 'created_at'  # Удобная навигация по датам сверху


@admin.register(Moderator)
class ModeratorAdmin(admin.ModelAdmin):
    list_display = ('login', 'email', 'is_staff', 'is_active', 'post', 'author', 'is_deleted')
    list_filter = ('is_staff', 'is_active', 'is_deleted', 'joined_at')
    search_fields = ('login', 'email', 'first_name', 'last_name', 'post__title')

    # Группируем поля: личные данные отдельно, рабочие (пост/решение) отдельно
    fieldsets = (
        ('Данные модератора', {
            'fields': ('login', 'email', 'first_name', 'last_name', 'profile_img', 'is_staff')
        }),
        ('Работа с контентом', {
            'fields': ('post', 'author', 'message', 'is_active', 'decision_by')
        }),
        ('Статус аккаунта', {
            'fields': ('is_delete', 'is_deleted', 'deleted_at', 'joined_at')
        }),
    )

    # Быстрое действие: сделать выбранных модераторов активными (staff)
    actions = ['make_staff']

    @admin.action(description="Назначить выбранных модераторами (Staff)")
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)

    def save_model(self, request, obj, form, change):
        if not obj.decision_by:
            # Импортируем вашу модель User
            from .models import User as MyUser
            try:
                # Ищем в ВАШЕЙ таблице пользователя с таким же логином/email
                current_user = MyUser.objects.get(login=request.user.username)
                obj.decision_by = current_user
            except MyUser.DoesNotExist:
                # Если в вашей таблице такого нет, оставляем пустым или выдаем ошибку
                pass
        super().save_model(request, obj, form, change)

    # Чтобы модератор не мог вручную выбрать кого-то другого,
    # можно сделать поле только для чтения
    readonly_fields = ('decision_by', 'joined_at', 'deleted_at')