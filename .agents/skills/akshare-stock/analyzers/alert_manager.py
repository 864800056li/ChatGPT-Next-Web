#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格预警系统 - 监控股价突破/跌破设定价位
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

class AlertType(Enum):
    PRICE_ABOVE = "突破"
    PRICE_BELOW = "跌破"
    CHANGE_PCT_ABOVE = "涨幅超过"
    CHANGE_PCT_BELOW = "跌幅超过"
    VOLUME_ABOVE = "放量"

@dataclass
class PriceAlert:
    """价格预警"""
    id: str
    code: str
    name: str
    alert_type: str
    threshold: float
    created_at: str
    triggered: bool = False
    triggered_at: Optional[str] = None
    message: str = ""

class AlertManager:
    """预警管理器"""
    
    def __init__(self):
        self.data_dir = Path.home() / ".openclaw" / "workspace" / "stock_alerts"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.alerts: List[PriceAlert] = []
        self.load()
    
    def load(self):
        """加载预警"""
        file_path = self.data_dir / "alerts.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.alerts = [PriceAlert(**a) for a in data.get('alerts', [])]
    
    def save(self):
        """保存预警"""
        file_path = self.data_dir / "alerts.json"
        data = {
            'alerts': [asdict(a) for a in self.alerts],
            'updated_at': datetime.now().isoformat()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_alert(self, code: str, name: str, alert_type: str, threshold: float, message: str = "") -> str:
        """添加预警"""
        import uuid
        alert_id = str(uuid.uuid4())[:8]
        
        alert = PriceAlert(
            id=alert_id,
            code=code,
            name=name,
            alert_type=alert_type,
            threshold=threshold,
            created_at=datetime.now().isoformat(),
            message=message or f"{name}({code}) {alert_type} {threshold}"
        )
        
        self.alerts.append(alert)
        self.save()
        return alert_id
    
    def remove_alert(self, alert_id: str) -> bool:
        """删除预警"""
        for i, alert in enumerate(self.alerts):
            if alert.id == alert_id:
                self.alerts.pop(i)
                self.save()
                return True
        return False
    
    def check_alerts(self, code: str, current_price: float, change_pct: float = 0, volume: float = 0) -> List[PriceAlert]:
        """检查是否触发预警"""
        triggered = []
        
        for alert in self.alerts:
            if alert.code != code or alert.triggered:
                continue
            
            is_triggered = False
            
            if alert.alert_type == AlertType.PRICE_ABOVE.value and current_price >= alert.threshold:
                is_triggered = True
            elif alert.alert_type == AlertType.PRICE_BELOW.value and current_price <= alert.threshold:
                is_triggered = True
            elif alert.alert_type == AlertType.CHANGE_PCT_ABOVE.value and change_pct >= alert.threshold:
                is_triggered = True
            elif alert.alert_type == AlertType.CHANGE_PCT_BELOW.value and change_pct <= alert.threshold:
                is_triggered = True
            
            if is_triggered:
                alert.triggered = True
                alert.triggered_at = datetime.now().isoformat()
                triggered.append(alert)
        
        if triggered:
            self.save()
        
        return triggered
    
    def get_active_alerts(self, code: str = None) -> List[PriceAlert]:
        """获取未触发的预警"""
        alerts = [a for a in self.alerts if not a.triggered]
        if code:
            alerts = [a for a in alerts if a.code == code]
        return alerts
    
    def get_triggered_alerts(self) -> List[PriceAlert]:
        """获取已触发的预警"""
        return [a for a in self.alerts if a.triggered]
    
    def clear_triggered(self):
        """清空已触发的预警"""
        self.alerts = [a for a in self.alerts if not a.triggered]
        self.save()
    
    def list_alerts(self) -> str:
        """列出所有预警"""
        if not self.alerts:
            return "📋 暂无预警设置"
        
        lines = ["📋 价格预警列表：", ""]
        
        active = self.get_active_alerts()
        triggered = self.get_triggered_alerts()
        
        if active:
            lines.append(f"🟢 监控中 ({len(active)}个)：")
            for alert in active:
                lines.append(f"  [{alert.id}] {alert.name}({alert.code}) - {alert.alert_type} {alert.threshold}")
        
        if triggered:
            lines.append("")
            lines.append(f"🔴 已触发 ({len(triggered)}个)：")
            for alert in triggered:
                lines.append(f"  [{alert.id}] {alert.name} - {alert.triggered_at}")
        
        return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    am = AlertManager()
    print("价格预警系统已加载")
    print(am.list_alerts())
