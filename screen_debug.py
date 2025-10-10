import time
from PIL import Image, ImageDraw
import subprocess

# 屏幕分辨率配置
RESOLUTIONS = {
    '1260x2800': {
        'word_area':(160, 600, 840, 730),
        'options_area_A': (145, 855, 830, 940),
        'options_area_B': (145, 1070, 830, 1155),
        'options_area_C': (145, 1280, 830, 1370),
        'options_area_D': (145, 1490, 830, 1580),
        'options_y_base': 900,
        'answer_area': (350, 1640, 470, 1740),
        'next_button': (1000, 2530),  # 下一题按钮位置
        'back_button': (130, 400),    # 返回按钮位置
        'start_test': (700, 900),  # 开始自测按钮位置
        'submit_test': (1100, 400),   # 提交考卷按钮位置
        'confirm':(900,1635),  # 确认按钮位置
        'store_answers': (500, 1300)  # 存储答案按钮位置
    }
}

def capture_screen():
    """截取手机屏幕"""
    subprocess.run('adb shell screencap -p /sdcard/screen.png', shell=True)
    subprocess.run('adb pull /sdcard/screen.png', shell=True)
    return Image.open('screen.png')

def debug_screen_positions():
    """调试屏幕位置"""
    print("开始屏幕位置调试...")
    print("按Ctrl+C停止")
    
    try:
        while True:
            # 截取屏幕
            img = capture_screen()
            
            # 获取当前分辨率配置
            res = RESOLUTIONS['1260x2800']
            
            # 绘制识别区域
            debug_img = img.copy()
            draw = ImageDraw.Draw(debug_img)
            
            # 绘制题目区域（红色）
            draw.rectangle(res['word_area'], outline="red", width=3)
            
            # 绘制选项区域（蓝色）
            draw.rectangle(res['options_area_A'], outline="blue", width=3)
            draw.rectangle(res['options_area_B'], outline="blue", width=3)
            draw.rectangle(res['options_area_C'], outline="blue", width=3)
            draw.rectangle(res['options_area_D'], outline="blue", width=3)

            draw.rectangle(res['answer_area'], outline="yellow", width=3)
            
            # 绘制选项点击位置（绿色）
            y_base = res['options_y_base']
            for i in range(4):
                y = y_base + i * 200
                draw.rectangle([250-50, y-50, 250+50, y+50], outline="green", width=2)
            
            # 绘制下一题和返回按钮位置（紫色）
            next_x, next_y = res['next_button']
            back_x, back_y = res['back_button']
            test_x, test_y = res['start_test']
            submit_x, submit_y = res['submit_test']
            confirm_x, confirm_y = res['confirm']
            store_answers_x, store_answers_y = res['store_answers']

            #draw.rectangle([next_x-50, next_y-50, next_x+50, next_y+50], outline="purple", width=3)
            #draw.rectangle([back_x-50, back_y-50, back_x+50, back_y+50], outline="purple", width=3)
            draw.rectangle([test_x-50, test_y-50, test_x+50, test_y+50], outline="purple", width=3)
            draw.rectangle([submit_x-50, submit_y-50, submit_x+50, submit_y+50], outline="purple", width=3)
            draw.rectangle([confirm_x-50, confirm_y-50, confirm_x+50, confirm_y+50], outline="purple", width=3)
            draw.rectangle([store_answers_x-50, store_answers_y-50, store_answers_x+50, store_answers_y+50], outline="purple", width=3)

            
            # 保存调试图片
            debug_img.save('screen_debug.png')
            print("调试图片已保存为 screen_debug.png")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n调试结束")

if __name__ == '__main__':
    debug_screen_positions()