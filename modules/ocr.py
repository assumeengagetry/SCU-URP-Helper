import re

import ddddocr


_ocr = None


def get_ocr():
    global _ocr
    if _ocr is None:
        _ocr = ddddocr.DdddOcr(show_ad=False)
    return _ocr


def normalize_captcha_code(code, length=4):
    code = re.sub(r"\s+", "", code or "")
    return code[-length:] if length else code


def classify_captcha(image_content, length=4):
    raw_code = get_ocr().classification(image_content)
    return normalize_captcha_code(raw_code, length)
