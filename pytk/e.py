#!/usr/bin/env python
#coding:utf-8
import tkinter as tk
import tkinter.filedialog as filedialog
import os,sys,hashlib,json,urllib.request
from urllib.parse import urlencode
import threading
import queue
 
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.w=320
        self.h=200
        self.root = master
        self.root.bind("<Escape>",self.die)
        self.root.title("射手字幕下载器 By xzap")
#        self.root.iconbitmap("ico/32.ico")
        self.root.resizable(False, False)   #禁止修改窗口大小
        self.pack()
        self.createWidgets()
        self.center()
        self.queues = queue.Queue()
        self.count = 0
 
    def createWidgets(self):
        self.content = tk.StringVar()        
        self.content.set("")
        self.show = tk.Label(self,textvariable =self.content)
        self.show.pack() 
        self.texts = tk.Text(self,width=40,height=9)
        self.texts.tag_config('textcolor',foreground = 'red')
        self.texts.tag_add('textcolor','0.0','2.1')
        self.fileb = tk.Button(self,text="选择要下载字幕的文件，可多选",width=36,height=2,bd=2,command=self.fd)
        self.fileb.pack(pady=10)
        self.pathb = tk.Button(self,text="选择要下载字幕的文件夹，递归下载",width=36,height=2,bd=2,command=self.dd)
        self.pathb.pack()        
        self.backb = tk.Button(text="退出",width=10,height=1,command=self.root.quit)
        self.backb.pack(side="bottom",pady=10)
 
    def loop(self):        
    # if self.running == 1 :
        while self.queues.qsize():
            try:
                self.msg = self.queues.get(0)
                self.texts.insert("0.0",self.msg)
            except :
                pass
        self.after(200,self.loop)
 
    def center(self):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = int( (ws/2) - (self.w/2) )
        y = int( (hs/2) - (self.h/2) )
        self.root.geometry('{}x{}+{}+{}'.format(self.w, self.h, x, y))
 
    def die(self,event):
        self.root.destroy()
        self.root.quit()
 
    def bback(self):
        self.fileb.pack(pady=10)
        self.pathb.pack()
        self.backb['text'] = "退出"
        self.backb['command'] = self.root.quit
        self.texts.forget()  
 
    def bhide(self) :
        self.fileb.forget()
        self.pathb.forget()
        self.backb['text'] = "返回"
        self.backb['command'] = self.bback   
        self.texts.pack()
        self.backb['state'] = 'disabled'
 
    def fd(self):
        self.files = filedialog.askopenfilenames(
        title="请选择要下载字幕的文件，可多选",
        filetypes=[('视频文件', '*.mkv *.avi *.rmvb *.mp4 *.MKV'),('All files', '*'),])
        #initialdir='d:/Movie')
        if self.files :
            self.bhide() 
            self.gs = threading.Thread(target=self.getsub,args=(self.files,))
            self.gs.start()
                #self.gs.join()
        else :
            return
    def getsub(self,files) :
        self.filelist=root.tk.splitlist(files)
 
        for i in self.filelist :
            self.loop() 
 
            self.getsubs(i)
        self.queues.put("任务完成，共找到了{}个字幕".format(self.count))
        self.backb['state'] = 'normal'
 
 
    def dd(self):
        self.path = filedialog.askdirectory()
        if self.path :
            self.bhide()
            self.gs = threading.Thread(target=self.getpath,args=(self.path,))
            self.gs.start()
        else :
            return
 
    def getpath(self,path) :
        self.loop()
        self.queues.put("{}\n".format(self.path))
        self.mov_ext=["avi","rmvb","mkv","mp4","rm"]
        for d,fd,fl in os.walk(path) :
            for ff in fl :  
                self.f=os.path.realpath(os.path.join(d,ff))
                self.file_ext=os.path.splitext(self.f)[1][1:]
                if self.file_ext.lower() in self.mov_ext :
                    self.getsubs(self.f)
        self.queues.put("任务完成，共找到了{}个字幕".format(self.count))
        self.backb['state'] = 'normal'
 
 
 
    def getsubs(self,mvfile) :
        self.mvfile = mvfile
        self.BlockSize = 4096
        self.NumOfSegments = 4
        self.strHash = []
        self.fileLength = os.path.getsize(mvfile)
        self.offset = []
        self.offset.append(self.BlockSize)
        self.offset.append(self.fileLength / 3 * 2)
        self.offset.append(self.fileLength / 3)
        self.offset.append(self.fileLength - 8192)
 
        if os.path.isfile(self.mvfile):
            self.queues.put("正在为 {} 查找字幕请耐心等待……\n".format(self.mvfile))
            with open(self.mvfile,"rb")  as self.movie :
                for i in range(0,self.NumOfSegments):
                    self.movie.seek(int(self.offset[i]))
                    self.buff = self.movie.read(self.BlockSize)
                    self.m = hashlib.md5()
                    self.m.update(self.buff)
                    self.strHash.append(self.m.hexdigest())
        else :
            self.queues.put("File could not be opened\n")
            return
        self.hashstr=";".join(self.strHash)
        self.user_agent = "SPlayer Build 1543"
        #ContentType = "multipart/form-data; boundary=----------------------------{:x}".format(random.getrandbits(48))
        self.headers = {
        'User-Agent' : self.user_agent,
        #'Content-Type' : ContentType,
        'Connection' : 'Keep-Alive',
        'Expect' : '100-continue'
        }     
        self.postdata = urllib.parse.urlencode({
        'filehash': self.hashstr, 
        'pathinfo': self.mvfile,
        'format': 'json',
        'lang': 'Chn'
        })
        self.postdata=self.postdata.encode("utf8")
        for i in range(5) :    
            self.url="http://splayer"+str(i)+".shooter.cn/api/subapi.php"
            self.req = urllib.request.Request(self.url, self.postdata, self.headers)
            self.c = urllib.request.urlopen(self.req).read()
            # self.queues.put("正在 {} 查找字幕请耐心等待……\n".format(self.url))
            if len(self.c) >10 :
                break
            self.url="https://splayer"+str(i)+".shooter.cn/api/subapi.php"
            self.req = urllib.request.Request(self.url, self.postdata, self.headers)
            self.c = urllib.request.urlopen(self.req).read()
            # self.queues.put("正在 {} 查找字幕请耐心等待……\n".format(self.url))
            if len(self.c) >10 :
                break
        if len(self.c) < 10 :
            self.queues.put("没有找到任何字幕\n")
            return 
        self.jsondict = json.loads(self.c.decode("utf8"))
        self.links=[]
        self.ext =[]
        for i in self.jsondict :
            self.links.append(i['Files'][0]["Link"]) 
            self.ext.append(i['Files'][0]["Ext"])
        self.alllinks=[self.links,self.ext]
        self.count += len(self.links)
        self.queues.put("找到了 {} 个字幕，正在保存……\n".format(len(self.links)))    
        for i in range(len(self.links)):
             self.a=urllib.request.urlopen(self.links[i]).read()
             path=os.path.dirname(mvfile)
             #self.path="d:/Movie/srt"
             #self.mvfile=os.path.basename(self.mvfile)
             if i == 0 :
                self.name=os.path.join(self.path,self.mvfile[:-3]+self.ext[i])
             else:
                self.extt=self.mvfile[:-3]+"chn"+str(i)+"."+self.ext[i]
                self.name=os.path.join(self.path,self.extt)
             self.queues.put('{}\n'.format(self.name))       
             with open(self.name,"wb") as self.srtfile :
                self.srtfile.write(self.a)
 
 
 
if __name__ == "__main__" :
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
