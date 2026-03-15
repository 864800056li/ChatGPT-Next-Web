#!/usr/bin/env python3
"""
处理客户数据文件：
1. 检测空号错号（格式验证）
2. 核实单位是否还在湖南
3. 输出清洗后的数据到桌面
"""

import pandas as pd
import re
import os
import sys
from pathlib import Path

def validate_phone_number(phone):
    """
    验证电话号码格式（中国手机号）
    格式：1开头，11位数字
    """
    if not isinstance(phone, str):
        phone = str(phone)
    
    # 清理空格和特殊字符
    phone = re.sub(r'[^\d]', '', phone)
    
    # 验证手机号格式
    if len(phone) == 11 and phone.startswith('1'):
        return phone, True
    else:
        return phone, False

def check_hunan_address(address):
    """
    检查地址是否包含"湖南"
    """
    if not isinstance(address, str):
        address = str(address)
    
    # 检查是否包含湖南关键词
    hunan_keywords = ['湖南', '湖南省', 'Hunan']
    for keyword in hunan_keywords:
        if keyword in address:
            return True
    return False

def process_large_file(input_file, output_file, phone_col='phone', address_col='address'):
    """
    处理大型数据文件（支持分块读取）
    """
    print(f"开始处理文件: {input_file}")
    print(f"输出文件: {output_file}")
    
    # 检测文件格式
    if input_file.endswith('.csv'):
        reader = pd.read_csv(input_file, chunksize=50000, low_memory=False)
    elif input_file.endswith(('.xlsx', '.xls')):
        # Excel文件可能需要一次性读取
        print("Excel文件检测中...")
        df = pd.read_excel(input_file)
        reader = [df]  # 作为单个块处理
    else:
        print("不支持的文件格式，请使用CSV或Excel文件")
        return False
    
    all_valid_data = []
    total_rows = 0
    valid_rows = 0
    
    for i, chunk in enumerate(reader):
        print(f"处理第 {i+1} 个数据块，大小: {len(chunk)} 行")
        
        # 确保列名存在
        if phone_col not in chunk.columns:
            print(f"错误：未找到电话列 '{phone_col}'，可用列: {list(chunk.columns)}")
            # 尝试猜测列名
            possible_cols = [col for col in chunk.columns if '电话' in col or '手机' in col or 'phone' in col.lower()]
            if possible_cols:
                phone_col = possible_cols[0]
                print(f"使用猜测的电话列: {phone_col}")
            else:
                print("请指定正确的电话列名")
                return False
        
        if address_col not in chunk.columns:
            print(f"警告：未找到地址列 '{address_col}'，可用列: {list(chunk.columns)}")
            possible_cols = [col for col in chunk.columns if '地址' in col or '单位' in col or 'address' in col.lower()]
            if possible_cols:
                address_col = possible_cols[0]
                print(f"使用猜测的地址列: {address_col}")
            else:
                print("继续处理，但不会验证地址")
                address_col = None
        
        # 处理每一行
        for idx, row in chunk.iterrows():
            total_rows += 1
            
            # 验证电话号码
            phone, is_valid_phone = validate_phone_number(row[phone_col])
            
            # 验证地址（如果地址列存在）
            is_hunan = True  # 默认通过
            if address_col and address_col in row:
                is_hunan = check_hunan_address(row[address_col])
            
            # 如果电话有效且在湖南，保留该行
            if is_valid_phone and is_hunan:
                valid_rows += 1
                # 更新清理后的电话号码
                row[phone_col] = phone
                all_valid_data.append(row)
        
        print(f"进度: 已处理 {total_rows} 行，有效 {valid_rows} 行")
        
        # 每处理10万行保存一次中间结果
        if len(all_valid_data) >= 100000:
            save_intermediate(all_valid_data, output_file, i+1)
            all_valid_data = []  # 清空已保存的数据
    
    # 保存剩余数据
    if all_valid_data:
        save_final_result(all_valid_data, output_file)
    
    print(f"处理完成！")
    print(f"总行数: {total_rows}")
    print(f"有效行数（格式正确且在湖南）: {valid_rows}")
    print(f"无效/空号/外地行数: {total_rows - valid_rows}")
    print(f"输出文件: {output_file}")
    
    return True

def save_intermediate(data, output_file, chunk_num):
    """保存中间结果"""
    temp_file = output_file.replace('.csv', f'_temp_chunk_{chunk_num}.csv')
    df = pd.DataFrame(data)
    
    # 如果是第一次保存，包含表头
    header = chunk_num == 1
    df.to_csv(temp_file, index=False, mode='w' if header else 'a', header=header)
    print(f"已保存中间文件: {temp_file}")

def save_final_result(data, output_file):
    """保存最终结果"""
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"最终结果已保存: {output_file}")

def main():
    # 设置桌面输出路径
    desktop = Path.home() / 'Desktop'
    output_file = desktop / 'cleaned_customer_data.csv'
    
    # 如果命令行提供了输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if not os.path.exists(input_file):
            print(f"文件不存在: {input_file}")
            sys.exit(1)
    else:
        print("请指定输入文件路径")
        print("用法: python data_processor.py <输入文件> [电话列名] [地址列名]")
        sys.exit(1)
    
    # 获取列名参数
    phone_col = sys.argv[2] if len(sys.argv) > 2 else 'phone'
    address_col = sys.argv[3] if len(sys.argv) > 3 else 'address'
    
    # 处理文件
    success = process_large_file(input_file, str(output_file), phone_col, address_col)
    
    if success:
        print(f"✅ 处理完成！结果已保存到桌面: {output_file}")
    else:
        print("❌ 处理失败")

if __name__ == '__main__':
    main()