from rest_framework import serializers
from .models import Order,OrderDetail
from datetime import datetime
import random
from django_redis import get_redis_connection
from course.models import Course,CourseExpire
from django.db import transaction

import logging
log = logging.getLogger("django")

class OrderModelSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    # coupon = CouponSerializer()
    class Meta:
        model = Order
        fields = [
            "id","order_title","total_price",
            "real_price","order_number","order_status",
            "pay_type","use_credit","credit",
            "use_coupon","coupon","pay_time",
        ]
        extra_kwargs = {
            "id":{ "read_only":True,},
            "order_title":{"read_only":True,},
            "total_price":{"read_only":True,},
            "real_price":{"read_only":True,},
            "order_number":{"read_only":True,},
            "order_status":{"read_only":True,},
            "pay_time":{"read_only":True,},
            "pay_type":{"required":True,},
            "use_credit":{"required":True,},
            "credit":{"required":True,"min_value":0},
            "use_coupon":{"required":True,},
        }

    def create(self, validated_data):
        """
        生成订单
        :param validated_data:
        :return:
        """
        # 接受客户端提交的数据
        pay_type = validated_data.get("pay_type")
        use_credit = validated_data.get("use_credit")
        credit = validated_data.get("credit")
        use_coupon = validated_data.get("use_coupon")
        coupon = validated_data.get("coupon",None)

        # 生成必要参数
        user_id = 1 # todo 回头我们学习怎么在序列化器中获取视图中的数据
        order_title = "路飞学城课程购买"
        order_number = datetime.now().strftime("%Y%m%d%H%M%S")+("%06d" % user_id)+("%04d" % random.randint(0,9999))
        order_status = 0


        with transaction.atomic():
            # 设置事务回滚的位置
            save_point = transaction.savepoint()
            # 生成订单记录
            order = super().create({
                "order_title":order_title,
                "total_price":0,
                "real_price":0,
                "order_number":order_number,
                "order_status":order_status,
                "pay_type":pay_type,
                "use_credit":use_credit,
                "credit": credit if use_credit else 0,
                "use_coupon":use_coupon,
                "coupon": coupon,
                "order_desc": "",
                "user_id": user_id,
            })

            try:
                # 连接redis
                redis = get_redis_connection("cart")

                # 从购物车中一区订单信息
                course_set = redis.smembers("selected_%s" % user_id )
                cart_list = redis.hgetall("cart_%s" % user_id )
            except:
                log.error("redis存储出错！")
                # 回滚事务！！注意，这里不是让程序重新执行，而是让已经在事务中执行mysql局域造成的影响消除掉！
                transaction.savepoint_rollback(save_point)
                return serializers.ValidationError("生成订单失败！请联系客服工作人员")

            # 声明订单总价格和订单实价
            total_price = 0

            # 开启redis的事务操作[管道操作]
            pip = redis.pipeline()
            pip.multi()

            for course_id_bytes in course_set:
                # 有效期选项
                course_expire_bytes = cart_list[course_id_bytes]
                expire_id = int(course_expire_bytes.decode())
                course_id = int(course_id_bytes.decode())
                try:
                    course = Course.objects.get(pk=course_id)
                except:
                    transaction.savepoint_rollback(save_point)
                    return serializers.ValidationError("对不起，商品课程不存在！")

                # 提取课程的有效期选项
                if expire_id > 0:
                    course_expire = CourseExpire.objects.get(pk=expire_id)
                    price = course_expire.price
                else:
                    price = course.price

                # 生成订单详情记录
                order_detail = OrderDetail.objects.create(
                    order=order,
                    course=course,
                    expire=expire_id,
                    price=price,
                    real_price=course.real_price(price),
                    discount_name=course.discount_type
                )

                # 记录订单总价
                total_price += order_detail.real_price

                # 从购物车中删除已经转移到订单里面的勾选商品
                pip.hdel("cart_%s" % user_id, course.id)
                pip.srem("selected_%s" % user_id, course.id)

            # 执行redis的管道操作
            pip.execute()

        # 返回相应给客户端的订单模型
        return order
