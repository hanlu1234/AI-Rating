# 问题诊断和修复指南

## 已修复的问题

### 1. DashScope API响应处理问题 ✅

**问题描述：**
- 原代码假设响应结构为 `response.output.choices[0].message.content`
- 没有处理不同的响应格式
- 错误信息获取方式不正确

**修复内容：**
- 添加了多种响应格式的兼容处理
- 改进了错误信息获取方式
- 添加了更详细的错误提示

### 2. JSON解析错误处理 ✅

**问题描述：**
- 当AI返回的JSON格式不正确时，程序会直接崩溃
- 没有显示原始响应内容，难以调试

**修复内容：**
- 添加了专门的 `JSONDecodeError` 异常处理
- 当JSON解析失败时，会显示前500个字符的响应内容
- 提供更清晰的错误信息

### 3. API Key验证 ✅

**问题描述：**
- 如果API Key未设置，程序会在调用API时才报错
- 错误信息不够明确

**修复内容：**
- 在初始化时就验证API Key
- 提供清晰的错误提示，说明如何设置API Key

### 4. 错误追踪 ✅

**问题描述：**
- 异常发生时没有完整的堆栈跟踪信息
- 难以定位问题根源

**修复内容：**
- 添加了 `traceback.print_exc()` 来显示完整的错误堆栈
- 便于调试和问题定位

## 常见错误及解决方案

### 错误1: `API调用失败 (状态码: XXX)`

**可能原因：**
1. API Key无效或过期
2. 账户余额不足
3. 模型名称不正确
4. 网络连接问题

**解决方案：**
```bash
# 1. 检查API Key是否正确
echo $QWEN_API_KEY

# 2. 检查账户余额
# 访问 https://dashscope.console.aliyun.com/

# 3. 尝试使用不同的模型
cd TitleDescription
python3 evaluator.py input/your_file.csv --model qwen-turbo

# 4. 检查网络连接
ping dashscope.aliyuncs.com
```

### 错误2: `JSON解析失败`

**可能原因：**
1. AI返回的内容不是有效的JSON格式
2. AI返回的内容被截断
3. Prompt设计导致AI返回格式不正确

**解决方案：**
1. 查看错误信息中显示的响应内容
2. 检查Prompt是否明确要求返回JSON格式
3. 尝试降低temperature参数（已在代码中设置为0.3）
4. 如果问题持续，可以尝试使用 `qwen-max` 模型（更准确）

### 错误3: `无法解析API响应`

**可能原因：**
1. DashScope API响应格式发生变化
2. 使用了不支持的模型

**解决方案：**
1. 检查dashscope库版本：`pip show dashscope`
2. 更新到最新版本：`pip install --upgrade dashscope`
3. 确认使用的模型名称正确（qwen-turbo, qwen-plus, qwen-max等）

### 错误4: `API Key未设置`

**解决方案：**
```bash
# 方式1: 设置环境变量
export QWEN_API_KEY=your_api_key_here

# 方式2: 创建.env文件
echo "QWEN_API_KEY=your_api_key_here" > .env

# 方式3: 命令行参数
cd TitleDescription
python3 evaluator.py input/your_file.csv --api-key your_api_key_here
```

## 调试技巧

### 1. 启用详细错误信息

代码已经包含了详细的错误信息输出，包括：
- 完整的堆栈跟踪
- API响应内容（JSON解析失败时）
- 错误状态码和消息

### 2. 测试单个商品

使用 `example_usage.py` 测试单个商品的评估：

```python
python example_usage.py
```

### 3. 检查CSV文件格式

确保CSV文件包含以下列：
- `original_title`
- `original_description`
- `optimized_title`
- `optimized_description`

### 4. 验证API连接

创建一个简单的测试脚本：

```python
import dashscope
from dashscope import Generation

dashscope.api_key = "your_api_key"

response = Generation.call(
    model='qwen-plus',
    messages=[{'role': 'user', 'content': 'Hello'}]
)

print(response)
```

## 性能优化建议

1. **批量处理时添加延迟**：如果遇到频率限制，可以在循环中添加 `time.sleep(1)`
2. **使用qwen-turbo**：对于大量数据，使用更快的模型可以节省时间
3. **分批处理**：将大文件分成多个小文件处理，避免一次性处理过多数据

## 联系支持

如果问题仍然存在，请提供以下信息：
1. 完整的错误信息（包括堆栈跟踪）
2. Python版本：`python --version`
3. dashscope版本：`pip show dashscope`
4. 使用的模型名称
5. 输入数据的示例（去除敏感信息）









