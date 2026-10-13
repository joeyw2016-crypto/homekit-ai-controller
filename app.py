"""
FastAPI 主服务：统一入口
- POST /api/ai          : AI 自然语言控制（"把灯打开"）
- GET/POST /api/devices : 设备状态管理
- GET /                 : 网页控制面板
"""
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from modules.intent_parser import parse_intent

app = FastAPI(title="HomeKit AI Controller")

# 设备状态（内存模拟；对接真实 HomeKit 配件时可扩展为读写桥接层）
DEVICES = {
    "灯": {"type": "light", "state": "off", "brightness": 100},
    "插座": {"type": "switch", "state": "off"},
    "风扇": {"type": "fan", "state": "off"},
}


def apply_action(device_name, action, value=None):
    """把结构化指令落到设备状态"""
    for key, dev in DEVICES.items():
        if key in device_name:  # 模糊匹配："客厅的灯" -> "灯"
            if action == "on":
                dev["state"] = "on"
                return f"{key}已打开"
            if action == "off":
                dev["state"] = "off"
                return f"{key}已关闭"
            if action == "brightness" and value is not None:
                dev["brightness"] = max(0, min(100, int(value)))
                dev["state"] = "on" if dev["brightness"] > 0 else "off"
                return f"{key}亮度调到{dev['brightness']}%"
    return f"未找到设备：{device_name}"


@app.post("/api/ai")
async def ai_control(request: Request):
    """AI 自然语言控制接口"""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        return JSONResponse({"error": "缺少 text 字段"}, status_code=400)

    intent = parse_intent(text)
    if "error" in intent:
        return JSONResponse(intent, status_code=422)

    result = apply_action(intent.get("device", ""), intent.get("action", ""), intent.get("value"))
    return {"intent": intent, "result": result, "devices": DEVICES}


@app.get("/api/devices")
async def list_devices():
    return {"devices": DEVICES}


@app.post("/api/devices/{device}/on")
async def turn_on(device: str):
    return {"result": apply_action(device, "on")}


@app.post("/api/devices/{device}/off")
async def turn_off(device: str):
    return {"result": apply_action(device, "off")}


@app.get("/", response_class=HTMLResponse)
async def panel():
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>HomeKit AI 控制台</title>
<style>body{font-family:system-ui;max-width:600px;margin:40px auto}
.card{border:1px solid #ddd;border-radius:12px;padding:16px;margin:12px 0}
button{font-size:16px;padding:8px 16px;margin:4px;border-radius:8px;border:none;cursor:pointer}
.on{background:#4CAF50;color:#fff}.off{background:#f44336;color:#fff}</style></head>
<body><h1>HomeKit AI 控制台</h1>
<div class="card"><h3>AI 指令（例：把客厅的灯打开）</h3>
<input id="cmd" style="width:70%;padding:8px" placeholder="说点什么来控制设备...">
<button onclick="ai()">发送</button><pre id="out"></pre></div>
<div id="devices"></div>
<script>
async function ai(){const t=document.getElementById('cmd').value;
const r=await fetch('/api/ai',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});
document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}
async function act(d,a){await fetch(`/api/devices/${d}/${a}`,{method:'POST'});load();}
async function load(){const r=await fetch('/api/devices');const j=await r.json();
let h='';for(const [k,v] of Object.entries(j.devices)){
h+=`<div class="card"><b>${k}</b> (${v.state}${v.brightness?' '+v.brightness+'%':''})<br>
<button class="on" onclick="act('${k}','on')">开</button>
<button class="off" onclick="act('${k}','off')">关</button></div>`;}
document.getElementById('devices').innerHTML=h;}
load();</script></body></html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
