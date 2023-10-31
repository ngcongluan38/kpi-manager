import arrow
from django.conf import settings
from django.db.models import Sum
from datetime import datetime, date
import user_agents

from django.views.generic import TemplateView, ListView

from kpi_manager.models import Profile, DepartmentMember, Tag, WorkTime
from utils.common import can_be_integer

# Create your views here.


class MainNavMixin(object):
    nav = ''

    def get_context_data(self, **kwargs):
        context = super(MainNavMixin, self).get_context_data(**kwargs)
        context['nav'] = self.nav
        return context

    def is_desktop(self):
        user_agent = user_agents.parse(self.request.META.get('HTTP_USER_AGENT'))
        return user_agent.is_pc


class HomeIndexView(MainNavMixin, TemplateView):
    nav = 'home'

    def get_template_names(self):
        # if self.request.user.is_authenticated:
        #     if self.request.user.profile.force_mobile:
        #         return ['index.html']
        user_agent = user_agents.parse(self.request.META.get('HTTP_USER_AGENT'))
        if user_agent.is_pc:
            return ['desktop/home.html']
        return ['index.html']


class StatisticTagView(MainNavMixin, TemplateView):
    def get_profile(self):
        user_id = self.request.user.id
        profile = Profile.objects.get(user__id=user_id)
        return profile

    def get_department_member(self):
        try:
            user_id = self.request.user.id
            profile = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
            return dpm
        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
            pass

    def get_tag_info(self):
        try:
            user_id = self.request.user.id
            year_request = self.kwargs['year_request']
            month_request = self.kwargs['month_request']
            profile = Profile.objects.get(user__id=user_id, removed=False)
            dpm = DepartmentMember.objects.get(department_member=profile, removed=False)
            start = arrow.now(). \
                replace(month=int(month_request), year=int(year_request)). \
                to(settings.TIME_ZONE).floor('month').datetime
            end = arrow.now(). \
                replace(month=int(month_request), year=int(year_request)). \
                to(settings.TIME_ZONE).ceil('month').datetime
            wt = WorkTime.objects.filter(user=dpm,
                                         date__range=(start, end),
                                         removed=False).aggregate(totalTime=Sum('time_total'))['totalTime']
            tag = Tag.objects.filter(user=dpm,
                                     created_at__range=(start, end),
                                     removed=False)
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

            return {
                'total_time': round(wt, 2) if wt else 0,
                'total_tag': total,
                'count_finished': count_finished,
                'count_progress': count_progress,
                'count_un_finished': count_un_finished,
            }
        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return {}

    def get_queryset(self):
        user_id = self.request.user.id
        year_request = self.kwargs['year_request']
        month_request = self.kwargs['month_request']
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
                start = arrow.now(). \
                    replace(month=int(month_request), year=int(year_request)). \
                    to(settings.TIME_ZONE).floor('month').datetime
                end = arrow.now(). \
                    replace(month=int(month_request), year=int(year_request)). \
                    to(settings.TIME_ZONE).ceil('month').datetime

                profile = Profile.objects.get(user__id=user_id)
                dpm = DepartmentMember.objects.get(department_member=profile)
                tag = Tag.objects.filter(user=dpm,
                                         created_at__range=(start, end),
                                         removed=False).order_by('-updated_at')
                return tag
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return []
        else:
            return []

    def get_context_data(self, **kwargs):
        context = super(StatisticTagView, self).get_context_data(**kwargs)
        context['data_profile'] = self.get_profile()
        context['data_department_profile'] = self.get_department_member()
        context['data_tag'] = self.get_queryset()
        context['data_tag_info'] = self.get_tag_info()
        return context

    def get_template_names(self):
        # if self.request.user.is_authenticated:
        #     if self.request.user.profile.force_mobile:
        #         return ['index.html']
        user_agent = user_agents.parse(self.request.META.get('HTTP_USER_AGENT'))
        if user_agent.is_pc:
            return ['print/tag_statistic.html']
        return ['index.html']


