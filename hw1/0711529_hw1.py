"""
Date: 2021/01/02
Describe: OS hw1 
Auther: Kuan-Ju Chen
ID: 0711529
"""
import time # to calculate the running time

## for task1
import hashlib 

## for task2
from bs4 import BeautifulSoup
import requests

## multithreading 
import threading
import queue

class MyThread(threading.Thread):
	def __init__(self, queue, num, task):
		threading.Thread.__init__(self)
		self.queue = queue
		self.num = num
		self.task = task

	def run(self):
		while self.queue.qsize() > 0:
			msg = self.queue.get()
			if self.task==1: 
				proof_of_work(msg)
			elif self.task==2:
				get_url_header(msg)

def multithreading(task, number, testcase, taskdata):
	# create the queue to put the unworking task in it
	my_queue = queue.Queue()

	# put the data to queue
	# and the max data size is 100
	for i in range(testcase):
		my_queue.put(taskdata[i])

	# create the thread and start
	threads = []
	for i in range(number):
		threads.append(MyThread(my_queue, i, task))
		threads[i].start()

	# wait for the tthread to finish
	for i in range(number):
		threads[i].join()

## multiprocessing
from multiprocessing import Pool 

def multiprocessing(task, number, testcase, taskdata):
	pool = Pool(number)
	if task == 1:
		pool.map(proof_of_work, taskdata[:testcase])
	elif task == 2:
		pool.map(get_url_header, taskdata[:testcase])
	pool.close()
	pool.join()

## coroutine
import asyncio

async def co_proof_of_work(str, loop):
	await loop.run_in_executor(None, proof_of_work, str)
	
async def co_get_url_header(url, loop):
	html = await loop.run_in_executor(None, requests.get, url)
	soup = BeautifulSoup(html.text, 'html.parser')
	title = soup.head.title.text
	print(title)

def coroutine(task, testcase, taskdata):
	loop = asyncio.get_event_loop()
	if task == 1:
		tasks = [loop.create_task(co_proof_of_work(t, loop))
				 for t in taskdata[:testcase]]
	elif task == 2:
		tasks = [loop.create_task(co_get_url_header(t, loop))
				 for t in taskdata[:testcase]]
	loop.run_until_complete(asyncio.wait(tasks))
	
## task
# task 1
def proof_of_work(str):
	
	a = b = c = d = 33 # initialize
	while True:
		for e in range(33, 127):
			s = hashlib.sha256()
			str2 = chr(a)+chr(b)+chr(c)+chr(d)+chr(e)+str
			s.update(str2.encode('utf-8'))
			h = s.hexdigest()
			if h[:5]=="00000":
				print(str2)
				return str2
		d += 1
		if d > 126:
			c += 1
			d = 33
		if c > 126:
			b += 1
			c = 33
		if b > 126:
			a += 1
			b = 33
		if a > 126:
			break

# task 2
def get_url_header(url):
	
	html = requests.get(url)
	soup = BeautifulSoup(html.text, 'html.parser')
	title = soup.head.title.text
	print(title)
	return title

def debug(task, testcase, taskdata):
	if task == 1:
		for i in range(testcase):
			proof_of_work(taskdata[i])
	elif task == 2:
		for i in range(testcase):
			get_url_header(taskdata[i])

def main():
	task = int(input()) # input the task you want to execute: 1 or 2
	m = input() # input the method: 1: multithreading, 2: multiprocessing, 3: coroutine
	m = m.split()
	if(len(m)==2):
		number = int(m[1])
	method = int(m[0])
	testcase = int(input())
	
	# taskdata
	file = open("task%d_sample.txt"%task)
	taskdata = []
	for line in file:
		taskdata.append(line.replace('\n', ""))
		
	start = time.perf_counter()
	if method == 1:
		# use multithreading
		multithreading(task, number, testcase, taskdata)
	elif method == 2:
		# use multiprocessing
		multiprocessing(task, number, testcase, taskdata)
	elif method == 3:
		# use coroutine
		coroutine(task, testcase, taskdata)
	elif method == 4:
		# for debug
		debug(task, testcase, taskdata)
	end = time.perf_counter()
	print("Total running time: %f"%(end-start))
	
if __name__=="__main__":
	main()