"""
过滤CSV文件中重复的title
对于每个URL，每个title只保留第一个出现的记录
"""

import csv
import os
from collections import defaultdict
from datetime import datetime


def filter_duplicate_titles(input_file: str, output_file: str = None):
    """过滤重复的title，每个URL中每个title只保留第一个
    
    Args:
        input_file: 输入CSV文件路径
        output_file: 输出CSV文件路径（可选）
    """
    
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在: {input_file}")
        return
    
    # 如果没有指定输出文件，自动生成
    if output_file is None:
        base_name = os.path.basename(input_file).replace(".csv", "")
        dir_name = os.path.dirname(input_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(dir_name, f"{base_name}_filtered_{timestamp}.csv")
    
    # 用于跟踪每个 (url, title) 组合是否已出现
    seen_combinations = set()
    unique_rows = []
    duplicate_count = 0
    total_count = 0
    
    # 读取CSV文件
    print(f"正在读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if 'title' not in fieldnames or 'url' not in fieldnames:
            print("错误: CSV文件必须包含 'title' 和 'url' 列")
            return
        
        for row in reader:
            total_count += 1
            title = row.get('title', '').strip()
            url = row.get('url', '').strip()
            
            # 创建唯一标识 (url, title)
            combination = (url, title)
            
            # 如果这个组合还没出现过，保留这一行
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                unique_rows.append(row)
            else:
                duplicate_count += 1
    
    # 写入新的CSV文件
    print(f"正在写入过滤后的文件: {output_file}")
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)
    
    # 打印统计信息
    print(f"\n✅ 过滤完成！")
    print(f"   原始记录数: {total_count}")
    print(f"   去重后记录数: {len(unique_rows)}")
    print(f"   删除重复记录数: {duplicate_count}")
    print(f"   保留率: {len(unique_rows)/total_count*100:.2f}%")
    print(f"   输出文件: {output_file}")
    
    # 统计每个URL的去重情况
    url_stats = defaultdict(lambda: {'total': 0, 'unique': 0})
    for row in unique_rows:
        url = row.get('url', '').strip()
        url_stats[url]['unique'] += 1
    
    # 重新读取原始文件统计每个URL的总数
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '').strip()
            url_stats[url]['total'] += 1
    
    print(f"\n📊 URL统计信息（前10个）:")
    sorted_urls = sorted(url_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    for url, stats in sorted_urls[:10]:
        print(f"   {url[:60]}...")
        print(f"      原始: {stats['total']}, 去重后: {stats['unique']}, 删除: {stats['total'] - stats['unique']}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='过滤CSV文件中重复的title（每个URL中每个title只保留第一个）')
    parser.add_argument('input_file', help='输入CSV文件路径')
    parser.add_argument('-o', '--output', help='输出CSV文件路径（可选，默认为输入文件名_filtered_时间戳.csv）')
    
    args = parser.parse_args()
    
    filter_duplicate_titles(args.input_file, args.output)


if __name__ == "__main__":
    main()

