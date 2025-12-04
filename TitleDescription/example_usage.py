"""
使用示例：演示如何使用商品内容评估器
"""

from evaluator import ProductContentEvaluator
import os

def example_single_evaluation():
    """单个商品评估示例"""
    
    # 确保设置了API Key
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("请先设置QWEN_API_KEY或DASHSCOPE_API_KEY环境变量")
        return
    
    # 创建评估器
    evaluator = ProductContentEvaluator(api_key=api_key, model="qwen-plus")
    
    # 评估单个商品
    result = evaluator.evaluate_product(
        original_title="Laptop Lenovo ThinkPad X1 Carbon 14 inch",
        original_description="High-performance business laptop with Intel i7 processor, 16GB RAM, 512GB SSD. Perfect for professionals.",
        optimized_title="Lenovo ThinkPad X1 Carbon 14 inch Laptop",
        optimized_description="The Lenovo ThinkPad X1 Carbon 14 inch Laptop is a high-performance business laptop featuring an Intel i7 processor, 16GB RAM, and 512GB SSD storage. This professional-grade laptop delivers exceptional performance for demanding business applications."
    )
    
    # 打印结果
    print("=" * 60)
    print("评估结果")
    print("=" * 60)
    print(f"Title评分: {result['title_score']}/2")
    print(f"Description评分: {result['description_score']}/2")
    print(f"综合评分: {result['overall_score']}/2")
    print("\nTitle详细评估:")
    print(result['title_evaluation'])
    print("\nDescription详细评估:")
    print(result['description_evaluation'])


def example_batch_evaluation():
    """批量评估示例"""
    
    # 确保设置了API Key
    api_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("请先设置QWEN_API_KEY或DASHSCOPE_API_KEY环境变量")
        return
    
    # 创建评估器
    evaluator = ProductContentEvaluator(api_key=api_key, model="qwen-plus")
    
    # 从CSV文件批量评估
    input_file = "input/input_template.csv"
    output_file = "results/evaluation_results.csv"
    
    print(f"开始批量评估，输入文件: {input_file}")
    evaluator.evaluate_from_csv(input_file, output_file)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        example_batch_evaluation()
    else:
        example_single_evaluation()
