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

import sys, threading, socket, os, platform

VERSION = '0.3.0'
PLAT = platform.system()
ARCH = platform.machine()
PATH = os.path.dirname(os.path.realpath(__file__))

if PLAT == 'Linux':
    if ARCH == 'x86_64':
        sys.path.insert(0, PATH+'/lib/Linux/x64')
    else:
        sys.path.insert(0, PATH+'/lib/Linux/x86')
elif PLAT == 'Darwin':
    sys.path.insert(0, PATH+'/lib/Mac')
elif PLAT == 'Windows':
    if ARCH == 'AMD64':
        sys.path.insert(0, PATH+'/lib/Windows/x64')
    else:
        sys.path.insert(0, PATH+'/lib/Windows/x86')

import Leap

if '--nogui' in sys.argv: 
    noGUI = True
else: 
    noGUI = False
    from Tkinter import *
    import tkFont


class LeapListener(Leap.Listener):

    hands_array = [['hand-one','false',[0,0,0],'false'],
                   ['hand-two','false',[0,0,0],'false']]

    tools_array = [['tool-one','false',[0,0,0]],
                   ['tool-two','false',[0,0,0]]]

    fingers_array = [['finger-one','false',[0,0,0]],
                     ['finger-two','false',[0,0,0]],
                     ['finger-three','false',[0,0,0]],
                     ['finger-four','false',[0,0,0]],
                     ['finger-five','false',[0,0,0]],
                     ['finger-six','false',[0,0,0]],
                     ['finger-seven','false',[0,0,0]],
                     ['finger-eight','false',[0,0,0]],
                     ['finger-nine','false',[0,0,0]],
                     ['finger-ten','false',[0,0,0]]]

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
    
                    # Get Hand coords
                    if not PLAT == 'Linux':
                        self.hands_array[i][2] = hand[i].stabilized_palm_position
                    else:
                        self.hands_array[i][2] = hand[i].palm_position
            
                    # Hand is visible
                    self.hands_array[i][1] = 'true'
            
                    # Check if Hand is holding a tool
                    if not hand[i].tools.empty:
                        if not PLAT == 'Linux':
                            self.tools_array[i][2] = hand[i].tools[0].stabilized_tip_position
                        else:
                            self.tools_array[i][2] = hand[i].tools[0].tip_position
            
                    # Get the Fingers attached to the Hand
                    fingers = hand[i].fingers

                    # If more than 3 Fingers are visible mark the Hand as open
                    if fingers.__len__() > 3: self.hands_array[i][3] = 'true'
                    else: self.hands_array[i][3] = 'false'

                    # Get each visible Finger coords
                    count = i * 5
                    for n in xrange(0, 5):
                        if n < fingers.__len__():
                            self.fingers_array[count][1] = 'true'
                            if not PLAT == 'Linux':
                                self.fingers_array[count][2] = fingers[n].stabilized_tip_position
                            else:
                                self.fingers_array[count][2] = fingers[n].tip_position
                        else:
                            self.fingers_array[count][1] = 'false'
                        count += 1
                else:
                    # Hand is not visible
                    self.hands_array[i][1] = 'false'
        
        else:
            self.hands_array[0][1] = 'false'
            self.hands_array[1][1] = 'false'        

    
        if scratch_thread.is_registered:
            response = '{"method":"update","params":['
            for i in xrange(0, 2):
                response += '["' + self.hands_array[i][0] + '-x","' + str(int(self.hands_array[i][2][0])) + '"],' \
                            '["' + self.hands_array[i][0] + '-y","' + str(int((self.hands_array[i][2][1] - 220) * 1.6)) + '"],' \
                            '["' + self.hands_array[i][0] + '-z","' + str(int(self.hands_array[i][2][2])) + '"],' \
                            '["' + self.hands_array[i][0] + '-visible",' + self.hands_array[i][1] + '],' \
                            '["' + self.hands_array[i][0] + '-open",' + self.hands_array[i][3] + '],'
            for i in xrange(0, 2):
                response += '["' + self.tools_array[i][0] + '-x","' + str(int(self.tools_array[i][2][0])) + '"],' \
                            '["' + self.tools_array[i][0] + '-y","' + str(int((self.tools_array[i][2][1] - 220) * 1.6)) + '"],' \
                            '["' + self.tools_array[i][0] + '-z","' + str(int(self.tools_array[i][2][2])) + '"],' \
                            '["' + self.tools_array[i][0] + '-visible",' + self.tools_array[i][1] + '],'
            for i in xrange(0, 10):
                response += '["' + self.fingers_array[i][0] + '-x","' + str(int(self.fingers_array[i][2][0])) + '"],' \
                            '["' + self.fingers_array[i][0] + '-y","' + str(int((self.fingers_array[i][2][1] - 220) * 1.6)) + '"],' \
                            '["' + self.fingers_array[i][0] + '-z","' + str(int(self.fingers_array[i][2][2])) + '"],' \
                            '["' + self.fingers_array[i][0] + '-visible",' + self.fingers_array[i][1] + '],'
            response += ']}\n'
            scratch_thread.send(response)

