import subprocess
import time

# 复用项目中的分辨率配置
RESOLUTIONS = {
    '1260x2800': {
        'next_button': (1000, 2530),
        'back_button': (130, 400),
        'start_test': (700, 900),  # 开始自测按钮位置
        'submit_test': (1100, 400),
        'confirm':(900,1635),  # 提交考卷按钮位置
        'store_answers': (500, 1300)
    }
}

def tap_back():
    """点击返回按钮"""
    x, y = RESOLUTIONS['1260x2800']['back_button']
    subprocess.run(f'adb shell input tap {x} {y}', shell=True)

def tap_start_test():
    """点击开始自测按钮"""
    x, y = RESOLUTIONS['1260x2800']['start_test']
    subprocess.run(f'adb shell input tap {x} {y}', shell=True)

def tap_submit_test():
    """点击提交考卷按钮"""
    x, y = RESOLUTIONS['1260x2800']['submit_test']
    subprocess.run(f'adb shell input tap {x} {y}', shell=True)

def tap_confirm():
    """点击确认按钮"""
    x, y = RESOLUTIONS['1260x2800']['confirm']
    subprocess.run(f'adb shell input tap {x} {y}', shell=True)

def tap_store_answers():
    """点击存储答案按钮并运行存储脚本"""
    x, y = RESOLUTIONS['1260x2800']['store_answers']
    subprocess.run(f'adb shell input tap {x} {y}', shell=True)
    time.sleep(6) 
    subprocess.run('python store_answers.py', shell=True)

if __name__ == '__main__':
    print("自动测试脚本启动...")
    print("将在启动时点击开始自测，5秒后点击提交考卷，然后等待6-7分钟循环执行")
    
    while True:
        tap_start_test()
        time.sleep(5)
        tap_submit_test()
        time.sleep(5)
        tap_confirm()
        time.sleep(5)
        tap_store_answers()
        time.sleep(300) 
        print("准备开始下一轮测试...")