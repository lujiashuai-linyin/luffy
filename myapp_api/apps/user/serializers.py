import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import User
from .utils import get_user_by_account


class UserModelSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text='短信验证码')
    token = serializers.CharField(max_length=1024, read_only=True, help_text='token认证字符串')
    re_password = serializers.CharField(max_length=32, write_only=True, required=True, help_text='确认密码')
    class Meta:
        model = User
        fields = ["id","username", "mobile","password", "re_password", "sms_code","token"]
        extra_kwargs = {
            "id":{
                "read_only":True,
            },
            "username":{
                "read_only":True,
            },
            "password":{
                "write_only":True,
            },
            "mobile":{
                "write_only":True,
            }
        }
    def validate(self, attrs):
        mobile = attrs.get("mobile")
        sms_code = attrs.get("sms_code")
        password = attrs.get("password")
        re_password = attrs.get('re_password')
        # 验证手机号码的格式
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            raise serializers.ValidationError("对不起，手机号格式有误！")

        # 验证码手机号是否已经被注册过了
        ret = get_user_by_account(mobile)
        if ret is not None:
            raise serializers.ValidationError("对不起，手机号已经被注册过！")

        # 验证两次密码是否输入一致
        if password != re_password:
            raise serializers.ValidationError("两次密码输入不一致，请重新输入")
        # 验证短信验证码是否正确
        redis_conn = get_redis_connection("sms_code")

        real_sms_code = redis_conn.get("sms_%s" % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError("本次验证码已失效，请重新发送！")
        # 本次验证以后，直接删除当前本次验证码，防止出现恶意暴力破解
        redis_conn.delete("sms_%s" % mobile)

        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError("对不起，短信验证码错误!")

        return attrs
    def create(self, validated_data):
        """用户信息"""
        # 移除掉不需要的数据
        validated_data.pop("sms_code")
        validated_data.pop('re_password')
        # 对密码进行加密
        raw_password =  validated_data.get("password")
        hash_password = make_password(raw_password)
        # 对用户名设置一个默认值
        username = validated_data.get("mobile")
        # 调用序列化器提供的create方法
        user = User.objects.create(
            mobile=username,
            username=username,
            password=hash_password,
        )

        # 使用restframework_jwt模块提供手动生成token的方法生成登录状态


        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)

        return user