class ScratchServer(threading.Thread):
        
    HOST = ''
    PORT = 50007
    sock = None
    conn = None
    is_running = True
    is_registered = False

    def run(self):
                
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.HOST, self.PORT))
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

class GUI:

    def __init__(self, master):

        self.logo = PhotoImage(file=PATH+'/res/logo.gif')
        self.red_led = PhotoImage(file=PATH+'/res/led_red.gif')
        self.green_led = PhotoImage(file=PATH+'/res/led_green.gif')
        self.btn_up = PhotoImage(file=PATH+'/res/btn_up.gif')
        self.btn_down = PhotoImage(file=PATH+'/res/btn_down.gif')

        bg_color = '#464646'
        fg_color = 'white'
        sub_color = '#BDBDBD'
        
        master.wm_title('LeapScratch')
        master.resizable(0,0)
        master.configure(background=bg_color)
        master.tk.call('wm', 'iconphoto', master._w, self.logo)
        master.protocol('WM_DELETE_WINDOW', gui_quit)
        
        title_font = tkFont.Font(family='Verdana', size=14, weight='bold')
        subtitle_font = tkFont.Font(family='Verdana', size=11)
        label_font = tkFont.Font(family='Verdana', size=13)

        self.title_frame = Frame(master)
        self.title_frame.configure(background=bg_color)
        Label(self.title_frame, font=title_font, bg=bg_color, fg=fg_color, text='Leap Motion to Scratch 2.0').pack()
        self.title_frame.pack(padx=30, pady=10)

        self.body_frame = Frame(master)
        self.body_frame.configure(background=bg_color)
        self.leap_status = Label(self.body_frame, bg=bg_color, image=self.red_led)
        self.leap_status.grid(row=0, column=0, sticky=W)
        Label(self.body_frame, text='Leap Motion', bg=bg_color, fg=fg_color, font=label_font).grid(row=0, column=1, padx=10, sticky=W)
        self.scratch_status = Label(self.body_frame, bg=bg_color, image=self.red_led)
        self.scratch_status.grid(row=1, column=0, sticky=W)
        Label(self.body_frame, text='Scratch 2.0', bg=bg_color, fg=fg_color, font=label_font).grid(row=1, column=1, padx=10, sticky=W)
        self.body_frame.pack(pady=3)
        
        self.foot_frame = Frame(master)
        self.foot_frame.configure(background=bg_color)
        self.quit_btn = Label(self.foot_frame, bg=bg_color, image=self.btn_up)
        self.quit_btn.bind('<Button-1>', self.quit_toggle)
        self.quit_btn.bind('<ButtonRelease-1>', self.quit)
        self.quit_btn.pack(pady=(10, 2))
        Label(self.foot_frame, font=subtitle_font, bg=bg_color, fg=sub_color, text='Created by Kreg Hanning 2013').pack(side=LEFT)
        Label(self.foot_frame, font=subtitle_font, bg=bg_color, fg=sub_color, padx=5, text='v'+VERSION).pack(side=RIGHT)
        self.foot_frame.pack(fill=X, padx=5, pady=(0,3))
        
    def quit(self, item):
        gui_quit()
        
    def quit_toggle(self, event):
        self.quit_btn.config(image=self.btn_down)
                
    def set_status(self, dev, connected):
        if dev == 'leap':
            if connected:
                self.leap_status.config(image=self.green_led)
            else:
                self.leap_status.config(image=self.red_led)
        elif dev == 'scratch':
            if connected:
                self.scratch_status.config(image=self.green_led)
            else: 
                self.scratch_status.config(image=self.red_led)

class ExitPrompt(threading.Thread):
    def run(self):
        input = None
        while input != 'q' and input != 'Q':
            input = raw_input('')
            refresh_screen()
        scratch_thread.is_running = False
        scratch_thread.close()
        listener.is_shutdown = True
        controller.remove_listener(listener)
        clear_screen()


def refresh_screen():

    if noGUI:
        clear_screen()

        print('LeapScratch.py - Leap Motion to Scratch 2.0')
        print('Created by Kreg Hanning - 2013')
        print('')
    
        if PLAT == 'Windows':
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
    else:
        gui.set_status('leap', controller.is_connected)
        gui.set_status('scratch', scratch_thread.is_registered)

def clear_screen():
    if PLAT == 'Linux' or PLAT == 'Darwin':
        os.system('clear')
    elif PLAT == 'Windows':
        os.system('CLS')

def gui_quit():
    scratch_thread.is_running = False
    scratch_thread.close()
    listener.is_shutdown = True
    controller.remove_listener(listener)
    root.quit()

scratch_thread = ScratchServer()

listener = LeapListener()
controller = Leap.Controller()
controller.set_policy_flags(controller.POLICY_BACKGROUND_FRAMES)

if noGUI:
    exit_thread = ExitPrompt()
    exit_thread.start()

    controller.add_listener(listener)

    scratch_thread.start()
else:
    root = Tk()
    gui = GUI(root)

    controller.add_listener(listener)

    scratch_thread.start()

    root.mainloop()
    root.destroy()
