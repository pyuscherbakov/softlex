# Статические файлы Softlex

Эта папка содержит все статические файлы проекта Softlex.

## Структура

```
static/
├── css/                    # Пользовательские CSS файлы
│   └── style.css          # Основные стили приложения
├── js/                    # Пользовательские JavaScript файлы
├── img/                   # Изображения
└── admin/                 # Статические файлы Django Admin
    ├── css/               # CSS файлы админки
    ├── js/                # JavaScript файлы админки
    └── img/               # Изображения админки
```

## Использование

### В шаблонах Django:
```html
{% load static %}
<link rel="stylesheet" type="text/css" href="{% static 'css/style.css' %}">
<script src="{% static 'js/app.js' %}"></script>
```

### В CSS файлах:
```css
background-image: url('../img/logo.png');
```

## Сборка статических файлов

Для продакшена статические файлы собираются в папку `staticfiles/`:

```bash
# Сборка статических файлов
uv run python softlex/manage.py collectstatic

# Или через make
make collectstatic
```

## Разработка

- **CSS**: Добавляйте стили в `css/style.css` или создавайте новые файлы
- **JavaScript**: Добавляйте скрипты в папку `js/`
- **Изображения**: Добавляйте изображения в папку `img/`
- **Admin**: Файлы админки автоматически копируются из Django

## Примечания

- Папка `staticfiles/` создается автоматически Django и не должна редактироваться вручную
- Все изменения делайте в папке `static/`
- После изменений запустите `collectstatic` для обновления `staticfiles/`
