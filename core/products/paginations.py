#django files

#rest files
from rest_framework.pagination import PageNumberPagination

#your files



class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 12








