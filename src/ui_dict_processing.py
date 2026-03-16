from typing import Any


def is_meaningful_node(node: dict[str, Any]) -> bool:
    resource_id = node.get("@resource-id", "")
    text = node.get("@text", "")
    content_desc = node.get("@content-desc", "")
    clickable = node.get("@clickable") == "true"

    if resource_id.startswith("com.android.systemui:id/"):
        return False

    if clickable:
        return True
    if text and text.strip():
        return True
    if content_desc and str(content_desc).strip():
        return True
    if resource_id and not resource_id.startswith("android:id/"):
        return True

    return False


def iter_child_values(d: dict[str, Any]):
    for key, value in d.items():
        if key.startswith("node"):
            yield value


def flatten_ui_tree(data: Any, out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if out is None:
        out = []

    if isinstance(data, dict):
        if is_meaningful_node(data):
            out.append(
                {
                    "resource_id": data.get("@resource-id"),
                    "text": data.get("@text"),
                    "content_desc": data.get("@content-desc"),
                    "clickable": data.get("@clickable") == "true",
                    "bounds": data.get("@bounds", ""),
                }
            )

        for child in iter_child_values(data):
            flatten_ui_tree(child, out)

    elif isinstance(data, list):
        for item in data:
            flatten_ui_tree(item, out)

    return out


def process_ui_dict(ui_dict):
    return flatten_ui_tree(ui_dict)
