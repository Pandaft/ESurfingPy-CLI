import time


def log(text: str = "", rewrite: bool = False) -> str:
    if rewrite:
        print("\r", end="")
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {text}')
    return text
