import base64
import xmltodict
import toon


def img_to_base64(img: bytes) -> str:
    return base64.b64encode(img).decode("ascii")


def img_to_content(img: bytes):
    b64 = img_to_base64(img)
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
    }


def xml_to_toon(xml: str):
    dict = xmltodict.parse(xml)
    dict = prune_ui_dict(dict)
    toonl = toon.encode(dict)
    return toonl


def prune_ui_dict(data):
    allowed_attrs = {"@resource-id", "@text", "@content-desc", "@bounds"}

    if isinstance(data, dict):
        pruned = {}
        for key, value in data.items():
            if key.startswith("@"):
                if value == "":
                    continue

                if key in allowed_attrs or (key == "@clickable" and value == "true"):
                    pruned[key] = value
            else:
                child_pruned = prune_ui_dict(value)

                if child_pruned:
                    pruned[key] = child_pruned

        return pruned

    elif isinstance(data, list):
        # Handle lists of nodes
        pruned_list = []
        for item in data:
            item_pruned = prune_ui_dict(item)
            if item_pruned:
                pruned_list.append(item_pruned)
        return pruned_list

    return data
