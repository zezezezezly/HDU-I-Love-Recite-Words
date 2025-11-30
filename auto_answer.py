"""
detect_question函数
从网页提取题目和选项
功能: 使用Playwright从网页中提取题目文本和选项内容，并进行文本清理
参数: 
    page: Playwright页面对象
    retry_count: 重试次数(默认0)
返回值: 
    tuple: (清理后的题目文本, 选项字典{'A':'选项A','B':'选项B','C':'选项C','D':'选项D'})
"""

"""
get_correct_answer函数
从数据库查询单词对应的正确答案
功能: 使用MySQL连接池查询题目对应的正确答案，支持缓存和大小写不敏感查询
参数: 
    word: 要查询的题目文本
返回值: 
    list: 匹配的正确答案列表(可能多个)或None(未找到)
"""

"""
select_answer函数
匹配选项与正确答案
功能: 将数据库查询结果与页面选项进行匹配，找出正确答案对应的选项索引
参数: 
    correct_answer: 从数据库获取的正确答案(字符串或列表)
    options_dict: 选项字典{'A':'选项A','B':'选项B','C':'选项C','D':'选项D'}
返回值: 
    int: 匹配的选项索引(0-3对应A-D)，未匹配返回-1
"""

"""
select函数
定位并点击指定答案选项
功能: 根据选项(A/B/C/D)定位对应的单选按钮并点击
参数: 
    page: Playwright页面对象
    answer: 要选择的答案('A'/'B'/'C'/'D')
"""

"""
answer_question_loop
处理答题循环逻辑
"""

"""
main_flow函数
自动答题主逻辑
"""

import os
from playwright.sync_api import sync_playwright
import time
import random
import mysql.connector

def detect_question(page, retry_count=0):
    try:
        question = page.locator('.van-col.van-col--17 span:nth-of-type(2)').inner_text()
        options = [
            opt.inner_text()
            for opt in page.query_selector_all('div.van-cell')
        ]
        
        import re
        # 清理问题文本：移除非文字符号（汉字、字母、数字）
        question = re.sub(r'[^\u4e00-\u9fffa-zA-Z0-9]', '', question)
        # 清理选项文本：先移除开头的ABCD选项，再移除非文字符号
        options = [re.sub(r'^[A-D][\.\s]*', '', opt) for opt in options]  # 移除开头的ABCD及符号
        options = [re.sub(r'[^\u4e00-\u9fffa-zA-Z0-9]', '', opt) for opt in options]
        options = [opt.lower() for opt in options]  # 将所有选项转换为小写
        
        """print(f"识别到的单词区域文本: {question}")
        print(f"识别到的选项区域A文本: {options[0]}")
        print(f"识别到的选项区域B文本: {options[1]}")
        print(f"识别到的选项区域C文本: {options[2]}")
        print(f"识别到的选项区域D文本: {options[3]}")"""
        
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


# 数据库连接池配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "xsdjsg1943",
    "database": "ilovewords",
    "port": "3306",
    "charset": "utf8mb4"
}

# 创建连接池
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="word_pool",
    pool_size=3,
    **db_config
)

# 带缓存和大小写不敏感的查询函数
from functools import lru_cache
@lru_cache(maxsize=1000)

