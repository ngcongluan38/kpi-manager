import arrow
import markdown2
from django.conf import settings
from datetime import datetime, date
# from django.db import models
from django.db.models import Sum, Count

from rest_framework import serializers

from kpi_manager.models import Department, DepartmentMember, Tag, Task, WorkTime, Comment
from web_api.utils import build_absolute_url


class GetDepartmentListSerializer(serializers.ModelSerializer):
    """
    Get department list
    """
    departmentId = serializers.IntegerField(source='pk', read_only=True)
    departmentName = serializers.CharField(source='department_name')
    departmentLevel = serializers.IntegerField(source='department_level')
    departmentDesc = serializers.CharField(source='department_desc')
    departmentLeader = serializers.SerializerMethodField()
    departmentLeaderTitle = serializers.SerializerMethodField()
    avatarUrl = serializers.SerializerMethodField()
    totalMember = serializers.SerializerMethodField()

    @staticmethod
    def get_departmentLeader(obj):
        member = DepartmentMember.objects.get(department=obj, is_leader=True, removed=False)
        return member.department_member.full_name

    @staticmethod
    def get_departmentLeaderTitle(obj):
        member = DepartmentMember.objects.get(department=obj, is_leader=True, removed=False)
        return member.position

    @staticmethod
    def get_avatarUrl(obj):
        member = DepartmentMember.objects.get(department=obj, is_leader=True, removed=False)
        return build_absolute_url(member.department_member.get_avatar_url()) if member.department_member else None

    @staticmethod
    def get_totalMember(obj):
        member = DepartmentMember.objects.filter(department=obj, removed=False)
        return len(member)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    class Meta:
        model = Department
        fields = ('departmentId', 'departmentName', 'departmentDesc', 'departmentLevel',
                  'departmentLeader', 'departmentLeaderTitle', 'avatarUrl', 'totalMember')


