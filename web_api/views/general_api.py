import re

import arrow
from django.conf import settings
from django.core.files.images import get_image_dimensions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from kpi_manager.models import Profile
from web_api.utils import build_absolute_url


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.page_size,
            'current': self.page.number,
            'results': data
        })


@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def get_user_api_view(request):
    user = request.user
    data = {'ok': False}
    if request.user.is_authenticated:

        try:
            profile = Profile.objects.get(user=user, removed=False)
            birthday = arrow.get(profile.birth_day).replace(tzinfo=settings.TIME_ZONE).datetime

            data = {
               'ok': True,
               'username': user.username,
               'avatar': build_absolute_url(user.profile.get_avatar_url()),
               'userId': user.id,
               'permission': profile.get_role(),
               'fullName': profile.full_name,
               'birthDay': birthday,
               'idNumber': profile.id_number,
               'address': profile.address,
               'sex': profile.get_sex_display(),
            }
        except Profile.DoesNotExist:
            pass
    return Response(data)


@api_view(['POST'])
def update_profile(request):
    """
        API cập nhật hồ sơ
    """
    full_name = request.data.get('fullName', '')
    birth_day = request.data.get('birthDay')
    id_number = request.data.get('idNumber')
    address = request.data.get('address')
    sex = request.data.get('sex')
    user = request.user

    sex_choices = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
    )

    if user.is_authenticated:
        profile = user.profile

        if len(full_name) > 150:
            return Response({'ok': False, 'msg': 'Họ tên chỉ nhập tối đa 150 ký tự!'})
        if len(address) > 200:
            return Response({'ok': False, 'msg': 'Địa điểm chỉ nhập tối đa 200 ký tự!'})

        profile.full_name = full_name.strip() if full_name else profile.full_name
        profile.address = address.strip() if address else profile.address

        profile.birth_day = arrow.get(birth_day).replace(tzinfo=settings.TIME_ZONE).datetime

        if re.compile("^([0-9]+)+$").match(id_number) and len(id_number) < 13:
            profile.id_number = id_number

        if sex:
            try:
                if sex == 'null':
                    profile.sex = ''
                else:
                    sex = next(y for x, y in sex_choices if x == sex)
                    profile.sex = sex
            except StopIteration:
                return Response({'ok': False, 'msg': 'Giới tính không hợp lệ, vui lòng kiểm tra lại!'})

        profile.save()
        return Response({'ok': True, 'msg': 'Cập nhật thông tin thành công!'})
    return Response({'ok': False, 'msg': 'Thông tin người dùng chưa xác thực!'})


@api_view(['POST'])
def upload_avatar_api_view(request):
    user = request.user
    avatar = request.FILES.get('avatar', False)

    if not avatar:
        return Response({'ok': False, 'msg': 'Không tìm thấy ảnh tải lên!'})

    if avatar.content_type.split('/')[1] not in ['jpg', 'jpeg', 'png']:
        return Response({'ok': False, 'msg': 'Chỉ chấp nhận ảnh có đuôi là JPG, JPEG hoặc PNG!'})

    height, width = get_image_dimensions(avatar)

    if height < 100 and width < 100:
        return Response({'ok': False,
                         'msg': 'Kích thước tối thiểu của ảnh là 100 x 100!'})

    if avatar.size > 1 * 1024 * 1024:
        return Response({'ok': False, 'msg': 'Kích thước ảnh tối đa là 1MB!'})

    try:
        profile = Profile.objects.get(user=user, removed=False)

        profile.avatar = avatar
        profile.save()

        return Response({'ok': True, 'msg': 'Đổi ảnh đại diện thành công!'})
    except (Profile.DoesNotExist, OSError):
        return Response({'ok': False, 'msg': 'Cập nhật thất bại!'})



