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
INSTAGRAM_CLIENT_ID = '353257bfcf7a417c99a2eb810835c51f'
INSTAGRAM_CLIENT_SCERET = '4561c19cc7144505ab7282c7faa1b816'
INSTAGRAM_ACCESS_TOKEN  = '7757810.353257b.659a5c92f14747d19d3f1a1b0b3ffde2'
INSTAGRAM_REDIRECT_URI = 'http://instagcn.sinaapp.com/oauth/callback'
INSTAGRAM_SCOPE = ['basic','comments','likes','relationships']