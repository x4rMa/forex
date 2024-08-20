from akash import calculate_rsi
from mt5_utils import get_live_data, trade_order, trade_order_wo_sl, trade_order_magic
from common_functions import check_duplicate_orders_time, write_json, check_duplicate_orders_magic

def boil_xian(symbol, window=20, num_std=2):

    accepted_symbol_list = ['XAUUSD']
    json_file_name = 'boil_xian'
    time_frame = 'M1'
    skip_min = 3

    if not symbol in accepted_symbol_list:
        # print('Symbol Not supported', symbol)
        return None

    running_trade_status_time, orders_json = check_duplicate_orders_time(symbol=symbol, skip_min=skip_min,
                                                               json_file_name=json_file_name)
    running_trade_status_magic = check_duplicate_orders_magic(symbol=symbol, code=0)
    if running_trade_status_time or running_trade_status_magic:
        return None

    df = get_live_data(symbol=symbol, time_frame=time_frame, prev_n_candles=100)

    # Function to calculate Bollinger Bands
    df['middle_band'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['middle_band'] + (num_std * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (num_std * df['std_dev'])

    curr_idx = -2
    prev_idx = -3

    action = None
    if df['high'].iloc[curr_idx] > df['upper_band'].iloc[curr_idx]:
        if df['open'].iloc[curr_idx] > df['close'].iloc[curr_idx]:
            action = 'sell'
            #band_diff = df['upper_band'].iloc[curr_idx] - df['middle_band'].iloc[curr_idx]
    elif df['low'].iloc[curr_idx] < df['lower_band'].iloc[curr_idx]:
        if df['open'].iloc[curr_idx] < df['close'].iloc[curr_idx]:
            action = 'buy'
            #band_diff = df['middle_band'].iloc[curr_idx] - df['lower_band'].iloc[curr_idx]

    high_band_diff = df['close'].iloc[curr_idx] - df['middle_band'].iloc[curr_idx]
    low_band_diff = df['middle_band'].iloc[curr_idx] - df['close'].iloc[curr_idx]

    if high_band_diff > 0:
        band_diff = high_band_diff
    else:
        band_diff = low_band_diff
    ## AVG Candle

    avg_high = (df['high'].iloc[-1] + df['high'].iloc[-2] + df['high'].iloc[-3] + df['high'].iloc[-4] + df['high'].iloc[
        -5] + df['high'].iloc[-6]) / 6
    avg_low = (df['low'].iloc[-1] + df['low'].iloc[-2] + df['low'].iloc[-3] + df['low'].iloc[-4] + df['low'].iloc[-5] +
               df['low'].iloc[-6]) / 6

    avg_candle_size = avg_high - avg_low

    # Tick Volume Analysis
    tick_signal = False
    if df['tick_volume'].iloc[-1] > df['tick_volume'].iloc[-2] > df['tick_volume'].iloc[-3]:
        tick_signal = True

    ## RSI
    df['RSI'] = calculate_rsi(df)

    rsi_action = None
    if df['RSI'].iloc[curr_idx] >= 70:
        ## Overbought
        if df['RSI'].iloc[curr_idx] < df['RSI'].iloc[prev_idx]:
            rsi_action = 'sell'
    elif df['RSI'].iloc[curr_idx] <= 30:
        ## Oversold
        if df['RSI'].iloc[curr_idx] > df['RSI'].iloc[prev_idx]:
            rsi_action = 'buy'

    if symbol == 'XAUUSD':
        ## 0.8 == 800
        avg_tp = avg_candle_size * 1000 * 1.5
        avg_sl = avg_candle_size * 1000 + df['spread'].iloc[-1]

    elif symbol == 'BTCUSD':
        avg_tp = avg_candle_size * 100 * 2
        avg_sl = avg_candle_size * 100 + df['spread'].iloc[-1]


    if symbol == 'XAUUSD':
        ## 0.8 == 800
        diff_tp = band_diff * 1000
        diff_sl = band_diff * 1000 * 1.5

    elif symbol == 'BTCUSD':
        diff_tp = band_diff * 100
        diff_sl = band_diff * 100 + df['spread'].iloc[-1]

    if avg_tp < diff_tp:
        tp = avg_tp
        sl = avg_sl
    else:
        tp = diff_tp
        sl = diff_sl

    print(symbol, ' ## AVG -->>',avg_candle_size,'## TP -->',tp,'## SL -->',sl, '## RSI -->>', df['RSI'].iloc[-1],rsi_action, '## Tick Power -->>',
          tick_signal, '## TP Diff-->> ', band_diff, '## Spread -->', df['spread'].iloc[-1])

    if tp < 500:
        print('LOW TP !!!!!!!')
        return
    lot = 0.1
    if action and (action == rsi_action):
        trade_order_magic(symbol=symbol, tp_point=tp, lot=lot, action=action, magic=True, code=0)
        write_json(json_dict=orders_json, json_file_name=json_file_name)
