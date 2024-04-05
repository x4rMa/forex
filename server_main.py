# This is a sample Python script.
import time
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from candlestick import candlestick


def ema(prices):
    tick = pd.DataFrame()
    ema = prices['close'].ewm(span=20).mean()
    a = ema.shift(1)
    return ema, a


def trendline(data, t):
    dhal = (data.iloc[-1] - data.iloc[0]) / (t - 0)

    return float(dhal)


def find_bollinger_signal(price, lower_band, upper_band):
    if price < lower_band:
        return 'buy'
    elif price > upper_band:
        return 'sell'
    else:
        return 'None'


def find_crossover_Ma(fast_sma, prev_fast_sma, slow_sma, mcd):
    # print(len(fast_sma),' ',len(prev_fast_sma),' ',len(slow_sma))
    price = 0
    dec = ""
    i = len(fast_sma) - 1
    # print(fast_sma[i], ' ', prev_fast_sma[i], ' ', slow_sma[i])
    # print('diff->', fast_sma[i] - slow_sma[i], ' ')

    if fast_sma[i] > slow_sma[i] and prev_fast_sma[i] < slow_sma[i]:
        # print('bullish crossover--->', fast_sma[i])
        j = i
        cnt = 0
        while j >= i - 10:
            if mcd[j] > 0:
                cnt = cnt + 1
            j = j - 1
        # print(j,' ',cnt)
        if cnt < 7:
            print('buy')
            price = fast_sma[i]
            dec = "buy"
    elif fast_sma[i] < slow_sma[i] and prev_fast_sma[i] > slow_sma[i]:
        # print('bearish crossover---->', fast_sma[i])
        j = i
        cnt = 0
        while j >= i - 10:
            if mcd[j] < 0:
                cnt = cnt + 1
            j = j - 1
        print(j, ' ', cnt)
        if cnt < 7:
            print('sell')
            price = fast_sma[i]
            dec = "sell"
    # for i in range(0,len(fast_sma)):
    else:
        dec = "None"

    return price, dec
    '''


    return 'None'''


def find_rsi_direction(rsis):
    print('')


def macd(prices):
    k = prices.ewm(span=12, adjust=False, min_periods=12).mean()
    # Get the 12-day EMA of the closing price
    d = prices.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    # Get the 9-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s

    return macd, macd_s, macd_h


def rsi(prices, rsi_period=14):
    """Compute the RSI given prices

    :param prices: pandas.Series
    :return: rsi
    """

    ''' # Calculate the difference between the current and previous close price
    delta = prices.diff()

    # Calculate the sum of all positive changes
    gain = delta.where(delta > 0, 0)

    # Calculate the sum of all negative changes
    loss = -delta.where(delta < 0, 0)

    # Calculate the average gain over the last n periods
    avg_gain = gain.rolling(n).mean()

    # Calculate the average loss over the last n periods
    avg_loss = loss.rolling(n).mean()

    # Calculate the relative strength
    rs = avg_gain / avg_loss

    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))
'''
    df = pd.DataFrame()
    df['gain'] = (prices['close'] - prices['open']).apply(lambda x: x if x > 0 else 0)
    df['loss'] = (prices['close'] - prices['open']).apply(lambda x: -x if x < 0 else 0)

    # here we use the same formula to calculate Exponential Moving Average
    df['ema_gain'] = df['gain'].ewm(span=rsi_period, min_periods=rsi_period).mean()
    df['ema_loss'] = df['loss'].ewm(span=rsi_period, min_periods=rsi_period).mean()

    # the Relative Strength is the ratio between the exponential avg gain divided by the exponential avg loss
    df['rs'] = df['ema_gain'] / df['ema_loss']

    # the RSI is calculated based on the Relative Strength using the following formula
    rsi = 100 - (100 / (df['rs'] + 1))
    return rsi


def ma(prices):
    tick = pd.DataFrame()

    a = prices['close'].rolling(50).mean()

    # tick['slow_sma'] = prices['close'].ewm(span=10, adjust=False).mean()
    a1 = a.shift(1)

    # tick['cross'] = np.vectorize(find_crossover_Ma)(tick['fast_sma'], tick['prev_fast_sma'], tick['slow_sma'])

    tick.dropna(inplace=True)
    return a, a1