class MemberStatisticTagView(MainNavMixin, TemplateView):
    def get_my_profile(self):
        user_id = self.request.user.id
        profile = Profile.objects.get(user__id=user_id)
        return profile

    def get_profile(self):
        profile_id = self.kwargs['profile_id']
        try:
            my_profile = Profile.objects.get(user__id=self.request.user.id, removed=False)
            profile = Profile.objects.get(id=profile_id, removed=False)
            if my_profile.get_role() == 'Director':
                return profile
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile)
                member = DepartmentMember.objects.get(department_member=profile)
                if int(me.department.id) == int(member.department.id):
                    return profile
                else:
                    return {}
            else:
                return {}
        except Profile.DoesNotExist:
            return {}

    def get_department_member(self):
        profile_id = self.kwargs['profile_id']
        try:
            my_profile = Profile.objects.get(user__id=self.request.user.id, removed=False)
            profile = Profile.objects.get(id=profile_id, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            if my_profile.get_role() == 'Director':
                return member
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                if int(me.department.id) == int(member.department.id):
                    return member
                else:
                    return {}
            else:
                return {}
        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist):
            return {}

    def get_tag_info(self):
        profile_id = self.kwargs['profile_id']
        year_request = self.kwargs['year_request']
        month_request = self.kwargs['month_request']
        try:
            start = arrow.now(). \
                replace(month=int(month_request), year=int(year_request)). \
                to(settings.TIME_ZONE).floor('month').datetime
            end = arrow.now(). \
                replace(month=int(month_request), year=int(year_request)). \
                to(settings.TIME_ZONE).ceil('month').datetime

            my_profile = Profile.objects.get(user__id=self.request.user.id, removed=False)
            profile = Profile.objects.get(id=profile_id, removed=False)
            member = DepartmentMember.objects.get(department_member=profile, removed=False)
            if my_profile.get_role() == 'Director':
                wt = WorkTime.objects.filter(user=member,
                                             date__range=(start, end),
                                             removed=False).aggregate(totalTime=Sum('time_total'))['totalTime']
                tag = Tag.objects.filter(user=member,
                                         created_at__range=(start, end),
                                         removed=False)
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

                return {
                    'total_time': round(wt, 2) if wt else 0,
                    'total_tag': total,
                    'count_finished': count_finished,
                    'count_progress': count_progress,
                    'count_un_finished': count_un_finished,
                }
            elif my_profile.get_role() == 'Manager':
                me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                if int(me.department.id) == int(member.department.id):
                    wt = WorkTime.objects.filter(user=member,
                                                 date__range=(start, end),
                                                 removed=False).aggregate(totalTime=Sum('time_total'))['totalTime']
                    tag = Tag.objects.filter(user=member,
                                             created_at__range=(start, end),
                                             removed=False)
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

                    return {
                        'total_time': round(wt, 2) if wt else 0,
                        'total_tag': total,
                        'count_finished': count_finished,
                        'count_progress': count_progress,
                        'count_un_finished': count_un_finished,
                    }
                else:
                    return {}
            else:
                return {}

        except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
            return {}

    def get_queryset(self):
        profile_id = self.kwargs['profile_id']
        year_request = self.kwargs['year_request']
        month_request = self.kwargs['month_request']
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
                start = arrow.now(). \
                    replace(month=int(month_request), year=int(year_request)). \
                    to(settings.TIME_ZONE).floor('month').datetime
                end = arrow.now(). \
                    replace(month=int(month_request), year=int(year_request)). \
                    to(settings.TIME_ZONE).ceil('month').datetime

                my_profile = Profile.objects.get(user__id=self.request.user.id)
                profile = Profile.objects.get(id=profile_id, removed=False)
                member = DepartmentMember.objects.get(department_member=profile)
                if my_profile.get_role() == 'Director':
                    tag = Tag.objects.filter(user=member,
                                             created_at__range=(start, end),
                                             removed=False).order_by('-updated_at')
                    return tag
                elif my_profile.get_role() == 'Manager':
                    me = DepartmentMember.objects.get(department_member=my_profile, removed=False)
                    if int(me.department.id) == int(member.department.id):
                        tag = Tag.objects.filter(user=member,
                                                 created_at__range=(start, end),
                                                 removed=False).order_by('-updated_at')
                        return tag
                    else:
                        return []
                else:
                    return []
            except (Profile.DoesNotExist, DepartmentMember.DoesNotExist, Tag.DoesNotExist):
                return []

        else:
            return []

    def get_context_data(self, **kwargs):
        context = super(MemberStatisticTagView, self).get_context_data(**kwargs)
        context['data_my_profile'] = self.get_my_profile()
        context['data_profile'] = self.get_profile()
        context['data_department_profile'] = self.get_department_member()
        context['data_tag'] = self.get_queryset()
        context['data_tag_info'] = self.get_tag_info()
        return context

    def get_template_names(self):
        # if self.request.user.is_authenticated:
        #     if self.request.user.profile.force_mobile:
        #         return ['index.html']
        user_agent = user_agents.parse(self.request.META.get('HTTP_USER_AGENT'))
        if user_agent.is_pc:
            return ['print/member_tag_statistic.html']
        return ['index.html']
