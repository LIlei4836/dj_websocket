from django.shortcuts import render
from dwebsocket.decorators import accept_websocket,require_websocket
from django.http import HttpResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

import threading

import time
import random
import json

# Create your views here.

clients = []


def index(request):
    return render(request, 'index.html',{'init':'init'})

def index2(request):
    return render(request, 'index2.html')

# @accept_websocket
# def echo(request):
#     if request.is_websocket:#如果是webvsocket
#         lock = threading.RLock() #rlock线程锁
#         try:
#             lock.acquire()#抢占资源
#             clients.append(request.websocket)#把websocket加入到clients
#             print(clients)
#             for message in request.websocket:
#                 if not message:
#                     break
#                 for client in clients:
#                     client.send(message)
#         finally:
#             clients.remove(request.websocket)
#             lock.release()#释放锁

def modify_message(message):
    return message.lower()


@accept_websocket
def echo(request):
    if not request.is_websocket():#判断是不是websocket连接
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request,'index.html')
    else:
        for message in request.websocket:
            request.websocket.send(message)#发送消息到客户端
            #request.websocket.send(message)
            for i in range(10):
                s={'test':'nihao'+str(i)}
                s=json.dumps(s).encode()
                request.websocket.send(s) #str(random.randint(1,20)).encode()
                time.sleep(0.1)
        

@require_websocket
def echo_once(request):
    message = request.websocket.wait()
    request.websocket.send(message)

def d3(rq):
    return render(rq, 'd3.html')

@accept_websocket
def ec_d3(request):
    if not request.is_websocket():#判断是不是websocket连接
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request,'index.html')
    else:
        for message in request.websocket:
            #request.websocket.send(message)#发送消息到客户端
            #request.websocket.send(message)
            for i in range(140):
                request.websocket.send(('%s'%(str(932+i)+','+str(random.randint(10,30))+','+str(932+i)+','+str(random.randint(10,30)))).encode()) #str(random.randint(1,20)).encode()
                time.sleep(0.5)

def getList(ts):
    # 时间,开盘价,最高价,最低价,收盘价,成交量
    return [
        [1000*(ts-60*10), 16580.0, 16700.0, 16530.0,16540.0, 124],
        [1000*(ts-60*9),16680.0,16800.0,16700.0,16700.0,98],
        [1000*(ts-60*8),16752.0,16880.0,16630.0,16760.0,179],
        [1000*(ts-60*7),16580.0,16780.0,16530.0,16748.0,152],
        [1000*(ts-60*6),16680.0,16800.0,16630.0,16710.0,360],
        [1000*(ts-60*5),16680.0,16790.0, 16680.0,16770.0,211],
        [ 1000*(ts-60*4),16730.0,16784.0,16582.0,16720.0,420],
        [1000*(ts-60*3),16800.0,16850.0,16730.0,16700.0,325],
        [1000*(ts-60*2),16680.0,16800.0,16530.0,16620.0,228],
        [1000*(ts-60*1),16660.0,16730.0,16630,16723.0,231],
        [1000*(ts),16548.0,16860.0,16430.0,16800.0,199]
    ]

def GetRealTimeData(is_socket):
    '''得到推送点数据'''
    unix=int(time.time())
    is_time=cache.get('is_time')
    if is_time and int(unix/60)==int(is_time/60): #若不满一分钟,返回空
        pass #return
    else:
        cache.set("objArr",None,60)
    cache.set('is_time',unix,60)
    lists=[]
    closePrice=cache.get('closePrice')
    if (closePrice != None and closePrice<16000) or (closePrice == None):
        closePrice=random.randint(16000,17000)
        cache.set('closePrice',closePrice,60*3) #60秒

    #开盘价  
    openPrice = cache.get('closePrice')
    # 新产生的价格
    price = openPrice + random.randint(-100, 100)
    #最高价  
    #heightPrice = openPrice + random.randint(0, 300)
    #最低价  
    #lowPrice = openPrice - random.randint(0, 300)
    #收盘价  
    #closePrice = lowPrice + random.randint(0, 300)
    #cache.set('closePrice',closePrice,60)
    cache.set('closePrice',price,60)
    #成交量       
    amount = random.randint(0, 20)
    objArr = cache.get("objArr")
    if not objArr:
        objArr = [
                    unix*1000, #时间  
                    price, #开盘价  
                    price, #高  
                    price, #低  
                    price, #收盘价  
                    amount #量  
                ]
        cache.set("objArr",objArr,60)
    else:
        objArr = [
                    unix*1000, #时间  
                    objArr[1], #开盘价  
                    price if objArr[2]<price else objArr[2], #高  
                    price if objArr[3]>price else objArr[3], #低  
                    price, #收盘价  
                    amount+objArr[5] #量  
                ]
        cache.set("objArr",objArr,60)
    if is_socket:
        return objArr
    lists.append(objArr)
    data={
            'des' : "注释",
            'isSuc' : True, #状态  
            'datas' : {
                    'USDCNY' : 6.83, #RMB汇率  
                    'contractUnit' : "BTC",
                    'data' : lists,
                    'marketName' : "凯瑞投资",
                    'moneyType' : "CNY",
                    'symbol' : 'btc38btccny',
                    'url' : '官网地址', #（选填）  
                    'topTickers' : [] #（选填）
            }
        }
    return data


