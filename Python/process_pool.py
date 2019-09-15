from multiprocessing import Pool
import os, time, random

NUM_PROCESSINGS = 3

def task(name):
	start = time.time()
	print("Child process {} run task {}".format(os.getpid(), name))
	time.sleep(random.random() * 3)
	end = time.time()
	print("Child process {} run task {} for {:.6f} second".format(os.getpid(), name, (end-start)))

if __name__ == '__main__':
	print("Parent process {}".format(os.getpid()))

	# 每次最多运行NUM_PROCESSINGS个进程
	pool = Pool(NUM_PROCESSINGS)
	for x in range(NUM_PROCESSINGS+1):
		pool.apply_async(task, args=(x,))
	print("Waiting all subprocessings finish...")
	pool.close()
	pool.join()
	print("All subprocessings finished.")
