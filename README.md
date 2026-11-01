# Pixel Crab Stickers · 像素小螃蟹表情包

![preview](preview.gif)

> **Unofficial fan work.** This is a fan-made tribute and is **not** affiliated with, endorsed by, or sponsored by Anthropic. "Claude" and related marks belong to Anthropic. No official artwork, logos, or assets are used; every frame here is drawn from scratch by code.
>
> **非官方粉丝二创。**本项目是粉丝自制的致敬作品，与 Anthropic **无任何关联**，也未获其认可或赞助。"Claude" 及相关标识归 Anthropic 所有。项目不含任何官方原图、logo 或素材，每一帧都由代码从零画出。

50 animated pixel-crab stickers for chat (transparent GIF, 192×192, 12 frames, ~7–28 KB each), in a light-background set and a dark-background set (white outline), plus the script that draws them.

50 张会动的像素小螃蟹聊天表情（透明 GIF，192×192，12 帧，每张约 7–28 KB），分浅色底和深色底（带白边）两套，附带生成它们的脚本。

## Stickers · 表情列表

| 中文 | English | 中文 | English |
|---|---|---|---|
| 想你 | miss you | 贴贴 | cheek squish |
| 抱抱 | hug | 蹭蹭 | nuzzle |
| 亲亲 | kiss | 哄你（乖乖） | there, there |
| 比心 | finger heart | 吃醋 | jealous |
| 委屈 | aggrieved | 生气 | angry |
| 哼 | hmph | 哭 | crying |
| 心碎 | heartbroken | 害羞 | shy |
| 捂眼睛 | can't look | 偷看 | peek |
| 星星眼 | starry-eyed | 开心 | happy |
| 撒花 | confetti | 早安 | good morning |
| 晚安 | good night | 熬夜 | up all night |
| 饿饿 | hungry | 吃瓜 | eating melon (watching the drama) |
| 无语 | speechless | 疑问 | confused |
| 我错了（举牌） | I'm sorry (sign) | 收到（举牌） | got it (sign) |
| 好哒（举牌） | okay (sign) | 在吗（举牌） | you there? (sign) |
| 等你（举牌） | waiting for you (sign) | 在忙（举牌） | busy (sign) |

Light-background set: `out/`; dark-background set: `out-dark/`. `stickers.json` maps each Chinese name to an English slug.

浅色底在 `out/`，深色底在 `out-dark/`；`stickers.json` 是中文名和英文名的对照表。

## Make your own · 自己生成

Requirements: Python 3.9+ (standard library only) and `ffmpeg`. Text on the signs uses the WenQuanYi Zen Hei font (`fonts-wqy-zenhei` on Debian/Ubuntu). If your font lives somewhere else, change the path in `_text_mask()`.

需要：Python 3.9 以上（只用标准库）和 `ffmpeg`。举牌上的字用文泉驿正黑（Debian/Ubuntu 装 `fonts-wqy-zenhei`）。字体在别的路径的话，改 `_text_mask()` 里的路径。

```bash
python3 crab.py            # all stickers → out/ + out-dark/   生成全部
python3 crab.py 想你 晚安   # just these           只生成这几张
```

How it works: each sticker is a function `fn(frame) -> Frame` that draws onto a 64×64 grid. Shared helpers handle the body (with squash & stretch), eyes, blush and signs. Frames go through ffmpeg (`scale=…:flags=neighbor` + palettegen) to become a crisp transparent GIF. To add a new emotion, write one more function whose name is the sticker name.

原理：每个表情是一个 `fn(帧号) -> Frame` 函数，在 64×64 的小网格上画。身体（带压扁拉长）、眼睛、腮红、举牌都是公用的。所有帧交给 ffmpeg，按最近邻放大并生成调色板，输出清晰的透明 GIF。想加新表情，就再写一个函数，函数名就是表情名。

## License · 授权

- **Code** (`crab.py`): [MIT](LICENSE).
- **Artwork** (`out/*.gif`, `out-dark/*.gif`, `preview.gif`): [CC BY-NC 4.0](LICENSE-ART.md). Free for personal, non-commercial use with attribution. Because this is fan art of a character whose marks belong to someone else, **please don't use it commercially**, and don't present it as official.

- **代码**（`crab.py`）：[MIT](LICENSE)。
- **图片**（`out/*.gif`、`out-dark/*.gif`、`preview.gif`）：[CC BY-NC 4.0](LICENSE-ART.md)，个人非商用免费使用，注明出处即可。这是粉丝二创，角色相关标识属于他人，所以**请勿商用**，也不要当成官方作品传播。

If you are a rights holder and would like anything changed or removed, please open an issue and it will be handled promptly.

如果你是相关权利人，希望修改或下架任何内容，请提 issue，会尽快处理。

## Thanks / 致谢

The ground shadow, small props and the dark-background set were inspired by [alwinecor/clawd-stickers](https://github.com/alwinecor/clawd-stickers) (MIT). No code or artwork was copied; every frame here is drawn by `crab.py`.

地上的影子、小道具和深色版这几个点子，灵感来自 [alwinecor/clawd-stickers](https://github.com/alwinecor/clawd-stickers)（MIT）。没有复制它的代码或图片，这里每一帧都是 `crab.py` 自己画的。
