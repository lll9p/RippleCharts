import websocket
import threading
import time
import json
import copy
'''
{
"id": 1,
"command": "subscribe",
"books": 
    [
    {
    "snapshot": true,
    "taker_gets": {"currency": "CNY", "issuer":"rnuF96W4SZoCJmbHYBFoJZpR8eCaxNvekK"},
    "taker_pays": {"currency": "XRP"}
    }
    ]
    }
'''

class retrieveData(object):
    def __init__(self,config=None):
        self.config = config
        self.silent = False
        self.queue = []#[{"index":self.index,"tradeOrder":{}}]
        self.queuelock = False
        self.seen =[]
        self.index = {
            "bids":{},
            "asks":{}
        }
        self.tradeOrder = {
        }

        self.ws = websocket.WebSocketApp("wss://s1.ripple.com:51233/",
                on_message = self.on_message,
                on_error = self.on_error,
                on_close = self.on_close,
                on_open = self.on_open)
        self.wstr = threading.Thread(target = self.ws.run_forever,args=())
        self.wstr.setDaemon(True)
        self.wstr.start()


    def _currencySimplifier(self,currency):
        ret = None
        try:
            currency["value"]
            ret = float(currency["value"])
        except:
            ret = float(currency)/1000000
        return ret

    def _takerGets(self, order):
        ret = None
        try:
            order["taker_gets_funded"]
            ret = self._currencySimplifier(order["taker_gets_funded"])
        except:
            ret = self._currencySimplifier(order["TakerGets"])
        return ret

    def _takerPays(self,order):
        ret = None
        try:
            order["taker_pays_funded"]
            ret = self._currencySimplifier(order["taker_pays_funded"])
        except:
            ret = self._currencySimplifier(order["TakerPays"])
        return ret

    def processBook(self, orders, book):
        self.silent = True
        for i in range(len(orders)):
            self.saveOrder(orders[i], book)
        self.silent = False
    
    def processTransaction(self, data):
        transaction = data["transaction"]
        if transaction["TransactionType"] == "OfferCancel" :
            if "Account" not in transaction :
                #print("#80")
                pass
            key = transaction["Account"] + "#" + str(transaction["OfferSequence"])
            self.deleteOrder(key)
            return
        
        if transaction["TransactionType"] == "OfferCreate" :
            try:
                transaction["TakerPays"]["value"]
                pays = transaction["TakerPays"]["currency"]
            except:
                pays = "XRP"
            book = 2 if(pays == self.config["base"]["currency"]) else 1
            # handle any trades / orders affected by this order
            for node in data["meta"]["AffectedNodes"] : 
                n = None
                if "DeletedNode" in node : 
                    n = node["DeletedNode"]
                    if "PreviousFields" not in n :
                    # user has killed there own order on the other book, remove it
                        if "Account" not in n["FinalFields"] :
                            #print("#100")
                            pass
                        else:
                            self.deleteOrder(n["FinalFields"]["Account"] + "#" + str(n["FinalFields"]["Sequence"]))
                            continue

                if "ModifiedNode" in node : n = node["ModifiedNode"]
                if (not n) or n["LedgerEntryType"] != "Offer" : continue
                if ("TakerGets" not in n["PreviousFields"]) or ("TakerPays" not in n["PreviousFields"]) : continue
                oldorder = self.createOrder(n["PreviousFields"],2 if book == 1 else 1)
                neworder = self.createOrder(n["FinalFields"],2 if book == 1 else 1)
                traded = {
                  "gets": oldorder["gets"] - neworder["gets"],
                  "pays": oldorder["pays"] - neworder["pays"],
                  "rate": oldorder["rate"]
                }
                if "ModifiedNode" in node : self.saveOrder(n["FinalFields"],2 if book == 1 else 1)
                if "DeletedNode" in node :
                    if "Account" not in n["FinalFields"] :
                        #print("#116")
                        pass
                    else:
                        self.deleteOrder(n["FinalFields"]["Account"] + "#" + str(n["FinalFields"]["Sequence"]))
                self.notifyTrade(traded, book)
            #add the newly created order, or what"s left of it.
            for node in data["meta"]["AffectedNodes"] :
                n = None
                if "CreatedNode" in node : n = node["CreatedNode"]
                if (not n) or n["LedgerEntryType"] != "Offer" : continue
                nn = n["NewFields"] if "NewFields" in n else n["FinalFields"]
                if ("TakerGets" not in nn) or ("TakerPays" not in nn) : continue
                neworder = self.saveOrder(nn, book)
                self.notifyOrder(neworder, book)
            return
        
    def deleteOrder(self,key):
        self.index["bids"].pop(key,None)
        self.index["asks"].pop(key,None)

    def notifyTrade(self,order, book):
        if book == 1:
            self.tradeOrder = {"sold":(order["pays"],self.config["base"]["currency"],order["rate"],self.config["counter"]["currency"])}
        else:
            self.tradeOrder = {"bought":(order["gets"],self.config["base"]["currency"],order["rate"],self.config["counter"]["currency"])}

    def notifyOrder(self,order, book): 
        if book == 1:
            self.tradeOrder = {"newsell":(order["gets"],self.config["base"]["currency"],order["rate"])}
        else:
            self.tradeOrder = {"newbuy":(order["pays"],self.config["base"]["currency"],order["rate"])}

    def saveOrder(self, order, book):
        if "Account" not in order :
            #print("#151")
            pass
        else:
            key = order["Account"]+"#"+str(order["Sequence"])
            temp = self.createOrder(order,book)
            if book == 1:
                self.index["asks"].update({key:temp})
            elif book == 2:
                self.index["bids"].update({key:temp})
            return temp

    def createOrder(self,order, book):
        temp = {
            "gets" : self._takerGets(order),
            "pays" : self._takerPays(order),
            "rate" : 0
        }
        if book == 1:
            try:
                temp["rate"] = temp["pays"] / temp["gets"]
            except:
                temp["rate"] = 0
        elif book == 2:
            try:
                temp["rate"] = temp["gets"] / temp["pays"]
            except:
                temp["rate"] = 0
            temp["gets"],temp["pays"] = temp["pays"],temp["gets"]
        return temp

    def on_message(self,ws,message):
        print("data Got ")
        data = json.loads(message)
        self.seen=self.seen[-100:] #取最新的100条，防止list过大
        #print(len(self.seen))
        if 'transaction' in data:
            if data["transaction"]["hash"] in self.seen:
                return
        if "id" in data:
            while 1:
                print("id")
                time.sleep(0.01)
                if len(self.queue) == 0 and not self.queuelock:
                    self.queuelock == True
                    self.processBook(data["result"]["offers"], data["id"])
                    self.queue.append({"index":self.index,"tradeOrder":self.tradeOrder})
                    self.queuelock == False
                    return
                elif len(self.queue)!=0 or self.queuelock:
                    continue
        elif "engine_result" in data:
            if data["engine_result"] == "tesSUCCESS":
                while 1:
                    print("engine")
                    time.sleep(0.01)
                    if len(self.queue) == 0 and not self.queuelock:
                        self.queuelock == True
                        self.tradeOrder = {}
                        self.processTransaction(data)
                        self.queue.append({"index":self.index,"tradeOrder":self.tradeOrder})
                        self.seen.append(data["transaction"]["hash"])
                        self.queuelock == False
                        return
                    elif len(self.queue)!=0 or self.queuelock:
                        continue
        if "id" in data:
            if data["id"] == 1 :
                return
        if "id" in data:
            if data["id"] == 2 : 
                print('### 连接成功，正在读取实时交易信息。###')
                return

    def on_error(self,ws,error):
        print(error)
        self.restart()
        print("### 重新启动 。###")

    def on_close(self,ws):
        print("### 关闭连接。 ###")


    def createSubscriptionMessage(self,id, base, counter):
        return json.dumps({
            "command": "subscribe", 
            "id": id, 
            "books": [{
                "snapshot": True,
                "taker_gets": base,
                "taker_pays": counter}]
        })

    def on_open(self,ws):
        def run(*args):
            self.ws.send(self.createSubscriptionMessage(1, self.config["base"], self.config["counter"]))
            self.ws.send(self.createSubscriptionMessage(2, self.config["counter"], self.config["base"]))
        print("### 启动连接 ###")
        self.wsthread = threading.Thread(target=run, args=())
        self.wsthread.setDaemon(True)
        self.wsthread.start()

    def stop(self):
        self.wstr.join(1)

    def restart(self):
        self.stop()
        self.silent = False
        self.queue = []#[{"index":self.index,"tradeOrder":{}}]
        self.queuelock = False
        self.seen =[]
        self.index = {
            "bids":{},
            "asks":{}
        }
        self.tradeOrder = {
        }
        self.ws = websocket.WebSocketApp("wss://s1.ripple.com:51233/",
                on_message = self.on_message,
                on_error = self.on_error,
                on_close = self.on_close)
        self.wstr = threading.Thread(target = self.ws.run_forever,args=())
        self.wstr.setDaemon(True)
        self.wstr.start()
    #websocket.enableTrace(True)

if __name__ == "__main__" :
    def test(data=None):
        t = time.time()
        f = 1
        while 1:
            if time.time() - t > 15 and f==1:
                f=0
                print("closing websocket")
                data.restart()
                print("restarting websocket")
            #print("test")
            time.sleep(0.01)
            try:
                data
                if len(data.queue) !=0 and not data.queuelock :
                    data.queuelock = True
                    result = data.queue.pop()
                    if result:
                        print("取得数据：")
                        print("买单：" + str(len(result["index"]["bids"])) + "\n" +
                              "卖单：" + str(len(result["index"]["asks"])) + "\n" +
                              "交易：" + str(result["tradeOrder"]) + "\n"
                              )
                    data.queuelock = False
                    continue
                else:
                    #print("continued")
                    continue
            except:
                import traceback
                traceback.print_exc()
    config = {
            "counter": {"currency": "CNY", "issuer":"rnuF96W4SZoCJmbHYBFoJZpR8eCaxNvekK"},
            "base": {"currency": "XRP"}
            }
    data = retrieveData(config=config)
    threading.Thread(target = test,args=(data,)).start()