def Strategy_Rsi_ma(price, time, lb, ub):
    r = rsi(price)
    m = ma(price, time)

    curr = r.iloc[-1]
    prev = r.iloc[-2]

    fast_sma = m['fast_sma'].iloc[-1]
    slow_sma = m['slow_sma'].iloc[-1]
    curr_price = price.iloc[-1]
    if fast_sma > curr_price:
        return 'sell'
    else:
        return 'buy'
    '''    if curr>=lb and curr<=ub:
        print(fast_sma,'  ',slow_sma,'  ',curr_price)
        if curr<ub and prev>ub :
            #print(r.to_string())
            print('sell ', curr)
            return 'sell'
        elif curr>lb and prev<lb :
            print('buy ', curr)
            return 'buy'''


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def Strategy_DoubleEma_macd(price, slow_p, fast_p):
    ema12 = ema(price['close'], period=slow_p)
    ema26 = ema(price['close'], period=fast_p)

    mcd, mcd_s, mcd_h = macd(price['close'])

    mcd_list = []
    mcd_s_list = []

    for i in range(33, len(mcd)):
        mcd_list.append(mcd.iloc[i])
    for i in range(33, len(mcd_s)):
        mcd_s_list.append(mcd_s.iloc[i])

    idx = np.argwhere(np.diff(np.sign(np.array(mcd_list) - np.array(mcd_s_list)))).flatten()
    if len(idx) > 0:
        print(mcd_s_list[idx[-1]])
        if mcd_s_list[idx[-1]] < 0:
            if mcd.iloc[-1] >= 0 and mcd.iloc[-1] < 0.1 and ema12.iloc[-1] > ema26.iloc[-1] and abs(
                    mcd.iloc[-1] - mcd_s.iloc[-1]) > 0.1:
                return 'buy', mcd_s_list[idx[-1]]
            else:
                return 'None', mcd_s_list[idx[-1]]
        elif mcd_s_list[idx[-1]] > 0:
            if mcd_s.iloc[-1] < 0 and mcd_s.iloc[-1] > -0.1 and ema12.iloc[-1] < ema26.iloc[-1] and abs(
                    mcd.iloc[-1] - mcd_s.iloc[-1]) > 0.1:
                return 'sell', mcd_s_list[idx[-1]]
            else:
                return 'None', mcd_s_list[idx[-1]]

        '''if ema12.iloc[-1]>ema26.iloc[-1]:
            return 'bull',mcd_s_list[idx[-1]]
        else:
            return 'bear',mcd_s_list[idx[-1]]'''
    else:
        return 'None', ''


def heikan_ashi(prices):
    df = prices.copy()

    df['HA_Close'] = (df.open + df.high + df.low + df.close) / 4

    df.reset_index(inplace=True)

    ha_open = [(df.open[0] + df.close[0]) / 2]
    [ha_open.append((ha_open[i] + df.HA_Close.values[i]) / 2) \
     for i in range(0, len(df) - 1)]
    df['HA_Open'] = ha_open

    df.set_index('index', inplace=True)

    df['HA_High'] = df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    df['HA_Low'] = df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    df['UP'] = df.HA_Close >= df.HA_Open

    prices['doji'] = 20 * abs(df['HA_Open'] - df['HA_Close']) <= (df['HA_High'] - df['HA_Low'])
    prices['Hammer'] = df['HA_Close'] >= (df['HA_High'] - (1 / 4) * (df['HA_High'] - df['HA_Low']))
    return prices['doji'], df, prices


