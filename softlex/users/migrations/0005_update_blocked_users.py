from django.db import migrations


def update_blocked_users(apps, schema_editor):
    """Обновляем пользователей с ролью 'blocked' - устанавливаем is_active=False и role='user'"""
    User = apps.get_model('users', 'User')
    
    # Находим всех пользователей с ролью 'blocked'
    blocked_users = User.objects.filter(role='blocked')
    
    # Обновляем их: устанавливаем is_active=False и role='user'
    for user in blocked_users:
        user.is_active = False
        user.role = 'user'
        user.save()


def reverse_update_blocked_users(apps, schema_editor):
    """Обратная миграция - восстанавливаем роль 'blocked' для неактивных пользователей"""
    User = apps.get_model('users', 'User')
    
    # Находим всех неактивных пользователей
    inactive_users = User.objects.filter(is_active=False)
    
    # Восстанавливаем роль 'blocked' (если она была в старых ROLE_CHOICES)
    for user in inactive_users:
        user.role = 'blocked'
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_role'),
    ]

    operations = [
        migrations.RunPython(update_blocked_users, reverse_update_blocked_users),
    ]
