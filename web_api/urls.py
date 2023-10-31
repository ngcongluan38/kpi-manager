from django.conf.urls import url, include
from web_api.views import general_api, department, tag, task, work_time

from . import views

urlpatterns = [
    url(r'^api-info/', views.index_api_view),
    url(r'^web-api/', include([
        # GET: Thông tin hồ sơ
        url(r'^current-profile/get/$', general_api.get_user_api_view),

        # GET: Thông tin cá nhân của tôi
        url(r'^profile/info/$', department.get_my_profile_info_in_department,
            name='profile_info'),

        # GET: Thông tin cá nhân trực thuộc phòng ban
        url(r'^profile/info/specific/$', department.get_profile_info_specific_in_department,
            name='profile_info_specific'),  # Xong - đã phân quyền

        # GET: Thông tin cá nhân trực thuộc phòng ban
        url(r'^profile/list/no-pagination/$', department.get_profile_list_no_pagination_api_view,
            name='np_profile_list'),  # Xong - đã phân quyền

        # POST: Chỉnh sửa hồ sơ
        url(r'^profile/update/$', general_api.update_profile),

        # GET: Danh sách phòng ban
        url(r'^department/list/$', department.GetDepartmentListView.as_view(),
            name='department_list'),  # Xong - đã phân quyền

        # GET: Thông tin cá nhân trực thuộc phòng ban
        url(r'^department/list/no-pagination/$', department.get_department_list_no_pagination_api_view,
            name='np_department_list'),  # Xong - đã phân quyền

        # GET: Danh sách nhân viên trong một phòng ban
        url(r'^members/list/$', department.GetMemberInDepartmentListView.as_view(),
            name='member_list'),  # Xong - đã phân quyền

        # GET: Danh sách KPI của tất cả nhân viên
        url(r'^tag/list/$', tag.GetTagListView.as_view(),
            name='tag_list'),  # Xong - đã phân quyền

        # GET: Danh sách tất cả KPI của một nhân viên
        url(r'^tag/member/$', tag.GetAllTagOfMemberView.as_view(),
            name='tag_member'),  # Xong - đã phân quyền

        # GET: Danh sách tất cả KPI của tôi
        url(r'^my-tag/list/$', tag.GetMyTagView.as_view(),
            name='my_tag'),  # Xong

        # GET: Đếm tổng số KPI của tôi
        url(r'^my-tag/list/statistics/$', tag.get_my_tag_statistics_api_view,
            name='my_tag_statistics'),  # Xong

        # GET: Đếm tổng số KPI của một nhân viên
        url(r'^tag/member/list/statistics/$', tag.get_member_tag_statistics_api_view,
            name='tag_member_statistics'),  # Xong

        # GET: Đếm tổng số KPI của tất cả nhân viên
        url(r'^tag/list/statistics/$', tag.get_tag_statistics_api_view,
            name='tag_statistics'),  # Xong

        # GET: Một KPI của một nhân viên
        url(r'^tag/member/detail/$', tag.get_one_tag_of_member_detail_api_view,
            name='tag_member_detail'),  # Xong

        # POST: Tạo mới một KPI cho một nhân viên
        url(r'^new-tag/add/$', tag.add_new_tag_api_view,
            name='tag_add'),  # Xong - đã phân quyền

        # POST: Chỉnh sửa một KPI của một nhân viên
        url(r'^tag/member/edit/$', tag.edit_tag_member_api_view,
            name='tag_edit'),  # Xong - đã phân quyền

        # GET: Một KPI của tôi
        url(r'^my-tag/detail/$', tag.get_one_tag_detail_of_me_api_view,
            name='my_tag_detail'),  # Xong

        # GET: DS KPI của tôi dùng để tạo task
        url(r'^my-tag/list/no-pagination/$', tag.get_tag_list_of_me_no_pagination_api_view,
            name='np_my_tag'),  # Xong

        # POST: Chỉnh sửa một task của tôi
        url(r'^my-tag/edit/$', tag.edit_my_tag_api_view,
            name='my_tag_edit'),  # Xong

        # POST: Tính toán kết quả của Task và cập nhật vào Tag
        url(r'^my-tag/computation/$', tag.my_tag_computation_api_view,
            name='my_tag_computation'),  # Xong

        # GET: Danh sách tất cả Task của một KPI
        url(r'^task/list/$', task.GetTaskListView.as_view(),
            name='task_list'),  # Xong

        # GET: Danh sách tất cả Task của một KPI của tôi
        url(r'^my-task/list/$', task.GetMyTaskListView.as_view(),
            name='my_task_list'),  # Xong

        # GET: Một Task của một KPI
        url(r'^task/member/detail/$', task.get_one_task_of_member_detail_api_view,
            name='task_member_detail'),

        # POST: Thêm một Task mới của tôi
        url(r'^new-task/add/$', task.add_new_task_api_view,
            name='task_add'),  # Xong

        # POST: Chỉnh sửa một Task của tôi
        url(r'^my-task/edit/$', task.edit_my_task_api_view,
            name='my_task_edit'),  # Xong

        # GET: Một Task của một KPI của tôi
        url(r'^my-task/detail/$', task.get_one_task_detail_of_me_api_view,
            name='my_task_detail'),

        # GET: Danh sách tất cả Comment của một Task
        url(r'^task/comment/list/$', task.GetCommentOfTaskView.as_view(),
            name='task_comment_list'),

        # GET: Danh sách tất cả Comment của một Task của tôi
        url(r'^my-task/comment/list/$', task.GetCommentOfMyTaskView.as_view(),
            name='my_task_comment_list'),

        # POST: Tạo một comment mới trong Task của tôi
        url(r'^my-task/comment/add/$', task.add_comment_for_my_task_api_view,
            name='my_task_comment_add'),

        # POST: Tạo một comment mới trong Task của người khác
        url(r'^task/comment/add/$', task.add_comment_for_member_task_api_view,
            name='task_comment_add'),

        # POST: Chỉnh sửa hoặc xóa một comment trong Task của tôi
        url(r'^my-task/comment/edit/$', task.edit_comment_for_my_task_api_view,
            name='my_task_comment_add'),

        # GET: Giờ làm việc của một nhân viên
        url(r'^work-time/member/list/$', work_time.GetWordTimeMemberListView.as_view(),
            name='work_time_member_list'),

        # GET: Giờ làm việc của tôi
        url(r'^my-work-time/list/$', work_time.GetWordTimeListView.as_view(),
            name='my_work_time_list'),

        # POST: Thêm giờ làm việc mới của tôi
        url(r'^my-work-time/add/$', work_time.add_my_work_time_api_view,
            name='my_work_time_add'),

        # POST: Chỉnh sửa hoặc xóa giờ làm việc của tôi
        url(r'^my-work-time/edit/$', work_time.edit_my_work_time_api_view,
            name='my_work_time_edit'),

        # GET: Đếm tổng số giờ làm việc của một nhân viên trong tháng này
        url(r'^work-time/member/statistic/$', work_time.work_time_member_statistic_api_view,
            name='work_time_member_statistic'),

        # GET: Đếm tổng số giờ làm việc của tôi trong tháng này
        url(r'^my-work-time/statistic/$', work_time.my_work_time_statistic_api_view,
            name='my_work_time_statistic'),

        # POST: Đổi ảnh đại diện
        url(r'^avatar/upload/$', general_api.upload_avatar_api_view,
            name='avatar_upload'),
    ])),
]
