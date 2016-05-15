from tkinter import *
from tkinter import font
from tkinter.ttk import *

from queue import Queue, Empty

from threading import Thread

from pythonosc import dispatcher, osc_server

import math

CHANNEL = 1
LAYER = 2

class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.grid(row=0, column=0, sticky='ew')
        self.makeWidgets()

        self.responseQueue = Queue()
        self.after(100, self.recieveResponses)

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/channel/%d/stage/layer/%d/file/time" % (CHANNEL, LAYER),
                            handle_time, self.responseQueue)
        self.dispatcher.map("/channel/%d/stage/layer/%d/file/path" % (CHANNEL, LAYER),
                            handle_file, self.responseQueue)

        self.server = osc_server.ThreadingOSCUDPServer(
            ("127.0.0.1", 5253), self.dispatcher)
        self.thread = Thread(target=runserver, args=(self.server,))
        self.thread.daemon = True
        self.thread.start()

    def makeWidgets(self):
        file = "Nothing"
        times = (0,0,0,0)
        left = (0,0)
        self.file = Label(self, font=font.Font(size=16, weight='bold'),
                                text="Playing:\n%s" % file,
                               justify='left')
        self.file.grid(row=0, column=0, sticky='ew', padx=(8,8), pady=(8,2))
        Separator(self, orient='horizontal').grid(row=1, column=0, sticky='ew')
        self.time = Label(self, font=font.Font(size=16, weight='bold'),
                                text="%d:%02d / %d:%02d" % times,
                               justify='left')
        self.time.grid(row=2, column=0, sticky='we', padx=(8,8), pady=(2,2))
        Separator(self, orient='horizontal').grid(row=3, column=0, sticky='ew')
        self.left = Label(self, font=font.Font(size=16, weight='bold'),
                                text="Time left: %d:%02d" % left,
                               justify='left')
        self.left.grid(row=4, column=0, sticky='ew', padx=(8,8), pady=(2,8))
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

    def updateTime(self, info):
        current, total = info
        current = math.floor(current)
        total = math.floor(total)
        cur_min, cur_sec = convert_seconds(current)
        tot_min, tot_sec = convert_seconds(total)
        rem = total - current
        rem_min, rem_sec = convert_seconds(rem)
        times = (cur_min, cur_sec, tot_min, tot_sec)
        rem_times = (rem_min, rem_sec)
        self.time.config(text="%d:%02d / %d:%02d" % times)
        self.left.config(text="Time left: %d:%02d" % rem_times)

    def updateFile(self, info):
        file = info
        self.file.config(text="Playing:\n%s" % file)
        self.file.grid(row=0, column=0, sticky='ew', padx=(8,8), pady=(8,2))

    def recieveResponses(self):
        try:
            response = self.responseQueue.get_nowait()
            while response != None:
                try:
                    if response[0] == 'TIME':
                        self.updateTime(response[1])
                    elif response[0] == 'FILE':
                        self.updateFile(response[1])
                    response = self.responseQueue.get_nowait()
                except Empty:
                    response = None
        except:
            pass
        finally:
            self.master.after(100, self.recieveResponses)

def handle_time(unused, args, *info):
    args[0].put_nowait(("TIME", info))

def handle_file(unused, args, *info):
    args[0].put_nowait(("FILE", info))

def runserver(server):
    server.serve_forever()

def convert_seconds(time, calc=math.floor):
    minutes = calc(time) // 60
    seconds = calc(time) % 60
    return minutes, seconds
        
root = Tk()
#root.minsize(300, 100)
root.title("OSC Video Timer")
img = PhotoImage(file="icons/clock.png")
root.tk.call('wm', 'iconphoto', root._w, img)
app = App(master=root)
app.mainloop()
try:
    root.destroy()
except:
    pass
app.server.shutdown()