class GetMemberInDepartmentSerializer(serializers.ModelSerializer):
    """
    Get profile member in department
    """
    userId = serializers.IntegerField(source='department_member.user.id', read_only=True)
    fullName = serializers.CharField(source='department_member')
    sex = serializers.SerializerMethodField()
    birthDay = serializers.SerializerMethodField()
    idNumber = serializers.CharField(source='department_member.id_number')
    address = serializers.CharField(source='department_member.address')
    avatarUrl = serializers.SerializerMethodField()
    position = serializers.CharField()
    isLeader = serializers.BooleanField(source='is_leader')
    department = serializers.CharField()
    totalTime = serializers.SerializerMethodField()
    totalTag = serializers.SerializerMethodField()
    totalTagFinished = serializers.SerializerMethodField()

    class Meta:
        model = DepartmentMember
        fields = ('userId', 'fullName', 'sex', 'birthDay', 'idNumber', 'address', 'avatarUrl', 'position',
                  'isLeader', 'department', 'totalTime', 'totalTag', 'totalTagFinished')

    @staticmethod
    def get_birthDay(obj):
        return arrow.get(obj.department_member.birth_day).replace(tzinfo=settings.TIME_ZONE).datetime

    @staticmethod
    def get_avatarUrl(obj):
        return build_absolute_url(obj.department_member.get_avatar_url()) if obj.department_member else None

    @staticmethod
    def get_totalTime(obj):
        start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
        end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
        wt = WorkTime.objects.filter(user=obj, removed=False,
                                     date__range=(start, end)).aggregate(value=Sum('time_total'))['value']
        return wt

    @staticmethod
    def get_totalTag(obj):
        start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
        end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
        t = Tag.objects.filter(user=obj, removed=False,
                               created_at__range=(start, end)).count()
        return t

    @staticmethod
    def get_totalTagFinished(obj):
        start = arrow.now().to(settings.TIME_ZONE).floor('month').datetime
        end = arrow.now().to(settings.TIME_ZONE).ceil('month').datetime
        tf = Tag.objects.filter(user=obj, removed=False, state='CO',
                                created_at__range=(start, end)).count()
        return tf

    @staticmethod
    def get_sex(obj):
        if obj.department_member.sex == 'M':
            return 'Nam'
        elif obj.department_member.sex == 'F':
            return 'Nữ'
        else:
            return ''

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GetTagOfMemberSerializer(serializers.ModelSerializer):
    """
    Get all tag of member in department
    """
    userId = serializers.IntegerField(source='user.department_member.user.id', read_only=True)
    profileId = serializers.IntegerField(source='user.department_member.id', read_only=True)
    fullName = serializers.CharField(source='user.department_member')
    avatarUrl = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    position = serializers.CharField(source='user.position')
    department = serializers.CharField(source='user.department')
    tagId = serializers.IntegerField(source='pk', read_only=True)
    tagName = serializers.CharField(source='tag_name')
    tagDescription = serializers.CharField(source='tag_description')
    periodStart = serializers.DateTimeField(source='period_start')
    periodEnd = serializers.DateTimeField(source='period_end')
    weight = serializers.IntegerField()
    quantity = serializers.IntegerField()
    finished = serializers.IntegerField()
    progress = serializers.FloatField()
    tagState = serializers.SerializerMethodField()
    createdBy = serializers.CharField(source='created_by')
    createdAvatarUrl = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Tag
        fields = ('userId', 'profileId', 'fullName', 'avatarUrl', 'sex', 'position', 'department', 'tagId', 'tagName',
                  'tagDescription', 'periodStart', 'periodEnd', 'weight', 'quantity', 'finished', 'progress',
                  'tagState', 'createdBy', 'createdAvatarUrl', 'createdAt', 'updatedAt')

    @staticmethod
    def get_sex(obj):
        if obj.user.department_member.sex == 'M':
            return 'Nam'
        elif obj.user.department_member.sex == 'F':
            return 'Nữ'
        else:
            return ''

    @staticmethod
    def get_avatarUrl(obj):
        return build_absolute_url(obj.user.department_member.get_avatar_url()) if obj.user.department_member else None

    @staticmethod
    def get_createdAvatarUrl(obj):
        return build_absolute_url(obj.created_by.get_avatar_url()) if obj.created_by else None

    @staticmethod
    def get_tagState(obj):
        if obj.state == 'NF':
            return 'Chưa Hoàn Thành'
        elif obj.state == 'PR':
            return 'Đang Thực Hiện'
        elif obj.state == 'CO':
            return 'Hoàn Thành'
        else:
            return ''

    # @staticmethod
    # def get_tagDescription(obj):
    #     if obj.tag_description:
    #         desc = markdown2.markdown(obj.tag_description, extras=["tables", "fenced-code-blocks", 'code-friendly'])
    #         return desc
    #     return obj.tag_description

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GetTaskOfMemberDependOnTagSerializer(serializers.ModelSerializer):
    """
    Get task of member depend on Tag
    """
    userId = serializers.IntegerField(source='user.department_member.user.id', read_only=True)
    fullName = serializers.CharField(source='user.department_member')
    avatarUrl = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    position = serializers.CharField(source='user.position')
    department = serializers.CharField(source='user.department')
    tagId = serializers.IntegerField(source='tag.id', read_only=True)
    taskId = serializers.IntegerField(source='pk', read_only=True)
    taskName = serializers.CharField(source='task_name')
    # taskDescription = serializers.SerializerMethodField()
    taskDescription = serializers.CharField(source='task_description')
    periodStart = serializers.DateTimeField(source='period_start')
    periodEnd = serializers.DateTimeField(source='period_end')
    unitOfMeasure = serializers.CharField(source='unit_of_measure')
    targetValue = serializers.IntegerField(source='target_value')
    resultValue = serializers.IntegerField(source='result_value')
    progress = serializers.FloatField()
    weight = serializers.IntegerField()
    taskState = serializers.SerializerMethodField()
    isFinished = serializers.BooleanField(source='is_finished')
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Task
        fields = ('userId', 'fullName', 'avatarUrl', 'sex', 'position', 'department', 'tagId', 'taskId',
                  'taskName', 'taskDescription', 'periodStart', 'periodEnd', 'unitOfMeasure', 'targetValue',
                  'resultValue', 'progress', 'weight', 'taskState', 'isFinished', 'createdAt', 'updatedAt')

    @staticmethod
    def get_avatarUrl(obj):
        return build_absolute_url(obj.user.department_member.get_avatar_url()) if obj.user.department_member else None

    @staticmethod
    def get_sex(obj):
        if obj.user.department_member.sex == 'M':
            return 'Nam'
        elif obj.user.department_member.sex == 'F':
            return 'Nữ'
        else:
            return ''

    # @staticmethod
    # def get_taskDescription(obj):
    #     if obj.task_description:
    #         desc = markdown2.markdown(obj.task_description, extras=["tables", "fenced-code-blocks", 'code-friendly'])
    #         return desc
    #     return obj.task_description

    @staticmethod
    def get_taskState(obj):
        if obj.state == 'NF':
            return 'Chưa Hoàn Thành'
        elif obj.state == 'PR':
            return 'Đang Thực Hiện'
        elif obj.state == 'CO':
            return 'Hoàn Thành'
        else:
            return ''

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GetWorkTimeOfMemberSerializer(serializers.ModelSerializer):
    workTimeId = serializers.IntegerField(source='pk', read_only=True)
    userId = serializers.IntegerField(source='user.department_member.user.id', read_only=True)
    fullName = serializers.CharField(source='user.department_member')
    sex = serializers.SerializerMethodField()
    avatarUrl = serializers.SerializerMethodField()
    position = serializers.CharField(source='user.position')
    date = serializers.DateField(format='%d/%m/%Y')
    startInDay = serializers.TimeField(source='start_in_day', format='%H:%M')
    endInDay = serializers.TimeField(source='end_in_day', format='%H:%M')
    restTime = serializers.FloatField(source='rest_time')
    totalTime = serializers.FloatField(source='time_total')
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = WorkTime
        fields = ('workTimeId', 'userId', 'fullName', 'sex', 'avatarUrl', 'position', 'date', 'startInDay', 'endInDay',
                  'restTime', 'totalTime', 'createdAt', 'updatedAt')

    @staticmethod
    def get_avatarUrl(obj):
        return build_absolute_url(obj.user.department_member.get_avatar_url()) if obj.user.department_member else None

    @staticmethod
    def get_sex(obj):
        if obj.user.department_member.sex == 'M':
            return 'Nam'
        elif obj.user.department_member.sex == 'F':
            return 'Nữ'
        else:
            return ''

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class GetCommentOfTaskSerializer(serializers.ModelSerializer):
    commentId = serializers.IntegerField(source='pk', read_only=True)
    fullName = serializers.CharField(source='user')
    avatarUrl = serializers.SerializerMethodField()
    isLeader = serializers.SerializerMethodField()
    commentContent = serializers.CharField(source='content')
    createdAt = serializers.DateTimeField(source='created_at')
    updateAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        model = Comment
        fields = ('commentId', 'fullName', 'avatarUrl', 'isLeader', 'commentContent', 'createdAt', 'updateAt')

    @staticmethod
    def get_avatarUrl(obj):
        return build_absolute_url(obj.user.get_avatar_url()) if obj.user else None

    @staticmethod
    def get_isLeader(obj):
        try:
            dpm = DepartmentMember.objects.get(department_member=obj.user)
            leader = dpm.is_leader
            return leader
        except DepartmentMember.DoesNotExist:
            return False

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


