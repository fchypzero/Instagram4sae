# -*- coding: UTF-8 -*-
import os,time,urllib,base64,re,urllib2
import sys
from datetime import timedelta
from instagram.client import InstagramAPI

from flask import Flask,  redirect, url_for, escape, session,request,make_response,flash,g,abort,Response,jsonify
from flask import render_template
from functools import wraps
try:
    import json
except ImportError:
    import simplejson as json

import util
from config import *

app = Flask(__name__,static_folder='static', template_folder='templates')
app.debug = False

app.config['SESSION_COOKIE_NAME'] = AUTH_COOKIE
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

app.secret_key = '2\xd13;\xb7\xeb8\xcb!2\xb3f\xad4\xd0\xb4<\x7f\xad\xfcB\xab\x17\xb8'


api = InstagramAPI(client_id=INSTAGRAM_CLIENT_ID, client_secret=INSTAGRAM_CLIENT_SCERET, redirect_uri=INSTAGRAM_REDIRECT_URI,access_token=INSTAGRAM_ACCESS_TOKEN)

import sae.kvdb


@app.template_filter('tohtml')
def tohtml(value):
    value = util.convertUser(value)
    value = util.convertTag(value)
    return value



@app.template_filter('datetime')
def datetime_filter(intdate):
    intdate = int(intdate)
    return util.friendtime(intdate)



@app.template_filter('strtotime')
def strtotime(val,isTimestamp=False):
    return util.friendtimeV2(val,isTimestamp)




@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
    
@app.errorhandler(500)
def server_error(error):
    print error
    return render_template('500.html'),500



@app.teardown_request
def teardown_request(exception):
    g.kvdb.disconnect_all()

@app.before_request
def before_request():
    g.user = None
    g.config = {'static':SAE_STORAGE,'sitename':SITE_CONFIG['SiteName']}
    g.start = time.time()
    g.id = ''
    g.kvdb = sae.kvdb.KVClient()
    g.autoload = True
    session.permanent = True
    if AUTH_COOKIE in session:
        g.user = session[AUTH_COOKIE]
        g.userjson = json.dumps(g.user[1])



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return json.dumps({'code':1,'message':'require login'})
        return f(*args, **kwargs)
    return decorated_function


@app.after_request 
def after_request(response): 
    return response

  

@app.route('/flushcache')
def FlushCache():
    util.FlushCache()
    return 'Flush Cache OK!'


@app.route('/oauth/')
def OAuth():
    redirect_uri = api.get_authorize_login_url(scope = INSTAGRAM_SCOPE)
    return redirect(redirect_uri)

@app.route('/profile')

def Profile():
    return render_template('profile.html')

@app.route('/oauth/callback')
def OAuthCallback():
    code = request.args.get('code', '')
    if code == '':
        abort(404)
    access_token = api.exchange_code_for_access_token(code)
    if access_token and access_token[1]['id']:
        session[AUTH_COOKIE] = access_token
        return redirect('/')
    else:
        return u'获取access_token失败，请重试'

    
@app.route('/logout')
def Logout():
    response = make_response(redirect('/?logout')) 
    if AUTH_COOKIE  in session:
        session.pop(AUTH_COOKIE,None)
    flash(u'您已成功退出')
    return response 



@app.route('/cron/popular')
def cron_popular():
    key = 'media_popular'
    data = api.media_popular(count=300)
    data = data['data']
    util.SetCache(key,data,600)
    return 'success'

@util.cacheV2('media_popular_{page}',600)
def media_popular(page):
    data =  api.media_popular(page=page)
    return data['data']


def _convert(data,slice=True):
    for x in data['data']:
            try:
                x['created_time'] = util.friendtimeV2(int(x['created_time']))
                if x['comments'].has_key('count') and x['comments']['count']>0:
                    if slice:
                        x['comments']['data'] = x['comments']['data'][:4]
                    for m in x['comments']['data']:
                        m['created_time'] = util.friendtimeV2(int(m['created_time']))
            except:
                pass
    return data


@app.route('/postcomment/<id>/',methods=['POST'])
@login_required
def postcomment(id):
    comment = request.form['comment']
    if comment.strip() !='':
        api.access_token = g.user[0]
        rtn = api.create_media_comment(media_id=id,text=comment)
        return json.dumps({'code':0})
    else:
        return json.dumps({'code':1,'message':u'评论内容为空'})

