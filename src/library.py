import csv
from PIL import Image, ImageDraw
import os
import difflib  # 引入内置模糊匹配库

# 配置
DATA_FILE = 'locations.csv'

def find_location(query):
    """
    增强版搜索逻辑：
    1. 精确/包含匹配 (Exact/Partial Match)
    2. 模糊匹配 (Fuzzy Match - 处理拼写错误)
    3. 索书号范围匹配 (Range Match)
    """
    query = query.strip().upper()
    
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # --- 第一阶段：精确或包含匹配 ---
    # 比如输入 "N607" 直接中，或者 "Researcher" 命中 "Researcher Room"
    for row in rows:
        name = row['name'].upper()
        call_start = row['call_start'].upper()
        if query == call_start or query in name:
            return row

    # --- 第二阶段：模糊匹配 (处理拼写错误) ---
    # 比如输入 "Resercher" (漏了 a) 或者 "N608" (想找相邻的)
    best_match = None
    highest_score = 0
    
    for row in rows:
        # 尝试匹配名字和 ID
        targets = [row['name'].upper(), row['call_start'].upper()]
        for target in targets:
            # SequenceMatcher 计算相似度 (0.0 - 1.0)
            score = difflib.SequenceMatcher(None, query, target).ratio()
            
            # 设置阈值，通常 0.6 以上认为是有意义的匹配
            if score > highest_score and score > 0.6:
                highest_score = score
                best_match = row
    
    if best_match:
        # 如果模糊匹配分值很高（比如 > 0.8），直接认为找到了
        # 如果在 0.6~0.8 之间，你也可以在日志里记录一下
        return best_match

    # --- 第三阶段：匹配索书号范围 (针对书架) ---
    # 这一步保持你原来的逻辑，用于处理 QA76 这种在 A-D 范围内的逻辑
    for row in rows:
        if row['type'].lower() == 'shelf':
            # 简单的字母序判断
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