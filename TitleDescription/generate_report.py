"""
生成HTML格式的评估结果报告
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict


class ReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        self.css_style = """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header .meta {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }
            
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .stat-card .value {
                font-size: 2.5em;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 5px;
            }
            
            .stat-card .label {
                color: #666;
                font-size: 0.9em;
            }
            
            .filters {
                padding: 20px 30px;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                align-items: center;
            }
            
            .filter-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .filter-group label {
                font-weight: 600;
                color: #495057;
            }
            
            .filter-group input,
            .filter-group select {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .filter-group input {
                min-width: 200px;
            }
            
            .products {
                padding: 30px;
            }
            
            .product-card {
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                margin-bottom: 25px;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .product-card:hover {
                box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            
            .product-header {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 20px;
                border-bottom: 2px solid #dee2e6;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .product-header:hover {
                background: linear-gradient(135deg, #e9ecef 0%, #adb5bd 100%);
            }
            
            .product-title {
                font-size: 1.3em;
                font-weight: 600;
                color: #212529;
                flex: 1;
            }
            
            .product-scores {
                display: flex;
                gap: 20px;
                align-items: center;
            }
            
            .score-badge {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9em;
            }
            
            .score-excellent {
                background: #d4edda;
                color: #155724;
            }
            
            .score-good {
                background: #d1ecf1;
                color: #0c5460;
            }
            
            .score-average {
                background: #fff3cd;
                color: #856404;
            }
            
            .score-poor {
                background: #f8d7da;
                color: #721c24;
            }
            
            .product-content {
                padding: 25px;
                display: none;
            }
            
            .product-content.expanded {
                display: block;
            }
            
            .section {
                margin-bottom: 25px;
            }
            
            .section-title {
                font-size: 1.2em;
                font-weight: 600;
                color: #495057;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #dee2e6;
            }
            
            .original-content {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 15px;
                border-left: 4px solid #6c757d;
            }
            
            .original-content h4 {
                color: #495057;
                margin-bottom: 8px;
                font-size: 0.9em;
                text-transform: uppercase;
            }
            
            .original-content p {
                color: #212529;
                line-height: 1.6;
            }
            
            .evaluation-details {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
            .criteria-group {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
            }
            
            .criteria-group h4 {
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.1em;
            }
            
            .criterion {
                background: white;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 12px;
                border-left: 4px solid #dee2e6;
            }
            
            .criterion-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            
            .criterion-name {
                font-weight: 600;
                color: #212529;
                font-size: 0.95em;
            }
            
            .criterion-score {
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 600;
                font-size: 0.85em;
            }
            
            .criterion-reason {
                color: #6c757d;
                font-size: 0.9em;
                line-height: 1.5;
                margin-top: 8px;
            }
            
            .overall-score {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-top: 20px;
            }
            
            .overall-score .value {
                font-size: 3em;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .overall-score .label {
                font-size: 1.1em;
                opacity: 0.9;
            }
            
            .no-results {
                text-align: center;
                padding: 60px 20px;
                color: #6c757d;
                font-size: 1.2em;
            }
            
            @media (max-width: 768px) {
                .evaluation-details {
                    grid-template-columns: 1fr;
                }
                
                .product-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 15px;
                }
                
                .product-scores {
                    width: 100%;
                    flex-wrap: wrap;
                }
            }
        </style>
        """
        
        self.js_script = """
        <script>
            function toggleProduct(element) {
                const content = element.nextElementSibling;
                content.classList.toggle('expanded');
            }
            
            function filterProducts() {
                const searchTerm = document.getElementById('search').value.toLowerCase();
                const scoreFilter = document.getElementById('scoreFilter').value;
                const cards = document.querySelectorAll('.product-card');
                let visibleCount = 0;
                
                cards.forEach(card => {
                    const title = card.querySelector('.product-title').textContent.toLowerCase();
                    const overallScore = parseInt(card.querySelector('.overall-score-value')?.textContent || '0');
                    
                    const matchesSearch = title.includes(searchTerm);
                    const matchesScore = scoreFilter === 'all' || 
                                        (scoreFilter === 'excellent' && overallScore === 2) ||
                                        (scoreFilter === 'good' && overallScore === 1) ||
                                        (scoreFilter === 'poor' && overallScore === 0);
                    
                    if (matchesSearch && matchesScore) {
                        card.style.display = 'block';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                // 更新统计信息
                document.getElementById('visibleCount').textContent = visibleCount;
            }
            
            // 页面加载时初始化
            document.addEventListener('DOMContentLoaded', function() {
                filterProducts();
            });
        </script>
        """
    
    def get_score_class(self, score):
        """根据分数返回CSS类名"""
        if score == 2:
            return "score-excellent"
        elif score == 1:
            return "score-good"
        elif score == 0:
            return "score-poor"
        else:
            return "score-average"
    
    def format_criteria(self, evaluation_data: Dict, criteria_type: str) -> str:
        """格式化评估标准"""
        html = ""
        
        if isinstance(evaluation_data, str):
            try:
                evaluation_data = json.loads(evaluation_data)
            except:
                return "<p>无法解析评估数据</p>"
        
        criteria_dict = evaluation_data.get(criteria_type, {})
        
        if not criteria_dict:
            return "<p>暂无数据</p>"
        
        for key, value in criteria_dict.items():
            if isinstance(value, dict):
                score = value.get('score', 0)
                reason = value.get('reason', 'No reason provided')
                
                score_class = self.get_score_class(score)
                
                html += f"""
                <div class="criterion">
                    <div class="criterion-header">
                        <span class="criterion-name">{key.replace('_', ' ').title()}</span>
                        <span class="criterion-score {score_class}">{score}/2</span>
                    </div>
                    <div class="criterion-reason">{reason}</div>
                </div>
                """
        
        return html
    
    def generate_html(self, csv_file: str, output_file: str = None) -> str:
        """生成HTML报告"""
        
        # 确保输入文件路径正确（支持从results文件夹读取）
        if not os.path.isabs(csv_file) and not os.path.exists(csv_file):
            # 尝试从results文件夹读取
            results_path = os.path.join("results", csv_file)
            if os.path.exists(results_path):
                csv_file = results_path
        
        if output_file is None:
            # 默认保存到reports文件夹
            base_name = os.path.basename(csv_file).replace('.csv', '').replace('_evaluated', '')
            os.makedirs("reports", exist_ok=True)
            output_file = os.path.join("reports", f"{base_name}_report.html")
        else:
            # 如果指定了输出文件，确保reports文件夹存在
            if not os.path.isabs(output_file):
                os.makedirs("reports", exist_ok=True)
                if not output_file.startswith("reports/"):
                    output_file = os.path.join("reports", output_file)
        
        # 读取CSV数据
        products = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        if not products:
            return "没有找到评估数据"
        
        # 计算统计信息
        total_products = len(products)
        avg_title_score = sum(float(p.get('title_score', 0)) for p in products) / total_products
        avg_desc_score = sum(float(p.get('description_score', 0)) for p in products) / total_products
        avg_overall = sum(float(p.get('overall_score', 0)) for p in products) / total_products
        
        excellent_count = sum(1 for p in products if float(p.get('overall_score', 0)) == 2)
        good_count = sum(1 for p in products if float(p.get('overall_score', 0)) == 1)
        poor_count = sum(1 for p in products if float(p.get('overall_score', 0)) == 0)
        
        # 生成HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>商品内容评估报告</title>
    {self.css_style}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 商品内容评估报告</h1>
            <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="value">{total_products}</div>
                <div class="label">总商品数</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_title_score:.2f}</div>
                <div class="label">平均Title评分</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_desc_score:.2f}</div>
                <div class="label">平均Description评分</div>
            </div>
            <div class="stat-card">
                <div class="value">{avg_overall:.2f}</div>
                <div class="label">平均综合评分</div>
            </div>
            <div class="stat-card">
                <div class="value">{excellent_count}</div>
                <div class="label">优秀 (2分)</div>
            </div>
            <div class="stat-card">
                <div class="value">{good_count}</div>
                <div class="label">良好 (1分)</div>
            </div>
            <div class="stat-card">
                <div class="value">{poor_count}</div>
                <div class="label">需改进 (0分)</div>
            </div>
            <div class="stat-card">
                <div class="value" id="visibleCount">{total_products}</div>
                <div class="label">当前显示</div>
            </div>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <label for="search">🔍 搜索:</label>
                <input type="text" id="search" placeholder="搜索商品标题..." oninput="filterProducts()">
            </div>
            <div class="filter-group">
                <label for="scoreFilter">📊 评分筛选:</label>
                <select id="scoreFilter" onchange="filterProducts()">
                    <option value="all">全部</option>
                    <option value="excellent">优秀 (2分)</option>
                    <option value="good">良好 (1分)</option>
                    <option value="poor">需改进 (0分)</option>
                </select>
            </div>
        </div>
        
        <div class="products">
"""
        
        # 生成每个商品的卡片
        for idx, product in enumerate(products):
            original_title = product.get('Title_Original', product.get('original_title', 'N/A'))
            original_desc = product.get('Description_original', product.get('original_description', 'N/A'))
            optimized_title = product.get('Title_AI_optimized', product.get('optimized_title', 'N/A'))
            optimized_desc = product.get('Description_optimized_AI', product.get('optimized_description', 'N/A'))
            
            title_score = float(product.get('title_score', 0))
            desc_score = float(product.get('description_score', 0))
            overall_score = float(product.get('overall_score', 0))
            
            title_eval = product.get('title_evaluation', '{}')
            desc_eval = product.get('description_evaluation', '{}')
            
            # 解析评估数据
            try:
                title_eval_data = json.loads(title_eval) if isinstance(title_eval, str) else title_eval
                desc_eval_data = json.loads(desc_eval) if isinstance(desc_eval, str) else desc_eval
            except:
                title_eval_data = {}
                desc_eval_data = {}
            
            score_class = self.get_score_class(int(overall_score))
            
            html += f"""
            <div class="product-card">
                <div class="product-header" onclick="toggleProduct(this)">
                    <div class="product-title">{original_title[:80]}{'...' if len(original_title) > 80 else ''}</div>
                    <div class="product-scores">
                        <span class="score-badge {self.get_score_class(int(title_score))}">Title: {title_score}/2</span>
                        <span class="score-badge {self.get_score_class(int(desc_score))}">Desc: {desc_score}/2</span>
                        <span class="score-badge {score_class}">Overall: {overall_score}/2</span>
                    </div>
                </div>
                
                <div class="product-content">
                    <div class="section">
                        <h3 class="section-title">📝 原始内容</h3>
                        <div class="original-content">
                            <h4>原始标题:</h4>
                            <p>{original_title}</p>
                        </div>
                        <div class="original-content">
                            <h4>原始描述:</h4>
                            <p>{original_desc[:500]}{'...' if len(original_desc) > 500 else ''}</p>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">✨ 优化后内容</h3>
                        <div class="original-content">
                            <h4>优化后标题:</h4>
                            <p>{optimized_title}</p>
                        </div>
                        <div class="original-content">
                            <h4>优化后描述:</h4>
                            <p>{optimized_desc[:500]}{'...' if len(optimized_desc) > 500 else ''}</p>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3 class="section-title">📊 详细评估</h3>
                        <div class="evaluation-details">
                            <div class="criteria-group">
                                <h4>Title 评估</h4>
                                <div>
                                    <h5 style="margin: 15px 0 10px 0; color: #28a745;">✓ Must Have 标准</h5>
                                    {self.format_criteria(title_eval_data, 'must_have')}
                                    <h5 style="margin: 15px 0 10px 0; color: #dc3545;">✗ Must Avoid 标准</h5>
                                    {self.format_criteria(title_eval_data, 'must_avoid')}
                                </div>
                            </div>
                            
                            <div class="criteria-group">
                                <h4>Description 评估</h4>
                                <div>
                                    <h5 style="margin: 15px 0 10px 0; color: #28a745;">✓ Must Have 标准</h5>
                                    {self.format_criteria(desc_eval_data, 'must_have')}
                                    <h5 style="margin: 15px 0 10px 0; color: #dc3545;">✗ Must Avoid 标准</h5>
                                    {self.format_criteria(desc_eval_data, 'must_avoid')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="overall-score">
                            <div class="value overall-score-value">{overall_score}</div>
                            <div class="label">综合评分 (满分: 2)</div>
                        </div>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
    </div>
    """ + self.js_script + """
</body>
</html>
"""
        
        # 保存HTML文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成HTML评估报告')
    parser.add_argument('input_file', help='输入的评估结果CSV文件路径')
    parser.add_argument('-o', '--output', help='输出HTML文件路径（可选）')
    
    args = parser.parse_args()
    
    generator = ReportGenerator()
    output_file = generator.generate_html(args.input_file, args.output)
    
    print(f"✅ 报告已生成: {output_file}")
    print(f"📂 请在浏览器中打开查看")


if __name__ == "__main__":
    main()