@app.route('/')
def Index():
    pagesize = 20
    page = int(request.args.get('page',1))
    callback = request.args.get('jsoncallback','json')
    data = media_popular(page)
    
    g.curr = '/'
    #data = data[(page-1)*pagesize:page*pagesize]
    if page > 1:
        for x in data:
            x['created_time'] = util.friendtimeV2(int(x['created_time']))
            if x['comments'].has_key('count') and x['comments']['count']>0:

                    x['comments']['data'] = x['comments']['data'][:2]
                    x['comments']['data'] = x['comments']['data'][-1::-1]
                    for m in x['comments']['data']:
                        m['created_time'] = util.friendtimeV2(int(m['created_time']))
        return callback+"("+json.dumps(data)+')'
    g.execute = time.time()-g.start
    return render_template('instagram.html',photos=data)


@app.route('/feed/')
def Feed():
    next_id = str(request.args.get('next',''))  
    callback = request.args.get('jsoncallback','json')  
    data = _feed(30,next_id)
    data = data[0]
    next_max_id = ''
    if data['pagination'].has_key('next_max_id'):
        next_max_id = data['pagination']['next_max_id']
    if next_id :
        data = _convert(data)
        return callback+"("+json.dumps(data)+')'
    g.curr = 'feed'
    g.subtitle = u'我订阅的图片'
    g.execute = time.time()-g.start
    return render_template('instagram.html',photos=data['data'],next = next_max_id)




def _feed(length,next_id):
    cachekey = 'feed-%s-%s' % (next_id,g.user[0])
    data = util.GetCache(cachekey)
    if not data:
        api.access_token = g.user[0]
        data = api.user_media_feed(count=length,max_id=next_id)
        util.SetCache(cachekey,data,120)
    return data

def _tag(next_id,tagname):    
    data = api.tag_recent_media(count=40, tag_name=tagname,max_id=next_id)
    return data


@app.route('/tag/<tag>/')
def Tag(tag):
    next_id = str(request.args.get('next',''))
    data = _tag(next_id,tag)
    data = data[0]
    next_max_id = ''
    if data['pagination'].has_key('next_max_id'):
        next_max_id = data['pagination']['next_max_id']
    callback = request.args.get('jsoncallback','json')  
    if next_id :
        data = _convert(data)
        return callback+"("+json.dumps(data)+')'
    g.curr = ''
    g.subtitle = u'tag-%s' % tag

    return render_template('instagram.html',photos=data['data'],next = next_max_id)


@app.route('/do/<action>/')
def do(action):
    if action == 'feed':
        pass

def _me(length,next_id):
    
    cachekey = 'self-%s' % next_id
    data = None #util.GetCache(cachekey)
    if not data:
        
        data = api.user_recent_media(count=40, user_id=g.user[1]['id'],max_id=next_id)

        util.SetCache(cachekey,data,300)
    return data



@util.cacheV2('u-{username}',300)
def _queryUser(username):
    key = str(username)
    #user = g.kvdb.get(key)
    #if not user :
    user = api.user_search(q=username,count=1)
    if user:
        if len(user['data']) > 0:
            uid = user['data'][0]['id']
            user = api.user(user_id=uid)
            user = user['data']
                #g.kvdb.add(key,user)
    return user

@app.route('/relation/<action>/<username>/')
def relation(action,username):
    next_cursor = request.args.get('cursor','')
    if not g.user:
        api.access_token = INSTAGRAM_ACCESS_TOKEN
    else:
        api.access_token = g.user[0]
    user = _queryUser(username)
    if action=='following':
        data = api.user_follows(user_id=user['id'],cursor=next_cursor)
    else:
        data = api.user_followed_by(user_id=user['id'],cursor=next_cursor)
    return json.dumps(data[0])

@app.route('/relation/<username>/')
def relationindex(username):
    
    if not g.user:
        api.access_token = INSTAGRAM_ACCESS_TOKEN
    else:
        api.access_token = g.user[0]
    user = _queryUser(username)
   
    data_following = api.user_follows(user_id=user['id'])
    
    data_followers = api.user_followed_by(user_id=user['id'])

    data = {'following':data_following[0],'followers':data_followers[0]}

    return json.dumps(data)



@app.route('/me/')
def Me():
    next_id = str(request.args.get('next',''))
    data = _me(30,next_id)
    data = data[0]
    next_max_id = ''
    if data['pagination'].has_key('next_max_id'):
        next_max_id = data['pagination']['next_max_id']
    callback = request.args.get('jsoncallback','json')  
    if next_id :
        data = _convert(data)
        return callback+"("+json.dumps(data)+')'
    g.curr = 'me'
    g.subtitle = u'我发表的图片'
    g.execute = time.time()-g.start
    return render_template('instagram.html',photos=data['data'],next = next_max_id)



