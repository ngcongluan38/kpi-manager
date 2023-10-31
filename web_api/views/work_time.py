import arrow
from django.conf import settings
from datetime import datetime, date
# from django.db import models
from django.db.models import Sum

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from kpi_manager.models import Profile, DepartmentMember, WorkTime
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


class GetWordTimeListView(generics.ListAPIView):
    """
    API lấy danh sách giờ làm việc Tag của tôi
    """
    serializer_class = serializer_api.GetWorkTimeOfMemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.user.id
        month_request = self.request.GET.get('month_request')
        year_request = self.request.GET.get('year_request')
        if self.request.user.is_authenticated:
            if user_id:
                if not can_be_integer(user_id):
                    return []

                if month_request and year_request:
                    if not can_be_integer(month_request):
                        return []

                    if not can_be_integer(year_request):
                        return []

                    if int(month_request) < 1 or int(month_request) > 12:
                        return []

                    if int(year_request) < 1990 or int(year_request) > arrow.now().year:
                        return []

                    try:
                        start = arrow.now().\
                            replace(month=int(month_request), year=int(year_request)).\
                            to(settings.TIME_ZONE).floor('month').datetime
                        end = arrow.now().\
                            replace(month=int(month_request), year=int(year_request)).\
                            to(settings.TIME_ZONE).ceil('month').datetime
                        profile = Profile.objects.get(user__id=user_id, removed=False)
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        return WorkTime.objects.filter(user=member, date__range=(start, end), removed=False)

                    except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
                        return []

                else:
                    try:
                        profile = Profile.objects.get(user__id=user_id, removed=False)
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        return WorkTime.objects.filter(user=member, removed=False)

                    except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
                        return []
        return []


class GetWordTimeMemberListView(generics.ListAPIView):
    """
    API lấy danh sách giờ làm việc Tag của một nhân viên
    """
    serializer_class = serializer_api.GetWorkTimeOfMemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        month_request = self.request.GET.get('month_request')
        year_request = self.request.GET.get('year_request')
        if self.request.user.is_authenticated:
            if user_id:
                if not can_be_integer(user_id):
                    return []

                if month_request and year_request:
                    if not can_be_integer(month_request):
                        return []

                    if not can_be_integer(year_request):
                        return []

                    if int(month_request) < 1 or int(month_request) > 12:
                        return []

                    if int(year_request) < 1990 or int(year_request) > arrow.now().year:
                        return []

                    try:
                        start = arrow.now().\
                            replace(month=int(month_request), year=int(year_request)).\
                            to(settings.TIME_ZONE).floor('month').datetime
                        end = arrow.now().\
                            replace(month=int(month_request), year=int(year_request)).\
                            to(settings.TIME_ZONE).ceil('month').datetime
                        my_profile = Profile.objects.get(user=self.request.user, removed=False)
                        profile = Profile.objects.get(user__id=user_id, removed=False)
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        if my_profile.get_role() == 'Director':
                            return WorkTime.objects.filter(user=member, date__range=(start, end), removed=False)
                        elif my_profile.get_role() == 'Manager':
                            me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                            if int(me.department.id) == int(member.department.id):
                                return WorkTime.objects.filter(user=member, date__range=(start, end), removed=False)
                            else:
                                return []
                        else:
                            return []

                    except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
                        return []

                else:
                    try:
                        my_profile = Profile.objects.get(user=self.request.user, removed=False)
                        profile = Profile.objects.get(user__id=user_id, removed=False)
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        if my_profile.get_role() == 'Director':
                            return WorkTime.objects.filter(user=member, removed=False)
                        elif my_profile.get_role() == 'Manager':
                            me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                            if int(me.department.id) == int(member.department.id):
                                return WorkTime.objects.filter(user=member, removed=False)
                            else:
                                return []
                        else:
                            return []

                    except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
                        return []
        return []