def kline(rq,xz):
    print(xz)
    if xz=='1':
        return render(rq, 'kline.html',{'xzs':'one'})
    elif xz=='2':
        return render(rq, 'kline.html',{'xzs':'two'})
    else:
        return HttpResponse('<h1>Not is param</h1>')

@csrf_exempt   #取消csrf验证
def getkline(rq):
    size=rq.POST.get('size')
    size=int(size) if size else 0
    types=rq.POST.get('type')
    if size>0:
        if cache.get('closePrice') == None:
            closePrice=random.randint(16000,17000)
            cache.set('closePrice',closePrice,60*3) #把数据缓存起来
        lists=getList(int(time.time()))
        data={
            'des' : "注释",
            'isSuc' : True, #状态  
            'datas' : {
                    'USDCNY' : 6.83, #RMB汇率  
                    'contractUnit' : "BTC",
                    'data' : lists,
                    'marketName' : "凯瑞投资",
                    'moneyType' : "CNY",
                    'symbol' : 'btc38btccny',
                    'url' : '官网地址', #（选填）  
                    'topTickers' : [] #（选填）
            }
        }
        return HttpResponse(json.dumps(data),content_type="application/json")
    else:
        #这段是时间到时的即时请求点数据（一个点数据）
        #表示请求一个点数据
        #if types == "1min": #1分钟线即时数据  
        data=GetRealTimeData(False) #一个点数据 
        return HttpResponse(json.dumps(data),content_type="application/json")
        '''else: #其他分钟类型
            data=GetRealTimeData() #一个点数据 
            return HttpResponse(json.dumps(data),content_type="application/json")'''
        

@accept_websocket
@csrf_exempt   #取消csrf验证
def getkline2(rq):
    size=rq.POST.get('size')
    size=int(size) if size else 0
    types=rq.POST.get('type')
    print('ajax........',rq.is_ajax(),size,types)
    if rq.is_ajax() and size>0:
        if cache.get('closePrice') == None:
            closePrice=random.randint(16000,17000)
            cache.set('closePrice',closePrice,60*3) #把数据缓存起来
        lists=getList(int(time.time()))
        data={
            'des' : "注释",
            'isSuc' : True, #状态  
            'datas' : {
                    'USDCNY' : 6.83, #RMB汇率  
                    'contractUnit' : "BTC",
                    'data' : lists,
                    'marketName' : "凯瑞投资",
                    'moneyType' : "CNY",
                    'symbol' : 'btc38btccny',
                    'url' : '官网地址', #（选填）  
                    'topTickers' : [] #（选填）
            }
        }
        return HttpResponse(json.dumps(data),content_type="application/json")
    elif rq.is_ajax() and size==0:
        if cache.get('closePrice') == None:
            closePrice=random.randint(16000,17000)
            cache.set('closePrice',closePrice,60*3) #把数据缓存起来
        lists=getList(int(time.time()))
        data={
            'des' : "注释",
            'isSuc' : True, #状态  
            'datas' : {
                    'USDCNY' : 6.83, #RMB汇率  
                    'contractUnit' : "BTC",
                    'data' : lists,
                    'marketName' : "凯瑞投资",
                    'moneyType' : "CNY",
                    'symbol' : 'btc38btccny',
                    'url' : '官网地址', #（选填）  
                    'topTickers' : [] #（选填）
            }
        }
        return HttpResponse(json.dumps(data),content_type="application/json")
    else:
        #这段是时间到时的即时请求点数据（一个点数据）
        #表示请求一个点数据
        #if types == "1min": #1分钟线即时数据  
        #data=GetRealTimeData() #一个点数据 
        #return HttpResponse(json.dumps(data),content_type="application/json")
        '''else: #其他分钟类型
            data=GetRealTimeData() #一个点数据 
            return HttpResponse(json.dumps(data),content_type="application/json")'''
        if rq.is_websocket():
            for message in rq.websocket:
                while 1:
                    data=GetRealTimeData(True)
                    rq.websocket.send(('%s'%(str(data)[1:-1])).encode())
                    time.sleep(1)