def Strategy_candle(prices):
    df = prices.copy()
    d = pd.DataFrame()
    d['up'] = (df.close >= df.open)

    pattern = []
    # df = candlestick.doji(df, target='doji')
    df = candlestick.bullish_engulfing(df, target='bullish_engulfing')
    df = candlestick.bearish_engulfing(df, target='bearish_engulfing')
    df = candlestick.bearish_harami(df, target='bearish_harami')
    df = candlestick.bullish_harami(df, target='bullish_harami')
    df = candlestick.evening_star(df, target='evening_star')
    df = candlestick.morning_star(df, target='morning_star')
    # df = candlestick.dark_cloud_cover(df, target='dark_cloud_cover')
    # df = candlestick.doji_star(df, target='doji_star')
    # df = candlestick.dragonfly_doji(df, target='dragonfly_doji')
    # df = candlestick.hammer(df, target='hammer')
    df = candlestick.hanging_man(df, target='hanging_man')
    df = candlestick.inverted_hammer(df, target='inverted_hammer')
    # df = candlestick.piercing_pattern(df, target='piercing_pattern')
    # df = candlestick.rain_drop(df, target='rain_drop')
    for i in range(0, len(df['bullish_engulfing'])):
        pattern.append('None')
    for i in range(0, len(df['bullish_engulfing'])):

        if df['bullish_engulfing'].iloc[i] == True:
            pattern[i] = 'bullish_engulfing'
            print('bullish_engulfing')
        if df['bearish_engulfing'].iloc[i] == True:
            pattern[i] = 'bearish_engulfing'
            print('bearish_engulfing')
        if df['bearish_harami'].iloc[i] == True:
            pattern[i] = 'bearish_harami'
            print('bearish_harami')
        if df['bullish_harami'].iloc[i] == True:
            pattern[i] = 'bullish_harami'
            print('bullish_harami')
        if df['evening_star'].iloc[i] == True:
            pattern[i] = 'evening_star'
            print('evening_star')
        if df['morning_star'].iloc[i] == True:
            pattern[i] = 'morning_star'
            print('morning_star')
        if df['hanging_man'].iloc[i] == True:
            pattern[i] = 'hanging_man'
            print('hanging_man')
        if df['inverted_hammer'].iloc[i] == True:
            pattern[i] = 'inverted_hammer'
            print('inverted_hammer')

    return pattern


def bot_candle(symbol, lot):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=60),
                                 datetime.now())
    ticks_frame1 = pd.DataFrame(rates)
    # print(ticks_frame1)
    pattern = Strategy_candle(ticks_frame1)
    print(pattern)
    dec = 'None'
    if pattern[-2] == 'bullish_engulfing':
        dec = 'buy'
    elif pattern[-2] == 'bearish_engulfing':
        dec = 'sell'
    elif pattern[-2] == 'bearish_harami':
        dec = 'sell'
    elif pattern[-2] == 'bullish_harami':
        dec = 'buy'
    elif pattern[-2] == 'evening_star':
        dec = 'sell'
    elif pattern[-2] == 'morning_star':
        dec = 'buy'

    if dec == "buy":
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - 30 * point
        tp = price + 40 * point
        '''if sl>price:
            sl = price - 50 * point'''

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('not done')
        else:
            print('buy done with bot 1')
    elif dec == "sell":

        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid

        sl = price + 30 * point
        tp = price - 40 * point

        '''if sl<price:
            sl = price + 50 * point'''

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('not done')
        else:
            print('sell done with bot 1')
    else:
        print('kiccu korar nai')


def bot(symbol, lot):
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M10, datetime.now() - timedelta(minutes=3000),
                                 datetime.now())

    ticks_frame1 = pd.DataFrame(rates)
    ma100, a = ma(ticks_frame1)
    ema20, b = ema(ticks_frame1)
    mcd, mcd_s, mcd_h = macd(ticks_frame1['close'])
    p, dec = find_crossover_Ma(np.array(ema20), np.array(b), np.array(ma100), np.array(mcd_s))

    if dec == "buy":
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask
        sl = price - 50 * point
        tp = price + 80 * point
        '''if sl>price:
            sl = price - 50 * point'''

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('not done')
        else:
            print('buy done with bot 1')
    elif dec == "sell":

        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid

        sl = price + 50 * point
        tp = price - 80 * point

        '''if sl<price:
            sl = price + 50 * point'''

        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # send a trading request
        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('not done')
        else:
            print('sell done with bot 1')
    else:
        None


