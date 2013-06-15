#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        函数库
# Purpose:
# Author:      yibin
#
# Created:     13-06-2010
# Copyright:   (c) yibin 2010
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import string,random
from time import mktime, time
from datetime import datetime, timedelta

import math
import hashlib
import time
try:
    import Image
except:
    from PIL import Image
import os
import inspect
import StringIO
import re




import pylibmc

cache = pylibmc.Client()

import base64




def sortDict(d):
    '''按字典KEY排序，返回元组'''
    return sorted(d.items(), key=lambda d:d[0])


def friendtime(dt,format='%Y-%m-%d %H:%M'):
    '''时间友好显示化'''
    t = time.localtime(time.time())
    today = time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t),'%Y-%m-%d %H:%M:%S'))
    yestoday = today - 3600*24
    if dt > today:
        return u'今天' + time.strftime('%H:%M',time.localtime(dt))
    if dt > yestoday and dt < today:
        return u'昨天' + time.strftime('%H:%M',time.localtime(dt))
    return time.strftime(format,time.localtime(dt))

def timesince(dt, default="now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


def friendtimeV2(timestamp,isTimestamp=True):
    if not isTimestamp:
        timestamp = time.mktime(time.strptime(str(timestamp),'%Y-%m-%d %H:%M:%S'))
    return friendtime(timestamp)
    it = int(timestamp) + 8*3600
    #return datetime.fromtimestamp(it).strftime('%Y-%m-%d %H:%M:%S')
    if (int(time.time())-it)<31536000:
        time1 = datetime.fromtimestamp(it)
        time_diff = (datetime.utcnow() + timedelta(hours =+ 8)) - time1
        days = time_diff.days
        if days:
            if days > 60:
                return u'%s月前' % (days / 30)
            if days > 30:
                return u'1月前'
            if days > 14:
                return u'%s周前' % (days / 7)
            if days > 7:
                return u'1周前'
            if days > 1:
                return u'%s 天前' % days
            return u'1天前'
        seconds = time_diff.seconds
        if seconds > 7200:
            return u'%s小时前' % (seconds / 3600)
        if seconds > 3600:
            return u'1小时前'
        if seconds > 120:
            return u'%s分钟前' % (seconds / 60)
        if seconds > 60:
            return u'1分钟前'
        if seconds > 1:
            return u'%s秒前' %seconds
        return u'%s秒前' % seconds
        
    else:
        return datetime.fromtimestamp(it).strftime('%Y-%m-%d %H:%M:%S')



def date_gmt(value):
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.gmtime(value))


def formattime(dt,format='%Y-%m-%d %H:%M'):
    mins = int(time.time())-dt
    if mins < 60:
        return u'%s 秒前' % mins
    elif mins < 3600:
        return u'%s 分钟前' % (mins / 60)
    elif mins < 24*3600:
        return u'%s 小时前' % (mins/3600)
    elif mins < 3*24*3600:
        return u'%s 天前' % (mins/(3600*24))
    _time = time.localtime(dt)
    _now = time.localtime(time.time())
    if _time.tm_year == _now.tm_year:
        format='%m-%d %H:%M'
    return time.strftime(format,time.localtime(dt))
  



def md5(val):
    return hashlib.md5(val).hexdigest()




def now():
    return int(time.time())

def randomstr(length=10,stringtype = 2):
    val = None
    if stringtype == 0:
        val = string.ascii_letters
    elif stringtype == 1:
        val = string.digits
    elif stringtype == 2:
        val = string.ascii_letters+string.digits
    return ''.join(random.sample(val,length))





def obj2json(obj):
    import StringIO
    stream = StringIO.StringIO()
    for key in obj.__dict__:
        stream.write(obj.__dict__[key])
    return stream




def sendemail(subject,toaddress,message,mailtype = 'active',**param):
    pass



def subString(s,length,dot=' ...'):
    
    try:
        us = unicode(s, 'utf-8')
    except:
        us = s
    gs = us.encode('gb2312')
    n = int(length)
    t = gs[:n]
    while True:
        try:
            unicode(t, 'gbk')
            break
        except:
            n -= 1
            t = gs[:n]
    return t.decode('gb2312')+dot



