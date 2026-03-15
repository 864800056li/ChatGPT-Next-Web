#!/usr/bin/env python3
"""
简单的数据处理器 - 使用Python内置csv模块
处理客户数据文件，验证电话和地址
"""

import csv
import re
import os
import sys
from pathlib import Path

def validate_phone(phone_str):
    """验证手机号格式"""
    if not isinstance(phone_str, str):
        phone_str = str(phone_str)
    
    # 清理非数字字符
    cleaned = re.sub(r'[^\d]', '', phone_str)
    
    # 验证: 11位且以1开头
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return cleaned, True
    return phone_str, False

def is_hunan_address(address_str):
    """检查地址是否在湖南"""
    if not isinstance(address_str, str):
        address_str = str(address_str)
    
    # 检查是否包含湖南关键词
    keywords = ['湖南', '湖南省', 'Hunan']
    return any(keyword in address_str for keyword in keywords)

def process_csv_stream(input_path, output_path, phone_col='phone', address_col='address'):
    """流式处理CSV文件"""
    
    print(f"开始处理: {input_path}")
    
    # 尝试自动检测列名
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.readline()
        if not sample:
            print("文件为空")
            return False
        
        # 猜测分隔符
        if ',' in sample:
            delimiter = ','
        elif ';' in sample:
            delimiter = ';'
        elif '\t' in sample:
            delimiter = '\t'
        else:
            delimiter = ','
        
        # 读取第一行作为表头
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter)
        fieldnames = reader.fieldnames
        
        if not fieldnames:
            print("无法读取CSV表头")
            return False
        
        print(f"检测到的列: {fieldnames}")
        
        # 查找电话和地址列
        if phone_col not in fieldnames:
            # 尝试猜测
            possible = [col for col in fieldnames if '电话' in col or '手机' in col or 'phone' in col.lower()]
            if possible:
                phone_col = possible[0]
                print(f"使用电话列: {phone_col}")
            else:
                print(f"请指定电话列名，可用列: {fieldnames}")
                return False
        
        if address_col not in fieldnames:
            possible = [col for col in fieldnames if '地址' in col or '单位' in col or 'address' in col.lower()]
            if possible:
                address_col = possible[0]
                print(f"使用地址列: {address_col}")
            else:
                print(f"警告: 未找到地址列，将跳过地址验证")
                address_col = None
        
        # 准备输出
        output_fields = fieldnames  # 保持原列顺序
        
        total = 0
        valid = 0
        
        with open(output_path, 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.DictWriter(out_f, fieldnames=output_fields)
            writer.writeheader()
            
            # 处理每一行
            for row in reader:
                total += 1
                
                # 验证电话
                phone_val = row.get(phone_col, '')
                phone_clean, phone_ok = validate_phone(phone_val)
                row[phone_col] = phone_clean
                
                # 验证地址
                address_ok = True
                if address_col and address_col in row:
                    address_val = row.get(address_col, '')
                    address_ok = is_hunan_address(address_val)
                
                # 如果电话格式正确且在湖南（或地址未验证），则保留
                if phone_ok and address_ok:
                    valid += 1
                    writer.writerow(row)
                
                # 进度显示
                if total % 10000 == 0:
                    print(f"已处理 {total} 行，有效 {valid} 行")
        
        print(f"处理完成!")
        print(f"总行数: {total}")
        print(f"有效行数: {valid}")
        print(f"无效行数: {total - valid}")
        print(f"输出文件: {output_path}")
        
        return True

def process_excel_file(input_path, output_path):
    """处理Excel文件 - 需要pandas"""
    try:
        import pandas as pd
    except ImportError:
        print("需要pandas库来处理Excel文件")
        print("请安装: pip3 install pandas openpyxl")
        return False
    
    print(f"读取Excel文件: {input_path}")
    
    # 读取Excel
    df = pd.read_excel(input_path)
    print(f"数据形状: {df.shape}")
    
    # 暂时使用简单的处理逻辑
    # 这里可以调用相同的验证函数
    
    # 保存为CSV
    df.to_csv(output_path, index=False)
    print(f"Excel已转换为CSV: {output_path}")
    
    # 然后处理CSV
    return process_csv_stream(output_path, output_path.replace('.csv', '_cleaned.csv'))

def main():
    if len(sys.argv) < 2:
        print("请指定输入文件路径")
        print("用法: python data_processor_simple.py <输入文件> [电话列名] [地址列名]")
        print("示例: python data_processor_simple.py data.csv phone address")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        sys.exit(1)
    
    # 设置输出路径
    desktop = Path.home() / 'Desktop'
    if not desktop.exists():
        desktop = Path.cwd()
    
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = desktop / f"{input_name}_cleaned.csv"
    
    # 列名参数
    phone_col = sys.argv[2] if len(sys.argv) > 2 else 'phone'
    address_col = sys.argv[3] if len(sys.argv) > 3 else 'address'
    
    # 根据文件类型选择处理方式
    if input_file.lower().endswith(('.csv', '.txt')):
        success = process_csv_stream(input_file, str(output_file), phone_col, address_col)
    elif input_file.lower().endswith(('.xlsx', '.xls')):
        success = process_excel_file(input_file, str(output_file))
    else:
        print(f"不支持的文件格式: {input_file}")
        success = False
    
    if success:
        print(f"✅ 处理完成! 结果保存在: {output_file}")
    else:
        print("❌ 处理失败")

if __name__ == '__main__':
    main()