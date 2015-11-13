# -*- coding: utf-8 -*-
#!/usr/bin/env python
# author: bambooom
'''
MyDiary Web Application
Open web browser and access http://bambooomdiary.sinaapp.com/
You can read the old diary and input new diary
'''

from bottle import Bottle, request, route, run, template
import sae
import sae.kvdb
from time import localtime, strftime

app = Bottle()
kv = sae.kvdb.Client()

def read_diary_all():
#	f = open('diary log.txt','a+')
#	return f.read()
	log = ""
	for i in kv.get_by_prefix("count"):
		log = log +i[1]['time']+"    "+i[1]['diary']+"\n" # i is type tuple with key-value
	#for j in range(count-1):
	#	print log[j]['time'], log[j]['diary']
	return log

def write_diary(newdiary,count=1):
	# key must be str()
	countkey = "count" + str(count)
	edit_time = strftime("%Y %b %d %H:%M:%S", localtime())
	diary = {'time':edit_time, 'diary':newdiary}
	kv.set(countkey,diary)
	count += 1
	return count
#	f = open('diary log.txt','a+')
	
#	f.write('%s    %s\n' % (edit_time, newdiary))
#	f.close()
count = write_diary("hello world")
count = write_diary("hello world again",count)
#print read_diary_all()
#write_diary("hello world 2","hh2")
#print read_diary_bykey(str(2))
#print read_diary("taghh2")



@app.route('/')
def start():
	log = read_diary_all()
	return template("diarysae", diarylog=log)

#@app.route('/', method='POST')
#def input_new():
#	newdiary = request.forms.get('newdiary')
#	write_diary(newdiary)
#	log = read_diary()
#	return template("diarysae", diarylog=log)

application = sae.create_wsgi_app(app)