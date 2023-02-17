import ddddocr


def ocr_image_file(img_file_path: str) -> (bool, str):
    """通过 ddddocr 识别文字"""
    try:
        with open(img_file_path, 'rb') as f:
            img_bytes = f.read()
        ocr = ddddocr.DdddOcr(show_ad=False)
        res = ocr.classification(img_bytes)
        return True, res
    except Exception as exc:
        return False, str(exc)
