from mcp.server.fastmcp import FastMCP
import os
import library

mcp = FastMCP("NYUSH_Library_Navigator")

@mcp.tool()
def get_library_map(query: str) -> str:
    """
    查找房间（如 'N607'）或索书号（如 'QA76.5'）的具体视觉位置。
    返回文字说明和生成的地图图片路径。
    """
    try:
        result_msg, image_path = library.search_and_draw(query)
        # 获取图片的绝对路径，方便 AI 客户端读取
        full_path = os.path.abspath(image_path)
        return f"{result_msg} 地图局部截图已保存至: {full_path}"
    except Exception as e:
        return f"查询失败: {str(e)}"

if __name__ == "__main__":
    mcp.run()