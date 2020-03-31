from django.shortcuts import render,redirect
from .models import  *
from django.http import  HttpResponse
import uuid
from utils.pay import  AliPay


# Create your views here.
def goods(request):
    goods_list = Goods.objects.all()
    return render(request,'goods.html',{'goods_list':goods_list})

def purchase(request,goods_id):
    obj_goods = Goods.objects.get(pk=goods_id)
    order_number = str(uuid.uuid4())
    Order.objects.create(order_number=order_number,goods=obj_goods)
    print('AAAAAAA')
    print(Order.objects.create(order_number=order_number,goods=obj_goods))
    #实例化对象
    alipay = AliPay(appid='2016102400749283',app_notify_url='http://127.0.0.1:8888/show_msg/',  # 支付宝发送支付状态信息的地址，支付宝会向这个地址发送post请求，可以先不写但是必须有内容(我这里用的是空格)
        alipay_public_key_path='zhifu/keys/alipay_public_key.txt',  # 支付宝公钥
        app_private_key_path='zhifu/keys/my_private_key.txt',  # 应用私钥
        return_url='http://127.0.0.1:8888/show_msg/',  # 将用户浏览器地址重定向回原来的地址，支付宝会向这个地址发送get请求，可以先不写但是必须有内容\
        debug=True
                    )
    # 定义请求地址传入的参数
    query_params = alipay.direct_pay(
        subject=obj_goods.goods_name,  # 商品的简单描述
        out_trade_no=order_number,  # 商品订单号
        total_amount=obj_goods.goods_price,  # 交易金额(单位是元，保留两位小数)
    )
    # 需要跳转到支付宝的支付页面，所以需要生成跳转的url
    pay_url = 'https://openapi.alipaydev.com/gateway.do?{0}'.format(query_params)
    return redirect(pay_url)


def show_msg(request):
    if request.method == 'GET':
        # alipay = AliPay(
        #     appid="2016102400749283",  # APPID
        #     app_notify_url='http://127.0.0.1:8888/check_order/',
        #     return_url='http://127.0.0.1:8888/show_msg/',
        #     app_private_key_path='zhifu/keys/alipay_private_2048.txt',  # 应用私钥
        #     alipay_public_key_path='zhifu/keys/alipay_public_2048.txt',  # 支付宝公钥
        #     debug=True,  # 默认是False
        # )

        alipay = AliPay(appid = '2016102400749283', app_notify_url = 'http://127.0.0.1:8888/check_order/', app_private_key_path = 'zhifu/keys/my_private_key.txt',
        alipay_public_key_path = 'zhifu/keys/alipay_public_key.txt', return_url = 'http://127.0.0.1:8888/show_msg/', debug = True)

        params = request.GET.dict()  # 获取请求携带的参数并转换成字典类型
        print(
            request.GET)  # <QueryDict: {'charset': ['utf-8'], 'out_trade_no': ['04f09b6f-e792-4a1d-8dbc-c68f1d046622'], ……}
        print(params)  # {'charset': 'utf-8', 'out_trade_no': '04f09b6f-e792-4a1d-8dbc-c68f1d046622',……}
        sign = params.pop('sign', None)  # 获取sign的值
        # 对sign参数进行验证
        status = alipay.verify(params, sign)
        print(status,"哈哈")
        if status:
            return render(request, 'show_msg.html', {'msg': '支付成功'})
        else:
            return render(request, 'show_msg.html', {'msg': '支付失败'})
    else:
        return render(request, 'show_msg.html', {'msg': '只支持GET请求，不支持其它请求'})

