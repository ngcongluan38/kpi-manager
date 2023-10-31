import arrow
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class IsReadOnly(permissions.BasePermission):
    """
        Object-level permission to only allow read-only operations.
        Đối tượng cấp quyền chỉ cho phép đọc.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(['GET'])
@permission_classes((IsReadOnly, ))
def index_api_view(request):
    return Response({
        'ok': True,
        'name': 'KPI Manager',
        'version': '1.0',
        'copyright': 'Thiện Lê - Trọng Hiền - K9 UIT',
        'techInfo': {
            'django': '1.11',
            'postgres': '10.4',
        },
    })
