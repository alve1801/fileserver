#!/usr/bin/env python
import socket
import threading
import time

response=b'''HTTP/1.1 200 OK\r\n\r\n
<!DOCTYPE html><html><body>
<form method="post" enctype="multipart/form-data" action="/posted">
	<input type="text" name="desc" placeholder="description goes here"><br>
	<input type="file" name="file" multiple><br>
	<button type="submit">upload</button>
</form></body></html>
'''

logfile=open('log','wb')

def parse(msg):
	print('request length ',len(msg))
	if msg[:3]==b'GET':
		print('get request for:')
		url=msg[4:msg.find(b' ',5)]
		print('\t',url)
		return 'get'
	if msg[:4]==b'POST':
		print('post request, length ',len(msg))
		contents,isfile={},0
		a=msg.find(b'boundary=')+9
		b=msg.find(b'\r\n',a)
		boundary=msg[a:b]
		a+=len(boundary)
		print('\tboundary is ',boundary)
		a=msg.find(boundary,a)
		while a!=-1:
			print('key at ',a)
			b=msg.find(b'name',a)+6
			key=msg[b:msg.find(b'"',b)]
			print('\tkey:',key)
			if key==b'file':
				isfile=1
				b=msg.find(b'filename',b)+10
				key=msg[b:msg.find(b'"',b)]
				print('\t\tfname:',key)

			b=msg.find(b'\r\n\r\n',b)+4
			a=msg.find(boundary,b)
			val=msg[b:(a-4,len(msg))[a==-1]]
			contents[key]=val

			if(isfile and key):
				with open('uploads/{}'.format(key.decode()),'wb') as x:
					x.write(val)

			if len(val)<20:
				print('\tcontent: ',val)
			else:
				print('\tcontent length: ',len(val))
			if a+len(boundary)+5>len(msg):a=-1

		return 'post'

		print(contents.keys())

		fname=contents.get(b'desc')
		if(fname):
			fdata=contents.get(fname)
			if fdata:
				print('writing file ',fname)
				with open(fname,'wb') as x:
					x.write(fdata)

		return 'post'
	print('unknown request')
	return ''

def handle_echo(client_connection, client_address):
	client_connection.settimeout(30)
	try:
		print("\n\nnew connection from {}".format(client_address))
		alldata=b''
		while 1:
			data = client_connection.recv(1024)
			alldata+=data
			if len(data)<1024:break
			time.sleep(.0005) # needs this so it actually receives the data and doesnt cancel prematurely
			# ideally, it shouldnt be a delay, but i have no idea how else to fix this
		logfile.write(bytes('\n\nrequest from {}\n'.format(client_address),'utf-8'))
		logfile.write(alldata)
		if parse(alldata)=='get':client_connection.send(response)

	except socket.timeout:print('timeout')
	client_connection.shutdown(1)
	client_connection.close()
	print('done with {}'.format(client_address))

def listen(host, port):
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	conn.bind((host, port)),conn.listen(5)
	while 1:
		current_conn, client_address = conn.accept()
		print('{} connected'.format(client_address))
		handler_thread = threading.Thread(
			target = handle_echo,
			args = (current_conn,client_address)
		)
		handler_thread.daemon = 1
		handler_thread.start()

try:listen('0.0.0.0',8000)
except KeyboardInterrupt:pass
logfile.close()
