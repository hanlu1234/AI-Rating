# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 设置API Key

### 方式1：使用环境变量（推荐）
```bash
export QWEN_API_KEY=your_api_key_here
```

### 方式2：创建.env文件
```bash
echo "QWEN_API_KEY=your_api_key_here" > .env
```

> 获取API Key: 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)

## 3. 准备输入文件

1. 进入TitleDescription目录：
```bash
cd TitleDescription
```

2. 创建文件夹结构（如果不存在）：
```bash
mkdir -p input results reports
```

3. 将您的CSV文件放到 `input/` 文件夹中

3. 确保CSV文件包含以下列：
- `Title_Original` 或 `original_title`
- `Description_original` 或 `original_description`
- `Title_AI_optimized` 或 `optimized_title`（可以是JSON数组格式，如 `["title1", "title2"]`）
- `Description_optimized_AI` 或 `optimized_description`
- `lang` (可选): 语言字段（`de`=德语, `en`=英语, `zh`=中文）

参考示例：`input/input_template.csv`

## 4. 运行评估

### 基本用法（推荐）
```bash
# 进入TitleDescription目录
cd TitleDescription

# 从input文件夹读取，结果自动保存到results文件夹
python3 evaluator.py input/your_file.csv
```

### 指定输出文件
```bash
cd TitleDescription
python3 evaluator.py input/your_file.csv -o results/custom_output.csv
```

### 使用不同模型
```bash
cd TitleDescription
# 使用qwen-turbo（更快更便宜）
python3 evaluator.py input/your_file.csv --model qwen-turbo

# 使用qwen-max（更准确）
python3 evaluator.py input/your_file.csv --model qwen-max
```

### 命令行指定API Key
```bash
cd TitleDescription
python3 evaluator.py input/your_file.csv --api-key your_api_key_here
```

> **注意**：在 macOS 和某些 Linux 系统上，需要使用 `python3` 而不是 `python`。如果您的系统上 `python` 命令可用，也可以使用 `python`。

## 5. 查看结果

### 方式1: 查看CSV文件

评估完成后，会生成包含以下信息的CSV文件：
- 原始数据
- `title_score`: Title评分 (0-2)
- `description_score`: Description评分 (0-2)
- `overall_score`: 综合评分 (0-2)
- `title_must_have_score`: Title Must Have评分
- `title_must_avoid_score`: Title Must Avoid评分
- `description_must_have_score`: Description Must Have评分
- `description_must_avoid_score`: Description Must Avoid评分
- `title_evaluation`: Title详细评估（JSON格式）
- `description_evaluation`: Description详细评估（JSON格式）

### 方式2: 生成HTML报告（推荐）

生成美观的网页报告，方便审核：

```bash
# 进入TitleDescription目录
cd TitleDescription

# 从results文件夹读取，报告自动保存到reports文件夹
python3 generate_report.py results/your_file_evaluated.csv
```

然后在浏览器中打开 `TitleDescription/reports/your_file_report.html` 查看。

报告特点：
- ✅ 美观的界面设计
- ✅ 统计信息总览
- ✅ 搜索和筛选功能
- ✅ 详细的评估原因展示
- ✅ 支持展开/折叠查看

## 常见问题

**Q: 如何选择模型？**
- `qwen-turbo`: 适合快速评估，成本低
- `qwen-plus`: 平衡性能和成本（推荐）
- `qwen-max`: 适合高精度要求

**Q: API调用失败怎么办？**
- 检查API Key是否正确
- 确认账户余额充足
- 检查网络连接
- 查看错误信息中的详细说明

**Q: 如何批量处理大量数据？**
- 系统会自动处理CSV中的所有行
- 注意API调用频率限制
- 建议分批处理大量数据
