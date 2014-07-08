#取出交易
from websocket import create_connection as cc
import json
import tkinter as tk
import threading
import queue
import time
from retrivedata import *
from table import *
from MarketDepth import *

def createSubscriptionMessage(id, base, counter):
    return json.dumps({
        "command": "subscribe", 
        "id": id, 
        "books": [{
            "snapshot": True,
            "taker_gets": base,
            "taker_pays": counter}]
    })
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.w=800
        self.h=500
        self.root = master
        self.root.title("Ripple 交易系统")
        #self.root.resizable(False, False)   #禁止修改窗口大小
        self.pack()
        self.createWidgets()
        self.queues = queue.Queue()
        self.depthCreated = 0

    def createWidgets(self):
        self.marketDepthb = tk.Button(self,text="市场深度",width=36,height=2,bd=2,command=self.createDepth)
        self.marketDepthb.pack(pady=10)
        self.orderb = tk.Button(self,text="交易",width=36,height=2,bd=2)
        self.orderb.pack()        
        self.quitb = tk.Button(text="退出",width=10,height=1,command=self.die)
        self.quitb.pack(side="bottom",pady=10)

    def createDepth(self):
        if self.depthCreated == 0:
            self.depthCreated = 1
            self.marketDepth = MarketDepth(master=tk.Toplevel(),config=config,topself=self)

    def die(self):
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    config = {
        "counter": {"currency": "CNY", "issuer":"rnuF96W4SZoCJmbHYBFoJZpR8eCaxNvekK"},
        "base": {"currency": "XRP"}
    }
    app = Application(master=root)
    app.mainloop()

    bottomlimit = 0.065;
    toplimit = 0.59;
    counter_precision = 4;
    base_precision = 1;
    json.dumps(config)

