---
name: finance-table-processor
description: 财务表格处理器 - 专门处理收支明细表。自动识别日期、金额、类型列，计算汇总统计，生成月度报表。支持Excel/CSV格式，输出带格式的财务报表。
---

# 财务表格处理器

专门处理**收支明细表**的财务工具，自动识别表格结构，计算汇总统计，生成专业报表。

## 功能特性

- ✅ 自动识别关键列（日期、金额、类型、备注）
- ✅ 数据清洗（日期格式统一、金额清理）
- ✅ 自动分类收入和支出
- ✅ 计算汇总统计（总收入、总支出、净收支）
- ✅ 生成月度报表
- ✅ 导出带格式的Excel报表

## 使用方法

### 基本用法

```bash
python3 skills/finance-table-processor/scripts/finance_processor.py 收支表.xlsx
```

### 指定输出路径

```bash
python3 skills/finance-table-processor/scripts/finance_processor.py 收支表.xlsx -o 我的报表.xlsx
```

### 仅分析表格结构

```bash
python3 skills/finance-table-processor/scripts/finance_processor.py 收支表.xlsx --analyze
```

## 支持的文件格式

- Excel: `.xlsx`, `.xls`
- CSV: `.csv`

## 自动识别的列名

### 日期列
- date, 日期, 时间, time, datetime

### 金额列
- amount, 金额, money, price, sum, total

### 类型列
- type, 类型, category, 分类, 收支, income_expense

### 备注列
- description, 备注, desc, 说明, 摘要, content

## 输出报表包含

1. **原始数据** - 清洗后的完整数据
2. **汇总统计** - 总收入、总支出、净收支、平均值
3. **月度报表** - 按月汇总的收支情况

## 示例

### 输入表格示例

| 日期 | 类型 | 金额 | 备注 |
|------|------|------|------|
| 2025-01-01 | 收入 | 10000 | 工资 |
| 2025-01-02 | 支出 | -200 | 餐饮 |
| 2025-01-03 | 支出 | -500 | 交通 |

### 输出汇总

```
📈 汇总统计:
  总记录数: 3
  总收入: ¥10,000.00
  总支出: ¥700.00
  净收支: ¥9,300.00
```

## 依赖安装

```bash
pip install pandas openpyxl
```

## 注意事项

- 金额支持自动清理（去除￥、$、逗号等符号）
- 日期自动转换为标准格式
- 支出金额可以是负数，也可以配合类型列识别
- 输出Excel包含格式美化（表头蓝色、自动列宽）
