# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=11"]
# ///
"""生成 web/public 下实际使用的图片：WebP（按尺寸多版本）+ PNG 兜底 + 站点图标。

运行：uv run scripts/optimize_images.py
原图只保存在 images/src，web/public 下的图片全部是生成物；换图后替换原图重跑即可。
矢量图标源文件是 web/public/favicon.svg（手写，不由本脚本生成）。
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'images' / 'src'
PUBLIC = ROOT / 'web' / 'public'

# (原图, 输出路径(无扩展名), 最大边长, 格式列表)
JOBS = [
    ('topik-home-logo.png', PUBLIC / 'img' / 'home-hero', 1080, ['webp', 'png']),
    ('topik-home-logo.png', PUBLIC / 'img' / 'home-hero-540', 540, ['webp']),
    *[
        (f'course-mindmap-{m}.png', PUBLIC / 'mindmaps' / f'{m}{suffix}', size, fmts)
        for m in ('cs', 'math', 'english')
        for suffix, size, fmts in (('', 1448, ['webp', 'png']), ('-720', 720, ['webp']))
    ],
]


def save(img: Image.Image, out: Path, fmt: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    path = out.with_suffix(f'.{fmt}')
    if fmt == 'webp':
        img.save(path, 'WEBP', quality=82, method=6)
    else:
        # PNG 兜底：调色板量化，体积约为原图的 1/4
        q = img.convert('RGBA').quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        q.save(path, 'PNG', optimize=True)
    print(f'{path.relative_to(ROOT)}  {img.width}x{img.height}  {path.stat().st_size / 1024:.0f} KB')


def brand_icon(size: int) -> Image.Image:
    """与 favicon.svg 一致的位图图标：青绿→靛蓝渐变圆角方块 + 白色书本。"""
    s = size * 4  # 超采样后缩小，边缘更平滑
    grad = Image.new('RGBA', (s, s))
    a, b = (0x14, 0xB8, 0xA6), (0x63, 0x66, 0xF1)
    px = grad.load()
    for y in range(s):
        for x in range(s):
            t = (x + y) / (2 * s - 2)
            px[x, y] = tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)
    mask = Image.new('L', (s, s))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, s - 1, s - 1), radius=s // 4, fill=255)
    icon = Image.new('RGBA', (s, s))
    icon.paste(grad, mask=mask)

    d = ImageDraw.Draw(icon)
    u = s / 24 * 0.6          # 24px 图标网格 → 画布，占 60%
    o = s * 0.2               # 居中偏移
    w = round(u * 2.2)
    P = lambda x, y: (o + x * u, o + y * u)  # noqa: E731
    d.line([P(4, 19.5), P(4, 5)], fill='white', width=w)
    d.arc([*P(4, 3), *P(8, 7)], 180, 270, fill='white', width=w)
    d.line([P(6, 3), P(19, 3), P(19, 18), P(6.5, 18)], fill='white', width=w, joint='curve')
    d.arc([*P(4, 18), *P(9, 23)], 90, 270, fill='white', width=w)
    d.line([P(6.5, 23), P(19, 23), P(19, 21)], fill='white', width=w, joint='curve')
    d.line([P(9, 7), P(15, 7)], fill='white', width=w)
    return icon.resize((size, size), Image.Resampling.LANCZOS)


for src, out, max_side, fmts in JOBS:
    img = Image.open(SRC / src)
    img = img.convert('RGBA') if img.mode in ('P', 'LA') else img
    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    for fmt in fmts:
        save(img, out, fmt)

for name, size in (('favicon-192', 192), ('apple-touch-icon', 180), ('favicon-32', 32)):
    path = PUBLIC / f'{name}.png'
    brand_icon(size).save(path, 'PNG', optimize=True)
    print(f'{path.relative_to(ROOT)}  {size}x{size}  {path.stat().st_size / 1024:.0f} KB')
