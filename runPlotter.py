import numpy as np
import sys
import time
import subprocess
import os

checkTime = 1 #seconds between checks of stdout
istart = 0

def waitproc(proc, startval):
	while proc.poll() is None:
		time.sleep(checkTime) #check this every x seconds
		for line in iter(proc.stdout.readline, b''):
			x = line.decode("utf-8").split()

			if (x[0].strip() == 'plotting'):
				try:
					startval = int(x[1].strip())
				except:
					print("bad startval ", startval)

			if (x[0].strip() == 'done.'):
				return -1

			print(">>> " + line.decode("utf-8"), startval)
	return startval

def followProcess(istart=0):
	proc = subprocess.Popen(['./plotPaths.py', '-i', str(istart)], stdout=subprocess.PIPE)

	startval = waitproc(proc, istart)

	print('process finished...', startval)

	if (int(startval) > 0):
		istart = startval
		print('restarting with istart = ',istart)
		followProcess(istart)

	else:
		print('finished.')


if __name__ == "__main__":

	followProcess(istart=istart);
	
