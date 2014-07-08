import threading
import time
import random
from retrivedata import *
import copy
from operator import itemgetter

class MarketDepth(object):
    def __init__(self,config=None,topself=None):
        object.__init__(self)
        self.config = config
        self.topself = topself
        self.retrivedata = None
        self.data = {"bids":{"original":[],"combined":[]},"asks":{"original":[],"combined":[]}}
        self.dataHeader={"original":["帐户","价格（CNY）","数量（XRP）","总价（CNY）"],
                         "combined":["账户","价格（CNY）","数量（XRP）","总价（CNY）","笔数"]}
        self.dataView = "combined"
        self.queues = []
        self.updateTime = 1
        self.updatelock = False
        self.getDataThread = threading.Thread(target = self.getData)
        self.getDataThread.daemon = True 
        self.getDataThread.setDaemon(1)
        self.getDataThread.start()
        self.updateDataThread = threading.Thread(target = self.updateData)
        self.updateDataThread.daemon = True 
        self.updateDataThread.setDaemon(1)
        self.updateDataThread.start()
    
    def index2List(self,index,name):
        '''
        account|pay|rate|get|sum
        '''
        AList= [[ids.split("#")[0],round(index[ids]["rate"],4),round(index[ids]["gets"],1),round(index[ids]["pays"],1)] for ids in index.keys()]
        RList=(x for x in map(itemgetter(1),AList))
        CList = {}
        #with open("dan.txt",encoding="utf8",mode="w") as f:
        #    f.write(str(AList)+"\n")
        #print(RList)
        for rs in RList:
            count = 0
            CList[rs]=['',rs,0,0,0]
            for i,r,g,p in AList:
                if r==rs and rs!=0:
                    CList[rs][0]+=(i+"\n")
                    CList[rs][2]+=g
                    CList[rs][3]+=p
                    count+=1
            CList[rs][4]=count
        CList = CList.values()
        if name == "bids" :
            reverse = True
        else:
            reverse = False
        AList = sorted(AList, key=itemgetter(1),reverse = reverse)
        CList = sorted(CList, key=itemgetter(1),reverse = reverse)
        for row in AList:
            row[1]="%.4f" % row[1]
            row[2]="%.1f" % row[2]
            row[3]="%.1f" % row[3]
            if len(row)==5: row[4]=str(row[4])
        for row in CList:
            row[1]="%.4f" % row[1]
            row[2]="%.1f" % row[2]
            row[3]="%.1f" % row[3]
            if len(row)==5: row[4]=str(row[4])
        AList = [tuple(x) for x in AList]
        CList = [tuple(x) for x in CList]
        print(CList)
        self.data[name]={"normal":AList,"combined":list(CList)}

    def getData(self):
        '''while 1:
            time.sleep(self.updateTime)
            if len(self.queues) != 1:
                i = random.randint(1,100)
                print(i)
                self.queues.append(i)
        '''
        self.retrivedata = retrieveData(config=self.config)
        
    
    def updateData(self):
        '''while 1:
            time.sleep(self.updateTime)
            if len(self.queues) == 1 and self.topself.depthCreated ==1:
                self.text.insert("1.0",str(self.queues.pop())+"\n")
        '''
        while 1:
            time.sleep(0.01)
            try:
                self.retrivedata
                if len(self.retrivedata.queue) !=0 and not self.retrivedata.queuelock:
                    self.retrivedata.queuelock = True
                    result = self.retrivedata.queue.pop()
                    self.retrivedata.queuelock = False
                    if result:
                        #self.text.insert("1.0","取得数据："+"\n")
                        #self.text.insert("1.0","买单：" + str(result["index"]["bids"]) + "\n" +
                        #      "卖单：" + str(result["index"]["asks"]) + "\n" +
                        #      "交易：" + str(result["tradeOrder"]) + "\n"
                        #      )
                        bids = copy.deepcopy(result["index"]["bids"])
                        asks = copy.deepcopy(result["index"]["asks"])
                        self.index2List(bids,"bids")
                        self.index2List(asks,"asks")
                        '''while 1:
                            time.sleep(0.01)
                            if self.updatelock:
                                continue
                            else:
                                break
                            '''
                        self.topself.asksTableView = self.topself.updateTableModel(self.topself.asksTable,header=self.dataHeader[self.dataView],data=self.data["bids"][self.dataView])
                        self.topself.bidsTableView = self.topself.updateTableModel(self.topself.bidsTable,header=self.dataHeader[self.dataView],data=self.data["asks"][self.dataView])
                    continue
                else:
                    #print("continued")
                    continue
            except:
                pass
                import traceback
                traceback.print_exc()

