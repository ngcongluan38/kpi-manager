# import markdown2
import arrow
from django.conf import settings

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from kpi_manager.models import Profile, Tag, Task, DepartmentMember, Comment
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


class GetTaskListView(generics.ListAPIView):
    """
    API lấy danh sách các Task của một nhân viên
    """
    serializer_class = serializer_api.GetTaskOfMemberDependOnTagSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.GET.get('user_id')
        tag_id = self.request.GET.get('tag_id')
        if self.request.user.is_authenticated:
            if user_id:
                if not can_be_integer(user_id):
                    return []
                if tag_id:
                    if not can_be_integer(tag_id):
                        return []

                    try:
                        profile = Profile.objects.get(user__id=user_id, removed=False)
                        member = DepartmentMember.objects.get(department_member=profile, removed=False)
                        tag = Tag.objects.get(id=tag_id, user=member, removed=False)
                        return Task.objects.filter(user=member, tag=tag, removed=False).order_by('-created_at')

                    except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                        return []
        return []


class GetMyTaskListView(generics.ListAPIView):
    """
    API lấy danh sách các Task của tôi
    """
    serializer_class = serializer_api.GetTaskOfMemberDependOnTagSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            tag_id = self.request.GET.get('tag_id')
            if tag_id:
                if not can_be_integer(tag_id):
                    return []
                try:
                    profile = Profile.objects.get(user__id=user_id, removed=False)
                    member = DepartmentMember.objects.get(department_member=profile, removed=False)
                    tag = Tag.objects.get(id=tag_id, user=member, removed=False)
                    return Task.objects.filter(user=member, tag=tag, removed=False).order_by('-created_at')

                except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                    return []
        return []


class GetCommentOfTaskView(generics.ListAPIView):
    """
    API lấy danh sách bình luận của một task
    """
    serializer_class = serializer_api.GetCommentOfTaskSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        task_id = self.request.GET.get('task_id')
        if self.request.user.is_authenticated:
            if task_id:
                if not can_be_integer(task_id):
                    return []

                try:
                    task = Task.objects.get(id=task_id, removed=False)
                    return Comment.objects.filter(task=task, removed=False).order_by('-created_at')

                except Task.DoesNotExist:
                    return []
        return []


class GetCommentOfMyTaskView(generics.ListAPIView):
    """
    API lấy danh sách bình luận của một task của tôi
    """
    serializer_class = serializer_api.GetCommentOfTaskSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            task_id = self.request.GET.get('task_id')
            if task_id:
                if not can_be_integer(task_id):
                    return []

                try:
                    task = Task.objects.get(id=task_id, user__department_member__user_id=user_id, removed=False)
                    return Comment.objects.filter(task=task, removed=False).order_by('-created_at')

                except Task.DoesNotExist:
                    return []
        return []


@api_view(['GET'])
def get_one_task_of_member_detail_api_view(request):
    """
    API lấy thông tin chi tiết một task của một nhân viên
    :param request: task_id
    :return:
    """
    user_id = request.GET.get('user_id')
    task_id = request.GET.get('task_id')
    if request.user.is_authenticated:
        if user_id and task_id:
            if not can_be_integer(user_id):
                return Response({})
            if not can_be_integer(task_id):
                return Response({})

            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                task = Task.objects.get(id=task_id, user=member, removed=False)
                # taskDesc = markdown2.markdown(task.task_description,
                #                               extras=["tables",
                #                                       "fenced-code-blocks",
                #                                       'code-friendly']) if task.task_description else None
                return Response({
                    'userId': task.user.department_member.user.id,
                    'fullName': task.user.department_member.full_name,
                    'avatarUrl': build_absolute_url(task.user.department_member.get_avatar_url()),
                    'sex': task.user.department_member.get_sex(),
                    'position': task.user.position,
                    'department': task.user.department.department_name,
                    'tagId': task.tag.id,
                    'taskId': task.pk,
                    'taskName': task.task_name,
                    'taskDescription': task.task_description,
                    # 'taskDescEdit': task.task_description,
                    'periodStart': task.period_start,
                    'periodEnd': task.period_end,
                    'unitOfMeasure': task.unit_of_measure,
                    'targetValue': task.target_value,
                    'resultValue': task.result_value,
                    'progress': task.progress,
                    'weight': task.weight,
                    'taskState': task.get_state(),
                    'isFinished': task.is_finished,
                    'createdAt': task.created_at,
                    'updatedAt': task.updated_at,
                })

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
                return Response({})

        return Response({})


