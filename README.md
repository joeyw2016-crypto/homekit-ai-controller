---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: e484fdc44aa47425620c0c086e7e2216_136f2972c71311f197b3525400248c00
    ReservedCode1: 8KG5TYTI9x7omwQCY3wvhelKX7RVvZap72kIQv7ly+nZrIOm/u6ORWRPTIoni5wbIb1mfZd6J/yBIX7S2cQd/xyr6N/Mh0l+MBMyblxJK/AjBe66vZ1KppJp3quhK4SBI64ezz7HyAGsuL9F86Y4eBzYBwcEpy/quc9wK6ockyXpCGjh9MmIQTZXFks=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: e484fdc44aa47425620c0c086e7e2216_136f2972c71311f197b3525400248c00
    ReservedCode2: 8KG5TYTI9x7omwQCY3wvhelKX7RVvZap72kIQv7ly+nZrIOm/u6ORWRPTIoni5wbIb1mfZd6J/yBIX7S2cQd/xyr6N/Mh0l+MBMyblxJK/AjBe66vZ1KppJp3quhK4SBI64ezz7HyAGsuL9F86Y4eBzYBwcEpy/quc9wK6ockyXpCGjh9MmIQTZXFks=
---

# HomeKit AI Controller（Apple 智能家居 AI 控制模块）

通过 iPhone 的 **Apple Intelligence（Siri / 家庭 App）** 控制智能设备的示例工程。
电脑用 pyhap 模拟 HomeKit 配件，iPhone 家庭 App 扫码配对后可控制；
同时内置 DeepSeek AI 意图解析，支持自然语言指令（"把客厅的灯打开"）。

## 技术架构

```
iPhone (家庭 App / Siri)
    │  局域网 mDNS 发现 + HomeKit 协议 (HAP)
    ▼
电脑 HomeKit 桥接 (pyhap 模拟 灯/插座/风扇)
    ▲
    │  AI 自然语言控制
    ▼
DeepSeek LLM ──意图解析──> 结构化指令 ──> 设备状态
```

## 快速开始

```bash
pip install -r requirements.txt
```

### 1. 启动 HomeKit 桥接（让 iPhone 发现设备）

```bash
python modules/homekit_bridge.py
```

看到 `配对码：123-45-678` 后，打开 iPhone **家庭 App** → 添加配件 →
扫描终端打印的二维码或输入配对码。添加成功后即可用 **Siri** 说
"关掉客厅的灯" 直接控制。

### 2. 启动 AI 控制服务

```bash
python app.py
```

浏览器打开 http://localhost:8000 ，输入自然语言指令测试；
或直接调用接口：

```bash
curl -X POST http://localhost:8000/api/ai \
  -H "Content-Type: application/json" \
  -d '{"text":"把客厅的灯打开"}'
```

返回示例：

```json
{
  "intent": {"device": "客厅灯", "action": "on"},
  "result": "灯已打开",
  "devices": {"灯": {"type": "light", "state": "on", "brightness": 100}}
}
```

## 接口一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/ai` | POST | AI 自然语言控制，body: `{"text": "..."}` |
| `/api/devices` | GET | 查看全部设备状态 |
| `/api/devices/{名}/on` | POST | 打开设备 |
| `/api/devices/{名}/off` | POST | 关闭设备 |
| `/` | GET | 网页控制面板 |

## 关键文件

- `modules/llm_client.py` — DeepSeek API 封装
- `modules/intent_parser.py` — 自然语言 → 结构化指令
- `modules/homekit_bridge.py` — pyhap 模拟 HomeKit 配件（灯/插座/风扇）
- `app.py` — FastAPI 主服务 + 控制面板

## 现实边界说明

- Apple Intelligence 本身**不开放第三方调用**，本方案走标准 HomeKit 链路：
  iPhone 家庭 App / Siri 通过 HAP 协议与本地桥接通信，等价于真实智能家居体验。
- 对接真实硬件（如 Yeelight、小米插座）时，把 `apply_action` 里的状态
  写入改为调用对应品牌 SDK / 局域网 API 即可，接口不变。
*（内容由AI生成，仅供参考）*
