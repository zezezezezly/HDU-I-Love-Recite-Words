# 单词识别与自动答题系统

## 项目简介

这是一个基于Python的单词识别与自动答题系统，专为杭州电子科技大学英语答题https://skl.hduhelp.com/#/english/list
设计。系统能够自动识别网页中的英语题目，从数据库中查询正确答案，并自动选择答案完成答题过程。注意网站在生活区校园网宽带环境下可能无法登录，需要切换至热点。

## 功能特点

- **自动登录**：支持自动填写用户名和密码并登录系统
- **题目识别**：自动识别网页中的英语题目和选项
- **智能匹配**：从MySQL数据库中查询正确答案并与选项进行匹配
- **自动答题**：自动选择正确答案并完成答题过程
- **数据库缓存**：使用LRU缓存提高查询效率

## 项目结构

```
word_identification_2.1/
├── auto_answer.py          # 自动答题主程序
├── store_answers.py        # 答案采集与存储工具
├── screen_debug.py         # 屏幕区域调试工具
├── screen_tap.py           # 自动点击与测试工具
├── README.md               # 项目说明文档
└── requirements.txt        # 项目依赖文件
```

## 技术栈

- **Python 3.12**：主要开发语言
- **Playwright**：网页自动化工具
- **MySQL**：数据库存储正确答案
- **正则表达式**：文本处理和清理
- **LRU缓存**：提高查询效率

## 环境要求

- Python 3.10+ 
- MySQL 5.7+ 
- 安装所需依赖包（详见安装说明）

## 安装说明

### 1. 克隆项目（或直接下载文件）

```bash
# 克隆项目（示例命令）
git clone <项目地址>
cd word_identification_2.1
```

### 2. 创建虚拟环境（可选但推荐）

```bash
# Windows
python -m venv word_identification_venv
word_identification_venv\Scripts\activate

# macOS/Linux
python3 -m venv word_identification_venv
source word_identification_venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

## 依赖管理

本项目通过`requirements.txt`文件管理依赖，包含以下核心库：
- `playwright`: 用于网页自动化操作
- `mysql-connector-python`: 用于数据库连接
- `Pillow`: 用于图像处理

其他库可根据需要选择性安装。

### 4. 配置数据库

1. 确保MySQL服务正在运行
2. 创建数据库和表结构：

```sql
CREATE DATABASE ilovewords CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ilovewords;

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    correct_answer VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询效率
CREATE INDEX idx_question ON questions(question);
```

3. 修改代码中的数据库配置（如果需要）：

```python
# 在auto_answer.py和store_answers.py中
# 找到以下代码并根据实际情况修改

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "xsdjsg1943",
    "database": "ilovewords",
    "port": "3306",
    "charset": "utf8mb4"
}
```

### 5. 配置用户名和密码

在`auto_answer.py`中，用户名和密码已经固定在代码中，您需要根据实际情况修改：

```python
# 在auto_answer.py中找到以下代码并修改
username = 'your_username'
password = 'your_password'
```

## 使用方法

### 自动答题

```bash
python auto_answer.py
```

程序会：
1. 自动打开浏览器并访问指定网页
2. 自动检测是否需要登录，如果需要则自动登录
3. 自动开始答题过程
4. 答题完成后，提示用户是否继续答题

## 功能详解

### 1. 自动登录功能

系统会自动检测当前页面是否需要登录，如果需要则自动填写用户名和密码并点击登录按钮。登录成功后，系统会自动点击"考试"标签和"开始考试"按钮。

### 2. 题目识别功能

系统使用Playwright从网页中提取题目文本和选项内容，然后进行文本清理：
- 移除非文字符号（汉字、字母、数字除外）
- 移除选项开头的ABCD标识
- 将所有文本转换为小写以进行大小写不敏感的匹配

### 3. 答案匹配功能

系统从MySQL数据库中查询正确答案，并与网页中的选项进行匹配。匹配过程支持大小写不敏感，以提高匹配成功率。

### 4. 自动答题功能

系统根据匹配结果自动选择正确的答案选项。如果未找到匹配的答案，系统会随机选择一个选项，并将未找到答案的题目信息保存为截图（保存在`None/`文件夹中）。

### 5. 答案采集与存储功能 (`store_answers.py`)

- 自动从网页中提取题目和选项信息
- 将提取的题目和答案保存到MySQL数据库中
- 支持创建数据库表结构
- 自动保存未识别的题目记录到`Nonew/`文件夹

### 6. 屏幕区域调试功能 (`screen_debug.py`)

- 针对1260x2800分辨率设备优化的屏幕区域定义
- 截取手机屏幕并在图片上绘制识别区域边框
- 可视化显示题目区域、选项区域和按钮位置
- 支持实时调试和位置微调

### 7. 自动点击与测试功能 (`screen_tap.py`)

- 通过ADB命令模拟点击手机屏幕特定位置
- 支持点击返回、开始自测、提交考卷、确认等按钮
- 实现定时循环执行测试的功能
- 与`store_answers.py`配合使用，实现自动测试和答案存储

## 常见问题与解决方案

### 1. 自动登录失败

- 检查用户名和密码是否正确
- 检查网页结构是否发生变化（可能需要更新选择器）

### 2. 无法识别题目或选项

- 检查网页结构是否发生变化（可能需要更新选择器）
- 确保网络连接正常，页面已完全加载

### 3. 数据库查询无结果

- 检查数据库连接配置是否正确
- 确保数据库中已存在相关题目的答案
- 检查题目文本是否与数据库中的记录匹配

## 注意事项

1. 本工具仅供学习和个人使用，请勿用于任何违反平台规则的行为
2. 自动答题可能违反某些在线学习平台的服务条款，请谨慎使用
3. 在实际使用中，建议根据目标平台的网页结构调整选择器和相关参数
4. 代码中固定的用户名和密码在生产环境中存在安全风险，建议在实际部署时采用更安全的认证方式

## 开发说明

### 调试模式

如需查看详细的调试信息，可以取消代码中的注释，例如：

```python
# 在detect_question函数中取消以下注释以查看识别到的文本
print(f"识别到的单词区域文本: {question}")
print(f"识别到的选项区域A文本: {options[0]}")
print(f"识别到的选项区域B文本: {options[1]}")
print(f"识别到的选项区域C文本: {options[2]}")
print(f"识别到的选项区域D文本: {options[3]}")
```

### 自定义延迟时间

可以根据需要调整自动答题过程中的延迟时间，以模拟更真实的人类操作：

```python
# 在answer_question_loop函数中修改以下代码
# 当前设置为固定的0.3秒
# delay = random.uniform(0.3, 0.3)

# 修改为随机延迟，例如：
delay = random.uniform(0.5, 1.5)
