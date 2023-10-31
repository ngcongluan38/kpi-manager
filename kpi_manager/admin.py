from django.contrib import admin

from . import models


@admin.register(models.Profile)
class Profile(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'birth_day', 'sex', 'id_number', 'address', 'removed')
    search_fields = ('full_name',)
    raw_id_fields = ('user',)
    list_filter = ('role', 'removed')
    list_editable = ('removed',)
    save_on_top = True


@admin.register(models.Department)
class Department(admin.ModelAdmin):
    list_display = ('department_name', 'department_desc', 'department_level', 'removed')
    list_filter = ('department_name',)
    list_editable = ('removed',)


@admin.register(models.DepartmentMember)
class DepartmentMember(admin.ModelAdmin):
    list_display = ('department_member', 'department', 'position', 'is_leader', 'removed')
    raw_id_fields = ('department_member',)
    search_fields = ('department_member__full_name',)
    list_filter = ('department', 'removed')
    list_editable = ('removed',)


@admin.register(models.Tag)
class Tag(admin.ModelAdmin):
    list_display = ['user', 'tag_name', 'quantity', 'finished', 'state', 'created_at', 'removed']
    search_fields = ('user__department_member__full_name',)
    raw_id_fields = ('user', 'created_by')
    list_filter = ('removed', 'state')
    list_editable = ('removed',)


@admin.register(models.Task)
class Task(admin.ModelAdmin):
    list_display = ('user', 'task_name', 'target_value', 'result_value', 'unit_of_measure', 'created_at', 'removed')
    search_fields = ('user__department_member__full_name',)
    raw_id_fields = ('user', 'tag')
    list_filter = ('removed', 'state')
    list_editable = ('removed',)


@admin.register(models.WorkTime)
class WorkTime(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_in_day', 'end_in_day', 'rest_time', 'time_total',
                    'created_at', 'updated_at', 'removed')
    search_fields = ('user__department_member__full_name',)
    raw_id_fields = ('user',)
    list_editable = ('removed',)


@admin.register(models.Comment)
class Comment(admin.ModelAdmin):
    list_display = ('user', 'task', 'content', 'created_at', 'updated_at', 'removed')
    search_fields = ('user__full_name',)
    raw_id_fields = ('user', 'task')
    list_editable = ('removed',)

