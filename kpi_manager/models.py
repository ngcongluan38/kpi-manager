import arrow
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
# import django.utils.timezone

from simplemde.fields import SimpleMDEField
from easy_thumbnails.fields import ThumbnailerImageField

from utils.common import generate_sha1


def upload_avatar(instance, filename):
    extension = filename.split('.')[-1].lower()
    if extension not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
        extension = 'jpg'
    salt, h = generate_sha1(instance.id)
    return 'profile/{0}.{1}'.format(h[:10], extension)


SEX_CHOICES = (
    ('M', 'Nam'),
    ('F', 'Nữ'),
)

PERMISSION_CHOICE = (
    ('DR', 'Director'),
    ('MG', 'Manager'),
    ('EM', 'Employee'),
)

STATE_TAG_CHOICE = (
    ('NF', 'Chưa Hoàn Thành'),
    ('PR', 'Đang Thực Hiện'),
    ('CO', 'Hoàn Thành'),
)

STATE_TASK_CHOICE = (
    ('NF', 'Chưa Hoàn Thành'),
    ('PR', 'Đang Thực Hiện'),
    ('CO', 'Hoàn Thành'),
)


class Profile(models.Model):
    # HỒ SƠ: TÀI KHOẢN, HỌ TÊN, NGÀY SINH, GIỚI TÍNH, CMND, ĐỊA CHỈ, ẢNH ĐẠI DIỆN, ROLE.
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True)
    birth_day = models.DateField(null=True, blank=True)
    id_number = models.CharField('CC/PP/CMND', max_length=200, null=True, blank=True)
    address = models.TextField('Địa Chỉ', max_length=2000, null=True, blank=True)

    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)
    avatar = ThumbnailerImageField(blank=True, upload_to=upload_avatar, resize_source={
        'size': (320, 320),
        'autocrop': True,
        'crop': 'smart'
    })
    role = models.CharField(max_length=2, choices=PERMISSION_CHOICE, blank=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        elif self.sex == 'F':
            return settings.PERSON_DEFAULT['female']
        return settings.PERSON_DEFAULT['male']

    def get_is_director(self):
        return True if self.role == 'DR' else False

    def get_is_manager(self):
        return True if self.role == 'MG' else False

    def get_is_employee(self):
        return True if self.role == 'EM' else False

    def get_role(self):
        return next(y for x, y in PERMISSION_CHOICE if self.role == x)

    def get_sex(self):
        return next(y for x, y in SEX_CHOICES if self.sex == x)

    def get_birth_day(self):
        return arrow.get(self.birth_day).replace(tzinfo=settings.TIME_ZONE).datetime


class Department(models.Model):
    # PHÒNG BAN: TÊN PHÒNG BAN, CẤP BẬC CỦA PHÒNG BAN, MÔ TẢ PHÒNG BAN, NGƯỜI ĐỨNG ĐẦU, CHỨC VỤ
    department_name = models.CharField(max_length=100, unique=True)
    department_level = models.IntegerField(default=0)
    department_desc = SimpleMDEField(null=True, blank=True)
    # department_leader = models.OneToOneField(Profile, related_name='+', null=True)
    # leader_title = models.CharField(max_length=225, default='Trưởng Phòng')
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.department_name


class DepartmentMember(models.Model):
    # THÀNH VIÊN PHÒNG BAN: THÀNH VIÊN (), PHÒNG BAN (FOREIGNKEY), CHỨC VỤ, LÀ QUẢN LÝ
    # 3 ROLE CHÍNH: DIRECTOR, MANAGER, EMPLOYEE
    department_member = models.OneToOneField(Profile, related_name='+', null=True, unique=True,
                                             verbose_name='Thành Viên')
    department = models.ForeignKey(Department, related_name='+', null=True, blank=True, on_delete=models.CASCADE,
                                   verbose_name='Phòng Ban')
    position = models.CharField(max_length=225, default='Nhân Viên', null=True, blank=True, verbose_name='Chức Vụ')
    is_leader = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.department_member.full_name


class Tag(models.Model):
    user = models.ForeignKey(DepartmentMember, related_name='+', null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name='Nhân Viên')
    tag_name = models.TextField(max_length=500, null=True, blank=True, verbose_name='Công Việc')
    tag_description = SimpleMDEField(null=True, blank=True, verbose_name='Mô Tả')
    period_start = models.DateTimeField(null=True, blank=True, verbose_name='Thời Gian Bắt Đầu')
    period_end = models.DateTimeField(null=True, blank=True, verbose_name='Thời Gian Kết Thúc')
    weight = models.IntegerField(default=0, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    finished = models.IntegerField(default=0, null=True, blank=True)
    progress = models.FloatField(default=0, null=True, blank=True)
    state = models.CharField(max_length=2, choices=STATE_TAG_CHOICE, null=True, blank=True, verbose_name='Trạng Thái')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(Profile, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.tag_name

    def get_state(self):
        return next(y for x, y in STATE_TAG_CHOICE if self.state == x)

    class Meta:
        ordering = ('-created_at',)


class Task(models.Model):
    user = models.ForeignKey(DepartmentMember, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    task_name = models.TextField(max_length=500, null=True, blank=True)
    task_description = SimpleMDEField(null=True, blank=True)
    period_start = models.DateTimeField(null=True, blank=True, verbose_name='Thời Gian Bắt Đầu')
    period_end = models.DateTimeField(null=True, blank=True, verbose_name='Thời Gian Kết Thúc')
    unit_of_measure = models.CharField(max_length=100, null=True, blank=True)
    target_value = models.IntegerField(default=0, null=True, blank=True)
    result_value = models.IntegerField(default=0, null=True, blank=True)
    progress = models.FloatField(default=0, null=True, blank=True)
    weight = models.IntegerField(default=0, null=True, blank=True)
    tag = models.ForeignKey(Tag, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    state = models.CharField(max_length=2, choices=STATE_TASK_CHOICE, null=True, blank=True, verbose_name='Trạng Thái')
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name

    def get_state(self):
        return next(y for x, y in STATE_TASK_CHOICE if self.state == x)

    class Meta:
        ordering = ('-created_at',)


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='+', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name


class WorkTime(models.Model):
    user = models.ForeignKey(DepartmentMember, related_name='+', null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    start_in_day = models.TimeField(blank=True, null=True)
    end_in_day = models.TimeField(blank=True, null=True)
    rest_time = models.FloatField(blank=True, null=True)
    time_total = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.department_member.full_name

    class Meta:
        ordering = ('-date', '-created_at')


class KpiManagerPermission(models.Model):
    class Meta:
        managed = False # No database table creation or deletion operations will be performed for this model.

        permissions = (
            ('director', 'Full permissions'),
            ('manager', 'Permissions for manage of system'),
            ('employee', 'Permission for employee of system'),
        )

