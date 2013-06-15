# -*- coding: UTF-8 -*-
import urllib,urllib2
try:
    import simplejson
except ImportError:
    try:
        import json as simplejson
    except ImportError:
        try:
            from django.utils import simplejson
        except ImportError:
            raise ImportError('A json library is required to use this python library')

class instagcn(object):
	setting = 	{	'client_id':'',
					'client_sceret':'',
					'access_token':''
				}
	def __init__(self,**kwg):
		if(kwg.has_key('access_token')):
			setting['access_token'] = kwg['access_token']