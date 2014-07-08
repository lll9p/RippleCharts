# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Main.ui'
#
# Created: Sun Dec  8 11:45:35 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

import sys
from MarketDepth import *
from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(711, 601)
        icon = QtGui.QIcon("./favicon.png")
        icon.addPixmap(QtGui.QPixmap("favicon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.quitButton = QtGui.QPushButton(self.centralwidget)
        self.quitButton.setObjectName("quitButton")
        self.gridLayout.addWidget(self.quitButton, 0, 1, 1, 1)

        '''self.updateButton = QtGui.QPushButton(self.centralwidget)
        self.updateButton.setObjectName("updateButton")
        self.gridLayout.addWidget(self.updateButton, 0, 0, 1, 1)'''

        self.tradeList = QtGui.QTableView(self.centralwidget)
        self.tradeListModel = QtGui.QStandardItemModel(0, 3, self)
        self.tradeListModel.setHeaderData(0, QtCore.Qt.Horizontal, "单")
        self.tradeListModel.setHeaderData(1, QtCore.Qt.Horizontal, "XRP")
        self.tradeListModel.setHeaderData(2, QtCore.Qt.Horizontal, "比率")
        self.tradeList.setModel(self.tradeListModel)
        self.tradeList.setObjectName("tradeView")
        self.gridLayout.addWidget(self.tradeList, 1, 0, 1, 1)

        self.depthGraphics = QtGui.QGraphicsView(self.centralwidget)
        self.depthGraphics.setObjectName("depthGraphics")
        self.gridLayout.addWidget(self.depthGraphics, 1, 1, 1, 1)

        self.asksTable = QtGui.QTableView(self.centralwidget)
        self.asksTable.setAlternatingRowColors(True)
        self.asksTable.setObjectName("asksTable")
        self.asksTable.setSortingEnabled(True)
        self.gridLayout.addWidget(self.asksTable, 3, 1, 1, 1)

        self.bidsTable = QtGui.QTableView(self.centralwidget)
        self.bidsTable.setObjectName("bidsTable")
        self.bidsTable.setAlternatingRowColors(True)
        self.bidsTable.setSortingEnabled(True)        
        self.gridLayout.addWidget(self.bidsTable, 3, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 711, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        #QtCore.QObject.connect(self.updateButton, QtCore.SIGNAL("clicked()"), lambda :self.clearTable(self.asksTableView))
        #QtCore.QObject.connect(self.updateButton, QtCore.SIGNAL("clicked()"), self.depthGraphics.update)
        QtCore.QObject.connect(self.quitButton, QtCore.SIGNAL("clicked()"), self.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tradeList, self.bidsTable)
        MainWindow.setTabOrder(self.bidsTable, self.asksTable)
        #MainWindow.setTabOrder(self.asksTable, self.updateButton)
        #MainWindow.setTabOrder(self.updateButton, self.quitButton)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.quitButton.setText(QtGui.QApplication.translate("MainWindow", "退出", None, QtGui.QApplication.UnicodeUTF8))
        #self.updateButton.setText(QtGui.QApplication.translate("MainWindow", "更新", None, QtGui.QApplication.UnicodeUTF8))

    def clearTable(self,model):
        if self.cleard:
            model.clear()
            self.cleard = True 
        else:
            self.asksTableView = self.updateTableModel(self.asksTable,header=["im ask"],data=["1","2"])
            self.cleard = False

    def addData(self,model,data):
        model.insertRow(0)
        for i in range(len(data)):
            model.setData(model.index(0, i), data[i])

    
    def addList(self,model,data,name):
        model.insertRow(0)
        model.setData(model.index(0, 0), name)
        if name == "新买单" or "卖单":
            xrp = round(data[0]/data[2],1)
        else:
            xrp = round(data[0])

        model.setData(model.index(0, 1), "%.1f" % xrp)
        model.setData(model.index(0, 2), "%.4f" % round(data[2],4))
        if name == "买单":
            for i in range(len(data[0])) :
                model.item(0).setBackground(QtGui.QColor(34,177,76))
        elif name == "卖单":
            for i in range(len(data[0])) :
                model.item(0,i).setBackground(QtGui.QColor(255,128,128))

    def updateTableModel(self,table,header,data):
        model = QtGui.QStandardItemModel(0, len(header), self)
        table.setModel(model)
        for i in range(len(header)):
            model.setHeaderData(i, QtCore.Qt.Horizontal, header[i])
        for info in data:
            self.addData(model, info)
        return model

if __name__ == '__main__':

    class Main(QtGui.QMainWindow,Ui_MainWindow):  
        def __init__(self,parent=None): #{{{
            super(Main,self).__init__(parent)  
            self.setupUi(self)
            self.cleard = False
            self.asksTableView = self.updateTableModel(self.asksTable,header=[""],data=[])
            self.bidsTableView = self.updateTableModel(self.bidsTable,header=[""],data=[])
            self.config = config
            self.retrivedata = None
            self.data = {"bids":{"original":[],"combined":[]},"asks":{"original":[],"combined":[]}}
            self.dataHeader={"original":["帐户","价格（CNY）","数量（XRP）","总价（CNY）"],
                             "combined":["账户","价格（CNY）","数量（XRP）","总价（CNY）","笔数"]}
            self.dataView = "combined"
            self.queues = []
            self.updateTime = 0.01
            self.updatelock = False
            self.getDataThread = threading.Thread(target = self.getData)
            self.getDataThread.daemon = True 
            self.getDataThread.setDaemon(1)
            self.getDataThread.start()
            self.updateDataThread = threading.Thread(target = self.updateData)
            self.updateDataThread.daemon = True 
            self.updateDataThread.setDaemon(1)
            self.updateDataThread.start()
        #}}}
        def index2List(self,index,name):#{{{
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
            if name == "asks" :
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
            #print(CList)
            self.data[name]={"normal":AList,"combined":list(CList)}
            #}}}

        def getData(self):#{{{
            self.retrivedata = retrieveData(config=self.config)
        #}}}
        
        def updateData(self):#{{{
            while 1:
                time.sleep(self.updateTime)
                try:
                    self.retrivedata
                    if len(self.retrivedata.queue) !=0 and not self.retrivedata.queuelock:
                        self.retrivedata.queuelock = True
                        result = self.retrivedata.queue.pop()
                        self.retrivedata.queuelock = False
                        if result:
                            bids = copy.deepcopy(result["index"]["bids"])
                            asks = copy.deepcopy(result["index"]["asks"])
                            tradeOrder = copy.deepcopy(result["tradeOrder"])
                            if "sold" in tradeOrder:
                                self.addList(self.tradeListModel,tradeOrder["sold"],"卖单")
                            if "bought" in tradeOrder:
                                self.addList(self.tradeListModel,tradeOrder["bought"],"买单")
                            if "newsell" in tradeOrder:
                                self.addList(self.tradeListModel,tradeOrder["newsell"],"新卖单")
                            if "newbuy" in tradeOrder:
                                self.addList(self.tradeListModel,tradeOrder["newbuy"],"新买单")

                            print("#########################"+str(tradeOrder))
                            self.index2List(bids,"bids")
                            self.index2List(asks,"asks")
                            self.asksTableView = self.updateTableModel(self.asksTable,header=self.dataHeader[self.dataView],data=self.data["asks"][self.dataView])
                            self.bidsTableView = self.updateTableModel(self.bidsTable,header=self.dataHeader[self.dataView],data=self.data["bids"][self.dataView])
                        continue
                    else:
                        #print("continued")
                        continue
                except:
                    pass
                    import traceback
                    traceback.print_exc()
                    #}}}

    app=QtGui.QApplication(sys.argv)  
    config = {
    "counter": {"currency": "CNY",
    #"issuer":"razqQKzJRdB4UxFPWf5NEpEG3WMkmwgcXA"#CHINA
    "issuer":"rnuF96W4SZoCJmbHYBFoJZpR8eCaxNvekK"#CN
    },
        "base": {"currency": "XRP"}
    }
    bottomlimit = 0.065;
    toplimit = 0.59;
    counter_precision = 4;
    base_precision = 1;
    json.dumps(config)
    window=Main()
    #window.setSourceModel(window.createTableModel(window,header=["ppp","ooo","pppdf","123"],data=None))
    window.show()  
    sys.exit(app.exec_())