def obj2dict(obj):
    """
    summary:
        将object转换成dict类型    
    """
    memberlist = [m for m in dir(obj)]

    _dict = {}
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    for m in memberlist:
        if m[0] != "_" and not callable(m):
            value = getattr(obj,m)
            if type(value) is  types.InstanceType : 
                _dict[m] = obj2dict(value)
            elif type(value) in (type(1),type(1.2)):
                _dict[m] = str(value)
            elif isinstance(value, datetime.datetime):
                d = safe_new_datetime(value)
                _dict[m] = d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
            else:
                _dict[m] = getattr(obj,m)
    return _dict



def addslashes(value):
    return value.replace("'","\\'").replace('"','\"').replace('\\','\\').replace('null','\\null')




def isemail(value):
    return re.match("\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*",value)

def ispassword(value):
    return re.match("^[a-zA-Z0-9]{1}([a-zA-Z0-9]|[._~!@#$%^&*()]){4,14}$",value)

def isusername(value):
    return re.match("^[a-zA-Z]{1}([a-zA-Z0-9_]){4,14}$",value)


def convertUser(value):
    return re.sub("@([\S]+)",'<a href="/u/\\1/" class="user">@\\1</a>',value)

def convertTag(value):
    return re.sub("#([\S]+)",'<a href="/tag/\\1/" class="tag">#\\1</a>',value)    


def deleteCache(key):
    cache.delete(key)

def FlushCache():
    cache.flush_all()

def SetCache(key,value,expire=3600):
    val =  cache.add(str(key),value,time = expire)
    #print 'set cache %s result:%s' % (key,val)

def GetCache(key):
    key = str(key)
    #print 'get cache %s ....' % key
    return cache.get(key)

def cacheV2(key_pattern, expire=3600):
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getargspec(f)
        if varargs or varkw:
            raise Exception("not support varargs")
        def _(*a, **kw):
            param = dict(zip(arg_names,a))
            key = key_pattern
            for k,v in param.items():
                key = key.replace('{'+str(k)+'}',str(v))
            for k,v in kw.items():
                key = key.replace('{'+str(k)+'}',str(v))
            val = cache.get(key)
            #print 'get cache %s ' % key
            if val is None:
                val = f(*a, **kw)
                if val is None:
                    pass
                else:
                    cache.add(key,val,time = expire)
                    #print 'add key %s OK!' % key
            else:
                pass                
            return val
        return _
    return deco



def getTime(daterange=1):
    '''获取指定时间戳'''
    t = time.localtime(time.time())
    t = list(t)
    t[3] = t[4] = t[5] = 0
    date = 0
    if daterange == 1:  #当天
        t[3] = t[4] = t[5] = 0
        date = time.mktime(tuple(t))
    elif daterange == 2:    #本周
        t[2] -= t[6]
        
        date = time.mktime(tuple(t))
    elif daterange == 3:    #本月
        t[2] = 1
        date = time.mktime(tuple(t))
    elif daterange == 4:    #昨天
        t[2] = t[2] - 1
        date = time.mktime(tuple(t))
    elif daterange == 5:    #前天
        t[2] = t[2] - 2
        date = time.mktime(tuple(t))
    else:
        return 0
    date = int(date)
    return date




def isImage(remoteUri):
    import urllib
    try:
        res = urllib.urlopen(remoteUri).read()
        
        req = StringIO.StringIO(res)
        im = Image.open(req)
        if im.format.lower() in ['jpg','jpeg','png']:
            #if im.size[0] < MAX_WIDTH or im.size[1] < MAX_HEIGHT : 
                #return (None,u'图片宽不能小于%s,高不能小于%s' % (MAX_WIDTH,MAX_HEIGHT))
            return (im,'')
        return (None,u'只支持jpg/jpeg格式图片')
    except Exception,e:
        pass
    return None,u'载入图片出错'

#import base64

#print base64.b64encode(desencrypt(u'yibin.net@gmail.com|1286791123'.encode('utf8')))