@api_view(['POST'])
def add_my_work_time_api_view(request):
    """
    API thêm giờ làm việc của tôi
    :param request:
    :return:
    """
    user_id = request.user.id
    work_date = request.data.get('date')
    start_in_day = request.data.get('start_in_day')
    end_in_day = request.data.get('end_in_day')
    rest_time = request.data.get('rest_time')

    if request.user.is_authenticated:
        if not work_date:
            return Response({
                'ok': False,
                'msg': 'Ngày làm việc không được để trống!',
            })

        if not start_in_day:
            return Response({
                'ok': False,
                'msg': 'Thời gian bắt đầu không được để trống!',
            })
        if work_date:
            work_date = arrow.get(work_date).to(settings.TIME_ZONE).date()

        if start_in_day:
            start_in_day = arrow.get(start_in_day).to(settings.TIME_ZONE).time()

        if end_in_day:
            end_in_day = arrow.get(end_in_day).to(settings.TIME_ZONE).time()

        if start_in_day and end_in_day and end_in_day < start_in_day:
            return Response({
                'ok': False,
                'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!',
            })

        try:
            profile = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=profile, removed=False)

            total = 0
            if start_in_day and end_in_day:
                start = datetime.combine(date.today(), start_in_day)
                end = datetime.combine(date.today(), end_in_day)
                total = end - start
                total = total.total_seconds()
                total = float(total) / 3600.0

                if rest_time:
                    total = float(total) - float(rest_time)

            worktime = WorkTime(
                user=dpm,
                date=work_date,
                start_in_day=start_in_day,
                end_in_day=end_in_day,
                rest_time=rest_time,
                time_total=total,
            )
            worktime.save()

            return Response({
                'ok': True,
                'msg': 'Báo cáo giờ làm việc thành công!',
            })
        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
            return Response({
                'ok': False,
                'msg': 'Lỗi dữ liệu!',
            })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def edit_my_work_time_api_view(request):
    """
    API chỉnh sửa hoặc xóa giờ làm việc của tôi
    :param request:
    :return:
    """
    user_id = request.user.id
    work_time_id = request.data.get('work_time_id')
    work_date = request.data.get('date')
    start_in_day = request.data.get('start_in_day')
    end_in_day = request.data.get('end_in_day')
    rest_time = request.data.get('rest_time')
    work_time_request = request.data.get('work_time_request')

    if request.user.is_authenticated:
        if not work_time_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại giờ làm việc này!',
            })

        if not can_be_integer(work_time_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy giờ làm việc của bạn!',
            })

        if not work_time_request:
            return Response({
                'ok': False,
                'msg': 'Không xác định được yêu cầu!',
            })

        if work_time_request != 'edit' and work_time_request != 'remove':
            return Response({
                'ok': False,
                'msg': 'Yêu cầu không hợp lệ!',
            })

        if work_time_request == 'remove':
            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
                wt = WorkTime.objects.get(id=work_time_id, user=dpm, removed=False)

                wt.removed = True
                wt.save()

                return Response({
                    'ok': True,
                    'msg': 'Xoá thành công!',
                })

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

        if work_time_request == 'edit':
            if not work_date:
                return Response({
                    'ok': False,
                    'msg': 'Ngày làm việc không được để trống!',
                })

            if not start_in_day:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian bắt đầu không được để trống!',
                })

            if work_date:
                work_date = arrow.get(work_date).to(settings.TIME_ZONE).date()

            if start_in_day:
                start_in_day = arrow.get(start_in_day).to(settings.TIME_ZONE).time()

            if end_in_day:
                end_in_day = arrow.get(end_in_day).to(settings.TIME_ZONE).time()

            if start_in_day and end_in_day and end_in_day < start_in_day:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!',
                })

            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
                wt = WorkTime.objects.get(id=work_time_id, user=dpm, removed=False)

                total = 0
                if start_in_day and end_in_day:
                    start = datetime.combine(date.today(), start_in_day)
                    end = datetime.combine(date.today(), end_in_day)
                    total = end - start
                    total = total.total_seconds()
                    total = float(total) / 3600.0

                    if rest_time:
                        total = float(total) - float(rest_time)

                wt.date = work_date
                wt.start_in_day = start_in_day
                wt.end_in_day = end_in_day
                wt.rest_time = rest_time
                wt.time_total = total
                wt.save()

                return Response({
                    'ok': True,
                    'msg': 'Cập nhật thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['GET'])
def my_work_time_statistic_api_view(request):
    """
    API đếm tổng số giờ làm việc của tôi trong tháng này
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user__id=request.user.id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
            start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
            end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
            wt = WorkTime.objects.filter(user=dpm,
                                         date__range=(start, end),
                                         removed=False).aggregate(totalTime=Sum('time_total'))['totalTime']
            return Response(wt)

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
            return Response({})
    return Response({})


@api_view(['GET'])
def work_time_member_statistic_api_view(request):
    """
    API đếm tổng số giờ làm việc của một nhân viên trong tháng này
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.GET.get('user_id')
        try:
            my_profile = Profile.objects.get(user=request.user, removed=False)
            profile = Profile.objects.get(user__id=user_id, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
            end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
            wt = WorkTime.objects.filter(user=member,
                                         date__range=(start, end),
                                         removed=False).aggregate(totalTime=Sum('time_total'))['totalTime']
            if my_profile.get_role() == 'Director':
                return Response(wt)
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                if int(me.department.id) == int(member.department.id):
                    return Response(wt)
                else:
                    return Response({})
            else:
                return Response({})

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, WorkTime.DoesNotExist):
            return Response({})
    return Response({})
