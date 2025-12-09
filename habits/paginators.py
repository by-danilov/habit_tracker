from rest_framework.pagination import PageNumberPagination

class HabitPaginator(PageNumberPagination):
    """
    Пагинатор для списка привычек.
    Использует стандартный PageNumberPagination DRF.
    """
    # По умолчанию у нас 5 элементов на странице (указано в settings.py)
    page_size = 5
    # Позволяет пользователю задать размер страницы через параметр page_size
    page_size_query_param = 'page_size'
    # Максимальное количество элементов на странице
    max_page_size = 100