def Mt5():
    path = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    login = 124207670
    password = "abcdABCD123!@#"
    server = "Exness-MT5Trial7"
    timeout = 10000
    portable = False

    # Use a breakpoint in the code line below to debug your script.
    if not mt5.initialize(path=path, login=login,
                          server=server, password=password):
        print("initialize() failed, error code =", mt5.last_error())
        quit()

    # display data on connection status, server name and trading account
    print(mt5.terminal_info())
    # display data on MetaTrader 5 version
    print(mt5.version())

    ct = datetime.now() - timedelta(days=5)
    pt = ct - timedelta(minutes=30)
    ext = pt - timedelta(minutes=30)

    audusd_ticks = mt5.copy_ticks_range("XAUUSDm", ct - timedelta(minutes=1), ct, mt5.COPY_TICKS_ALL)
    rates = mt5.copy_rates_range("XAUUSDm", mt5.TIMEFRAME_M1, pt, ct)
    rates_prev = mt5.copy_rates_range("XAUUSDm", mt5.TIMEFRAME_M1, ext, ct)
    # print()
    ticks_frame = pd.DataFrame(rates)
    ticks_frame1 = pd.DataFrame(rates_prev)
    ticks_frame2 = pd.DataFrame(audusd_ticks)
    '''v = ticks_frame['tick_volume'].values
    tp = (ticks_frame['low'] + ticks_frame['close'] + ticks_frame['high']).div(3).values
    ticks_frame = ticks_frame.assign(vwap=(tp * v).cumsum() / v.cumsum())'''
    # print(ticks_frame)
    # ticks_frame['rsi']=rsi(ticks_frame)
    # ticks_frame['rsi'] = ticks_frame['rsi'].fillna(0)
    # ticks_frame['fast_sma'],ticks_frame['slow_sma'] = ma(ticks_frame)
    ema12 = ema(ticks_frame1['close'], period=12)
    ema26 = ema(ticks_frame1['close'], period=26)

    print(Strategy_DoubleEma_macd(ticks_frame1, 12, 26))

    mcd, mcd_s, mcd_h = macd(ticks_frame1['close'])
    # print(mcd)
    # print(mcd_s)
    fig, ax = plt.subplots(2, 2)
    width = .4
    width2 = .05

    # define up and down prices
    up = ticks_frame[ticks_frame.close >= ticks_frame.open]
    down = ticks_frame[ticks_frame.close < ticks_frame.open]

    # define colors to use
    col1 = 'green'
    col2 = 'red'

    # plot up prices
    ax[0, 0].bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    ax[0, 0].bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    ax[0, 0].bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    # plot down prices
    ax[0, 0].bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    ax[0, 0].bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    ax[0, 0].bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)

    ax[1, 1].plot(ticks_frame1['time'], ema12, 'C1', label='ask')
    ax[1, 1].plot(ticks_frame1['time'], ema26, 'C2', label='ask')
    ax[1, 1].plot(ticks_frame1['time'], ticks_frame1['close'], 'k', label='ask')

    # .plot(ticks_frame['time'], ticks_frame['close'], 'r', label='ask')
    # ax[0, 0].plot(ticks_frame['time'], ticks_frame['open'], 'g', label='ask')# row=0, col=0
    ax[1, 0].plot(ticks_frame1['time'], mcd, 'b', label='ask')
    ax[1, 0].plot(ticks_frame1['time'], mcd_s, 'k', label='ask')
    ax[0, 1].plot(ticks_frame2['time'], ticks_frame2['bid'], 'k', label='ask')  #
    ax[0, 1].plot(ticks_frame2['time'], ticks_frame2['ask'], 'b', label='ask')

    # plt.plot(ticks_frame['time'], a, 'C2', label='fast sma')

    # add the header
    plt.title('EURAUD ticks')

    # display the chart
    plt.show()

    # showing figure in output
    '''    fig = go.Figure(data=[go.Candlestick(x=ticks_frame.index,
                                         open=ticks_frame['open'],
                                         high=ticks_frame['high'],
                                         low=ticks_frame['low'],
                                         close=ticks_frame['close'], name='AAPL')])

    fig.add_trace(go.Scatter(
        x=ticks_frame.index,
        y=ticks_frame['vwap'],
        mode='lines',
        name='vwap',
        line=dict(color='royalblue', width=2)
    ))

    fig.update_layout(
        height=600
    )
    fig.show()'''
    ###EMA
    '''ticks_frame = pd.DataFrame(audusd_ticks)
    ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

    ema25 = ema(ticks_frame['ask'],period=25)
    ema50 = ema(ticks_frame['ask'], period=50)
    ema100 = ema(ticks_frame['ask'], period=100)
    #ema50.is_monotonic_increasing

    print(trendline(ema25,60))

    # display ticks on the chart
    plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
    plt.plot(ticks_frame['time'], ema25, 'b-', label='ema25')
    plt.plot(ticks_frame['time'], ema50, 'b-', label='ema50')
    plt.plot(ticks_frame['time'], ema100, 'b-', label='ema100')'''
    # plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')
    ###Bollingar bands
    ''' ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
    ticks_frame['sma']=ticks_frame['ask'].rolling(20).mean()
    ticks_frame['sd'] = ticks_frame['ask'].rolling(20).std()

    # calculate lower band
    ticks_frame['lb'] = ticks_frame['sma'] - 2 * ticks_frame['sd']

    # calculate upper band
    ticks_frame['ub'] = ticks_frame['sma'] + 2 * ticks_frame['sd']

    ticks_frame.dropna(inplace=True)
    ticks_frame['signal'] = np.vectorize(find_bollinger_signal)(ticks_frame['ask'], ticks_frame['lb'], ticks_frame['ub'])
    # display the legends
    print(ticks_frame)
    plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
    plt.plot(ticks_frame['time'], ticks_frame['lb'], 'b-', label='lb')
    plt.plot(ticks_frame['time'], ticks_frame['ub'], 'b-', label='ub')'''

    '''    #Moving Average
    ticks_frame['fast_sma'] = ticks_frame['ask'].rolling(10).mean()
    ticks_frame['slow_sma'] = ticks_frame['ask'].rolling(30).mean()

    ticks_frame['prev_fast_sma'] = ticks_frame['fast_sma'].shift(1)

    ticks_frame['crossover'] = np.vectorize(find_crossover_Ma)(ticks_frame['fast_sma'], ticks_frame['prev_fast_sma'], ticks_frame['slow_sma'])

    ticks_frame.dropna(inplace=True)

    #print(ticks_frame['crossover'])
    plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
    plt.plot(ticks_frame['time'], ticks_frame['fast_sma'], 'C1', label='fast sma')
    plt.plot(ticks_frame['time'], ticks_frame['slow_sma'], 'C2', label='slow sma')


    plt.legend(loc='upper left')

    # add the header
    plt.title('EURAUD ticks')

    # display the chart
    plt.show()


    r=rsi(ticks_frame['ask'])
    print(r)

    plt.plot(ticks_frame['time'], r, 'r-', label='ask')
    plt.legend(loc='upper left')

    # add the header
    plt.title('EURAUD ticks')

    # display the chart
    plt.show()
    plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')



    plt.legend(loc='upper left')

    # add the header
    plt.title('EURAUD ticks')

    # display the chart
    plt.show()
    '''
    mt5.shutdown()


