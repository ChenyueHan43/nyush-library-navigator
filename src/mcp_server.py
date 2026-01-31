from mcp.server.fastmcp import FastMCP
import library  # 假设你之前的核心逻辑在这个文件里

# 1. 初始化 MCP 服务
mcp = FastMCP("NYUSH_Library_Navigator")

# 2. 定义一个“工具” (Tool)
# 这个描述非常重要，AI 就是根据这段话决定什么时候调用这个工具的
@mcp.tool()
def get_library_map(query: str) -> str:
    """
    Finds the visual location for a room name (e.g., 'N607') or 
    a Library of Congress call number (e.g., 'QA76.5').
    Returns a message and saves a map image.
    """
    try:
        # 调用你之前写的逻辑
        result_msg, image_path = library.search_and_draw(query)
        
        # 告诉 AI 结果和图片保存的位置
        return f"Result: {result_msg}. Map generated at: {image_path}"
    except Exception as e:
        return f"Error finding location: {str(e)}"

if __name__ == "__main__":
    mcp.run()