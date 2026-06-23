#!/usr/bin/env python3
"""
数据重置工具 - 清空日记和上传文件，保留指定账户
用法:
    python reset_data.py                      # 保留 admin 账户，清空其他
    python reset_data.py admin 周晓轩          # 保留 admin 和 周晓轩
    python reset_data.py admin 周晓轩 --dry-run # 预览模式，不实际删除
"""

import sqlite3
import sys
from pathlib import Path
from config import DATABASE, UPLOAD_DIR

KEEP_USERS = []


def parse_args():
    global KEEP_USERS
    dry_run = False
    args = sys.argv[1:]
    
    if '--dry-run' in args:
        dry_run = True
        args.remove('--dry-run')
    
    if len(args) == 0:
        KEEP_USERS = ['admin']
    else:
        KEEP_USERS = args
    
    return dry_run


def main():
    dry_run = parse_args()
    
    print("\n" + "=" * 60)
    print("🧹 家庭日记数据重置工具")``
    print("=" * 60)
    print(f"保留账户: {', '.join(KEEP_USERS)}")
    print(f"模式: {'🔍 预览（不实际删除）' if dry_run else '⚠️ 执行删除'}")
    print("=" * 60)
    
    if not dry_run:
        confirm = input("\n确认要删除所有日记和上传文件吗？(输入 YES 确认): ")
        if confirm != 'YES':
            print("❌ 已取消")
            return
    
    # 1. 获取要保留的用户ID
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    keep_ids = []
    for username in KEEP_USERS:
        cursor.execute('SELECT id, username FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            keep_ids.append(user['id'])
            print(f"✓ 找到保留用户: {user['username']} (ID: {user['id']})")
        else:
            print(f"⚠ 用户不存在: {username}")
    
    if not keep_ids:
        print("❌ 没有找到任何保留用户，取消操作")
        conn.close()
        return
    
    # 2. 统计和删除日记
    cursor.execute('SELECT COUNT(*) as cnt FROM diaries')
    diary_count = cursor.fetchone()['cnt']
    print(f"\n📚 日记总数: {diary_count}")
    
    # 获取所有日记（删除全部日记和全部文件，只保留账户）
    cursor.execute('SELECT id, images, videos, files FROM diaries')
    to_delete = cursor.fetchall()
    print(f"📚 要删除的日记: {len(to_delete)} 篇")
    
    # 收集要删除的文件
    import json
    files_to_delete = []
    for diary in to_delete:
        for key in ['images', 'videos', 'files']:
            val = diary[key]
            if val:
                try:
                    file_list = json.loads(val) if isinstance(val, str) else val
                    if isinstance(file_list, list):
                        for f in file_list:
                            files_to_delete.append(f)
                except (json.JSONDecodeError, TypeError):
                    pass
    
    print(f"📁 关联文件数: {len(files_to_delete)}")
    
    if dry_run:
        print("\n🔍 [预览] 将删除以下内容:")
        for d in to_delete:
            print(f"  - 日记 ID:{d['id']}")
        for f in files_to_delete[:10]:
            print(f"  - 文件: {f}")
        if len(files_to_delete) > 10:
            print(f"  ... 还有 {len(files_to_delete) - 10} 个文件")
        conn.close()
        return
    
    # 3. 执行删除
    print("\n🗑️ 开始删除...")
    
    # 删除日记记录（全部删除）
    cursor.execute('DELETE FROM diaries')
    deleted_diary_count = cursor.rowcount
    conn.commit()
    print(f"✓ 已删除日记: {deleted_diary_count} 篇")
    
    # 删除上传文件
    upload_dir = Path(UPLOAD_DIR)
    deleted_file_count = 0
    
    for file_path in files_to_delete:
        full_path = upload_dir / file_path.replace('uploads/', '')
        if full_path.exists():
            try:
                full_path.unlink()
                deleted_file_count += 1
            except Exception as e:
                print(f"  ✗ 删除文件失败: {full_path}, {e}")
    
    print(f"✓ 已删除文件: {deleted_file_count} 个")
    
    # 4. 删除所有上传文件（全部日记已删除，所有文件都是孤立文件）
    orphan_count = 0
    for subfolder in ['images', 'videos', 'documents']:
        folder = upload_dir / subfolder
        if folder.exists():
            for f in folder.rglob('*'):
                if f.is_file():
                    try:
                        f.unlink()
                        orphan_count += 1
                    except Exception:
                        pass
    
    print(f"✓ 已清理所有上传文件: {orphan_count} 个")
    
    # 5. 删除空目录
    for subfolder in ['images', 'videos', 'documents']:
        folder = upload_dir / subfolder
        if folder.exists():
            try:
                # 删除空子目录
                for d in sorted(folder.rglob('*'), reverse=True):
                    if d.is_dir() and not any(d.iterdir()):
                        d.rmdir()
            except Exception:
                pass
    
    # 统计剩余
    cursor.execute('SELECT COUNT(*) as cnt FROM diaries')
    remaining_diaries = cursor.fetchone()['cnt']
    cursor.execute('SELECT COUNT(*) as cnt FROM users')
    remaining_users = cursor.fetchone()['cnt']
    
    remaining_files = 0
    for subfolder in ['images', 'videos', 'documents']:
        folder = upload_dir / subfolder
        if folder.exists():
            remaining_files += len(list(folder.rglob('*')))
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 重置完成！")
    print("=" * 60)
    print(f"保留用户: {remaining_users} 个")
    print(f"保留日记: {remaining_diaries} 篇")
    print(f"保留文件: {remaining_files} 个")
    print(f"保留账户: {', '.join(KEEP_USERS)}")
    print("=" * 60)


if __name__ == '__main__':
    main()