def get_correct_answer(word):
    
    try:
        # 调试日志：打印原始输入和预处理后的单词
        print(f"数据库查询输入: 原始='{word}' 预处理='{word.strip().lower()}'") 
        conn = db_pool.get_connection()
        cursor = conn.cursor(buffered=True)
        # 使用预处理语句和批量查询
        query = """
        SELECT correct_answer FROM questions 
        WHERE LOWER(question) = LOWER(%s)
        LIMIT 5
        """
        cursor.execute(query, (word.strip().lower(),))  # 统一使用小写
        results = [row[0].strip().lower() for row in cursor.fetchall()]  # 结果也统一小写
        
        # 调试日志：打印查询结果
        print(f"数据库查询结果: {results}")
        
        return results if results else None
    except Exception as e:
        print(f"数据库查询错误: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def select_answer(correct_answer, options_dict):
    if not correct_answer:
        print("未获取到正确答案")
        return -1
        
    # 预处理答案和选项文本
    correct_answers = [correct_answer] if isinstance(correct_answer, str) else correct_answer
    
    # 调试日志：打印输入参数
    print(f"匹配输入: 正确答案={correct_answers} 选项A='{options_dict['A']}' 选项B='{options_dict['B']}' 选项C='{options_dict['C']}' 选项D='{options_dict['D']}'")
    
    for answer in correct_answers:
        answer = answer.strip().lower()
        for opt_key in ['A', 'B', 'C', 'D']:
            option_text = options_dict[opt_key].strip().lower()
            if option_text == answer:
                print(f"匹配成功: 选项{opt_key} '{option_text}' == 答案 '{answer}'")
                return ord(opt_key) - ord('A')
    
    print(f"未匹配到答案，详情：\n正确答案: {correct_answers}\n选项A: '{options_dict['A']}'\n选项B: '{options_dict['B']}'\n选项C: '{options_dict['C']}'\n选项D: '{options_dict['D']}'")
    return -1

def select(page, answer):
    index_mapping = {"A": 1, "B": 2, "C": 3, "D": 4}
    xpath = f"(//div[@class='van-radio__icon van-radio__icon--round'])[{index_mapping[answer]}]"
    button = page.locator(xpath)
    button.click()

def answer_question_loop(page):
    
    question_count = 1
    for _ in range(100):
        print(f"\n=== 题目 {question_count} ===")
        word, options = detect_question(page)
        
        # 从数据库获取正确答案
        correct_answer = get_correct_answer(word)
        question_count += 1
        
        if correct_answer is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            print(f"未找到答案: not_found_{timestamp}")
            
            
        choice = select_answer(correct_answer, options)

        if choice != -1:
            select(page, chr(choice+ord('A')))
            print(f"选择答案: {chr(choice+ord('A'))}")
        else:
            select(page, random.choice(['A', 'B', 'C', 'D']))
            
        # 添加随机延迟，模拟人类操作
        delay = random.uniform(0.3, 0.3)
        print(f"等待 {delay:.2f} 秒后自动跳转下一题")
        page.wait_for_timeout(delay * 1000)

def main_flow(page):
    """主业务流程"""
    while True:
        try:
            # 执行答题循环
            answer_question_loop(page)

            # 点击提交考卷按钮
            page.wait_for_selector("span.van-nav-bar__text:has-text('提交考卷')", timeout=10000)
            page.click("span.van-nav-bar__text:has-text('提交考卷')")
            print("已点击提交考卷按钮")
            
            # 点击确认按钮
            page.wait_for_selector("button:has-text('确认')", timeout=10000)
            page.click("button:has-text('确认')")
            print("已点击确认按钮")
        
            # 用户交互
            while True:
                user_input = input("\n是否继续答题？(y/n): ").strip().lower()
                if user_input == 'y':
                    print("准备开始新一轮答题...")
                    return True  # 继续答题
                elif user_input == 'n':
                    print("程序即将退出...")
                    return False  # 停止程序
                else:
                    print("请输入 y 或 n")
        except Exception as e:
            print(f"发生错误: {str(e)}")
            if input("是否重试？(y/n): ") == 'y':
                continue
            else:
                return False

if __name__ == '__main__':
    print("自动化答题脚本启动...")
    
    # 固定用户名和密码
    username = '24051109'
    password = 'Xsdjsg1943@'
    
    with sync_playwright() as p:
        # 初始化浏览器配置
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 10; SM-G973F)...",
            viewport={"width": 380, "height": 600}
        )
        page = context.new_page()
        
        try:
            # 初次打开网页
            page.goto("https://skl.hduhelp.com/#/english/list", timeout=60000)
            
            # 等待页面加载
            page.wait_for_timeout(5000)
            
            # 检查是否需要登录
            if "login" in page.url or "登录" in page.content():
                print("检测到登录页面，正在自动登录...")
                
                # 尝试填写用户名和密码
                # 注意：这里需要根据实际的页面结构调整选择器
                try:
                    # 等待登录表单元素出现
                    page.wait_for_selector("input[name='username'][maxlength='200'][autocomplete='username']", timeout=2000)
                    page.wait_for_selector("input[type='password'][maxlength='200'][autocomplete='new-password']", timeout=2000)
                    page.wait_for_selector("button:has-text('登    录')", timeout=2000)
                    
                    # 填写用户名和密码
                    page.fill("input[name='username'][maxlength='200'][autocomplete='username']", username)
                    page.fill("input[type='password'][maxlength='200'][autocomplete='new-password']", password)
                    
                    # 点击登录按钮
                    page.click("button:has-text('登    录')")
                    
                    # 等待登录完成
                    page.wait_for_timeout(5000)
                    print("自动登录完成")
                    
                    # 点击考试标签
                    #page.wait_for_selector("span.van-tab__text.van-tab__text--ellipsis:has-text('考试')", timeout=10000)
                    #page.click("span.van-tab__text.van-tab__text--ellipsis:has-text('考试')")
                    #print("已点击考试标签")
                    
                    page.wait_for_selector("div.van-tabbar-item__text:has-text('我')", timeout=500)
                    page.click("div.van-tabbar-item__text:has-text('我')")
                    print("已点击'我'标签")
                    # 点击考试标签
                    page.wait_for_selector("span.van-grid-item__text:has-text('我爱记单词')", timeout=500)
                    page.click("span.van-grid-item__text:has-text('我爱记单词')")
                    print("已点击'我爱记单词'")
                    # 点击开始考试按钮
                    page.wait_for_selector("span.van-tab__text.van-tab__text--ellipsis:has-text('考试')", timeout=300)
                    page.click("span.van-tab__text.van-tab__text--ellipsis:has-text('考试')")
                    print("已点击考试标签")
                    # 点击开始考试按钮
                    page.wait_for_selector("span.van-button__text:has-text('开始考试')", timeout=300)
                    page.click("span.van-button__text:has-text('开始考试')")
                    print("已点击开始考试按钮")
                    # 点击确认开考按钮
                    page.wait_for_selector("button:has-text('确认开考')", timeout=300)
                    page.click("button:has-text('确认开考')")
                    print("已点击确认开考按钮")

                except Exception as e:
                    print(f"自动登录失败: {str(e)}")
            else:
                print("未检测到登录页面")
            
            print("请登录并准备考试...")
            page.wait_for_selector('.van-col.van-col--17', timeout=300000)
            
            # 主循环控制
            while True:
                if not main_flow(page):
                    break  # 用户选择退出
        finally:
            # 确保资源释放
            context.close()
            browser.close()
