var config = {
    counter: {currency: "CNY", issuer:"rnuF96W4SZoCJmbHYBFoJZpR8eCaxNvekK"},
    base: {currency: "XRP"}
}
var bottomlimit = 0.065;
var toplimit = 0.59;
counter_precision = 4;
base_precision = 1;
function fix(str,precision){
    return parseFloat(str).toFixed(precision).toString()
}

google.load("visualization", "1", {
  packages : [ "corechart" ]
});
google.setOnLoadCallback(drawChart);

var OrderBook = function(config) {
  this.config = config;
};
OrderBook.prototype = {
  config: null,
  silent: false,
  index : {
    bids : {},
    asks : {}
  },
  connect: function(callback) {
    function createSubscriptionMessage(id, base, counter) {
      return JSON.stringify({
        command: "subscribe", id: id, books: [{
          snapshot: true,
          taker_gets: base,
          taker_pays: counter
        }]
      });
    }
    var ob = this;
    var seen = {};
    var socket = "wss://s1.ripple.com:51233/";
    var websocket = new WebSocket(socket);
    websocket.onopen = function(evt) {
      websocket.send(createSubscriptionMessage(1, ob.config.base, ob.config.counter));
      websocket.send(createSubscriptionMessage(2, ob.config.counter, ob.config.base));
      ob.writeLog('正在建立连接...', 'info');
    };
    websocket.onclose = function(evt) {
      // silent close
    };
    websocket.onmessage = function(evt) {
      var data = JSON.parse(evt.data);
      console.log(data);
      if('transaction' in data && data.transaction.hash in seen) return;
      if(data.id) {
        ob.processBook(data.result.offers, data.id);
      } else if(data.engine_result == "tesSUCCESS") {
        ob.processTransaction(data);
        seen[data.transaction.hash] = 1;
      }
      if(data.id == 1) return;
      callback(ob.index);
      if(data.id == 2) ob.writeLog('连接成功，正在读取实时交易信息。');
    };
    websocket.onerror = function(evt) {
      // handle error
      ob.writeLog('连接出错。嗯?', 'info');
    };
  },
  _currencySimplifier : function(currency) {
    return typeof currency.value == 'undefined' ? currency / 1000000
        : parseFloat(currency.value);
  },
  _takerGets : function(order) {
    return typeof order.taker_gets_funded == 'undefined' ? this
        ._currencySimplifier(order.TakerGets) : this
        ._currencySimplifier(order.taker_gets_funded);
  },
  _takerPays : function(order) {
    return typeof order.taker_pays_funded == 'undefined' ? this
        ._currencySimplifier(order.TakerPays) : this
        ._currencySimplifier(order.taker_pays_funded);
  },
  processBook : function(orders, book) {
    this.silent = true;
    for ( var i in orders) this.saveOrder(orders[i], book);
    this.silent = false;
  },
  saveOrder : function(order, book) {
    var key = order.Account + '#' + order.Sequence;
    var temp = this.createOrder(order,book);
    switch (book) {
      case 1:
        this.index.asks[key] = temp;
      break;
      case 2:
        this.index.bids[key] = temp;
      break;
    }
    return temp;
  },
  createOrder : function(order, book) {
    var temp = {
      gets : this._takerGets(order),
      pays : this._takerPays(order),
      rate : 0
    }
    switch (book) {
      case 1:
        temp.rate = temp.pays / temp.gets;
      break;
      case 2:
        temp.rate = temp.gets / temp.pays;
      break;
    }
    return temp;
  },
  writeLog : function(text, color) {
    $('.live-feed').prepend( $('<p>').text(text).addClass(color) );
  },
  deleteOrder : function(key) {
    delete this.index.bids[key];
    delete this.index.asks[key];
  },
  notifyTrade : function(order, book) {
    if(book == 1) this.writeLog('卖出: '+ fix(order.pays,base_precision) + ' ' + this.config.base.currency + ' @ ' + fix(order.rate,counter_precision) + ' ' + this.config.counter.currency, 
    'red');
    else this.writeLog('买入: ' + fix(order.gets,base_precision) + ' ' + this.config.base.currency + ' @ ' + fix(order.rate,counter_precision) + ' ' + this.config.counter.currency,
    'green');
  },
  notifyOrder : function(order, book) {
    if(book == 1) this.writeLog('新卖单: ' + fix(order.gets,base_precision) + ' ' + this.config.base.currency + ' @ ' + fix(order.rate,counter_precision), 'black');
    else this.writeLog('新买单: ' + fix(order.pays,base_precision) + ' ' + this.config.base.currency + ' @ ' + fix(order.rate,counter_precision), 'black');
  },
  processTransaction : function(data) {
    var transaction = data.transaction;
    if(transaction.TransactionType == 'OfferCancel') {
      var key = transaction.Account + '#' + transaction.OfferSequence;
      this.deleteOrder(key);
      return;
    }
    if(transaction.TransactionType == 'OfferCreate') {
      var pays = typeof transaction.TakerPays.value == 'undefined' ? 'XRP' : transaction.TakerPays.currency;
      var book = pays == this.config.base.currency ? 2 : 1;
      // handle any trades / orders affected by this order
      for(var index in data.meta.AffectedNodes) {
        var n = undefined;
        var node = data.meta.AffectedNodes[index];
        if('DeletedNode' in node) {
          n = node.DeletedNode;
          if(!('PreviousFields' in n)) {
            // user has killed there own order on the other book, remove it
            this.deleteOrder(n.FinalFields.Account + '#' + n.FinalFields.Sequence);
            continue;
          }
        }
        if('ModifiedNode' in node) n = node.ModifiedNode;
        if(!n || n.LedgerEntryType != 'Offer') continue;
        if(!('TakerGets' in n.PreviousFields) || !('TakerPays' in n.PreviousFields)) continue;
        var oldorder = this.createOrder(n.PreviousFields, book == 1 ? 2 : 1);
        var neworder = this.createOrder(n.FinalFields, book == 1 ? 2 : 1);
        var traded = {
          gets: oldorder.gets - neworder.gets,
          pays: oldorder.pays - neworder.pays,
          rate: oldorder.rate,
        };
        if('ModifiedNode' in node) this.saveOrder(n.FinalFields, book == 1 ? 2 : 1);
        if('DeletedNode' in node) this.deleteOrder(n.FinalFields.Account + '#' + n.FinalFields.Sequence);
        this.notifyTrade(traded, book);          
      }
      // add the newly created order, or what's left of it.
      for(var index in data.meta.AffectedNodes) {
        var n = undefined;
        var node = data.meta.AffectedNodes[index];
        if('CreatedNode' in node) n = node.CreatedNode;
        if(!n || n.LedgerEntryType != 'Offer') continue;
        var nn = 'NewFields' in n ? n.NewFields : n.FinalFields;
        if(!('TakerGets' in nn) || !('TakerPays' in nn)) continue;
        var neworder = this.saveOrder(nn, book);
        this.notifyOrder(neworder, book);          
      }
      return;
    }
  }
};
var ob = new OrderBook(config);

