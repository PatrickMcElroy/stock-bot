import robin_stocks as r
import datetime
import sched, time


s = sched.scheduler(time.time, time.sleep)

# the stocks we are trading with
#stocks = ["BTC"]
r.login("pdmcelroy@cox.net", "s9ozbzkNv$T5S8IHPm$h", expiresIn = 86400) # change expiresIn
trailing_stop = False
trailing_buy = False
# runs every minute to check if a buy or sell order should be generated
def check_market(sc):
    print("Checking market...")
    global trailing_stop
    global trailing_buy

    # Log in to Robinhood app (will prompt for two-factor)

    # get open crypto positions
    past_crypto = r.orders.get_all_crypto_orders()
    bought_at = (past_crypto[1]["average_price"])
    open_crypto = r.crypto.get_crypto_positions("cost_bases")
    btc_purchase_price = open_crypto[0][0]["direct_cost_basis"]
    btc_quantity = open_crypto[0][0]["direct_quantity"]
    
    low_prices = r.crypto.get_crypto_historicals("BTC", "15second", "hour", "24_7", "low_price")
    open_prices = r.crypto.get_crypto_historicals("BTC", "15second", "hour", "24_7", "open_price")
    day_prices = r.crypto.get_crypto_historicals("BTC", "5minute", "day", "24_7", "open_price")
    current_price = r.crypto.get_crypto_quote("BTC", "ask_price")
    
    min = 0
    full = 0
    lows = 0
    i = 0
    for open in open_prices:
        i += 1
        full += float(open)
        if (i > 220):
            min += float(open)
    average_price_hour = full/240
    average_price_5_minutes = min/20
            
    fulll = 0
    i = 0
    for price in day_prices:
        i +=1
        full += float(price)
    average_price_day = full/288
    
    


    if (float(btc_quantity) == 0.0 and not trailing_buy): # buy if price is low
        percent_diff = (float(current_price)/float(open_prices[0]) - 1) * 100
        print("The current price is $" + current_price + ". The price an hour ago was $" + open_prices[0] + ". Percent difference is " + str(percent_diff) + "%.")
        if (percent_diff < -.8):
            trailing_buy = True
            print("Trailing buy triggered at $" + current_price + ".")
        else:
            trailing_buy = False
    
    if (trailing_buy):
        percent_diff = (float(open_prices[220])/float(current_price) - 1) * 100
        if (percent_diff >= .2):
            r.orders.order_buy_crypto_by_price("BTC", 100, timeInForce='gtc', jsonify=True)
            print("Bought BTC for $" + current_price + ".")
            trailing_buy = False
            time.sleep(45)

    # sell if a % profit can be generated
    if (float(btc_quantity) != 0.0 and not trailing_stop):
        bought_at = (past_crypto[0]["average_price"])
        percent_diff = 100*(float(current_price)/float(bought_at) - 1)
        print("The current price is $" + current_price + ". We bought at around $" + bought_at + " and we now have a " + str(percent_diff) + "% difference.")
        if (percent_diff > 1):
            trailing_stop = True
            print("Trailing stop triggered at $" + current_price + ".")
            
            
    if (trailing_stop):
        percent_diff = (float(open_prices[220])/float(current_price) - 1) * 100
        if (percent_diff <= -.2):
            r.orders.order_buy_crypto_by_price("BTC", 100, timeInForce='gtc', jsonify=True)
            print("Bought BTC for $" + current_price + ".")
            trailing_stop = False
            time.sleep(45)
        
    
    # buy if price is within .05% of hourly low and previous position is closed
    #

#    positions = r.account.get_open_stock_positions()

#    urls = r.account.get_open_stock_positions("instrument")
#
#
#    print(position_tickers)
#
#    print(r.orders.get_all_open_stock_orders())
#
#    # sell if the a 2% profit could be generated for the position
#    for stock in positions:
#        ticker = r.get_symbol_by_url(stock["instrument"])
#        last_updated = stock["updated_at"][0:10]
#        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
#        bought_at = stock["average_buy_price"]
#        current_price = r.stocks.get_quotes(ticker, "ask_price")[0]
#        if (float(bought_at) != 0):
#            if (float(current_price)/float(bought_at) > 1.01 and current_date != last_updated):
#                profit = float(current_price) - float(bought_at)
#                print("Sold " + ticker + " for " + str(profit) + " profit.")
#                r.order_sell_market(ticker, stock["quantity"])
#
#
#    for stock in stocks:
#        sum = 0
#        n = 0
#        for open_price in r.stocks.get_stock_historicals(stock, "hour", "week", "regular", "open_price") :
#            sum += float(open_price)
#            n += 1.0
#        average_open_price = sum/n
#        current_price = r.stocks.get_quotes(stock, "ask_price")[0]
#
#        if(float(current_price)/average_open_price < .985 and not (stock in position_tickers)):
#            position_tickers.append(stock)
#            print("Bought " + stock + " for " + current_price)
#            print(position_tickers)
#            r.order_buy_fractional_by_price(stock, 100, 'gfd', 'ask_price')




    s.enter(1, 1, check_market, (sc,)) # change first number to change time between market checking


s.enter(1, 1, check_market, (s,))
s.run()
#has_bought_today = 0
