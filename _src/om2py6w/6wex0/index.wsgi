# -*- coding: utf-8 -*-
#!/usr/bin/env python
# author: bambooom
'''
MyDiary Wechat Application
Open web browser and access http://omoocpy.sinaapp.com/
Wechat platform: bambooom
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bottle import Bottle, request, route, run
import sae
import sae.kvdb
import time
from time import localtime, strftime
import hashlib
import xml.etree.ElementTree as ET

app = Bottle()
kv = sae.kvdb.Client()

@app.route('/wechat')
def check_signature():
	'''
	wechat access verification
	'''
	token = "bambooom2bpythonic"
	signature = request.GET.get('signature',None)
	timestamp = request.GET.get('timestamp',None)
	nonce = request.GET.get('nonce',None)
	echostr = request.GET.get('echostr',None)
	L = [token,timestamp,nonce]
	L.sort()
	s=L[0]+L[1]+L[2]
	if hashlib.sha1(s).hexdigest() == signature:
		return echostr
	else:
		return None

def parse_xml_msg():
	recv_xml = request.body.read()
	root = ET.fromstring(recv_xml)
	msg = {}
	for child in root:
		msg[child.tag] = child.text
	return msg

def read_diary_all():
	log = [i[1]['diary'] for i in list(kv.get_by_prefix("key"))]
	logstr = "\n".join(log)
	return log,logstr

def write_diary(newdiary,tags,count):
	# key must be str()
	countkey = "key" + str(count)
	edit_time = strftime("%Y %b %d %H:%M:%S", localtime())
	diary = {'time':edit_time,'diary':newdiary,'tags':tags}
	kv.set(countkey,newdiary)

@app.route('/')
def start():
	diarylog = read_diary_all()[0]
	return template("diarysae", diarylog=diarylog)

@app.route('/wechat', method = 'POST')
def response_wechat():
	'''
	response in wechat platform
	'''
	msg = parse_xml_msg()
	#msg={'FromUserName': 'omoocpy', 'MsgId': 'hdsicwecewew2233333', 
	#'ToUserName': 'bambooom', 'Content': 'diary WTF', 'MsgType': 'text', 
	#'CreateTime': '20151120'}

	response_msg = '''
	<xml>
	<ToUserName><![CDATA[%s]]></ToUserName>
	<FromUserName><![CDATA[%s]]></FromUserName>
	<CreateTime>%s</CreateTime>
	<MsgType><![CDATA[text]]></MsgType>
	<Content><![CDATA[%s]]></Content>
	</xml>
	'''
	HELP = '''
	目前可使用的姿势:
	- diary..# ~吐槽贴个#标签
	    - 例如"diary..cool#nice"
	    - cool为吐槽,nice为标签
	- see    ~吐过的槽
	- see#  ~吐过#标签的槽
	    - 例如"see#nice"
	    - 返回"cool"
	- help  ~怎么吐槽
	    - 返回姿势指南
	'''

	if msg['Content'].startswith('diary'):
		newdiary = msg['Content'][5:]
		count = len(read_diary_all()[0])
		write_diary(newdiary,count)
		echo_str = u"Got! "+str(count+1)+u"条吐槽啦!"
	elif msg['Content'] == 'see':
		echo_str = read_diary_all()[1]
	else:
		echo_str = HELP
		
	echo_msg = response_msg % (
		msg['FromUserName'],msg['ToUserName'],str(int(time.time())),echo_str)
	
	return echo_msg



	#count = len(read_diary_all())
	#newdiary = unicode(request.forms.get('newdiary'),'utf-8')
	#tags = unicode(request.forms.get('tags'),'utf-8')
	#write_diary(newdiary,tags,count)
	#diarylog = read_diary_all()
	#return template("diarysae", diarylog=diarylog)

@app.route('/', method='DELETE')
def delete():
	temp = kv.getkeys_by_prefix("key#")
	for i in temp:
		kv.delete(i)

application = sae.create_wsgi_app(app)
