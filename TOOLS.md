# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 财务表格处理技能

### Excel / XLSX (ivangdavila/excel-xlsx)
**用途**: 创建、编辑Excel文件，处理公式、日期、格式

**核心规则**:
- 分析用 pandas，公式/格式用 openpyxl
- Excel日期是序列号（1900/1904系统）
- 保持工作簿活跃：写入公式而非硬编码结果
- 保护数据类型（长ID、电话号码存为文本）
- 保存前重新计算，检查 #REF! / #DIV/0! 错误

**常用代码**:
```python
import openpyxl

# 读取
wb = openpyxl.load_workbook('file.xlsx')
ws = wb.active

# 写入公式
ws['A1'] = '=SUM(B1:B10)'

# 保存
wb.save('file.xlsx')
```

### Sheetsmith (CrimsonDevil333333/sheetsmith)
**用途**: Pandas驱动的CSV/Excel快速分析

**命令**:
```bash
# 查看摘要
python3 skills/sheetsmith/scripts/sheetsmith.py summary file.csv

# 数据描述统计
python3 skills/sheetsmith/scripts/sheetsmith.py describe file.xlsx

# 预览前N行
python3 skills/sheetsmith/scripts/sheetsmith.py preview file.csv --rows 10

# 过滤数据
python3 skills/sheetsmith/scripts/sheetsmith.py filter file.csv --query "amount > 1000" --output filtered.csv

# 转换格式
python3 skills/sheetsmith/scripts/sheetsmith.py convert file.csv --output file.xlsx

# 数据转换（添加列、重命名、删除）
python3 skills/sheetsmith/scripts/sheetsmith.py transform file.csv --expr "total = quantity * price" --output new.csv
```

**依赖**: pandas, openpyxl, xlrd, tabulate

---

Add whatever helps you do your job. This is your cheat sheet.
