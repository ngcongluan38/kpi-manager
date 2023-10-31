from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from kpi_manager.models import Profile, Department, DepartmentMember
from utils.common import can_be_integer
from web_api.utils import build_absolute_url
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


class GetDepartmentListView(generics.ListAPIView):
    """
    API lấy danh sách phòng ban
    """
    serializer_class = serializer_api.GetDepartmentListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            try:
                department = Department.objects.filter(removed=False).order_by('-department_level')
                return department
            except Department.DoesNotExist:
                return []
        return []


class GetMemberInDepartmentListView(generics.ListAPIView):
    """
    API lấy danh sách nhân viên trong một phòng ban
    """
    serializer_class = serializer_api.GetMemberInDepartmentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            department_id = self.request.GET.get('department_id')
            try:
                my_profile = Profile.objects.get(user__id=self.request.user.id, removed=False)
                if not department_id:
                    if my_profile.get_role() == 'Director':
                        return DepartmentMember.objects.filter(removed=False)
                    elif my_profile.get_role() == 'Manager':
                        me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                        d_id = me.department.id
                        department = Department.objects.get(pk=d_id)
                        return DepartmentMember.objects.filter(department=department, removed=False)
                    else:
                        return []
                if department_id:
                    if not can_be_integer(department_id):
                        return []

                    if my_profile.get_role() == 'Director':
                        department = Department.objects.get(pk=department_id)
                        return DepartmentMember.objects.filter(department=department, removed=False)
                    elif my_profile.get_role() == 'Manager':
                        me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                        d_id = me.department.id
                        if int(d_id) == int(department_id):
                            department = Department.objects.get(pk=department_id)
                            return DepartmentMember.objects.filter(department=department, removed=False)
                        else:
                            return []
                    else:
                        return []
            except (Profile.DoesNotExist, Department.DoesNotExist, Department.DoesNotExist):
                return []
        return []


@api_view(['GET'])
def get_my_profile_info_in_department(request):
    """
    API lấy thông tin của tôi trong một phòng ban
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        user = request.user
        try:
            profile = Profile.objects.get(user=user, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            return Response({
                'userId': member.department_member.user.id,
                'profileId': member.department_member.id,
                'fullName': member.department_member.full_name,
                'sex': member.department_member.get_sex(),
                'birthDay': member.department_member.get_birth_day(),
                'idNumber': member.department_member.id_number,
                'email': member.department_member.user.email,
                'address': member.department_member.address,
                'avatarUrl': build_absolute_url(member.department_member.get_avatar_url()),
                'position': member.position,
                'isLeader': member.is_leader,
                'department': member.department.department_name,
            })

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
            return Response({})
    return Response({})


@api_view(['GET'])
def get_profile_info_specific_in_department(request):
    """
    API lấy thông tin cơ bản của một nhân viên
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        pern = request.user.profile.get_role()
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({})
        if not can_be_integer(user_id):
            return Response({})
        try:
            if pern == 'Director':
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                return Response({
                    'userId': member.department_member.user.id,
                    'profileId': member.department_member.id,
                    'fullName': member.department_member.full_name,
                    'sex': member.department_member.get_sex(),
                    'avatarUrl': build_absolute_url(member.department_member.get_avatar_url()),
                    'position': member.position,
                    'departmentId': member.department.id,
                    'department': member.department.department_name,
                })
            elif pern == 'Manager':
                profile = Profile.objects.get(user__id=user_id, removed=False)
                my_profile = Profile.objects.get(user__id=request.user.id, removed=False)

                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                if int(me.department.id) == int(member.department.id):
                    return Response({
                        'userId': member.department_member.user.id,
                        'profileId': member.department_member.id,
                        'fullName': member.department_member.full_name,
                        'sex': member.department_member.get_sex(),
                        'avatarUrl': build_absolute_url(member.department_member.get_avatar_url()),
                        'position': member.position,
                        'departmentId': member.department.id,
                        'department': member.department.department_name,
                    })
                else:
                    return Response({})
            else:
                return Response({})

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
            return Response({})
    return Response({})


@api_view(['GET'])
def get_profile_list_no_pagination_api_view(request):
    """
    API lấy danh sách tag của tôi và không phân trang
    :param request: department_id
    :return:
    """
    if request.user.is_authenticated:
        pern = request.user.profile.get_role()
        department_id = request.GET.get('department_id')
        data = []
        if not department_id:
            if pern != 'Director' and pern != 'Manager':
                return Response([])
            try:
                if pern == 'Director':
                    profile = Profile.objects.filter(removed=False)
                    for item in profile:
                        data.append({
                            'userId': item.user.id,
                            'profileId': item.id,
                            'fullName': item.full_name,
                        })

                    return Response(data)
                if pern == 'Manager':
                    dpm = DepartmentMember.objects.get(department_member=request.user.profile, removed=False)
                    profile = DepartmentMember.objects.filter(department__id=dpm.department.id, removed=False)
                    for item in profile:
                        data.append({
                            'userId': item.department_member.user.id,
                            'profileId': item.department_member.id,
                            'fullName': item.department_member.full_name,
                        })

                    return Response(data)
            except (Profile.DoesNotExist,):
                return Response([])
        elif department_id:
            if not can_be_integer(department_id):
                return Response([])
            if pern != 'Director' and pern != 'Manager':
                return Response([])
            dpm = DepartmentMember.objects.get(department_member=request.user.profile, removed=False)
            if pern != 'Director' and dpm.department.id != int(department_id):
                return Response([])
            try:
                profile = DepartmentMember.objects.filter(department__id=department_id, removed=False)
                for item in profile:
                    data.append({
                        'userId': item.department_member.user.id,
                        'profileId': item.department_member.id,
                        'fullName': item.department_member.full_name,
                    })

                return Response(data)

            except (DepartmentMember.DoesNotExist,):
                return Response([])

    return Response([])


@api_view(['GET'])
def get_department_list_no_pagination_api_view(request):
    """
    API lấy danh sách phòng ban
    :param request: department_id
    :return:
    """
    if request.user.is_authenticated:
        pern = request.user.profile.get_role()
        data = []
        if pern != 'Director' and pern != 'Manager':
            return Response([])
        try:
            department = Department.objects.filter(removed=False)
            for item in department:
                data.append({
                    'departmentId': item.id,
                    'departmentName': item.department_name,
                    'departmentLevel': item.department_level,
                })

            return Response(data)

        except (Department.DoesNotExist,):
            return Response([])

    return Response([])