@app.route('/like/<id>/')
def like(id):
    if not g.user:
        return json.dumps({'code':1,'message':u'请登录后再操作'})
    api.access_token = g.user[0]
    code = 1
    try:
        rtn = api.like_media(media_id=id)
        code = rtn['meta']['code']
    except Exception,e:
        print e
    return json.dumps({'code':code,'message':u'OK'})

@app.route('/follow/<action>/')
def follow(action):
    if not g.user:
        return json.dumps({'code':1,'message':u'请登录后再操作'})
    uid = request.args.get('uid','')
    api.access_token = g.user[0]
    rtn = None
    if uid:
        if action == 'do':
            rtn = api.follow_user(user_id=uid)
        elif action =='undo':
            rtn = api.unfollow_user(user_id=uid)
        return json.dumps({'code':0,'message':u'OK'})
    else:
        return json.dumps({'code':1,'message':u'参数不正确'})



@util.cacheV2('p_{id}',300)
def _queryMedia(id):
    data = api.media(media_id=id)
    data['data']['created_time'] = util.friendtimeV2(int(data['data']['created_time']))
    for d in data['data']['comments']['data']:
        d['created_time'] = util.friendtimeV2(int(d['created_time']))
    return data

@app.route('/Media/<id>/')
def Media(id):
    data = _queryMedia(id)
    return json.dumps(data)



@util.cacheV2('um{count}{user_id}{max_id}',300)
def _user_recent_media(count=20,user_id=0,max_id=''):
    data= api.user_recent_media(count=count,user_id=user_id,max_id=max_id)
    return data


@app.route('/p/<id>/')
def P(id):
    uid = id.split(id)[1]
    data = _queryMedia(id)
    g.id = id
    return U(data['data']['user']['username'])

@app.route('/expore/<latitude>/<longitude>/')
def Expore(latitude,longitude):
    g.subtitle=u'身边的......'
    g.access_token = INSTAGRAM_ACCESS_TOKEN
    data = api.media_search(lat=latitude,lng=longitude,min_timestamp=time.time()-172800,distance=5000)
    data = _convert(data)
    callback = request.args.get('jsoncallback','json')
    #for x in data['data']:
    #    x['created_time'] = util.friendtimeV2(int(x['created_time']))
    return callback+"("+json.dumps(data)+')'


@app.route('/location/')
def location():
    g.curr = 'location'
    g.autoload = False
    return render_template('expore.html')


@app.route('/subscription/')
def subscription():
    if not g.user:
        return json.dumps({'code':1,'message':u'请登录后再操作'})
    api.create_subscription(object='user', aspect='media', callback_url='http://instagcn.sinaapp.com/instagram')
    #api.access_token = g.user[0]
    #print api.list_subscriptions()
    return 'OK'


@app.route('/u/<username>/')
def U(username):
    uid = ''
    next_id = request.args.get('next','')
    user = None
    try:
        user = _queryUser(username)
    except Exception,e:
        print e
        return redirect('/')
    if not user or not user.has_key('id'):
        abort(404)
    uid = user['id']
    key = str('user-media-%s-%s' % (uid,next_id))
    try:
        data= _user_recent_media(20,user_id=uid,max_id=next_id)
    except Exception,e:
        print e
        return redirect('/')
    next_max_id = ''
    data = data[0]
    if data['pagination'].has_key('next_max_id'):
        next_max_id = data['pagination']['next_max_id']
    callback = request.args.get('jsoncallback','json')  
    if next_id :
        data = _convert(data)
        return callback+"("+json.dumps(data)+')'
    g.subtitle = u'%s 的页面' % user['username']
    isfollowing = False
    isfollower =  False
    #判断是否关注对方
    rtn = None
    if g.user:
        api.access_token = g.user[0]
        try:
            rtn = api.user_relationship(user_id=uid)
            if rtn['data']['outgoing_status'] == 'follows':
                isfollowing = True
            if rtn['data']['incoming_status'] == 'followed_by':
                isfollower = True
        except:
            pass
    return render_template('profile.html',isfollowing=isfollowing,isfollower=isfollower, user=user,uid=id, next=next_max_id,photos=data['data'],isfirst=next_id)