function drawChart() {
  ob.connect(function(books) {
    // BIDS
    var coredata = [];
    var keys = [];
    for(var i in books.bids) {
      var floored = parseFloat(books.bids[i].rate).toFixed(counter_precision);
      if (typeof coredata[floored] == 'undefined') {
        coredata[floored] = 0;
        keys.push(floored);
      }
      coredata[floored] += books.bids[i].gets;
    }
    keys.sort(function(a, b) { return a - b; }).reverse();
    var chartdata = [];
    var total = 0;
    $('#bids tbody').empty();
    for(var x in keys) {
      if(keys[x] < bottomlimit) continue;
      $('#bids tbody').append(
        $('<tr>')
        .append($('<td>').text(keys[x]))
        .append($('<td>').text((coredata[keys[x]] / keys[x]).toFixed(base_precision)))
        .append($('<td>').text((coredata[keys[x]]).toFixed(counter_precision)))
      );
      total += (coredata[keys[x]]);
      chartdata.push([ keys[x] + "", Math.floor(total) ]);
    }
    chartdata.reverse();
    // asks
    coredata = [];
    keys = [];
    for ( var i in books.asks) {
      var ceiled = parseFloat(books.asks[i].rate).toFixed(counter_precision);
      if (typeof coredata[ceiled] == 'undefined') {
        coredata[ceiled] = 0;
        keys.push(ceiled);
      }
      coredata[ceiled] += books.asks[i].pays;
    }
    keys.sort(function(a, b) { return a - b; });
    total = 0;
    $('#asks tbody').empty()
    for(var x in keys) {
      if(keys[x] > toplimit) continue;
      $('#asks tbody').append(
        $('<tr>')
        .append($('<td>').text(keys[x]))
        .append($('<td>').text((coredata[keys[x]] / keys[x]).toFixed(base_precision)))
        .append($('<td>').text((coredata[keys[x]]).toFixed(counter_precision)))
      );
      total += (coredata[keys[x]]);
      chartdata.push([ keys[x] + "", Math.floor(total) ]);
    }
    chartdata.unshift([ config.base.currency,config.counter.currency ]);
    
    data = google.visualization.arrayToDataTable(chartdata);
    var options = {
      isStacked : true,
      legend : { position : 'none' },
      chartArea : { width : '100%', height : '75%' },
      titlePosition : 'in',
      axisTitlesPosition : 'in',
      hAxis : { textPosition : 'out' },
      vAxis : { textPosition : 'in'}
    };
    var chart = new google.visualization.SteppedAreaChart(document.getElementById('chart_div'));
    chart.draw(data, options);
  });
}

sfHover = function() {
	var sfEls = document.getElementById("dropdown").getElementsByTagName("LI");
	for (var i=0; i<sfEls.length; i++) {
		sfEls[i].onmouseover=function() {
			this.className+=" sfhover";
		}
		sfEls[i].onmouseout=function() {
			this.className=this.className.replace(new RegExp(" sfhover\\b"), "");
		}
	}
}
if (window.attachEvent) window.attachEvent("onload", sfHover);

