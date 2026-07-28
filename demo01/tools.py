import requests
import os
from tavily import TavilyClient

def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        # 格式化成自然语言返回
        return f"{city}当前天气:{weather_desc}，气温{temp_c}摄氏度"
        
    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"




def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，使用Tavily Search API搜索并返回优化后的景点推荐。
    """
    # 1. 从环境变量中读取API密钥
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误:未配置TAVILY_API_KEY环境变量。"

    # 2. 初始化Tavily客户端
    tavily = TavilyClient(api_key=api_key)
    
    # 3. 构造一个精确的查询
    query = f"'{city}' 在'{weather}'天气下最值得去的旅游景点推荐及理由"
    
    try:
        # 4. 调用API，include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)
        
        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get("answer"):
            return response["answer"]
        
        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"- {result['title']}: {result['content']}")
        
        if not formatted_results:
             return "抱歉，没有找到相关的旅游景点推荐。"

        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)

    except Exception as e:
        return f"错误:执行Tavily搜索时出现问题 - {e}"


# ============================================================
# 增强功能：用户画像 & 门票查询
# ============================================================

# 模块级用户画像存储（记忆功能）
_user_profile = {}

# 模拟售罄列表（Demo 用）
_SOLD_OUT_ATTRACTIONS = {"故宫", "环球影城", "迪士尼"}


def update_user_preference(key: str, value: str) -> str:
    """记录用户偏好到内存。Agent 发现用户偏好时调用。"""
    _user_profile[key] = value
    return f"已记录用户偏好: {key} = {value}"


def get_user_preferences() -> str:
    """读取所有已记录的用户偏好。Agent 在推荐前应调用此工具。"""
    if not _user_profile:
        return "暂无用户偏好记录。"
    items = [f"- {k}: {v}" for k, v in _user_profile.items()]
    return "用户偏好:\n" + "\n".join(items)


def check_ticket_availability(attraction: str, date: str = "today") -> str:
    """
    模拟查询景点门票是否可购（Demo 用）。
    部分热门景点会返回"已售罄"以触发备选推荐逻辑。
    """
    for sold_out in _SOLD_OUT_ATTRACTIONS:
        if sold_out in attraction:
            return f"❌ {attraction} 在 {date} 的门票已售罄，请推荐其他景点。"
    return f"✅ {attraction} 在 {date} 的门票可购买。"
