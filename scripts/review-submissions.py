#!/usr/bin/env python3
"""Owner-only submission review and gallery release. No public approval endpoint."""
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get('BUBBLE_STUDIO_DATA', str(ROOT / '.local')))
REVIEW_CONFIG = DATA / 'review.json'
if REVIEW_CONFIG.exists():
    settings = json.loads(REVIEW_CONFIG.read_text())
    if settings.get('repository'):
        ROOT = Path(settings['repository']).expanduser().resolve()
if os.environ.get('BUBBLE_STUDIO_REVIEW_ROOT'):
    ROOT = Path(os.environ['BUBBLE_STUDIO_REVIEW_ROOT']).expanduser().resolve()
QUEUE = 'kaitongg-bit/DIYcodex-bubble-submissions'
APPROVED = ROOT / 'community' / 'approved'
MANIFEST = APPROVED / 'manifest.json'
REMOVED = ROOT / 'community' / 'removed.json'
ID = re.compile(r'[a-f0-9-]{36}\Z')


def gh(*args, body=None):
    command = ['gh', *args]
    if body is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def content(path):
    return gh('api', f'repos/{QUEUE}/contents/{path}')


def read(path):
    return base64.b64decode(content(path)['content'])


def record(sid):
    if not isinstance(sid, str) or not ID.fullmatch(sid):
        raise ValueError('Invalid submission ID')
    return json.loads(read(f'pending/{sid}/submission.json'))


def removed_ids():
    return set(json.loads(REMOVED.read_text())['ids']) if REMOVED.exists() else set()


def published_ids():
    response = gh('api', 'repos/kaitongg-bit/DIYcodex-bubble/contents/community-gallery/manifest.json?ref=gh-pages')
    manifest = json.loads(base64.b64decode(response['content']))
    return {item['id'] for item in manifest['items']}


def queue_items():
    try:
        entries = content('pending')
    except subprocess.CalledProcessError as error:
        if '404' not in (error.stderr or ''):
            raise
        entries = []
    return [record(entry['name']) for entry in entries if entry['type'] == 'dir']


def mark(row, status, reason):
    row = {**row, 'status': status, 'reviewReason': reason}
    path = f'pending/{row["id"]}/submission.json'
    old = content(path)
    gh('api', '--method', 'PUT', f'repos/{QUEUE}/contents/{path}', body={
        'message': f'Review submission {row["id"]}: {status}',
        'sha': old['sha'],
        'content': base64.b64encode(json.dumps(row, ensure_ascii=False, indent=2).encode()).decode(),
    })
    return row


def pages_worktree():
    if not (ROOT / '.git').exists():
        raise RuntimeError('审核发布需要连接作者的源码仓库；请在本机数据目录 review.json 中配置 repository。DMG 应用不包含 Git 仓库。')
    if os.environ.get('PAGES_WORKTREE'):
        path = Path(os.environ['PAGES_WORKTREE'])
    else:
        path = None
        blocks = subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], cwd=ROOT, text=True)
        for block in blocks.split('\n\n'):
            if '\nbranch refs/heads/gh-pages' in block:
                path = Path(block.splitlines()[0].removeprefix('worktree '))
                break
        if path is None:
            candidate = ROOT.parent.parent / 'work' / 'community-site'
            if candidate.is_dir() and (candidate / '.git').exists():
                path = candidate
    if path is None or not path.is_dir():
        raise RuntimeError('找不到 gh-pages 工作树，请设置 PAGES_WORKTREE')
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=path, text=True).strip()
    if branch != 'gh-pages':
        raise RuntimeError('Pages 工作树当前不在 gh-pages 分支')
    return path


