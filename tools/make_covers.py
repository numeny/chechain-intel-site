from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 900
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msyh.ttc"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / (H - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def text(draw, xy, value, f, fill, anchor="la"):
    draw.text(xy, value, font=f, fill=fill, anchor=anchor)


def stat_card(draw, x, y, w, h, number, label, accent):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=24, fill=(255, 255, 255, 18), outline=(255, 255, 255, 40), width=2)
    text(draw, (x + 32, y + 26), number, font(FONT_BOLD, 54), accent, "la")
    text(draw, (x + 32, y + 100), label, font(FONT_REG, 24), (220, 230, 240), "la")


def cover(path, kicker, title, subtitle, stats, footer, accent, top, bottom, note="公开信息整理 · 来源链接可核验 · 标准包不含联系方式"):
    img = gradient(top, bottom).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rectangle((0, 0, W, 12), fill=accent)
    draw.rounded_rectangle((48, 56, 330, 108), radius=26, fill=(255, 255, 255, 22))
    text(draw, (70, 70), kicker, font(FONT_REG, 24), (220, 235, 245), "la")

    text(draw, (48, 150), title, font(FONT_BOLD, 64), (255, 255, 255), "la")
    text(draw, (48, 240), subtitle, font(FONT_REG, 28), (190, 210, 225), "la")

    card_w = (W - 96 - 48) // 3
    for i, (number, label) in enumerate(stats):
        stat_card(draw, 48 + i * (card_w + 24), 350, card_w, 160, number, label, accent)

    draw.line((48, 590, W - 48, 590), fill=(255, 255, 255, 45), width=2)
    text(draw, (48, 630), "覆盖范围", font(FONT_BOLD, 30), (255, 255, 255), "la")
    text(draw, (48, 680), footer, font(FONT_REG, 26), (200, 215, 230), "la")

    text(draw, (48, 806), note, font(FONT_REG, 22), (160, 180, 200), "la")
    text(draw, (W - 48, 806), "2026-10", font(FONT_REG, 22), (160, 180, 200), "ra")

    out = Image.alpha_composite(img, overlay).convert("RGB")
    out.save(path, quality=95)
    print(path)


def main():
    out = Path("sales/covers")
    out.mkdir(parents=True, exist_ok=True)
    cover(
        out / "australia.png",
        "汽车出海情报 · 澳洲",
        "澳洲汽车经销商渠道地图",
        "353 家企业 · 254 条品牌代理 · 按州筛选",
        [("353", "经销商企业"), ("132", "比亚迪门店"), ("122", "名爵门店")],
        "NSW 115 · VIC 97 · QLD 72 · SA 34 · WA 21\nACT 6 · TAS 5 · NT 2 · 98 条集团/门店关系",
        (242, 193, 78),
        (10, 31, 51),
        (18, 59, 92),
    )
    cover(
        out / "brazil.png",
        "汽车出海情报 · 巴西",
        "巴西汽车经销商渠道地图",
        "378 家企业 · 335 条品牌代理 · 27 个州",
        [("378", "经销商企业"), ("235", "比亚迪门店"), ("100", "奇瑞门店")],
        "SP 83 · MG 30 · SC 24 · RS 22 · RJ 22 · PR 22\nGO 14 · BA 14 · PE 13 · DF 12 · 94 条集团关系",
        (53, 196, 138),
        (8, 35, 28),
        (12, 66, 52),
    )
    cover(
        out / "custom.png",
        "汽车出海情报 · 定制",
        "海外汽车渠道定制调研",
        "澳洲 · 巴西 · 日本 · 7 个工作日交付",
        [("3,000", "元起 / 单"), ("3", "国家可选"), ("7", "个工作日")],
        "按国家、品牌、州/城市筛选\n核验代理关系 · 可选公开企业联系方式",
        (255, 138, 76),
        (44, 23, 18),
        (92, 42, 24),
        note="公开信息 · 可核验 · 不碰个人隐私",
    )


if __name__ == "__main__":
    main()
