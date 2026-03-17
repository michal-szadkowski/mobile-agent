from dataclasses import dataclass
from io import BytesIO
import uiautomator2 as u2
from xmltodict import parse


@dataclass
class AndroidDevice:
    d: u2.Device

    @classmethod
    def connect(cls, serial: str | None = None) -> "AndroidDevice":
        d = u2.connect(serial) if serial else u2.connect_usb()
        return cls(d)

    def tap(self, x: int, y: int) -> None:
        self.d.click(x, y)

    def tap_on_id(self, id: str) -> str:
        element = self.d(resourceId=id)
        if element.exists:
            info = element.info
            clickable = info.get("clickable")
            element.click()
            if not clickable:
                return f"Clicked {id}, but item is not clickable (clickable=false)."
            return f"Successfully clicked {id}."
        return f"{id} not found on screen."

    def tap_on_text(self, text: str) -> str:
        if self.d(text=text).exists:
            self.d(text=text).click()
            return f"Success, clicked {text}."
        else:
            return f"{text} not found on screen."

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.2) -> None:
        self.d.swipe(x1, y1, x2, y2, duration=duration)

    def type_text(self, text: str) -> None:
        self.d.send_keys(text)

    def press_enter(self) -> None:
        self.d.press("enter")

    def press_back(self) -> None:
        self.d.press("back")

    def press_home(self) -> None:
        self.d.press("home")

    def app_start(self, package: str) -> None:
        self.d.app_start(package)

    def dump_ui(self) -> dict:
        return parse(self.d.dump_hierarchy())

    def screenshot(self) -> bytes | None:
        image = self.d.screenshot()
        if image is None:
            return
        max_dimension = 800
        image.thumbnail((max_dimension, max_dimension))
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=80)
        return buffer.getvalue()

    def window_size(self) -> tuple[int, int]:
        info = self.d.window_size()
        return int(info[0]), int(info[1])
