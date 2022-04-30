import random
import re
import ssl

from django.conf import settings
from django.shortcuts import render
from django_redis import get_redis_connection

from myapp_api.settings import constants

pc_geetest_id = "4884f212bac718ccf442611b59a9f344"
pc_geetest_key = "83233f4206f6d4e0e11b35f99c762ffc"
# Create your views here.
from myapp_api.libs.geetest import GeetestLib
from rest_framework.response import Response
from .utils import get_user_by_account
from rest_framework import status as http_status, serializers, status
from rest_framework.views import APIView
class CaptchaAPIView(APIView):
    """验证码视图类"""
    status = False
    user_id = 0
    def get(self,request):
        """获取验证码"""
        username = request.query_params.get("username")
        user = get_user_by_account(username)
        if user is None:
            return Response({"message":"对不起，用户不存在！"},status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        # todo 后面增加status和user_id保存到redis数据库
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self,request):
        """验证码的验证方法"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        if self.status:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status":"success"} if result else {"status":"fail"}
        return Response(result)

from rest_framework.generics import CreateAPIView
from .models import User
from .serializers import UserModelSerializer
class UserAPIView(CreateAPIView):
    """用户信息视图"""
    queryset = User.objects.all()
    serializer_class = UserModelSerializer

class MobileAPIView(APIView):
    def get(self, request, mobile):

        ret = get_user_by_account(mobile)
        if ret is not None:
            return Response({"message":"手机号已经被注册过！"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"ok"})

class SMSAPIView(APIView):
    def get(self,request):
        """短信发送"""
        template = request.query_params.get('template')
        mobile = request.query_params.get('mobile')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(template)
        if not template_id:
            return Response({"message":"短信模版错误"},status=status.HTTP_400_BAD_REQUEST)

        # 1. 判断手机号码是否在60秒内曾经发送过短信
        redis_conn = get_redis_connection("sms_code")
        ret = redis_conn.get("mobile_%s" % mobile)
        if ret is not None:
            # 避免绕过前段，使用接口去重复请求发短信
            return Response({"message":"对不起，60秒内已经发送过短信，请耐心等待"},status=status.HTTP_400_BAD_REQUEST)

        # 2. 生成短信验证码
        sms_code = "%d" % random.randint(100000, 999999)
        print(sms_code)

        # 3. 保存短信验证码到redis[使用事务把多条命令集中发送给redis]
        # 创建管道对象
        pipe = redis_conn.pipeline()
        # 开启事务【无法管理数据库的读取数据操作】
        pipe.multi()
        # 把事务中要完成的所有操作，写入到管道中
        pipe.setex("sms_%s" % mobile, constants.SMS_EXPIRE_TIME, sms_code)
        pipe.setex("mobile_%s" % mobile, constants.SMS_INTERVAL_TIME,"_")
        # 执行事务
        pipe.execute()

        # 4. 调用短信sdk，发送短信
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            from mycelery.sms.tasks import send_sms
            from mycelery.mail.tasks import send_mail
            # send_mail.delay()
            # response = send_sms.delay(mobile, template_id, [sms_code, ])

            # ccp = CCP()
            # ret = ccp.send_template_sms(mobile, [sms_code, constants.SMS_EXPIRE_TIME//60], constants.SMS_TEMPLATE_ID)
            # if not ret:
            #     log.error("用户注册短信发送失败！手机号：%s" % mobile)
            #     return Response({"message":"发送短信失败！"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response({"message":"发送短信失败！"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. 响应发送短信的结果
        return Response({"message":"发送短信成功！", 'code': sms_code}, status=status.HTTP_200_OK)