def Mt5_backTest(muldhon, Current_time, window, totalTime):
    capital = muldhon
    pt = Current_time
    if not mt5.initialize(path="C:\Program Files\MetaTrader 5\\terminal64.exe", login=115557421,
                          server="Exness-MT5Trial6", password="FUCKnibirr2023#"):
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    print(mt5.terminal_info())
    print(mt5.version())
    trades = []
    total_ask = []
    total_time = []
    loss = 0
    labh = 0
    lot = 0.01
    symbol = 'EURUSDm'
    '''point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    sl = price - 50 * point
    tp = price + 100 * point

    print(price,'  ',sl,'  ',tp)
    deviation = 20
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # send a trading request
    result = mt5.order_send(request)
    print(result)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print('not done')
    else:
        print('done')'''
    prev_time = datetime.now().minute
    cur_time = prev_time
    while True:
        print(prev_time, '    ', cur_time)
        cur_time = datetime.now().minute
        if (cur_time % 10) == 0:
            print('new candle')
            prev_time = cur_time
            # print('-------------------|---------------------')
            orders_eurousdm = mt5.positions_get(symbol='EURUSDm')
            orders_usdjpym = mt5.positions_get(symbol='USDJPYm')

            orders_gbpusdm = mt5.positions_get(symbol='GBPUSDm')
            orders_eurjpym = mt5.positions_get(symbol='EURJPYm')
            orders_audusdm = mt5.positions_get(symbol='AUDUSDm')
            orders_usdcadm = mt5.positions_get(symbol='USDCADm')
            orders_gbpjpym = mt5.positions_get(symbol='GBPJPYm')

            if len(orders_eurousdm) < 1:

                print("Trade slot --------- > EURUSDm")
                bot_candle('EURUSDm', lot)
            else:
                None
                # print("Trade slot is not open for EURUSDm")

            if len(orders_usdjpym) < 1:
                # print("Trade slot --------- > USDJPYm")
                bot_candle('USDJPYm', lot)
            else:
                None

        '''
        if len(orders_gbpusdm)<1:
            print("Trade slot --------- >GBPUSDm")
            bot('GBPUSDm', lot)
        else:
            print("Trade slot is not open for GBPUSDm")

        if len(orders_eurjpym)<1:
            print("Trade slot --------- > EURJPYm")
            bot('EURJPYm', lot)
        else:
            print("Trade slot is not open for EURJPYm")

        if len(orders_audusdm)<1:
            print("Trade slot --------- > AUDUSDm")
            bot('AUDUSDm', lot)
        else:
            print("Trade slot is not open for AUDUSDm")

        if len(orders_usdcadm)<1:
            print("Trade slot --------- > USDCADm")
            bot('USDCADm', lot)
        else:
            print("Trade slot is not open for USDCADm")

        if len(orders_gbpjpym)<1:
            print("Trade slot --------- > GBPJPYm")
            bot('GBPJPYm', lot)
        else:
            print("Trade slot is not open for GBPJPYm")'''

        # bot('EURUSDm',lot)
        # bot('USDJPYm', lot)
        time.sleep(5)

        # ax[0, 1].plot(ticks_frame1['time'], mcd_h, 'C3', label='fast sma')

        # plt.plot(ticks_frame['time'], a, 'C2', label='fast sma')
        # ax[1, 0].plot(ticks_frame2['time'], r, 'C2', label='fast sma')

        # add the header

        # display the chart

        # time.sleep(5)

    """while True:

        #pt = ct - timedelta(minutes=30)
        #ext = pt - timedelta(minutes=30)

        pt =  pt+ timedelta(seconds=window)
        if pt>Current_time+totalTime and len(trades)==0:
            break

        symbol = "XAUUSDm"
        audusd_ticks = mt5.copy_ticks_range("EURUSD", pt - timedelta(minutes=1), pt, mt5.COPY_TICKS_ALL)
        rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M1, pt - timedelta(minutes=30), pt)
        rates_prev = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M1, pt - timedelta(minutes=60), pt)

        ticks_frame = pd.DataFrame(audusd_ticks)
        ticks_frame1 = pd.DataFrame(rates)
        ticks_frame2 = pd.DataFrame(rates_prev)

        #print(ticks_frame)

        total_ask.extend(ticks_frame['ask'])
        total_time.extend(ticks_frame['time'])
        print('------')
        print()
        if len(trades)>0:
            if trades[0]['B/S'] == 'Buy':
                for j in range(len(ticks_frame)):
                    print('bid->',ticks_frame.iloc[j]['bid'],'   ask->',ticks_frame.iloc[j]['ask'])
                    if ticks_frame.iloc[j]['bid'] >= trades[0]['tp']:

                        labh = labh + 1
                        muldhon = muldhon + (ticks_frame.iloc[j]['bid']-trades[0]['Price'])
                        print('sold','--',muldhon,'price ',trades[0]['Price'],' bid ',ticks_frame.iloc[j]['bid'])
                        trades.pop()
                        break
                    elif ticks_frame.iloc[j]['bid'] <= trades[0]['sl']:
                        muldhon = muldhon + (ticks_frame.iloc[j]['bid'] - trades[0]['Price'])
                        print('loss','--',muldhon,'price ',trades[0]['Price'],' bid ',ticks_frame.iloc[j]['bid'])
                        loss = loss + 1

                        trades.pop()
                        break
            else:
                for j in range(len(ticks_frame)):
                    print('bid->', ticks_frame.iloc[j]['bid'], '   ask->', ticks_frame.iloc[j]['ask'])
                    if ticks_frame.iloc[j]['ask'] <= trades[0]['tp']:

                        labh = labh + 1
                        muldhon = muldhon + ( trades[0]['Price'] - ticks_frame.iloc[j]['ask'] )
                        print('sold', '--', muldhon, 'price ', trades[0]['Price'], ' ask ', ticks_frame.iloc[j]['ask'])
                        trades.pop()
                        break
                    elif ticks_frame.iloc[j]['ask'] >= trades[0]['sl']:
                        muldhon = muldhon + (trades[0]['Price'] - ticks_frame.iloc[j]['ask'])
                        print('loss', '--', muldhon, 'price ', trades[0]['Price'], ' ask ', ticks_frame.iloc[j]['ask'])
                        loss = loss + 1

                        trades.pop()
                        break
                # print(i)
        else:
            #a,b=Strategy_DoubleEma_macd(ticks_frame2, 12, 26)
            #print(a)
            a,b=Strategy_candle(ticks_frame1)
            #a,b,c=heikan_ashi(ticks_frame1)
            r=rsi(ticks_frame2, rsi_period=14)
            print('  type->',a[-1],'   green->',b.iloc[-1])
            ema12 = ema(ticks_frame2['close'], period=12)
            ema26 = ema(ticks_frame2['close'], period=26)


            mcd, mcd_s, mcd_h = macd(ticks_frame2['close'])
            # print(mcd)
            # print(mcd_s)
            fig, ax = plt.subplots(2, 2)
            width = .4
            width2 = .05

            # define up and down prices
            up = ticks_frame1[ticks_frame1.close >= ticks_frame1.open]
            down = ticks_frame1[ticks_frame1.close < ticks_frame1.open]

            # define colors to use
            col1 = 'green'
            col2 = 'red'

            '''            # plot up prices
            ax[0, 0].bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
            ax[0, 0].bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
            ax[0, 0].bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

            # plot down prices
            ax[0, 0].bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
            ax[0, 0].bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
            ax[0, 0].bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)


            # plt.plot(ticks_frame['time'], a, 'C2', label='fast sma')
            ax[1, 0].plot(ticks_frame2['time'], r, 'C2', label='fast sma')
            # add the header
            plt.title('EURAUD ticks')

            # display the chart
            plt.show()'''



            #a=Strategy_Rsi_ma(ticks_frame['ask'],ticks_frame['time'],30,70)'''

            '''if a=='buy':
                price = ticks_frame.iloc[-1]['ask']

                # muldhon = muldhon - price
                sl = ticks_frame1.iloc[-1]['low']
                tp = ticks_frame1.iloc[-1]['high']+0.2
                d_row = {'Price': price, 'sl': sl, 'tp': tp, 'B/S': 'Buy'}
                print(d_row)
                # trades.append(d_row, ignore_index=True)
                trades.append(d_row)

            elif a=='sell':
                price = ticks_frame.iloc[-1]['bid']

                # muldhon = muldhon - price
                tp = ticks_frame1.iloc[-1]['low']-0.2
                sl = ticks_frame1.iloc[-1]['high']
                d_row = {'Price': price, 'sl': sl, 'tp': tp, 'B/S': 'Sell'}
                print(d_row)
                # trades.append(d_row, ignore_index=True)
                trades.append(d_row)'''"""

    print('Capital->', capital, 'capital-after->', muldhon, '  Loss->', loss, '  labh->', labh, 'simulation_time->',
          totalTime, 'Strategy->', 'random')

    '''    plt.plot(total_time,total_ask, 'C1', label='ask')
    print(len(total_ask))
    plt.legend(loc='upper left')

    # add the header
    plt.title('EURAUD ticks')


    # display the chart
    plt.show()'''
    mt5.shutdown()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Mt5()
    Mt5_backTest(5000, datetime.now() - timedelta(days=0.5), 60, timedelta(minutes=120))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