@api_view(['GET'])
def get_one_task_detail_of_me_api_view(request):
    """
    API lấy thông tin chi tiết một task của tôi
    :param request: task_id
    :return:
    """
    if request.user.is_authenticated:
        user_id = request.user.id
        task_id = request.GET.get('task_id')
        if task_id:
            if not can_be_integer(task_id):
                return Response({})

            try:
                profile = Profile.objects.get(user__id=user_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile, removed=False)
                task = Task.objects.get(id=task_id, user=member, removed=False)
                # taskDesc = markdown2.markdown(task.task_description,
                #                               extras=["tables",
                #                                       "fenced-code-blocks",
                #                                       'code-friendly']) if task.task_description else None
                return Response({
                    'userId': task.user.department_member.user.id,
                    'fullName': task.user.department_member.full_name,
                    'avatarUrl': build_absolute_url(task.user.department_member.get_avatar_url()),
                    'sex': task.user.department_member.get_sex(),
                    'position': task.user.position,
                    'department': task.user.department.department_name,
                    'tagId': task.tag.id,
                    'taskId': task.pk,
                    'taskName': task.task_name,
                    'taskDescription': task.task_description,
                    # 'taskDescEdit': task.task_description,
                    'periodStart': task.period_start,
                    'periodEnd': task.period_end,
                    'unitOfMeasure': task.unit_of_measure,
                    'targetValue': task.target_value,
                    'resultValue': task.result_value,
                    'progress': task.progress,
                    'weight': task.weight,
                    'taskState': task.get_state(),
                    'isFinished': task.is_finished,
                    'createdAt': task.created_at,
                    'updatedAt': task.updated_at,
                })

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
                return Response({})

        return Response({})


