from langchain.tools import tool
from android import AndroidDevice


def build_phone_tools(device: AndroidDevice):
    @tool
    def phone_tap(x: int, y: int) -> str:
        """Tap the screen at absolute pixel coordinates (x, y). Use this tool only when other tap functions are insufficient."""
        device.tap(x, y)
        return f"Tapped at ({x}, {y})"

    @tool
    def phone_tap_id(id: str) -> str:
        """Tap a visible UI element by its Android resource ID."""
        return device.tap_on_id(id)

    @tool
    def phone_tap_text(text: str) -> str:
        """Tap a visible UI element by its displayed text."""
        return device.tap_on_text(text)

    @tool
    def phone_swipe(x1: int, y1: int, x2: int, y2: int, duration: float = 0.2) -> str:
        """Swipe from (x1, y1) to (x2, y2) using absolute pixel coordinates."""
        device.swipe(x1, y1, x2, y2, duration)
        return f"Swiped from ({x1}, {y1}) to ({x2}, {y2})"

    @tool
    def phone_type_text(text: str) -> str:
        """Type text into the currently focused input field."""
        device.type_text(text)
        return f"Typed text: {text}"

    @tool
    def phone_back() -> str:
        """Press the Android back button."""
        device.press_back()
        return "Pressed back"

    @tool
    def phone_home() -> str:
        """Press the Android home button."""
        device.press_home()
        return "Pressed home"

    @tool
    def phone_open_app(package: str) -> str:
        """Open an Android app by package name."""
        device.app_start(package)
        return f"Opened app: {package}"

    return [
        phone_tap,
        phone_tap_id,
        phone_tap_text,
        phone_swipe,
        phone_type_text,
        phone_back,
        phone_home,
        phone_open_app,
    ]
