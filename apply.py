# VSети: переносит название, значок и цвета в исходники Telegram Desktop.
# Запуск: python apply.py <папка tdesktop>
import os, re, shutil, sys

here = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1]
T = os.path.join(root, 'Telegram')


def edit(path, fn):
    p = os.path.join(T, path)
    with open(p, encoding='utf-8', newline='') as f:
        s = f.read()
    n = fn(s)
    if n == s:
        raise SystemExit('Не изменилось: ' + path)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(n)
    print('OK', path)


# 1. Значки: все размеры делаются из двух исходных картинок
from PIL import Image
import io, struct
full = Image.open(os.path.join(here, 'icon_full.png')).convert('RGBA')
small = Image.open(os.path.join(here, 'icon_notext.png')).convert('RGBA')
A = os.path.join(T, 'Resources', 'art')
def ic(n):
    return (small if n <= 64 else full).resize((n, n), Image.LANCZOS)
for n in (16, 32, 48, 64, 128, 256, 512):
    ic(n).save(os.path.join(A, 'icon%d.png' % n))
    ic(n * 2).save(os.path.join(A, 'icon%d@2x.png' % n))
ic(1024).save(os.path.join(A, 'icon_green.png'))
ic(256).save(os.path.join(A, 'iconbig_green.png'))
full.resize((1024, 1024), Image.LANCZOS).save(os.path.join(A, 'icon_round512@2x.png'))
logo = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
logo.alpha_composite(full.resize((200, 200), Image.LANCZOS), (28, 28))
logo.save(os.path.join(A, 'logo_256.png'))
full.resize((256, 256), Image.LANCZOS).save(os.path.join(A, 'logo_256_no_margin.png'))
sizes = (16, 24, 32, 48, 64, 128, 256)
blobs = []
for n in sizes:
    b = io.BytesIO()
    (small if n <= 48 else full).resize((n, n), Image.LANCZOS).save(b, 'PNG')
    blobs.append(b.getvalue())
ico = struct.pack('<HHH', 0, 1, len(sizes)); off = 6 + 16 * len(sizes); ent = b''
for n, d in zip(sizes, blobs):
    ent += struct.pack('<BBBBHHII', n % 256, n % 256, 0, 0, 1, 32, len(d), off); off += len(d)
with open(os.path.join(A, 'icon256.ico'), 'wb') as f:
    f.write(ico + ent + b''.join(blobs))
print('OK значки')

# 2. Цвета: тёмно-зелёная тема по умолчанию (из темы Night Green, перекрашенной под VSети)
import zipfile, colorsys
t = zipfile.ZipFile(os.path.join(T, 'Resources', 'night-green.tdesktop-theme')).read('colors.tdesktop-theme').decode()
vals = {m.group(1): m.group(2) for m in re.finditer(
    r'^\s*([A-Za-z0-9_]+)\s*:\s*(#[0-9a-fA-F]{6,8}|[A-Za-z0-9_]+)\s*;', t, re.M)}
def rec(h):
    hx = h[1:]; a = hx[6:8] if len(hx) == 8 else ''
    r, g, b = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    H, S_, V = colorsys.rgb_to_hsv(r, g, b)
    if S_ > 0.22 and 70 <= H * 360 <= 265: H = 148 / 360
    elif V < 0.42: H = 150 / 360; S_ = min(0.85, 0.6 + S_); V = V * 0.6
    R, G, B = [round(x * 255) for x in colorsys.hsv_to_rgb(H, S_, V)]
    return '#%02x%02x%02x%s' % (R, G, B, a)
fix = {'msgOutBg': '#0d4a2c', 'msgOutBgSelected': '#11603a'}
pp = os.path.join(T, 'lib_ui', 'ui', 'colors.palette')
out = []
for ln in open(pp, encoding='utf-8', newline='').read().split('\n'):
    m = re.match(r'^(\s*)([A-Za-z0-9_]+)(\s*:\s*)([^;]+)(;.*)$', ln)
    if m and (m.group(2) in vals or m.group(2) in fix):
        v = fix.get(m.group(2)) or vals[m.group(2)]
        if v.startswith('#') and m.group(2) not in fix: v = rec(v)
        ln = m.group(1) + m.group(2) + m.group(3) + v + m.group(5)
    out.append(ln)
