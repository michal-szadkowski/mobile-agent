import base64


def img_to_base64(img: bytes) -> str:
    return base64.b64encode(img).decode("ascii")


def img_to_content(img: bytes):
    b64 = img_to_base64(img)
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
    }
