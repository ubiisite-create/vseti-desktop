# VSети: готовит русский перевод Telegram Desktop для VSети (Telegram -> VSети в текстах).
import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
if '"lng_' not in s:
    raise SystemExit('Русский перевод не скачался')
def fix(m):
    v = m.group(2)
    v = v.replace('Telegram Premium', 'VSети Premium').replace('Telegram', 'VSети').replace('Телеграм', 'VSети')
    return m.group(1) + v + m.group(3)
s = re.sub(r'^("[^"]+"\s*=\s*")(.*)(";\s*)$', fix, s, flags=re.M)
open(dst, 'w', encoding='utf-8', newline='\n').write(s)
print('ru strings:', s.count('"lng_'))
