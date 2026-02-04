import csv
from PIL import Image, ImageDraw
import os
import difflib  # 引入内置模糊匹配库

# 配置
DATA_FILE = 'locations.csv'

def find_location(query):
    query = query.strip().upper()
    if not os.path.exists(DATA_FILE): return None

    with open(DATA_FILE, mode='r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    best_match = None
    highest_score = 0

    for row in rows:
        name = row['name'].upper()
        call_id = row['call_start'].upper()
        
        # --- 策略 1：精确子串包含 (优先级最高) ---
        if query in name or query in call_id:
            return row # 只要包含，直接返回，这就是最准的

        # --- 策略 2：改进的模糊匹配 (处理拼写错误) ---
        # 我们不仅匹配全名，还要匹配名字里的每一个词
        # 比如把 "Researcher Room (N607)" 拆开
        words = name.replace('(', ' ').replace(')', ' ').split()
        words.append(call_id)
        
        for word in words:
            # 计算单词级别的相似度
            score = difflib.SequenceMatcher(None, query, word).ratio()
            
            # 如果单词匹配度极高 (比如 Resercher vs Researcher)
            if score > highest_score:
                highest_score = score
                best_match = row

    # 提高阈值到 0.7，防止乱匹配
    if highest_score > 0.7:
        return best_match

    # --- 策略 3：索书号范围 ---
    for row in rows:
        if row['type'].lower() == 'shelf':
            if row['call_start'].upper() <= query <= row['call_end'].upper():
                return row
    
    return None


def search_and_draw(query):
    """
    主入口：在完整地图上标点并返回
    """
    location = find_location(query)
    if not location:
        raise ValueError(f"找不到关于 '{query}' 的位置。")

    try:
        x, y = int(location['x']), int(location['y'])
        base_map_path = location['map_file']
        
        if not os.path.exists(base_map_path):
            raise FileNotFoundError(f"底图 {base_map_path} 不存在，请检查文件名是否正确。")
        
        # 打开底图
        img = Image.open(base_map_path)
        draw = ImageDraw.Draw(img)
        
        # --- 绘图逻辑：在完整地图上画一个醒目的标记 ---
        # 画一个大红点
        radius = 60 
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill="red", outline="white", width=15)
        # 画一个中心白点
        draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill="white")
        
        # 保存整张地图
        output_filename = f"full_map_{location['name'].replace(' ', '_')}.jpg"
        img.save(output_filename)
        
        msg = f"已在 {location['floor']} 地图上标注了 '{location['name']}' 的位置。"
        return msg, output_filename

    except Exception as e:
        raise Exception(f"生成地图失败: {str(e)}")