def publish_many(rows):
    """Stage all selected images, then push main and Pages once each."""
    if not rows:
        return {'status': 'unchanged', 'count': 0}
    forbidden = removed_ids()
    for row in rows:
        if row['status'] != 'approved' or row['id'] in forbidden:
            raise ValueError(f'{row["id"]} 不可发布')
    pages = pages_worktree()
    APPROVED.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'version': 1, 'items': []}
    existing = {item['id']: item for item in manifest['items']}
    count = 0
    for row in rows:
        sid = row['id']
        if sid in existing:
            continue
        png = read(f'pending/{sid}/bubble.png')
        if hashlib.sha256(png).hexdigest() != row['sha256']:
            raise ValueError(f'{sid} 图片校验失败')
        config = row.get('config') or {
            'width': row['width'], 'height': row['height'],
            'left': round(row['width'] * .35), 'right': round(row['width'] * .73),
            'top': round(row['height'] * .45), 'bottom': round(row['height'] * .55),
            'scale': .6, 'padding': [29, 37, 36, 48], 'color': '#44362f',
            'radius': 0, 'borderWidth': 0, 'borderColor': '#d0d0d0',
        }
        filename = f'{sid}.png'
        (APPROVED / filename).write_bytes(png)
        (APPROVED / f'{sid}.bubble.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
        manifest['items'].append({
            'id': sid, 'community': True, 'name': row.get('name') or 'Untitled bubble',
            'nameEn': row.get('name') or 'Untitled bubble', 'filename': filename,
            'author': row.get('nickname') or 'Anonymous', 'license': 'Non-commercial only',
            'config': config, 'description': {
                'zh': '经人工审核收录的社区作品。',
                'en': 'A community bubble accepted after manual review.',
            },
        })
        count += 1
    if count:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        subprocess.run(['git', 'add', 'community/approved'], cwd=ROOT, check=True)
        subprocess.run(['git', 'commit', '-m', f'Publish {count} community bubbles'], cwd=ROOT, check=True,
                       capture_output=True, text=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT, check=True, capture_output=True, text=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/export-gallery.py'), str(pages)], cwd=ROOT,
                   check=True, capture_output=True, text=True)
    subprocess.run(['git', 'add', '-A'], cwd=pages, check=True)
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=pages).returncode != 0:
        subprocess.run(['git', 'commit', '-m', f'Publish {count} community bubbles'], cwd=pages,
                       check=True, capture_output=True, text=True)
        subprocess.run(['git', 'push', 'origin', 'gh-pages'], cwd=pages,
                       check=True, capture_output=True, text=True)
    return {'status': 'published', 'count': len(rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['list', 'inspect', 'approve', 'reject', 'batch-approve', 'publish-approved'])
    parser.add_argument('id', nargs='?')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--reason', default='')
    args = parser.parse_args()
    if args.action == 'list':
        published, forbidden = published_ids(), removed_ids()
        rows = [row for row in queue_items() if row['status'] == 'pending' or
                (row['status'] == 'approved' and row['id'] not in published | forbidden)]
        print(json.dumps({'pendingCount': len(rows), 'submissions': rows}, ensure_ascii=False, indent=2))
        return
    if args.action in ('batch-approve', 'publish-approved'):
        ids = json.loads(args.id or '[]')
        if not isinstance(ids, list) or not 1 <= len(ids) <= 50 or len(ids) != len(set(ids)):
            raise ValueError('批量审核数量无效')
        rows = [record(sid) for sid in ids]
        if any(row['status'] not in ('pending', 'approved') for row in rows):
            raise ValueError('选中的作品包含不可发布的审核状态')
        if any(row['id'] in removed_ids() for row in rows):
            raise ValueError('选中的作品包含已撤下的作品')
        pages_worktree()
        approved = [mark(row, 'approved', args.reason) if row['status'] == 'pending' else row for row in rows]
        result = publish_many(approved)
        print(json.dumps({'results': [{'id':row['id'], 'status':'approved'} for row in approved], **result}, ensure_ascii=False))
        return
    row = record(args.id)
    if args.action == 'inspect':
        png = read(f'pending/{args.id}/bubble.png')
        if hashlib.sha256(png).hexdigest() != row['sha256']:
            raise ValueError('Image integrity check failed')
        if args.output:
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / 'bubble.png').write_bytes(png)
            (args.output / 'submission.json').write_text(json.dumps(row, ensure_ascii=False, indent=2))
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return
    if row['status'] != 'pending':
        raise ValueError('Submission already reviewed')
    if args.action == 'approve':
        pages_worktree()
        row = mark(row, 'approved', args.reason)
        result = publish_many([row])
    else:
        row = mark(row, 'rejected', args.reason)
        result = {'status': 'rejected'}
    print(json.dumps({'id': row['id'], **result}, ensure_ascii=False))


if __name__ == '__main__':
    main()
