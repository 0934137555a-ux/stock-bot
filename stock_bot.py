import time
import datetime
import pandas as pd
import numpy as np
import yfinance as yf
import telebot
from telebot import TeleBot
import warnings
warnings.filterwarnings('ignore')

TOKEN = "8806687341:AAHrvH-WINwC1G1ZksupGpt7dr5OM21_S4M"
CHAT_ID = "1154014789"

bot = TeleBot(TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(CHAT_ID, text, parse_mode='HTML')
        print("✅ Telegram 已發送")
    except Exception as e:
        print(f"❌ Telegram 發送失敗: {e}")

print("🚀 Render 除錯診斷版已啟動...")
send_telegram_message("✅ 除錯診斷版已啟動！\n開始每60秒發送報告")

def analyze_stock(code, name):
    try:
        df = yf.Ticker(code).history(period="1y")
        if df.empty:
            raise ValueError("無法下載資料")

        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['Close', 'Volume'])

        price = float(df['Close'].iloc[-1])
        volume = float(df['Volume'].iloc[-1])

        # 模擬資金流
        np.random.seed(int(time.time()) % 100)
        foreign = np.random.randint(-8000, 10000)
        trust = np.random.randint(-3000, 5000)
        dealer = np.random.randint(-2000, 3000)
        total = foreign + trust + dealer

        message = f"""
📊 <b>{name} ({code}) 診斷報告</b>
🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 目前股價： <b>{price:,.2f} 元</b>
📊 成交量： {volume:,.0f} 股

🏦 模擬三大法人：
• 外資 {foreign:+,} 張
• 投信 {trust:+,} 張
• 自營 {dealer:+,} 張
• 合計 <b>{total:+,} 張</b>
        """
        send_telegram_message(message)
        print(f"✅ {name} 報告已發送")

    except Exception as e:
        error_msg = f"❌ {name} 錯誤: {str(e)[:100]}"
        print(error_msg)
        send_telegram_message(error_msg)

# ================== 主循環 ==================
while True:
    analyze_stock("2408.TW", "南亞科")
    analyze_stock("3017.TW", "奇鋐")
    time.sleep(60)