@api_view(['POST'])
def add_new_task_api_view(request):
    """
    API tạo một task mới
    :param request:
    :return:
    """
    user_id = request.user.id
    tag_id = request.data.get('tag_id')
    task_name = request.data.get('task_name')
    task_description = request.data.get('task_description')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    unit_of_measure = request.data.get('unit_of_measure')
    target_value = request.data.get('target_value')
    weight = request.data.get('weight')

    if request.user.is_authenticated:
        if not tag_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại KPI!',
            })

        if not can_be_integer(tag_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy KPI bạn lựa chọn!',
            })

        if not task_name:
            return Response({
                'ok': False,
                'msg': 'Tiêu đề không được để trống!',
            })

        if not task_description:
            task_description = None

        if not target_value:
            return Response({
                'ok': False,
                'msg': 'Chỉ tiêu không được để trống!',
            })

        if not unit_of_measure:
            unit_of_measure = None

        if not can_be_integer(target_value):
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

        if period_start:
            period_start = arrow.get(period_start).to(settings.TIME_ZONE).datetime

        if period_end:
            period_end = arrow.get(period_end).to(settings.TIME_ZONE).datetime

        if period_start and period_end and period_end < period_start:
            return Response({
                'ok': False,
                'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!',
            })

        if period_start and not period_end:
            return Response({
                'ok': False,
                'msg': 'Thời gian kết thúc không được để trống!',
            })

        if not period_start and period_end:
            return Response({
                'ok': False,
                'msg': 'Thời gian bắt đầu không được để trống!',
            })

        if not period_start:
            period_start = None

        if not period_end:
            period_end = None

        try:
            p = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=p, removed=False)
            t = Tag.objects.get(id=tag_id)
            if dpm.department_member.user.id != t.user.department_member.user.id:
                return Response({
                    'ok': False,
                    'msg': 'Không tồn tại KPI này!',
                })

            if t.state == 'CO':
                return Response({
                    'ok': False,
                    'msg': 'KPI này đã hoàn thành nên không thể tạo Task!',
                })

            task = Task(
                user=dpm,
                task_name=task_name,
                task_description=task_description,
                period_start=period_start,
                period_end=period_end,
                unit_of_measure=unit_of_measure,
                target_value=target_value,
                progress=0,
                weight=weight,
                state='PR',
                tag=t,
            )
            task.save()
            return Response({
                'ok': True,
                'msg': 'Tạo Task thành công!',
            })
        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return Response({
                'ok': False,
                'msg': 'Không tồn tại nhân viên hoặc KPI!',
            })
    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def edit_my_task_api_view(request):
    """
    API chỉnh sửa task của tôi
    :param request:
    :return:
    """
    user_id = request.user.id
    tag_id = request.data.get('tag_id')
    task_id = request.data.get('task_id')
    edit_task = request.data.get('edit_task')
    task_name = request.data.get('task_name')
    task_description = request.data.get('task_description')
    period_start = request.data.get('period_start')
    period_end = request.data.get('period_end')
    unit_of_measure = request.data.get('unit_of_measure')
    result_value = request.data.get('result_value')
    weight = request.data.get('weight')
    task_state = request.data.get('task_state')

    if request.user.is_authenticated:
        if not task_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại Task!',
            })

        if not can_be_integer(task_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy Task của bạn!',
            })

        if not edit_task:
            return Response({
                'ok': False,
                'msg': 'Không xác định được yêu cầu chỉnh sửa task!',
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

        if edit_task == 'remove':
            try:
                p = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=p, removed=False)
                task = Task.objects.get(id=task_id, user=dpm, removed=False)

                task.removed = True

                task.save()

                if task.state == 'CO':
                    tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)
                    task_list = Task.objects.filter(tag=tag, removed=False)
                    count = 0

                    for item in task_list:
                        if item.state == 'CO':
                            count += int(item.result_value)

                    tag.finished = count
                    tag.save()

                return Response({
                    'ok': True,
                    'msg': 'Xóa Task thành công!',
                })

            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

        if edit_task == 'title':
            if not task_name:
                return Response({
                    'ok': False,
                    'msg': 'Tiêu đề không được để trống!',
                })

            if not task_description:
                task_description = None

            try:
                p = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=p, removed=False)
                task = Task.objects.get(id=task_id, user=dpm, removed=False)

                task.task_name = task_name
                task.task_description = task_description

                task.save()

                return Response({
                    'ok': True,
                    'msg': 'Cập nhật Task thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

        if edit_task == 'compact':
            if not result_value:
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu đã đạt không được để trống!',
                })

            if not can_be_integer(result_value):
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu phải nhập số!',
                })

            if not task_state:
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái task không được để trống!',
                })

            if task_state != 'Chưa Hoàn Thành' and task_state != 'Đang Thực Hiện' and task_state != 'Hoàn Thành':
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái task không hợp lệ!',
                })

            if task_state == 'Chưa Hoàn Thành':
                task_state = 'NF'

            if task_state == 'Đang Thực Hiện':
                task_state = 'PR'

            if task_state == 'Hoàn Thành':
                task_state = 'CO'

            try:
                p = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=p, removed=False)
                task = Task.objects.get(id=task_id, user=dpm, removed=False)

                if task.is_finished:
                    return Response({
                        'ok': False,
                        'msg': 'Task này đã hoàn thành nên không thể chỉnh sửa!',
                    })

                task.result_value = result_value
                task.state = task_state

                percent = float(result_value) / float(task.target_value) * 100.0
                percent = round(percent, 2)

                task.progress = percent

                if task_state == 'CO':
                    task.is_finished = True

                task.save()

                if task.state == 'CO':
                    tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)
                    task_list = Task.objects.filter(tag=tag, removed=False)
                    count = 0

                    for item in task_list:
                        if item.state == 'CO':
                            count += int(item.result_value)

                    tag.finished = count
                    tag.save()

                return Response({
                    'ok': True,
                    'msg': 'Cập nhật Task thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist, Tag.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

        if edit_task == 'total':
            if not result_value:
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu đã đạt không được để trống!',
                })

            if not unit_of_measure:
                unit_of_measure = None

            if not can_be_integer(result_value):
                return Response({
                    'ok': False,
                    'msg': 'Chỉ tiêu đã đạt phải nhập số!',
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

            if not task_state:
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái task không được để trống!',
                })

            if task_state != 'Chưa Hoàn Thành' and task_state != 'Đang Thực Hiện' and task_state != 'Hoàn Thành':
                return Response({
                    'ok': False,
                    'msg': 'Trạng thái task không hợp lệ!',
                })

            if task_state == 'Chưa Hoàn Thành':
                task_state = 'NF'

            if task_state == 'Đang Thực Hiện':
                task_state = 'PR'

            if task_state == 'Hoàn Thành':
                task_state = 'CO'

            if period_start:
                period_start = arrow.get(period_start).to(settings.TIME_ZONE).datetime

            if period_end:
                period_end = arrow.get(period_end).to(settings.TIME_ZONE).datetime

            if period_start and period_end and period_end < period_start:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian kết thúc không được trước thời gian bắt đầu!',
                })

            if period_start and not period_end:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian kết thúc không được để trống!',
                })

            if not period_start and period_end:
                return Response({
                    'ok': False,
                    'msg': 'Thời gian bắt đầu không được để trống!',
                })

            if not period_start:
                period_start = None

            if not period_end:
                period_end = None

            try:
                p = Profile.objects.get(user__id=user_id, removed=False)
                dpm = DepartmentMember.objects.get(department_member=p, removed=False)
                task = Task.objects.get(id=task_id, user=dpm, removed=False)

                if task.is_finished:
                    return Response({
                        'ok': False,
                        'msg': 'Task này đã hoàn thành nên không thể chỉnh sửa!',
                    })

                task.period_start = period_start
                task.period_end = period_end
                task.unit_of_measure = unit_of_measure
                task.result_value = result_value

                percent = float(result_value) / float(task.target_value) * 100.0
                percent = round(percent, 2)

                task.progress = percent
                task.weight = weight
                task.state = task_state

                if task_state == 'CO':
                    task.is_finished = True

                task.save()

                if task.state == 'CO':
                    tag = Tag.objects.get(id=tag_id, user=dpm, removed=False)
                    task_list = Task.objects.filter(tag=tag, removed=False)
                    count = 0

                    for item in task_list:
                        if item.state == 'CO':
                            count += int(item.result_value)

                    tag.finished = count
                    tag.save()

                return Response({
                    'ok': True,
                    'msg': 'Cập nhật Task thành công!',
                })
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist, Tag.DoesNotExist):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })
        return Response({
            'ok': False,
            'msg': 'Chỉnh sửa task thất bại!',
        })
    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def add_comment_for_my_task_api_view(request):
    """
    API thêm bình luận vào task của tôi
    :param request:
    :return:
    """
    user_id = request.user.id
    task_id = request.data.get('task_id')
    cmt_content = request.data.get('cmt_content')

    if request.user.is_authenticated:
        if not task_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại Task!',
            })

        if not can_be_integer(task_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy Task của bạn!',
            })

        if not cmt_content:
            return Response({
                'ok': False,
                'msg': 'Bạn chưa nhập gì cả!',
            })

        try:
            p = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=p, removed=False)
            task = Task.objects.get(id=task_id, user=dpm, removed=False)

            comment = Comment(
                task=task,
                user=p,
                content=cmt_content
            )
            comment.save()

            return Response({
                'ok': True,
                'msg': 'Gửi bình luận thành công!',
            })

        except(Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
            return Response({
                'ok': False,
                'msg': 'Lỗi dữ liệu!',
            })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def add_comment_for_member_task_api_view(request):
    """
    API thêm bình luận vào task của người khác
    :param request:
    :return:
    """
    user_id = request.data.get('user_id')
    task_id = request.data.get('task_id')
    cmt_content = request.data.get('cmt_content')

    if request.user.is_authenticated:
        if not task_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại Task!',
            })

        if not can_be_integer(task_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy Task của bạn!',
            })

        if not cmt_content:
            return Response({
                'ok': False,
                'msg': 'Bạn chưa nhập gì cả!',
            })

        try:
            my_profile = Profile.objects.get(user__id=request.user.id, removed=False)
            p = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=p, removed=False)
            task = Task.objects.get(id=task_id, user=dpm, removed=False)

            if my_profile.get_role() == 'Director' or my_profile.get_role() == 'Manager':
                comment = Comment(
                    task=task,
                    user=my_profile,
                    content=cmt_content
                )
                comment.save()

                return Response({
                    'ok': True,
                    'msg': 'Gửi bình luận thành công!',
                })
            else:
                return Response({
                    'ok': False,
                    'msg': 'Không đủ quyền để thao tác!',
                })

        except(Profile.DoesNotExist, DepartmentMember.DoesNotExist, Task.DoesNotExist):
            return Response({
                'ok': False,
                'msg': 'Lỗi dữ liệu!',
            })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })


