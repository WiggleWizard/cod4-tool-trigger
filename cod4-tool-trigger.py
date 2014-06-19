import socket
import time
import random

import threading
import subprocess

# ==================================================== #
# Fiddles (for now)
# ==================================================== #
SERVER_IP      = "127.0.0.1"
SERVER_PORT    = 28960
PCNT_THRESHOLD = 6 # Player count threshold
PROC           = ""

Q_TIME    = 60 # Seconds between queries
PROC_TIME = 50 # Seconds the process runs for

# Local RX/TX ports
QPORT_MIN = 28961
QPORT_MAX = 30000


# ==================================================== #
# Process helper.
# Runs a process for x seconds and then terminates it.
# ==================================================== #
class Runner(threading.Thread):
	def __init__(self, seconds, cmd):
		self.seconds = seconds
		self.cmd     = cmd
		self.proc    = None
		threading.Thread.__init__(self)

	def run(self):
		self.proc = subprocess.Popen(self.cmd.split(), shell=False,
							 stdout = subprocess.PIPE,
							 stderr = subprocess.PIPE)
		time.sleep(self.seconds)
		self.proc.terminate()


# ==================================================== #
# Main.
# ==================================================== #
while True:
	# Send a request for "status" to the server
	try:
		# Set up UDP socket comms
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		port = random.randint(QPORT_MIN, QPORT_MAX);
		sock.bind(("", port))
		sock.settimeout(2);
		
		print("Querying from port %s to %s:%s" % (port, SERVER_IP, SERVER_PORT))
		sock.sendto("\xff\xff\xff\xff\rgetstatus\0", (SERVER_IP, SERVER_PORT))
		data, addr  = sock.recvfrom(2048) # buffer size is 1024 bytes

		# Split the data up so we can parse through it
		dataSplit   = data.split("\x0a")
		playerCount = len(dataSplit) - 3

		# If the threshold is reached then exec
		if(playerCount >= PCNT_THRESHOLD):
			print("Threshold of %s players reached (%s total), executing" % (PCNT_THRESHOLD, playerCount))
		
			runner = Runner(PROC_TIME, PROC)
			runner.start()

			time.sleep(PROC_TIME)
			
	except:
		sock.close()
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		newPort = random.randint(QPORT_MIN, QPORT_MAX);
		sock.bind(("", newPort))
		print("Lost session, recreating on port %s" % (newPort))

	time.sleep(Q_TIME)
