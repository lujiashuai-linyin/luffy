import ssl

from mycelery.main import app
import logging

log = logging.getLogger("django")

from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError
from django.conf import settings
@app.task(name="send_sms")
def send_sms(phone_num, template_id, template_param_list):
    """
    单条发送短信
    :param phone_num: 手机号
    :param template_id: 腾讯云短信模板ID
    :param template_param_list: 短信模板所需参数列表，例如:【验证码：{1}，描述：{2}】，则传递参数 [888,666]按顺序去格式化模板
    :return:
    """
    ssl._create_default_https_context = ssl._create_unverified_context
    appid = settings.TENCENT_SMS_APP_ID  # 自己应用ID
    appkey = settings.TENCENT_SMS_APP_KEY  # 自己应用Key
    sms_sign = settings.TENCENT_SMS_SIGN  # 自己腾讯云创建签名时填写的签名内容（使用公众号的话这个值一般是公众号全称或简称）
    sender = SmsSingleSender(appid, appkey)
    try:
        response = sender.send_with_param(86, phone_num, template_id, template_param_list, sign=sms_sign)
    except HTTPError as e:
        print(e)
        log.error(e)
        response = {'result': 1000, 'errmsg': "网络异常发送失败"}
    return response