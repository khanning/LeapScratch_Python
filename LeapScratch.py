############################################################################
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.   #
############################################################################

import sys, threading, socket, os, platform, time

plat = platform.system()
arch = platform.machine()
if plat == 'Linux':
	if arch == 'x86_64':
		sys.path.insert(0, 'lib/Linux/x64')
	else:
		sys.path.insert(0, 'lib/Linux/x86')
elif plat == 'Darwin':
	sys.path.insert(0, 'lib/Mac')
elif plat == 'Windows':
	if arch == 'AMD64':
		sys.path.insert(0, 'lib/Windows/x64')
	else:
		sys.path.insert(0, 'lib/Windows/x64')

import Leap

hands_array = [['hand-one',[0,0,0]],
	       ['hand-two',[0,0,0]]]

fingers_array = [['finger-one',[0,0,0]],
		 ['finger-two',[0,0,0]],
		 ['finger-three',[0,0,0]],
		 ['finger-four',[0,0,0]],
		 ['finger-five',[0,0,0]],
		 ['finger-six',[0,0,0]],
		 ['finger-seven',[0,0,0]],
		 ['finger-eight',[0,0,0]],
		 ['finger-nine',[0,0,0]],
		 ['finger-ten',[0,0,0]]]

class LeapListener(Leap.Listener):
    is_shutdown = False
    def on_init(self, controller):
        pass

    def on_connect(self, controller):
	refresh_screen()

    def on_disconnect(self, controller):
	refresh_screen()
	
    def on_exit(self, controller):
        pass

    def on_frame(self, controller):
        frame = controller.frame()

        if not frame.hands.empty:
            hand = frame.hands

	    for i in xrange(0,2):
	    	if hand[i].is_valid:
			hands_array[i][1] = hand[i].stabilized_palm_position

			fingers = hand[i].fingers
			if not fingers.empty:
				count = i * 5
				for finger in fingers:
					fingers_array[count][1] = finger.stabilized_tip_position
					count += 1
	    
	    if scratch_thread.is_registered:
                        response = '{"method":"update","params":['
			for i in xrange(0, 2):
				response += '["' + hands_array[i][0] + '-x","' + str(int(hands_array[i][1][0] + 50)) + '"],' \
					    '["' + hands_array[i][0] + '-y","' + str(int((hands_array[i][1][1] - 220) * 1.6)) + '"],' \
					    '["' + hands_array[i][0] + '-z","' + str(int(hands_array[i][1][2])) + '"],'
			for i in xrange(0, 10):
				response += '["' + fingers_array[i][0] + '-x","' + str(int(fingers_array[i][1][0] + 50)) + '"],' \
                                            '["' + fingers_array[i][0] + '-y","' + str(int((fingers_array[i][1][1] - 220) * 1.6)) + '"],' \
                                            '["' + fingers_array[i][0] + '-z","' + str(int(fingers_array[i][1][2])) + '"],'
			response += ']}\n'
                        scratch_thread.send(response)

class ScratchServer(threading.Thread):
	sock = None
	conn = None
	is_running = True
	is_registered = False
        
	def run(self):
                
		HOST = ''
                PORT = 50007
		
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind((HOST, PORT))
		except: 
			print('ERROR: Socket already in use')		
		while self.is_running:
			self.is_registered = False
			refresh_screen()
	        	try:
				self.sock.listen(1)
       	        		self.conn, addr = self.sock.accept()
			except socket.error as msg:
				print('Error: Socket already in use')
        		while self.is_running:
            			try: data = self.conn.recv(1024)
                		except: pass
				if not data: break
                		if '<policy-file-request/>' in data:
                    			self.conn.sendall('<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>\x00')
                        		self.sock.listen(1)
                        		self.conn, addr = self.sock.accept()
                        		self.is_registered = True
					refresh_screen()
				elif not self.is_registered and 'poll' in data:
					self.is_registered = True
					refresh_screen()
			self.is_registered = False
	def send(self, data):
		self.conn.send(data)
	def close(self):
		if self.is_registered:
			try:
				self.sock.shutdown(socket.SHUT_RDWR)
				self.sock.close()
			except: pass
		else:
			x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			x.connect(('127.0.0.1', 50007))
			x.close()

class ExitPrompt(threading.Thread):
        def run(self):
                input = None
                while input != 'q':
                        input = raw_input('')
			refresh_screen()
		scratch_thread.is_running = False
		scratch_thread.close()
		listener.is_shutdown = True
		controller.remove_listener(listener)
		clear_screen()

def refresh_screen():
	clear_screen()

	print('LeapScratch.py - Leap Motion to Scratch 2.0')
	print('Created by Kreg Hanning - 2013')
	print('')
	
	if plat == 'Windows':
		bold = ''
		red = ''
		green = ''
		none = ''
	else:
		bold = '\033[1m'
		red = '\033[91m'
		green = '\033[92m'
		none = '\033[0m'
	
	if controller.is_connected:
		print(bold + 'Leap Motion:  ' + green + 'Connected' + none)
	else:
		print(bold + 'Leap Motion:  ' + red + 'Not Connected' + none)

	if scratch_thread.is_registered:
		print(bold + 'Scratch 2.0:  ' + green + 'Connected' + none)
	else:
		print(bold + 'Scratch 2.0:  ' + red + 'Not Connected' + none)

	print('\nPress ' + bold + '[q] [ENTER]' + none + ' to Quit\n')

def clear_screen():
	if plat == 'Linux' or plat == 'Darwin':
		os.system('clear')
	elif plat == 'Windows':
		os.system('CLS')

scratch_thread = ScratchServer()

listener = LeapListener()
controller = Leap.Controller()
controller.set_policy_flags(controller.POLICY_BACKGROUND_FRAMES)
controller.add_listener(listener)

exit_thread = ExitPrompt()
exit_thread.start()

scratch_thread.start()
