#!/usr/bin/env python3
"""
电士多日报看板更新脚本
功能：
  1. 从日报产出目录复制 HTML 到看板 reports/ 目录
  2. 重新扫描生成 data.json 索引
  3. 输出更新摘要

用法：
  python update_dashboard.py [--source SOURCE_DIR] [--target DASHBOARD_DIR]
  
  默认：
    source = daily_report_system/outputs/
    target = 当前脚本所在 dashboard 目录
"""

import os
import sys
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

# ===== 配置 =====
SCRIPT_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = SCRIPT_DIR
REPORTS_DIR = DASHBOARD_DIR / "reports"
DATA_JSON = DASHBOARD_DIR / "data.json"

# 日报产出目录（默认）
DEFAULT_SOURCE = Path("C:/Users/TXair/WorkBuddy/2026-06-16-22-56-28/daily_report_system/outputs")

WEEKDAY_MAP = ['一', '二', '三', '四', '五', '六', '日']


def parse_args():
    """解析命令行参数"""
    source = DEFAULT_SOURCE
    target = str(DASHBOARD_DIR)
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--source' and i + 1 < len(args):
            source = Path(args[i + 1])
            i += 2
        elif args[i] == '--target' and i + 1 < len(args):
            target = Path(args[i + 1])
            i += 2
        else:
            i += 1
    
    return source, target


def scan_reports_dir(directory):
    """扫描目录中的运营日报 HTML 文件，返回 {date_str: filename} 字典"""
    reports = {}
    pattern = re.compile(r'运营日报_(\d{4}-\d{2}-\d{2})\.html$')
    
    if not directory.exists():
        print(f"[WARN] 目录不存在: {directory}")
        return reports
    
    for f in directory.iterdir():
        if f.is_file():
            m = pattern.match(f.name)
            if m:
                date_str = m.group(1)
                reports[date_str] = f.name
    
    return reports


def generate_data_json():
    """扫描 reports/ 目录，生成 data.json"""
    if not REPORTS_DIR.exists():
        REPORTS_DIR.mkdir(parents=True)
    
    existing = scan_reports_dir(REPORTS_DIR)
    
    report_list = []
    for date_str, filename in sorted(existing.items(), reverse=True):
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            weekday = WEEKDAY_MAP[dt.weekday()]
            report_list.append({
                'date': date_str,
                'file': filename,
                'weekday': weekday
            })
        except ValueError:
            continue
    
    data = {
        'reports': report_list,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': len(report_list)
    }
    
    with open(DATA_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return len(report_list)


def update_dashboard(source_dir):
    """核心逻辑：从 source 复制新日报到 reports/"""
    
    if not REPORTS_DIR.exists():
        REPORTS_DIR.mkdir(parents=True)
    
    # 扫描来源目录
    source_reports = scan_reports_dir(source_dir)
    if not source_reports:
        print("[ERROR] 来源目录中没有找到日报文件")
        print(f"  来源目录: {source_dir}")
        return 0
    
    # 扫描目标目录（已有）
    existing_reports = scan_reports_dir(REPORTS_DIR)
    
    # 找出需要新增的
    new_count = 0
    new_dates = []
    
    for date_str, filename in sorted(source_reports.items()):
        if date_str not in existing_reports:
            src_path = source_dir / filename
            dst_path = REPORTS_DIR / filename
            
            shutil.copy2(src_path, dst_path)
            new_count += 1
            new_dates.append(date_str)
            print(f"[COPY] {filename}")
    
    # 重新生成索引
    total = generate_data_json()
    
    # 输出摘要
    print(f"\n{'='*50}")
    print(f"看板更新完成")
    print(f"  来源: {source_dir}")
    print(f"  目标: {REPORTS_DIR}")
    print(f"  新增: {new_count} 份")
    print(f"  总计: {total} 份")
    
    if new_dates:
        print(f"  新增日期: {', '.join(new_dates)}")
    
    print(f"  data.json 已更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    return new_count


def main():
    source_dir, target_dir = parse_args()
    
    # 如果指定了 --target，更新路径
    global DASHBOARD_DIR, REPORTS_DIR, DATA_JSON
    if target_dir != str(DASHBOARD_DIR):
        DASHBOARD_DIR = Path(target_dir)
        REPORTS_DIR = DASHBOARD_DIR / "reports"
        DATA_JSON = DASHBOARD_DIR / "data.json"
    
    print(f"电士多日报看板更新")
    print(f"  来源目录: {source_dir}")
    print(f"  看板目录: {DASHBOARD_DIR}")
    print()
    
    new_count = update_dashboard(source_dir)
    
    return 0 if new_count >= 0 else 1


if __name__ == '__main__':
    sys.exit(main())
