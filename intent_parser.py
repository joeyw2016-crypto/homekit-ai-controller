"""
AI 意图解析模块：自然语言指令 → 结构化设备控制指令
示例输入："把客厅的灯打开" → {"device": "客厅灯", "action": "on"}
"""
from modules.llm_client import call_llm

INTENT_PROMPT = """你是智能家居控制中枢。把用户的自然语言指令解析成 JSON，格式：
{"device": "设备名", "action": "on|off|brightness", "value": 数值(仅brightness时), "room": "房间(可选)"}
设备只允许：灯、插座、风扇。动作只允许：on/off/brightness。
只输出 JSON，不要解释。"""


def parse_intent(text):
    """解析自然语言指令，返回 dict"""
    raw = call_llm(INTENT_PROMPT, f"用户指令：{text}")
    # 提取 JSON 部分
    import json
    import re
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return {"error": f"无法解析: {raw}"}
    try:
        return json.loads(match.group())
    except Exception as e:
        return {"error": f"JSON解析失败: {e}, 原始: {raw}"}
