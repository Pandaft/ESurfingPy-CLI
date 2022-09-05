import ddddocr


def ocr_img(img_file):
    """调用 ddddocr 识别验证码"""
    try:
        ocr = ddddocr.DdddOcr()
        with open(img_file, 'rb') as f:
            img_bytes = f.read()
        result = ocr.classification(img_bytes)
        return True, result
    except Exception as Exc:
        return False, Exc
