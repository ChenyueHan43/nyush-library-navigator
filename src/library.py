import csv
from PIL import Image, ImageDraw
import os

# 配置
DATA_FILE = 'locations.csv'

def find_location(query):
    """搜索逻辑：匹配房间名、ID 或 索书号范围"""
    query = query.strip().upper()
    
    with open(DATA_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 1. 匹配房间名或 ID
    for row in rows:
        if query == row['call_start'].upper() or query in row['name'].upper():
            return row

    # 2. 匹配索书号范围 (针对书架)
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