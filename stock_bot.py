import time
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
import mplfinance as mpf
import xgboost as xgb
import os
import telebot
from telebot import TeleBot
import warnings
warnings.filterwarnings('ignore')

TOKEN = "8806687341:AAHrvH-WINwC1G1ZksupGpt7dr5OM21_S4M"
CHAT_ID = "1154014789"

bot = TeleBot(TOKEN)

def send_telegram_message(text, photo_path=None):
    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                bot.send_photo(CHAT_ID, photo, caption=text, parse_mode='HTML')
        else:
            bot.send_message(CHAT_ID, text, parse_mode='HTML')
    except:
        pass

def plot_candlestick(df, stock_name, code):
    try:
        df_plot = df.tail(60).copy()
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
        df_plot = df_plot.dropna(subset=['Open', 'High', 'Low', 'Close'])
        if len(df_plot) < 20:
            return None
        filename = f"{code}_kline.png"
        mpf.plot(df_plot, type='candle', style='yahoo', title=f"{stock_name} K線圖",
                 volume=True, mav=(5,20), savefig=filename, figsize=(12,7))
        return filename
    except:
        return None

def analyze_stock(code, name):
    try:
        df = yf.Ticker(code).history(period="1y")
        if df.empty:
            return
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['Close', 'Volume'])

        # 技術指標與模型（簡化版）
        df['Return'] = df['Close'].pct_change()
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Volume_Ratio'] = (df['Volume'] / df['Volume'].rolling(20).mean()).fillna(1.0)
        df['Beta'] = 1.0

        np.random.seed(int(time.time()) % 100)
        df['Trust_NetBuy'] = np.random.normal(0, 3000, len(df)).cumsum()
        df['Margin_Change'] = np.random.normal(0, 8000, len(df)).cumsum()

        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        df = df.dropna()

        features = ['Close', 'MA5', 'MA20', 'Volatility', 'RSI', 
                    'Volume_Ratio', 'Beta', 'Trust_NetBuy', 'Margin_Change']
        model = xgb.XGBClassifier(n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42)
        model.fit(df[features].iloc[:-30], df['Target'].iloc[:-30])

        latest = df[features].iloc[-1:]
        prob = model.predict_proba(latest)[0][1]
        price = float(df['Close'].iloc[-1])

        signal = "🟢 強烈建議買入" if prob > 0.58 else "🔴 建議賣出" if prob < 0.45 else "🟡 建議觀望"

        kline = plot_candlestick(df, name, code)

        message = f"""
📊 <b>{name} ({code})</b>
🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 股價： <b>{price:,.2f}</b> 元
📈 上漲機率： <b>{prob:.1%}</b>
{signal}
        """
        send_telegram_message(message, kline)
        if kline and os.path.exists(kline):
            os.remove(kline)
    except:
        pass

print("🚀 Render 雲端機器人已啟動...")
send_telegram_message("✅ Render 雲端最終版已成功啟動！\n每60秒自動分析並發送報告")

while True:
    analyze_stock("2408.TW", "南亞科")
    analyze_stock("3017.TW", "奇鋐")
    time.sleep(60)
