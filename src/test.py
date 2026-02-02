import library
import os

def quick_test():
    target = "N607" # 你可以换成任何 CSV 里有的名字
    print(f"--- 正在测试查找: {target} ---")
    
    try:
        msg, img_path = library.search_and_draw(target)
        print(f"成功！AI 回复: {msg}")
        print(f"地图路径: {os.path.abspath(img_path)}")
        
        # 自动打开生成的地图看一眼
        if os.name == 'nt': os.startfile(img_path)
        else: os.system(f"open {img_path}")
    except Exception as e:
        print(f"失败: {e}")

if __name__ == "__main__":
    quick_test()