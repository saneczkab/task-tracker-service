class NotFoundError(Exception):
    """Ресурс не найден"""


class ConflictError(Exception):
    """Конфликт данных (дубликат и т.п.)"""


class ForbiddenError(Exception):
    """Нет прав доступа"""
