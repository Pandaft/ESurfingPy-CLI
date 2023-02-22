import ddddocr


def ocr_image(img: any) -> (bool, str):
    """通过 ddddocr 识别文字"""
    try:
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = ocr.classification(img)
        return True, res
    except Exception as exc:
        return False, str(exc)
