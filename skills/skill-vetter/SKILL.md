# SKILL.md - Skill Vetter

## Description
技能审查，在安装来自ClawHub、GitHub或其他来源的任何技能前帮你检查是否安全。

## When to Use
- 安装新技能前
- 检查技能安全性
- 防止API密钥与隐私泄露

## Usage

### 审查技能
```
审查技能：[技能名称或路径]
```

### 检查要点
1. 读取SKILL.md文件
2. 检查是否需要额外权限
3. 检查是否需要API密钥
4. 检查是否有可疑操作
5. 确认安全后安装

## Example

审查技能：
```
请帮我审查这个技能是否安全：/path/to/skill
```

## Security Checklist
- [ ] 不需要管理员权限
- [ ] 不需要敏感API密钥
- [ ] 不访问隐私数据
- [ ] 不执行危险命令
- [ ] 代码开源可审计

## Note
当前为简化版，使用人工审查+代码检查。
