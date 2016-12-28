import time
from threading import Timer

def print_time():
	print 'Your time:', time.time()
	
def cancel_time():
	print 'Cancel function'
	
t1 = Timer(5, print_time, ())
t2 = Timer(10, cancel_time, ())

t1.start()
t2.start()

time.sleep(1)

t1.cancel()

t1 = Timer(5, print_time, ())

t1.start()

