from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler


class CustomJWTSerializer(JSONWebTokenSerializer):

    # username_field = 'username_or_email'

    def validate(self, attrs):

        password = attrs.get("password")
        user_obj = User.objects.filter(username=attrs.get("username")).first()
        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = _('User account is disabled.')
                        raise serializers.ValidationError(msg)

                    payload = jwt_payload_handler(user)

                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
                else:
                    msg = _('Unable to log in with provided credentials.')
                    raise serializers.ValidationError(msg)

            else:
                msg = _('Must include "{username_field}" and "password".')
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = _('Account with this email/username does not exists')
            raise serializers.ValidationError(msg)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
