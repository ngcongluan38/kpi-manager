import arrow
from django.conf import settings
from django.db.models import Sum

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from kpi_manager.models import Profile, Tag, Task, DepartmentMember, WorkTime
from utils.common import can_be_integer
from .. import serializers as serializer_api


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


class GetTagListView(generics.ListAPIView):
    """
    API lấy danh sách các Tag của tất cả nhân viên (Direct) và thuộc phòng ban (Manager)
    """
    serializer_class = serializer_api.GetTagOfMemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.user.id
        query = self.request.GET.get('query')
        if self.request.user.is_authenticated:
            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                if profile.get_role() == 'Director':
                    if not query:
                        # lấy theo query=current
                        return Tag.objects.filter(period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-created_at')
                    elif query == 'all':
                        return Tag.objects.filter(removed=False).order_by('-created_at')
                    elif query == 'current':
                        # kpi chưa hết hạn
                        return Tag.objects.filter(period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-created_at')
                    elif query == 'tmonth':
                        # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                        start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                        end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                        return Tag.objects.filter(period_start__range=(start, end),
                                                  period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  created_at__range=(start, end),
                                                  removed=False).order_by('-created_at')
                    elif query == 'outdated':
                        return Tag.objects.filter(period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-created_at')
                    else:
                        return []

                elif profile.get_role() == 'Manager':
                    member = DepartmentMember.objects.get(department_member=profile, removed=False)
                    d_id = member.department.id
                    if not query:
                        # lấy theo query=current
                        return Tag.objects.filter(user__department__id=d_id,
                                                  period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-updated_at')
                    elif query == 'all':
                        return Tag.objects.filter(user__department__id=d_id,
                                                  removed=False).order_by('-updated_at')
                    elif query == 'current':
                        # kpi chưa hết hạn
                        return Tag.objects.filter(user__department__id=d_id,
                                                  period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-updated_at')
                    elif query == 'tmonth':
                        # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                        start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                        end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                        return Tag.objects.filter(user__department__id=d_id,
                                                  period_start__range=(start, end),
                                                  period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  created_at__range=(start, end),
                                                  removed=False).order_by('-updated_at')
                    elif query == 'outdated':
                        return Tag.objects.filter(user__department__id=d_id,
                                                  period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                  removed=False).order_by('-updated_at')
                    else:
                        return []
                else:
                    return []

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return []
        return []


class GetAllTagOfMemberView(generics.ListAPIView):
    """
    API lấy danh sách các Tag của một nhân viên
    """
    serializer_class = serializer_api.GetTagOfMemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        query = self.request.GET.get('query')
        if self.request.user.is_authenticated:
            if user_id:
                if not can_be_integer(user_id):
                    return []

                try:
                    profile = Profile.objects.get(user__id=user_id, removed=False)
                    my_profile = Profile.objects.get(user__id=self.request.user.id, removed=False)
                    if my_profile.get_role() == 'Director':
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        if not query:
                            # lấy theo query=current
                            return Tag.objects.filter(user=member,
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                        elif query == 'all':
                            return Tag.objects.filter(user=member,
                                                      removed=False).order_by('-created_at')
                        elif query == 'current':
                            # kpi chưa hết hạn
                            return Tag.objects.filter(user=member,
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                        elif query == 'tmonth':
                            # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                            start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                            end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                            return Tag.objects.filter(user=member,
                                                      period_start__range=(start, end),
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      created_at__range=(start, end),
                                                      removed=False).order_by('-created_at')
                        elif query == 'outdated':
                            return Tag.objects.filter(user=member,
                                                      period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                        else:
                            return []

                    elif my_profile.get_role() == 'Manager':
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                        d_id = me.department.id
                        if not query:
                            return Tag.objects.filter(user=member,
                                                      user__department__id=d_id,
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                        elif query == 'all':
                            return Tag.objects.filter(user=member,
                                                      user__department__id=d_id,
                                                      removed=False).order_by('-created_at')
                        elif query == 'current':
                            # kpi chưa hết hạn
                            return Tag.objects.filter(user=member,
                                                      user__department__id=d_id,
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                        elif query == 'tmonth':
                            # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                            start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                            end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                            return Tag.objects.filter(user=member,
                                                      user__department__id=d_id,
                                                      period_start__range=(start, end),
                                                      period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      created_at__range=(start, end),
                                                      removed=False).order_by('-created_at')
                        elif query == 'outdated':
                            return Tag.objects.filter(user=member,
                                                      user__department__id=d_id,
                                                      period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime,
                                                      removed=False).order_by('-created_at')
                    else:
                        return []

                except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                    return []

        return []


class GetMyTagView(generics.ListAPIView):
    """
    API lấy danh sách các Tag của tôi
    """
    serializer_class = serializer_api.GetTagOfMemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.GET.get('query')
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                if not query:
                    return Tag.objects.filter(user=member,
                                              period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                              removed=False).order_by('-created_at')
                elif query == 'all':
                    return Tag.objects.filter(user=member,
                                              removed=False).order_by('-created_at')
                elif query == 'current':
                    # kpi chưa hết hạn
                    return Tag.objects.filter(user=member,
                                              period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                              removed=False).order_by('-created_at')
                elif query == 'tmonth':
                    # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                    start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                    end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                    return Tag.objects.filter(user=member,
                                              period_start__range=(start, end),
                                              period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                              created_at__range=(start, end),
                                              removed=False).order_by('-created_at')
                elif query == 'outdated':
                    return Tag.objects.filter(user=member,
                                              period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime,
                                              removed=False).order_by('-created_at')
                else:
                    return []

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return []

        return []


@api_view(['GET'])
def get_one_tag_of_member_detail_api_view(request):
    """
    API lấy thông tin chi tiết của một tag của một nhân viên
    :param request: user_id, tag_id
    :return:
    """
    user_id = request.GET.get('user_id')
    tag_id = request.GET.get('tag_id')
    if request.user.is_authenticated:
        if user_id and tag_id:
            if not can_be_integer(user_id):
                return Response({})
            if not can_be_integer(tag_id):
                return Response({})

            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                my_profile = Profile.objects.get(user__id=request.user.id, removed=False)

                if my_profile.get_role() == 'Director':
                    tag = Tag.objects.get(id=tag_id, user=member, removed=False)
                    serializer = serializer_api.GetTagOfMemberSerializer(tag)
                    return Response(serializer.data)
                elif my_profile.get_role() == 'Manager':
                    me = DepartmentMember.objects.get(department_member=my_profile, removed=False)

                    if int(me.department.id) == int(member.department.id):
                        tag = Tag.objects.get(id=tag_id, user=member, removed=False)
                        serializer = serializer_api.GetTagOfMemberSerializer(tag)
                        return Response(serializer.data)
                    else:
                        return Response({})
                else:
                    return Response({})

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return Response({})

    return Response({})


@api_view(['GET'])
def get_one_tag_detail_of_me_api_view(request):
    """
    API lấy thông tin chi tiết của một tag của tôi
    :param request: tag_id
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.user.id
        tag_id = request.GET.get('tag_id')
        if tag_id:
            if not can_be_integer(tag_id):
                return Response({})

            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                tag = Tag.objects.get(id=tag_id, user=member, removed=False)
                serializer = serializer_api.GetTagOfMemberSerializer(tag)
                return Response(serializer.data)

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return Response({})

    return Response({})


@api_view(['GET'])
def get_tag_list_of_me_no_pagination_api_view(request):
    """
    API lấy danh sách tag của tôi và không phân trang
    :param request: user_id, tag_id
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.user.id
        data = []
        try:
            profile = Profile.objects.get(user__id=user_id, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            tag = Tag.objects.filter(user=member, removed=False)
            for item in tag:
                data.append({
                    'tagId': item.id,
                    'tagName': item.tag_name,
                })
            return Response(data)

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return Response([])

    return Response([])


@api_view(['POST'])
def add_new_tag_api_view(request):
    """
    API tạo một kpi mới
    :param request: profile_id, tag_name, tag_description, period_start, period_end, quantity, weight
    :return: tạo mới một tag
    """
    user_id = request.user.id
    profile_id = request.data.get('profile_id')
    tag_name = request.data.get('tag_name')
    tag_description = request.data.get('tag_description')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    quantity = request.data.get('quantity')
    weight = request.data.get('weight')

    if request.user.is_authenticated:
        try:
            my_profile = Profile.objects.get(user__id=user_id, removed=False)
            if my_profile.get_role() != 'Director' and my_profile.get_role() != 'Manager':
                return Response({
                    'ok': False,
                    'msg': 'Bạn không có quyền tạo KPI!',
                })

        except (Profile.DoesNotExist,):
            return Response({
                'ok': False,
                'msg': 'Lỗi dữ liệu!',
            })

        if not profile_id:
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy nhân viên!',
            })

        if not can_be_integer(profile_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy nhân viên này!',
            })

        if not tag_name:
            return Response({
                'ok': False,
                'msg': 'Tiêu đề không được để trống!',
            })

        if not tag_description:
            tag_description = None

        if not quantity:
            return Response({
                'ok': False,
                'msg': 'Chỉ tiêu không được để trống!',
            })

        if not can_be_integer(quantity):
            return Response({
                'ok': False,
                'msg': 'Chỉ tiêu phải nhập số!',
            })

        if not weight:
            weight = 1

        if not can_be_integer(weight):
            return Response({
                'ok': False,
                'msg': 'Trọng số phải nhập số!',
            })

        if int(weight) < 1 or int(weight) > 10:
            return Response({
                'ok': False,
                'msg': 'Trọng số phải có giá trị từ 1 đến 10!',
            })

        if not period_start:
            return Response({
                'ok': False,
                'msg': 'Thời gian bắt đầu không được để trống!'
            })

        if not period_end:
            return Response({
                'ok': False,
                'msg': 'Thời gian kết thúc không được để trống!'
            })

        period_start = arrow.get(period_start).to(settings.TIME_ZONE).datetime
        period_end = arrow.get(period_end).to(settings.TIME_ZONE).datetime

        if period_end < period_start:
            return Response({
                'ok': False,
                'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!'
            })

        if my_profile.get_role() == 'Director':
            try:
                fp = Profile.objects.get(user__id=user_id, removed=False)
                tp = Profile.objects.get(id=profile_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=tp, removed=False)

                tag = Tag(
                    user=dpm,
                    tag_name=tag_name,
                    tag_description=tag_description,
                    period_start=period_start,
                    period_end=period_end,
                    weight=weight,
                    quantity=quantity,
                    finished=0,
                    progress=0,
                    state='PR',
                    created_by=fp,
                )
                tag.save()
                return Response({
                    'ok': True,
                    'msg': 'Tạo KPI thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Không tồn tại nhân viên này!',
                })

        if my_profile.get_role() == 'Manager':
            try:
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                tp = Profile.objects.get(id=profile_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=tp, removed=False)
                if int(me.department.id) != int(dpm.department.id):
                    return Response({
                        'ok': False,
                        'msg': 'Nhân viên này không thuộc phòng ban của bạn!',
                    })
                else:
                    tag = Tag(
                        user=dpm,
                        tag_name=tag_name,
                        tag_description=tag_description,
                        period_start=period_start,
                        period_end=period_end,
                        weight=weight,
                        quantity=quantity,
                        finished=0,
                        progress=0,
                        state='PR',
                        created_by=my_profile,
                    )
                    tag.save()
                    return Response({
                        'ok': True,
                        'msg': 'Tạo KPI thành công!',
                    })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Không tồn tại nhân viên này!',
                })
    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def edit_tag_member_api_view(request):
    """
    API chỉnh sửa một Tag
    :param request: user_id, tag_id, tag_name, tag_description, period_start, period_end, quantity, weight
    :return: tạo mới một tag
    """
    profile_id = request.data.get('profile_id')
    tag_id = request.data.get('tag_id')
    tag_request = request.data.get('tag_request')
    tag_name = request.data.get('tag_name')
    tag_description = request.data.get('tag_description')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    quantity = request.data.get('quantity')
    weight = request.data.get('weight')

    if request.user.is_authenticated:
        if not profile_id:
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy nhân viên!',
            })

        if not can_be_integer(profile_id):
            return Response({
                'ok': False,
                'msg': 'Không tồn tại nhân viên!',
            })

        if not tag_id:
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy KPI!',
            })

        if not can_be_integer(tag_id):
            return Response({
                'ok': False,
                'msg': 'Không tồn tại KPI!',
            })

        if not tag_request:
            return Response({
                'ok': False,
                'msg': 'Không xác định được yêu cầu!',
            })

        if tag_request != 'edit' and tag_request != 'remove':
            return Response({
                'ok': False,
                'msg': 'Yêu cầu không hợp lệ!',
            })

        if tag_request == 'remove':
            try:
                my_profile = Profile.objects.get(user__id=request.user.id, removed=False)

                if my_profile.get_role() == 'Director':
                    tp = Profile.objects.get(id=profile_id, removed=False)
                    dpm = DepartmentMember.objects.get(department_member=tp, removed=False)
                    tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)

                    tag.removed = True

                    tag.save()

                    return Response({
                        'ok': True,
                        'msg': 'Xóa KPI Thành Công!',
                    })

                elif my_profile.get_role() == 'Manager':
                    me = DepartmentMember.objects.get(department_member=my_profile, removed=False)

                    tp = Profile.objects.get(id=profile_id, removed=False)
                    dpm = DepartmentMember.objects.get(department_member=tp, removed=False)

                    if int(me.department.id) == int(dpm.department.id):
                        tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)

                        tag.removed = True
                        tag.save()

                        return Response({
                            'ok': True,
                            'msg': 'Xóa KPI Thành Công!',
                        })
                    else:
                        return Response({
                            'ok': False,
                            'msg': 'Bạn không có quyền xóa KPI này!',
                        })

                else:
                    return Response({
                        'ok': False,
                        'msg': 'Bạn không có quyền xóa KPI này!',
                    })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

        if tag_request == 'edit':

            if not tag_name:
                return Response({
                    'ok': False,
                    'msg': 'Tiêu đề không được để trống!',
                })

            if not tag_description:
                tag_description = None

            if not quantity:
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu không được để trống!',
                })

            if not can_be_integer(quantity):
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu phải nhập số!',
                })

            if not weight:
                weight = 1

            if not can_be_integer(weight):
                return Response({
                    'ok': False,
                    'msg': 'Trọng số phải nhập số!',
                })

            if int(weight) < 1 or int(weight) > 10:
                return Response({
                    'ok': False,
                    'msg': 'Trọng số phải có giá trị từ 1 đến 10!',
                })

            if not period_start:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian bắt đầu không được để trống!'
                })

            if not period_end:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian kết thúc không được để trống!'
                })

            period_start = arrow.get(period_start).to(settings.TIME_ZONE).datetime
            period_end = arrow.get(period_end).to(settings.TIME_ZONE).datetime

            if period_end < period_start:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!'
                })

            try:
                fp = Profile.objects.get(user__id=request.user.id, removed=False)
                tp = Profile.objects.get(id=profile_id, removed=False)
                me = DepartmentMember.objects.get(department_member=fp, removed=False)
                dpm = DepartmentMember.objects.get(department_member=tp, removed=False)

                if fp.get_role() == 'Director':
                    tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)

                    tag.tag_name = tag_name
                    tag.tag_description = tag_description
                    tag.period_start = period_start
                    tag.period_end = period_end
                    tag.weight = weight
                    tag.quantity = quantity
                    tag.created_by = fp

                    percent = float(tag.finished) / float(quantity) * 100.0
                    percent = round(percent, 2)

                    tag.progress = percent

                    tag.save()

                    return Response({
                        'ok': True,
                        'msg': 'Cập nhật KPI thành công!',
                    })

                elif fp.get_role() == 'Manager':
                    if int(me.department.id) == int(dpm.department.id):
                        tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)

                        tag.tag_name = tag_name
                        tag.tag_description = tag_description
                        tag.period_start = period_start
                        tag.period_end = period_end
                        tag.weight = weight
                        tag.quantity = quantity
                        tag.created_by = fp

                        percent = float(tag.finished) / float(quantity) * 100.0
                        percent = round(percent, 2)

                        tag.progress = percent

                        tag.save()

                        return Response({
                            'ok': True,
                            'msg': 'Cập nhật KPI thành công!',
                        })
                    else:
                        return Response({
                            'ok': False,
                            'msg': 'Bạn không có quyền chỉnh sửa KPI này!',
                        })
                else:
                    return Response({
                        'ok': False,
                        'msg': 'Bạn không có quyền chỉnh sửa KPI này!',
                    })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def edit_my_tag_api_view(request):
    """
    API cập nhật KPI của tôi
    :param request: profile_id, tag_id, finished, tag_state
    :return: tạo mới một tag
    """
    user_id = request.user.id
    profile_id = request.data.get('profile_id')
    tag_id = request.data.get('tag_id')
    finished = request.data.get('finished')
    tag_state = request.data.get('tag_state')

    if request.user.is_authenticated:
        if profile_id:
            if not can_be_integer(profile_id):
                return Response({
                    'ok': False,
                    'msg': 'Nhân viên không tồn tại!',
                })

            if not tag_id:
                return Response({
                    'ok': False,
                    'msg': 'Không tìm thấy KPI!',
                })

            if not can_be_integer(tag_id):
                return Response({
                    'ok': False,
                    'msg': 'Không tồn tại KPI!',
                })

            if not tag_state:
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái KPI không được để trống!',
                })

            if tag_state != 'Chưa Hoàn Thành' and tag_state != 'Đang Thực Hiện' and tag_state != 'Hoàn Thành':
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái KPI không hợp lệ!',
                })

            if tag_state == 'Chưa Hoàn Thành':
                tag_state = 'NF'

            if tag_state == 'Đang Thực Hiện':
                tag_state = 'PR'

            if tag_state == 'Hoàn Thành':
                tag_state = 'CO'

            if not finished:
                return Response({
                    'ok': False,
                    'msg': 'Kết quả đạt được không được để trống!',
                })

            if not can_be_integer(finished):
                return Response({
                    'ok': False,
                    'msg': 'Kết quả đạt được phải nhập số!',
                })

            try:
                tp = Profile.objects.get(user__id=user_id, id=profile_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=tp, removed=False)
                tag = Tag.objects.get(id=tag_id, user=dpm)

                if tag.state == 'CO':
                    return Response({
                        'ok': False,
                        'msg': 'KPI này đã hoàn thành nên không thể chỉnh sửa!',
                    })

                percent = float(finished) / float(tag.quantity) * 100.0
                percent = round(percent, 2)

                tag.finished = finished
                tag.progress = percent
                tag.state = tag_state

                tag.save()
                return Response({
                    'ok': True,
                    'msg': 'Cập nhật KPI thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })
        return Response({
            'ok': False,
            'msg': 'Chỉnh sửa KPI thất bại!',
        })
    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def my_tag_computation_api_view(request):
    """
    API cộng tất cả kết quả đạt được của Task rồi cập nhật cho Tag của tôi
    :param request: profile_id, tag_id
    :return: tạo mới một tag
    """
    user_id = request.user.id
    profile_id = request.data.get('profile_id')
    tag_id = request.data.get('tag_id')

    if request.user.is_authenticated:
        if profile_id:
            if not can_be_integer(profile_id):
                return Response({
                    'ok': False,
                    'msg': 'Nhân viên không tồn tại!',
                })

            if not tag_id:
                return Response({
                    'ok': False,
                    'msg': 'Không tìm thấy KPI!',
                })

            if not can_be_integer(tag_id):
                return Response({
                    'ok': False,
                    'msg': 'Không tồn tại KPI!',
                })

            try:
                tp = Profile.objects.get(user__id=user_id, id=profile_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=tp, removed=False)
                tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)
                task = Task.objects.filter(tag=tag, removed=False)

                count = 0

                for item in task:
                    if item.state == 'CO':
                        count += int(item.result_value)

                tag.finished = count

                percent = float(count) / float(tag.quantity) * 100.0
                percent = round(percent, 2)

                tag.progress = percent

                tag.save()
                return Response({
                    'ok': True,
                    'msg': 'Đồng bộ dữ liệu thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist, Task.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })
        return Response({
            'ok': False,
            'msg': 'Chỉnh sửa KPI thất bại!',
        })
    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['GET'])
def get_my_tag_statistics_api_view(request):
    """
    API lấy số liệu thông kê của Tag
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.user.id
        query = request.GET.get('query')
        try:
            profile = Profile.objects.get(user__id=user_id, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
            end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
            wt = WorkTime.objects.filter(user=member, removed=False,
                                         date__range=(start,
                                                      end)).aggregate(totalTime=Sum('time_total'))['totalTime']
            tag = None
            if not query:
                tag = Tag.objects.filter(user=member,
                                         removed=False,
                                         period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
            elif query == 'all':
                tag = Tag.objects.filter(user=member, removed=False)
            elif query == 'current':
                tag = Tag.objects.filter(user=member,
                                         removed=False,
                                         period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
            elif query == 'tmonth':
                # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                tag = Tag.objects.filter(user=member,
                                         removed=False,
                                         period_start__range=(start, end),
                                         period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                         created_at__range=(start, end))
            elif query == 'outdated':
                tag = Tag.objects.filter(user=member,
                                         removed=False,
                                         period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime)
            if tag:
                total = 0
                count_finished = 0
                count_progress = 0
                count_un_finished = 0
                for item in tag:
                    total += 1
                    if item.state == 'CO':
                        count_finished += 1
                    elif item.state == 'PR':
                        count_progress += 1
                    elif item.state == 'NF':
                        count_un_finished += 1

                return Response({
                    'total_time': wt,
                    'total_tag': total,
                    'count_finished': count_finished,
                    'count_progress': count_progress,
                    'count_un_finished': count_un_finished,
                })
            else:
                return Response({
                    'total_time': wt,
                    'total_tag': 0,
                    'count_finished': 0,
                    'count_progress': 0,
                    'count_un_finished': 0,
                })

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return Response({})

    return Response({})


@api_view(['GET'])
def get_member_tag_statistics_api_view(request):
    """
    API lấy số liệu thông kê của Tag của một nhân viên
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({})

        if not can_be_integer(user_id):
            return Response({})
        try:
            my_profile = Profile.objects.get(user__id=request.user.id, removed=False)
            profile = Profile.objects.get(user__id=user_id, removed=False)
            if my_profile.get_role() == 'Director':
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                wt = WorkTime.objects.filter(user=member, removed=False,
                                             date__range=(start,
                                                          end)).aggregate(totalTime=Sum('time_total'))['totalTime']
                tag = Tag.objects.filter(user=member, removed=False, created_at__range=(start, end))
                total = 0
                count_finished = 0
                count_progress = 0
                count_un_finished = 0
                for item in tag:
                    total += 1
                    if item.state == 'CO':
                        count_finished += 1
                    elif item.state == 'PR':
                        count_progress += 1
                    elif item.state == 'NF':
                        count_un_finished += 1
                return Response({
                  'total_time': wt,
                  'total_tag': total,
                  'count_finished': count_finished,
                  'count_progress': count_progress,
                  'count_un_finished': count_un_finished,
                })
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
                if int(me.department.id) == int(dpm.department.id):
                    member = DepartmentMember.objects.get(department_member=profile, removed=False)
                    start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                    end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                    wt = WorkTime.objects.filter(user=member, removed=False,
                                                 date__range=(start,
                                                              end)).aggregate(totalTime=Sum('time_total'))['totalTime']
                    tag = Tag.objects.filter(user=member, removed=False, created_at__range=(start, end))
                    total = 0
                    count_finished = 0
                    count_progress = 0
                    count_un_finished = 0
                    for item in tag:
                        total += 1
                        if item.state == 'CO':
                            count_finished += 1
                        elif item.state == 'PR':
                            count_progress += 1
                        elif item.state == 'NF':
                            count_un_finished += 1
                    return Response({
                        'total_time': wt,
                        'total_tag': total,
                        'count_finished': count_finished,
                        'count_progress': count_progress,
                        'count_un_finished': count_un_finished,
                    })
                else:
                    return Response({})
            else:
                return Response({})

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return Response({})

    return Response({})


@api_view(['GET'])
def get_tag_statistics_api_view(request):
    """
    API lấy số liệu thông kê của Tag của tất cả nhân viên hoặc nhân viên một phòng ban
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        query = request.GET.get('query')
        try:
            my_profile = Profile.objects.get(user__id=request.user.id, removed=False)
            if my_profile.get_role() == 'Director':
                tag = None
                if not query:
                    tag = Tag.objects.filter(removed=False,
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
                elif query == 'all':
                    tag = Tag.objects.filter(removed=False)
                elif query == 'current':
                    tag = Tag.objects.filter(removed=False,
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
                elif query == 'tmonth':
                    # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                    start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                    end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                    tag = Tag.objects.filter(removed=False,
                                             period_start__range=(start, end),
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                             created_at__range=(start, end))
                elif query == 'outdated':
                    tag = Tag.objects.filter(removed=False,
                                             period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime)
                if tag:
                    total = 0
                    count_finished = 0
                    count_progress = 0
                    count_un_finished = 0
                    for item in tag:
                        total += 1
                        if item.state == 'CO':
                            count_finished += 1
                        elif item.state == 'PR':
                            count_progress += 1
                        elif item.state == 'NF':
                            count_un_finished += 1
                    return Response({
                      'total': total,
                      'count_finished': count_finished,
                      'count_progress': count_progress,
                      'count_un_finished': count_un_finished,
                    })
                else:
                    return Response({})
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                tag = None
                if not query:
                    tag = Tag.objects.filter(user__department__id=me.department.id,
                                             removed=False,
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
                elif query == 'all':
                    tag = Tag.objects.filter(user__department__id=me.department.id, removed=False)
                elif query == 'current':
                    tag = Tag.objects.filter(user__department__id=me.department.id,
                                             removed=False,
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime)
                elif query == 'tmonth':
                    # kpi được tạo trong tháng này, bắt đầu trong tháng này, kết thúc sau hôm nay
                    start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
                    end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
                    tag = Tag.objects.filter(user__department__id=me.department.id,
                                             removed=False,
                                             period_start__range=(start, end),
                                             period_end__gt=arrow.now().to(settings.TIME_ZONE).datetime,
                                             created_at__range=(start, end))
                elif query == 'outdated':
                    tag = Tag.objects.filter(user__department__id=me.department.id,
                                             removed=False,
                                             period_end__lt=arrow.now().to(settings.TIME_ZONE).datetime)
                if tag:
                    total = 0
                    count_finished = 0
                    count_progress = 0
                    count_un_finished = 0
                    for item in tag:
                        total += 1
                        if item.state == 'CO':
                            count_finished += 1
                        elif item.state == 'PR':
                            count_progress += 1
                        elif item.state == 'NF':
                            count_un_finished += 1
                    return Response({
                        'total': total,
                        'count_finished': count_finished,
                        'count_progress': count_progress,
                        'count_un_finished': count_un_finished,
                    })
                else:
                    return Response({})
            else:
                return Response({})

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return Response({})

    return Response({})