@api_view(['POST'])
def edit_comment_for_my_task_api_view(request):
    """
    API chỉnh sửa hoặc xóa bình luận trong task của tôi
    :param request:
    :return:
    """
    comment_id = request.data.get('comment_id')
    cmt_content = request.data.get('cmt_content')
    cmt_request = request.data.get('cmt_request')

    if request.user.is_authenticated:
        if not comment_id:
            return Response({
                'ok': False,
                'msg': 'Không tồn tại bình luận!',
            })

        if not can_be_integer(comment_id):
            return Response({
                'ok': False,
                'msg': 'Không tìm thấy bình luận của bạn!',
            })

        if not cmt_request:
            return Response({
                'ok': False,
                'msg': 'Không xác định được yêu cầu của bạn!',
            })

        if cmt_request != 'edit' and cmt_request != 'remove':
            return Response({
                'ok': False,
                'msg': 'Yêu cầu không hợp lệ!',
            })

        if cmt_request == 'remove':
            try:
                comment = Comment.objects.get(id=comment_id, user=request.user.profile, removed=False)
                comment.removed = True
                comment.save()

                return Response({
                    'ok': True,
                    'msg': 'Xóa bình luận thành công!',
                })
            except (Comment.DoesNotExist,):
                return Response({
                    'ok': True,
                    'msg': 'Lỗi dữ liệu!',
                })

        if cmt_request == 'edit':
            if not cmt_content:
                return Response({
                    'ok': False,
                    'msg': 'Bạn chưa nhập gì cả!',
                })

            try:
                comment = Comment.objects.get(id=comment_id, user=request.user.profile, removed=False)
                comment.content = cmt_content

                comment.save()

                return Response({
                    'ok': True,
                    'msg': 'Cập nhật bình luận thành công!',
                })

            except(Comment.DoesNotExist,):
                return Response({
                    'ok': False,
                    'msg': 'Lỗi dữ liệu!',
                })

    return Response({
        'ok': False,
        'msg': 'Bạn chưa đăng nhập!',
    })