open(pp, 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('OK цвета')

# 3. Название программы и отдельная папка данных (не мешает Telegram на этом же ПК)
edit('SourceFiles/core/version.h', lambda s: s
     .replace('AppName = "Telegram Desktop"_cs', 'AppName = "VSeti Desktop"_cs')
     .replace('AppId = "{53F49750-6209-4FBF-9CA8-7A333C87D1ED}"_cs',
              'AppId = "{7B1D5E2A-4C3F-4E8B-9A61-5D2C0F3B8E47}"_cs'))
edit('SourceFiles/platform/win/windows_app_user_model_id.cpp', lambda s: s
     .replace('L"Telegram.TelegramDesktop.Store"', 'L"VSeti.VSetiDesktop.Store"')
     .replace('L"Telegram.TelegramDesktop"', 'L"VSeti.VSetiDesktop"'))

# 4. Не перехватывать ссылки tg:// у настоящего Telegram
edit('SourceFiles/core/application.cpp', lambda s: s.replace(
    'if (!OptionSkipUrlSchemeRegister.value()) {', 'if (false && !OptionSkipUrlSchemeRegister.value()) {', 1))

# 5. Подписи exe-файлов
for rc in ('Resources/winrc/Telegram.rc', 'Resources/winrc/Updater.rc'):
    edit(rc, lambda s: s.replace('Telegram Desktop', 'VSeti').replace('"Telegram FZ-LLC"', '"VSeti"'))

# 6. Тексты интерфейса: Telegram -> VSети (только значения, не ключи)
def strings(s):
    return re.sub(r'^("[^"]+"\s*=\s*")(.*)(";)([ \t\r]*)$',
                  lambda m: m.group(1) + m.group(2).replace('Telegram', 'VSети') + m.group(3) + m.group(4),
                  s, flags=re.M)
edit('Resources/langs/lang.strings', strings)
print('Готово')

# 7. Свой сервер VSети вместо серверов Telegram (как в Android: 51.250.73.233:10443) и его ключ
VS_KEY = r"""-----BEGIN RSA PUBLIC KEY-----\n\
MIIBCgKCAQEAqabVavdmO84huetgow/UJPGp+WUAVyEZdWTqEOflNKmL2FcrrJZe\n\
NwMFFgMo3IVHTE5A51aR5xu9A8XMwGvuwrmj13WYGEvx2OmMsG3ZPdREcfxaI6Ij\n\
Sc8IrvP3e5BRs1zx7usEsdeHaFB0uqzgoQUXz6IBBksqREwChjhEnv8QpFGIDGPj\n\
i1Rvn/6AH9tH7jeU9G5FcGdFOSrikyjF4x6YYKTSHP5txqAyAx8Zr44whb6or7Vf\n\
+PTwhDKFNNHbZ+55BBBgHiD8Lepuya3BC6AKGC4tvr1ViqcZp2wi/vJdE7vkxCoM\n\
uXULvX5wRv65Xvtq5+yQwuOR1y9hiNShUwIDAQAB\n\
-----END RSA PUBLIC KEY-----\n"""
def dcs(s):
    s = re.sub(r'const BuiltInDc kBuiltInDcs\[\] = \{.*?\};',
               'const BuiltInDc kBuiltInDcs[] = {\n\t{ 1, "51.250.73.233", 10443 },\n};', s, count=1, flags=re.S)
    s = re.sub(r'const BuiltInDc kBuiltInDcsIPv6\[\] = \{.*?\};',
               'const BuiltInDc kBuiltInDcsIPv6[] = {\n\t{ 1, "51.250.73.233", 10443 },\n};', s, count=1, flags=re.S)
    s = re.sub(r'const char \*kPublicRSAKeys\[\] = \{ ".*?" \};',
               lambda m: 'const char *kPublicRSAKeys[] = { "\\\n' + VS_KEY + '" };', s, count=1, flags=re.S)
    return s
edit('SourceFiles/mtproto/mtproto_dc_options.cpp', dcs)

# 8. Сервер Teamgram понимает схему до слоя 230 (как в Android)
edit('SourceFiles/mtproto/session_private.cpp', lambda s: s.replace('push_back(kCurrentLayer)', 'push_back(230 /* VSети */)'))
print('Готово: сервер')

# 9. Главный сервер — №1 (у Telegram по умолчанию №2, у нас он один)
edit('SourceFiles/mtproto/mtp_instance.h', lambda s: s.replace('static constexpr auto kDefaultMainDc = 2;', 'static constexpr auto kDefaultMainDc = 1; // VSети'))

# 10. Не искать «запасные» адреса серверов Telegram через Google/Firebase
edit('SourceFiles/mtproto/config_loader.cpp', lambda s: re.sub(
    r'(void ConfigLoader::refreshSpecialLoader\(\) \{(\r?\n))', lambda m: m.group(1) + '\tif (true) { _specialLoader.reset(); return; } // VSети: только свой сервер' + m.group(2), s, count=1))

# 11. Заголовок окна: VSети вместо Telegram
edit('SourceFiles/window/main_window.cpp', lambda s: s.replace('u"Telegram"_q', 'u"VSети"_q'))
edit('SourceFiles/core/crash_report_window.cpp', lambda s: s.replace('u"Telegram"_q', 'u"VSети"_q'))

# 12. Значок в центре QR на экране входа: значок VSети вместо самолётика
QR_OLD = ("\t\tp.setBrush(QrActiveColor());\n\t\tp.setPen(Qt::NoPen);\n"
          "\t\tp.drawEllipse(QRect(QPoint(), size));\n"
          "\t\tst::introQrPlane.paintInCenter(p, QRect(QPoint(), size));")
QR_NEW = ("\t\t// VSети: свой значок\n"
          "\t\tp.drawImage(QRect(QPoint(), size), QImage(u\":/gui/art/logo_256_no_margin.png\"_q));")
edit('SourceFiles/intro/intro_qr.cpp', lambda s: re.sub(
    r'p\.setBrush\(QrActiveColor\(\)\);\s*p\.setPen\(Qt::NoPen\);\s*p\.drawEllipse\(QRect\(QPoint\(\), size\)\);\s*st::introQrPlane\.paintInCenter\(p, QRect\(QPoint\(\), size\)\);',
    lambda m: 'p.drawImage(QRect(QPoint(), size), QImage(u":/gui/art/logo_256_no_margin.png"_q)); // VSети: свой значок', s, count=1))
print('Готово: сервер №1, заголовок, QR')

# 13. Русский язык с первого запуска: встроенный перевод (файл vseti_ru_RU.strings рядом с VSeti.exe).
# Включается сразу после запуска хранилища, если выбран не наш файл (в т.ч. при первом запуске).
edit('SourceFiles/core/application.cpp', lambda s: re.sub(
    r'(void Application::startLocalStorage\(\) \{\s*Ui::GL::DetectLastCheckCrash\(\);\s*Local::start\(\);)',
    lambda m: m.group(1) + '\n\t{ // VSети: русский по умолчанию\n\t\tconst auto vsRu = cExeDir() + u"vseti_ru_RU.strings"_q;\n\t\tif (Lang::GetInstance().id() != Lang::CustomLanguageId() && QFileInfo::exists(vsRu)) {\n\t\t\tLang::GetInstance().switchToCustomFile(vsRu);\n\t\t}\n\t}',
    s, count=1))
print('Готово: русский язык')

# 14. Стартовый экран: название VSети вместо «Telegram Desktop» и значок VSети вместо самолётика
edit('SourceFiles/intro/intro_start.cpp', lambda s: s.replace('setTitleText(rpl::single(u"Telegram Desktop"_q));', 'setTitleText(rpl::single(u"VSети"_q));'))
edit('SourceFiles/intro/intro_step.cpp', lambda s: s.replace(
    '\tst::introCoverIcon.paint(p, planeLeft, planeTop, width());',
    '\t{ // VSети: свой значок вместо самолётика\n'
    '\t\tstatic const auto vsLogo = QImage(u":/gui/art/logo_256_no_margin.png"_q);\n'
    '\t\tconst auto sz = st::introCoverIcon.height();\n'
    '\t\tconst auto cx = planeLeft + st::introCoverIcon.width() / 2;\n'
    '\t\tp.setRenderHint(QPainter::SmoothPixmapTransform);\n'
    '\t\tp.drawImage(QRect(cx - sz / 2, planeTop, sz, sz), vsLogo);\n'
    '\t}'))
print('Готово: стартовый экран')
