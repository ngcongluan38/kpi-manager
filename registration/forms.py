from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from unidecode import unidecode


class DesktopCrispyMixin(object):
    def __init__(self, *args, **kwargs):
        super(DesktopCrispyMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'bootstrap4'
        self.helper.form_tag = False


class MobileCrispyMixin(object):
    def __init__(self, *args, **kwargs):
        super(MobileCrispyMixin, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = 'mobile_crispy'
        self.helper.form_tag = False


class DesktopLoginForm(DesktopCrispyMixin, AuthenticationForm):
    username = forms.CharField(required=True, label='Username', min_length=3, max_length=50,
                               help_text='Tên đăng nhập có phân biệt HOA-thường.',
                               widget=forms.TextInput(attrs={'autocapitalize': 'none', 'autofocus': True}))
    password = forms.CharField(max_length=30, required=True, label='Mật Khẩu',
                               help_text='Cẩn thận: mật khẩu có thể bị dính tiếng Việt bật bộ gõ.',
                               widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(DesktopLoginForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.helper.layout = Layout('username', 'password')


class MobileLoginForm(MobileCrispyMixin, AuthenticationForm):
    username = forms.CharField(required=True, label='Username', min_length=3, max_length=50,
                               help_text='Tên đăng nhập có phân biệt HOA-thường.',
                               widget=forms.TextInput(attrs={'autocapitalize': 'none', 'autofocus': ''}))
    password = forms.CharField(max_length=30, required=True, label='Mật Khẩu',
                               help_text='Cẩn thận: mật khẩu có thể bị dính tiếng Việt bật bộ gõ.',
                               widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(MobileLoginForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
        self.helper.layout = Layout('username', 'password')
