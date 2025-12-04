# 商品内容AI评估系统

这是一个使用AI评估优化后商品标题（Title）和描述（Description）是否符合标准的自动化工具。

## 功能特点

- ✅ 自动评估商品标题是否符合7项标准
- ✅ 自动评估商品描述是否符合8项标准
- ✅ 使用0/1/2三级评分系统（0=不符合，1=部分符合，2=完全符合）
- ✅ 批量处理CSV文件
- ✅ 生成详细的评估报告

## 安装

1. 进入项目目录：
```bash
cd TitleDescription
```

2. 安装Python依赖：
```bash
pip install -r requirements.txt
```

3. 设置Qwen/DashScope API Key：

方式1：创建`.env`文件
```bash
echo "QWEN_API_KEY=your_api_key_here" > .env
# 或者
echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
```

方式2：使用环境变量
```bash
export QWEN_API_KEY=your_api_key_here
# 或者
export DASHSCOPE_API_KEY=your_api_key_here
```

> 注意：您可以在[阿里云DashScope控制台](https://dashscope.console.aliyun.com/)获取API Key

## 文件组织结构

项目使用以下文件夹结构：

```
TitleDescription/
├── input/          # 输入CSV文件
├── results/        # 评估结果CSV文件
├── reports/        # HTML报告文件
├── evaluator.py    # 评估脚本
└── generate_report.py  # 报告生成脚本
```

## 输入文件格式

输入文件应为CSV格式，**建议放在 `input/` 文件夹中**，包含以下列：

- `Title_Original`: 原始标题
- `Description_original`: 原始描述
- `Title_AI_optimized`: AI优化后的标题（可以是JSON数组格式，如 `["title1", "title2"]`，系统会自动评估所有并选择最佳）
- `Description_optimized_AI`: AI优化后的描述
- `lang` (可选): 语言字段，指定源语言（如 `de`=德语, `en`=英语, `zh`=中文）。如果设置了此字段，系统将直接使用该语言进行评估，跳过自动语言检测

> **注意**：代码也支持旧的列名（`original_title`, `original_description`, `optimized_title`, `optimized_description`）以保持向后兼容。

> **语言处理**：
> - 如果CSV中有 `lang` 字段，系统将直接使用该字段的值作为源语言进行评估
> - 如果没有 `lang` 字段，系统会自动检测语言
> - 系统会使用指定的或检测到的语言进行评估
> - 评估结果中的reason字段始终为英文
> - 原始内容不会被翻译，保持原始语言

> **多个优化Title**：如果 `Title_AI_optimized` 字段包含多个title（JSON数组格式），系统会分别评估每个title并自动选择评分最高的一个。

示例文件：`input/input_template.csv`

## 使用方法

### 命令行使用

```bash
# 进入TitleDescription目录
cd TitleDescription

# 从input文件夹读取文件，结果保存到results文件夹
python3 evaluator.py input/your_file.csv

# 或者指定完整路径
python3 evaluator.py input/your_file.csv -o results/output_file.csv
```

> **注意**：在 macOS 和某些 Linux 系统上，需要使用 `python3` 而不是 `python`

参数说明：
- `input_file.csv`: 输入的CSV文件路径（必需，建议放在 `input/` 文件夹中）
- `-o, --output`: 输出文件路径（可选，默认保存到 `results/` 文件夹，文件名为 `输入文件名_evaluated.csv`）
- `--api-key`: Qwen/DashScope API Key（可选，如果已设置环境变量则不需要）
- `--model`: 使用的模型名称（可选，默认: qwen-plus，可选: qwen-turbo, qwen-max等）

### Python代码使用

```python
from evaluator import ProductContentEvaluator

# 初始化评估器（默认使用qwen-plus模型）
evaluator = ProductContentEvaluator(api_key="your_api_key", model="qwen-plus")

# 评估单个商品
result = evaluator.evaluate_product(
    original_title="原始标题",
    original_description="原始描述",
    optimized_title="优化后的标题",
    optimized_description="优化后的描述"
)

# 从CSV文件批量评估
evaluator.evaluate_from_csv("input/input.csv", "results/output.csv")
```

## 评估标准

### Title评估标准

**必须满足的要求：**
1. **Clear Product Type**: 标题必须包含产品类型，且与原始内容一致
2. **Key Details**: 包含原始内容中的关键规格信息（尺寸、材质、品牌等）

**必须避免的问题：**
1. **No Extra Details**: 不添加原始内容中没有的信息
2. **No Repetition or Stuffing**: 避免重复单词或同义词堆砌
3. **Short and Clear**: 长度3-128字符（理想50-80字符），以产品类型开头
4. **No Forbidden Content**: 不包含价格、增值税、运费、公司名称等
5. **No Brand/Model Only**: 不能只是品牌或型号，必须包含产品类型

### Description评估标准

**必须满足的要求：**
1. **Match Title and Original**: 与标题和原始文本一致，无矛盾
2. **Key Details Upfront**: 第一句话包含产品类型和关键规格
3. **Clear Structure**: 清晰的结构（介绍句、要点列表、结论）
4. **Proper Length**: 根据输入文本长度调整输出长度
   - 输入太少：可能<601字符
   - 输入充足：必须>610字符（目标610-700）
   - 输入太多：必须600-700字符

**必须避免的问题：**
1. **No Extra Details**: 不添加原始内容中没有的益处、用例等
2. **No Repetition or Stuffing**: 避免重复单词或关键词堆砌
3. **No Forbidden Content**: 不包含价格、增值税、运费等
4. **No Care Tips or Extras**: 不添加食谱、维护建议等

## 评分系统

每个标准使用三级评分：
- **0**: 不符合标准（poor/fail）
- **1**: 部分符合标准（average/partial）
- **2**: 完全符合标准（good/success）

最终输出包含：
- 每个标准的详细评分和理由
- Title总体评分（0-2）
- Description总体评分（0-2）
- 综合评分（0-2）

## 输出格式

输出CSV文件包含原始数据以及以下评估结果列：
- `title_score`: Title总体评分
- `description_score`: Description总体评分
- `overall_score`: 综合评分
- `title_evaluation`: Title详细评估结果（JSON格式）
- `description_evaluation`: Description详细评估结果（JSON格式）
> **注意**：
> - 所有评估理由（reason字段）均为英文
> - 原始内容不会被翻译，保持原始语言

## 注意事项

1. 需要有效的Qwen/DashScope API Key（可在[阿里云DashScope控制台](https://dashscope.console.aliyun.com/)获取）
2. 评估过程会调用DashScope API，会产生费用
3. 默认使用`qwen-plus`模型，也可选择`qwen-turbo`（更快更便宜）或`qwen-max`（更准确）
4. 批量处理时请注意API调用频率限制
5. 支持的模型列表：
   - `qwen-turbo`: 快速响应，成本较低
   - `qwen-plus`: 平衡性能和成本（推荐）
   - `qwen-max`: 最高性能，成本较高

## 生成HTML报告

评估完成后，可以生成美观的HTML报告方便人工审核：

```bash
# 进入TitleDescription目录
cd TitleDescription

# 从results文件夹读取评估结果，报告保存到reports文件夹
python3 generate_report.py results/your_file_evaluated.csv

# 或者指定完整路径
python3 generate_report.py results/your_file_evaluated.csv -o reports/report.html
```

报告功能：
- 📊 统计信息总览（平均评分、评分分布等）
- 🔍 搜索和筛选功能
- 📝 详细的评估结果展示
- ✅ Must Have 和 Must Avoid 标准分别展示
- 💡 每个标准的评分和详细原因
- 📱 响应式设计，支持移动端查看

## 示例

```bash
# 1. 进入TitleDescription目录
cd TitleDescription

# 2. 将输入文件放到input文件夹
# cp your_file.csv input/

# 3. 运行评估（结果自动保存到results文件夹）
python3 evaluator.py input/your_file.csv

# 4. 生成HTML报告（报告自动保存到reports文件夹）
python3 generate_report.py results/your_file_evaluated.csv
```

评估完成后会显示：
- 评估的商品数量
- 平均Title评分
- 平均Description评分
- 平均综合评分
