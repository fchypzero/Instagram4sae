#coding=utf-8
from StringIO import StringIO



import os
#from sae.const import SAE_TMP_PATH
#站点配置
SITE_CONFIG = {
	'SiteName':u'Instagram',
}
SAE_STORAGE = 'http://tukoo-storage.stor.sinaapp.com'
#cookie名称
AUTH_COOKIE = '_auth'

#Instagram PageCount
INSTAGRAM_PAGECOUNT = 20
INSTAGRAM_CLIENT_ID = '<YOUR_CLIENT_ID>'
INSTAGRAM_CLIENT_SCERET = 'YOUR_CLIENT_SCERET'
INSTAGRAM_ACCESS_TOKEN  = 'YOUR_DEFAULT_ACCESS_TOKEN'
INSTAGRAM_REDIRECT_URI = 'OAuth_Callback_URI'
INSTAGRAM_SCOPE = ['basic','comments','likes','relationships']