from playwright.sync_api import sync_playwright
import mysql.connector
from mysql.connector import Error
import time
import os
import random



DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "xsdjsg1943",
    "database": "ilovewords",
    "port": "3306",
    "charset": "utf8mb4"
}

def create_database():
    """创建简化后的数据库表"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def detect_question(page, retry_count=0):
    """从网页提取题目和选项"""
    try:
        question = page.locator('.van-col.van-col--17 span:nth-of-type(2)').inner_text()
        options = [
            opt.inner_text()
            for opt in page.query_selector_all('div.van-cell')
        ]
        
        # 清理题目文本：移除所有非文字符号和空格
        import re
        question = re.sub(r'[^\w\s]', '', question)
        question = re.sub(r'\s+', '', question)
        
        # 清理选项文本：移除开头的ABCD字母、末尾的符号空格和所有空格
        options = [re.sub(r'^[A-D]\.?\s*', '', opt).rstrip(' .!?,;:') for opt in options]
        options = [re.sub(r'\s+', '', opt) for opt in options]
        
        print(f"识别到的单词区域文本: {question}")
        print(f"识别到的选项区域A文本: {options[0]}")
        print(f"识别到的选项区域B文本: {options[1]}")
        print(f"识别到的选项区域C文本: {options[2]}")
        print(f"识别到的选项区域D文本: {options[3]}")
        
        if (not question.strip() or not options) and retry_count < 3:
            print(f"识别失败，正在重试... (第{retry_count+1}次)")
            page.wait_for_timeout(500)
            return detect_question(page, retry_count+1)
            
        return question, {
            'A': options[0],
            'B': options[1],
            'C': options[2],
            'D': options[3]
        }
    except Exception as e:
        print(f"提取网页元素出错: {e}")
        if retry_count < 3:
            print(f"正在重试... (第{retry_count+1}次)")
            page.wait_for_timeout(500)
            return detect_question(page, retry_count+1)
        return "", {'A':'', 'B':'', 'C':'', 'D':''}

if __name__ == '__main__':
    create_database()
    count = 0  # 总处理计数器
    new_count = 0  # 新增数据计数器
    
    # 创建Nonew文件夹用于存储未识别记录
    nonew_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Nonew')
    os.makedirs(nonew_dir, exist_ok=True)
    
    print("自动化采集脚本启动...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36",
            viewport={"width": 380, "height": 600},
        )
        page = context.new_page()
        
        # 增加重试机制和更长的超时时间
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                page.goto("https://skl.hduhelp.com/#/english/list", timeout=60000)
                print("已开启窗口，请登录，并于5分钟内开始考试，否则窗口将自动关闭。")
                page.wait_for_selector('.van-col.van-col--17', timeout=300000)
                break
            except Exception as e:
                retry_count += 1
                print(f"页面加载失败，正在重试... (第{retry_count}次)")
                if retry_count == max_retries:
                    raise
                page.wait_for_timeout(5000)
                continue
        
        try:
            while True:
                # 识别内容
                question, options = detect_question(page)
                
                # 获取正确答案文本
                correct = options['A']  # 默认存储A选项作为正确答案
                
                # 无论识别成功与否都计数
                count += 1
                
                # 当未识别到题目或答案时记录
                if not question or not correct:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    with open(os.path.join(nonew_dir, f'nonew_{timestamp}.txt'), 'w') as f:
                        f.write(f"Question: {question}\nOptions: {options}")
                    print(f"未识别到题目或答案，记录已保存: nonew_{timestamp}.txt")
                
                # 有效数据存储（只有当question和correct都不为空时才存储）
                if question and correct:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        
                        # 检查是否已存在相同记录
                        cursor.execute("""
                            SELECT id FROM questions 
                            WHERE question = %s AND correct_answer = %s
                            LIMIT 1
                        """, (question, correct))
                        
                        if cursor.fetchone() is None:  # 不存在重复记录
                            cursor.execute("""
                                INSERT INTO questions (question, correct_answer)
                                VALUES (%s, %s)
                            """, (question, correct))
                            conn.commit()
                            new_count += 1  # 新增数据计数
                            print(f"已存储: Q:{question[:15]}... A:{correct[:10]}...")
                        else:
                            print(f"记录已存在，跳过存储: Q:{question[:15]}... A:{correct[:10]}...")
                            
                    except Error as e:
                        print(f"存储失败: {e}")
                    finally:
                        if conn.is_connected():
                            cursor.close()
                            conn.close()
                else:
                    print(f"识别结果为空，跳过存储: Q:{question} A:{correct}")
                    
                # 点击下一题
                page.locator("(//div[@class='van-radio__icon van-radio__icon--round'])[1]").click()
                
                # 存储100组后点击返回
                if count >= 99:
                    page.locator("(//div[@class='van-nav-bar__left']//i)[1]").click()
                    break
                
                # 添加随机延迟，模拟人类操作
                delay = random.uniform(0.3, 0.5)
                page.wait_for_timeout(delay * 1000)
                
        except KeyboardInterrupt:
            print("\n采集服务已停止")
        finally:
            print(f"已完成 {count} 组数据采集")
            print(f"新增存储 {new_count} 条数据")
            browser.close()