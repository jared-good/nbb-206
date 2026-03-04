import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fix_and_load_json(raw_data):
    """自動修復斷尾的 JSON 數據，不再報錯"""
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        try:
            # 發現斷尾，暴力補上結尾括號
            fixed_data = raw_data.strip()
            if not fixed_data.endswith(']'):
                if fixed_data.endswith('}'):
                    fixed_data += ']'
                else:
                    fixed_data += '"}]' 
            return json.loads(fixed_data)
        except Exception as e:
            print(f"⚠️ 老闆，數據格式破壞太嚴重無法修復：{e}")
            return []

def get_playsport_odds(date_str):
    """瘋狗進攻模式：直連抓取玩運彩最新盤口"""
    print(f"🔥 正在鎖定 {date_str} 玩運彩運彩盤口...")
    url = f"https://www.playsport.cc/livescore/2?mode=2&gamedate={date_str}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        games = []
        # 尋找賽事區塊 (若玩運彩改版，需配合微調 class name)
        game_blocks = soup.select('.team-block') if soup.select('.team-block') else soup.select('table tr')
        
        if not game_blocks:
            print("⚠️ 抓取不到賽事，可能無官方開盤或遭遇防護牆。")
            return games

        for game in game_blocks:
            # 簡易防錯抓取邏輯
            text_content = game.text.strip()
            if "vs" in text_content.lower() or "-" in text_content:
                games.append({"raw_info": text_content[:50].replace('\n', ' ')})
                
        return games
    except Exception as e:
        print(f"❌ 盤口對接失敗：{e}")
        return []

def calculate_pnl(data):
    """無限制結算系統 (解除所有注額上限，全速衝刺)"""
    total_profit = sum(item.get('p', 0) for item in data)
    print("\n=====================================")
    print(f"💰 瘋狗進攻模式 - 總損益結算：{total_profit:+.2f} u")
    print("=====================================\n")
    return total_profit

if __name__ == "__main__":
    # 1. 載入並修復你之前報錯的歷史操盤數據
    raw_json_input = """[
{"n":"火腿","p":17.6,"date":"2026-03-04T11:40:35.558Z"},
{"n":"養","p":-20,"date":"2026-03-04T11:40:28.744Z"},
{"n":"歐","p":17.6,"date":"2026-03-04T11:40:22.907Z"},
{"n":"澳2","p":-20,"date":"2026-03-04T10:01:42.460Z"},
{"n":"澳1","p":-20,"date":"2026-03-04T10:01:38.134Z"},
{"n":"快1","p":17.6,"date":"2026-03-03T05:09:01.897Z"}""" # 這裡故意留斷尾測試
    
    print("🛠️ 正在修復歷史數據並啟動無限制結算...")
    betting_history = fix_and_load_json(raw_json_input)
    calculate_pnl(betting_history)

    # 2. 測試對接明早 (3/5) 的玩運彩盤口
    live_odds = get_playsport_odds("20260305")
    if live_odds:
        print("🎯 成功抓取最新盤口資訊：")
        for idx, game in enumerate(live_odds[:5]): # 先印出前 5 筆預覽
            print(f"[{idx+1}] {game['raw_info']}")
