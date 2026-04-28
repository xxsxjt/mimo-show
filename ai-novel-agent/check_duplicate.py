"""检测章节标题是否重复。用法：python check_duplicate.py "新标题" """

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

ch_dir = r"path/to/novel/workspace/chapters"  # 替换为实际路径
if len(sys.argv) < 2:
    print('用法: python check_duplicate.py "新标题"')
    sys.exit(1)

new_title = sys.argv[1].strip()
# 提取冒号后面的短标题
if '：' in new_title:
    short = new_title.split('：')[-1]
elif ':' in new_title:
    short = new_title.split(':')[-1]
else:
    short = new_title

existing = {}
for f in os.listdir(ch_dir):
    if not f.endswith('.md'):
        continue
    num = f.split('-')[0]
    with open(os.path.join(ch_dir, f), 'r', encoding='utf-8') as fh:
        first = fh.readline().strip()
    title = first.lstrip('#').strip()
    s = title.split('：')[-1] if '：' in title else title.split(':')[-1] if ':' in title else title
    existing[num] = (f, s, title)

dupes = []
for num, (f, s, full) in existing.items():
    if s == short:
        dupes.append((num, full))

if dupes:
    print(f'冲突! "{short}" 与以下章节重复:')
    for num, full in dupes:
        print(f'   第{num}章: {full}')
else:
    print(f'"{short}" 无冲突，可以使用')
