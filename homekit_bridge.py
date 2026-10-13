"""
HomeKit 桥接模块：用 pyhap 把电脑模拟成智能家居配件（灯/插座/风扇），
iPhone 家庭 App 在同一 WiFi 下扫码即可发现并添加，之后可用
Siri / 家庭 App 直接控制，或通过本服务 AI 指令控制。
"""
import asyncio
import signal
import logging

# Python 3.12+ 移除 asyncio.SafeChildWatcher / set_child_watcher，pyhap
# 主线程启动仍会引用，注入空实现兼容垫片（HomeKit 桥接不依赖子进程监视）。
if not hasattr(asyncio, "SafeChildWatcher"):

    class _SafeChildWatcher:
        def attach_loop(self, loop):
            pass

        def close(self):
            pass

    asyncio.SafeChildWatcher = _SafeChildWatcher

if not hasattr(asyncio, "set_child_watcher"):

    def _set_child_watcher(watcher):
        pass

    asyncio.set_child_watcher = _set_child_watcher

from pyhap.accessory import Accessory, CATEGORY_OTHER
from pyhap.accessory_driver import AccessoryDriver

logging.basicConfig(level=logging.INFO)

ACCESSORY_PIN = b"123-45-678"  # 家庭 App 配对码（pyhap 5.0 要求 bytes）


class SmartLight(Accessory):
    """模拟智能灯：支持开关 + 亮度调节"""

    category = CATEGORY_OTHER

    def __init__(self, *args, name="客厅灯", **kwargs):
        super().__init__(*args, display_name=name, **kwargs)
        self._name = name
        serv_light = self.add_preload_service("Lightbulb", ["On", "Brightness"])
        self._on = serv_light.configure_char("On", setter_callback=self._on_change)
        self._brightness = serv_light.configure_char(
            "Brightness", setter_callback=self._brightness_change
        )

    def _on_change(self, value):
        state = "开" if value else "关"
        print(f"[HomeKit] {self._name} -> {state}")

    def _brightness_change(self, value):
        print(f"[HomeKit] {self._name} 亮度 -> {value}%")


class SmartSwitch(Accessory):
    """模拟智能插座"""

    category = CATEGORY_OTHER

    def __init__(self, *args, name="插座", **kwargs):
        super().__init__(*args, display_name=name, **kwargs)
        self._name = name
        serv_switch = self.add_preload_service("Switch", ["On"])
        self._on = serv_switch.configure_char("On", setter_callback=self._on_change)

    def _on_change(self, value):
        state = "开" if value else "关"
        print(f"[HomeKit] {self._name} -> {state}")


def start_bridge(light_name="客厅灯", switch_name="插座"):
    """启动 HomeKit 桥接（阻塞运行，Ctrl+C 退出）"""
    driver = AccessoryDriver(
        port=51826,
        persist_file="homekit.state",
        pincode=ACCESSORY_PIN,
    )
    driver.add_accessory(SmartLight(driver, name=light_name))
    driver.add_accessory(SmartSwitch(driver, name=switch_name))
    print("=" * 50)
    print(f"HomeKit 桥接已启动，配对码：{ACCESSORY_PIN.decode()}")
    print("请打开 iPhone 家庭 App -> 添加配件 -> 输入配对码 123-45-678")
    print("=" * 50)
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()


if __name__ == "__main__":
    start_bridge()
