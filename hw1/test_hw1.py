import time # to calculate the running time

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

async def co_proof_of_work(str):
	proof_of_work(str)
	
async def co_get_url_header(url):
	get_url_header(url)
	
async def co_main(task, testcase, taskdata):
	if task == 1:
		for i in range(testcase):
			todo = asyncio.create_task(co_proof_of_work(taskdata[i]))
	elif task == 2:
		for i in range(testcase):
			todo = asyncio.create_task(co_get_url_header(taskdata[i]))

def coroutine(task, testcase, taskdata):
	asyncio.run(co_main(task, testcase, taskdata))
	
## task
import hashlib 

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
 
import requests

# task 2
def get_url_header(url):
	
	from bs4 import BeautifulSoup
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

timer = []
def main(task, method, number, testcase):
	# task = int(input()) # input the task you want to execute: 1 or 2
	# m = input() # input the method: 1: multithreading, 2: multiprocessing, 3: coroutine
	# m = m.split()
	# if(len(m)==2):
		# number = int(m[1])
	# method = int(m[0])
	# testcase = int(input())
	
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
	# print("Total running time: %f"%(end-start))
	timer.append(end-start)
	
if __name__=="__main__":
	# main(2, 2, 100, 100)
	# main(2, 2, 100, 100)
	# main(2, 2, 100, 100)
	# main(2, 2, 4, 100)
	# main(2, 2, 4, 100)
	# main(2, 2, 4, 100)
	# main(2, 2, 2, 100)
	# main(2, 2, 2, 100)
	# main(2, 2, 2, 100)
	main(2, 4, 1, 100)
	main(2, 4, 1, 100)
	main(2, 4, 1, 100)
	print("time 100: %f %f %f"%(timer[0], timer[1], timer[2]))
	# print("time 4: %f %f %f"%(timer[3], timer[4], timer[5]))
	# print("time 2: %f %f %f"%(timer[6], timer[7], timer[8]))
	# print("time 1: %f %f %f"%(timer[9], timer[10], timer[11]))