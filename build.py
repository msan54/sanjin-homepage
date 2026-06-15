#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建叁斤个人介绍主页。
把 11 篇代表作正文（本地 md + 飞书 PDF）清洗成 HTML，注入 _模板.html，生成 index.html。
以后新增 / 调整文章，改下面 ARTICLES 列表再跑一次：python3 build.py
"""
import re, subprocess, os, html

HOME = "/Users/wenjintao/Documents/叁斤的大脑/07-工具库/网站项目/个人介绍主页"
BASE = "/Users/wenjintao/Documents/叁斤的大脑"
FS = HOME + "/飞书文章备份"
PUB = BASE + "/01-内容生产/已发布"
BK = BASE + "/03-知识资产/案例库/爆款文稿库"

# 顺序 = 页面展示顺序（越靠前越贴近当前业务）
ARTICLES = [
    dict(id="a1", tag="AI 知识库", type="pdf",
         src=FS + "/Obsidian  +  Claude code，它们正在替我赚钱丨我的 AI  知识库拆解.pdf",
         title="Obsidian + Claude Code，它们正在替我赚钱｜我的 AI 知识库拆解",
         intro="把定位、写作风格、方法论、产品体系全喂进 Obsidian + Claude Code，一个人干一支团队的活。完整拆解怎么搭、怎么用、为什么有效。"),
    dict(id="a2", tag="AI 内容获客", type="md",
         src=PUB + "/20260513-公众号-Obsidian加AI知识库小红书自动获客-v1.md",
         title="我用 Obsidian 加 AI，搭了个小红书自动获客系统",
         intro="企业做小红书，最大的问题其实不是流量，是人。把老板的经验沉淀成 AI 能调用的知识库，普通运营也能稳定做出 80 分内容。"),
    dict(id="a3", tag="一人公司复盘", type="pdf",
         src=FS + "/做小红书 5 年，一个人，一套 AI 体系，月入10w+ 的实操复盘.pdf",
         title="做小红书 5 年，一个人，一套 AI 体系，月入 10w+ 的实操复盘",
         intro="深耕小红书第六年，我把所有业务推翻重做——账号被封那一周，收入没有减少。一套 AI 体系怎么撑起一个人。"),
    dict(id="a4", tag="AI 内容实操", type="md",
         src=PUB + "/20260614-公众号-3个动作让AI写的小红书笔记测不出AI味-v1.md",
         title="3 个动作，让 AI 写的小红书笔记没有 AI 味",
         intro="AI 味的根源不在「改」，在信息量。喂够真实信息、分步写、用清单检测，从源头收窄 AI 的输出范围。"),
    dict(id="a5", tag="AI 变现实操", type="md",
         src=BK + "/我用 AI 做虚拟电商，4个月卖了6万+（附完整SOP + 工具清单）.md",
         title="我用 AI 做虚拟电商，4 个月卖了 6 万+（附完整 SOP + 工具清单）",
         intro="从选品、做产品、写文案到上架，AI 帮我做了 80% 的工作。完整 SOP 和工具清单公开。"),
    dict(id="a6", tag="AI × 生活", type="pdf",
         src=FS + "/如何让 AI 接管自己的生活，替我赚钱？.pdf",
         title="如何让 AI 接管自己的生活，替我赚钱？",
         intro="3 个月把 AI 渗透进生活每个角落——身体管理、消费决策、学习、内容系统、产品升级。不只是提效，是换个脑子。"),
    dict(id="a7", tag="认知", type="md",
         src=BK + "/AI时代，流量能力比产品本身重要100倍.md",
         title="AI 时代，流量能力比产品本身重要 100 倍",
         intro="AI 解决了「做出来」，但「被看到」这件事 AI 帮不了你，而且越来越稀缺。这是普通人真正的护城河。"),
    dict(id="a8", tag="产品升级", type="md", drop_from="加入方式",
         src=BK + "/我不再教小红书了.md",
         title="我不再教小红书了",
         intro="做了两年的小红书运营社群，我把它推翻重来——从「教你做小红书」，变成「帮你搭一套靠自己赚钱的系统」。"),
    dict(id="a9", tag="方法论", type="md",
         src=BK + "/虚拟资料就是垃圾项目，90%的人都赚不到钱。.md",
         title="虚拟资料就是垃圾项目，90% 的人都赚不到钱",
         intro="90% 的人赚不到钱，是从第一步就做错了。我把踩过的坑整理成 6 条经验。"),
    dict(id="a10", tag="经验背书", type="md",
         src=BK + "/复盘贴丨6年小红书运营经验，全写在这了丨认知篇.md",
         title="复盘贴｜6 年小红书运营经验，全写在这了｜认知篇",
         intro="流量和生意，根本是两件事。6 年下来我最大的转变，是从「流量操盘手」变成「资产搭建者」。"),
    dict(id="a11", tag="个人故事", type="md",
         src=BK + "/30岁，盘点我尝试过的副业，失败了19个，最后all in小红书。.md",
         title="30 岁，盘点我尝试过的副业，失败了 19 个，最后 all in 小红书",
         intro="裸辞两年，盘点做过的十几个副业，有成功有失败。我并没有一帆风顺。"),
]

def read_src(a):
    if a["type"] == "pdf":
        return subprocess.run(["pdftotext", "-nopgbrk", a["src"], "-"],
                              capture_output=True, text=True).stdout
    with open(a["src"], encoding="utf-8") as f:
        t = f.read()
    t = re.sub(r'^﻿?---\n.*?\n---\n', '', t, flags=re.S)        # 去 frontmatter
    t = re.split(r'\n#{1,6}\s*相关方法论', t)[0]                      # 去文末「相关方法论」
    return t

def norm_key(s):
    return re.sub(r'[\s|｜丨+＋·,，。、？！：]', '', s).lower()

def clean_inline(s):
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)                       # 图片
    s = re.sub(r'\[\[([^\]|]*)\|([^\]]*)\]\]', r'\2', s)             # [[a|b]] -> b
    s = re.sub(r'\[\[([^\]]*)\]\]', r'\1', s)                        # [[a]]   -> a
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)                           # 粗体
    s = re.sub(r'^[-*]\s+', '', s)                                   # 列表符
    s = re.sub(r'^>\s*', '', s)                                      # 引用符
    return s.strip()

def is_head(s):
    if re.match(r'^[0-9]{1,2}、\S', s) and len(s) <= 32 and not s.endswith(('。', '！', '？', '，')):
        return True
    if re.match(r'^[一二三四五六七八九十]+、\S', s) and len(s) <= 32:
        return True
    if re.match(r'^[0-9]{1,2}\.[0-9]{1,2}[\s\.、]', s) and len(s) <= 40:
        return True
    return False

def to_html(text, title, src_type, drop_from=None):
    text = text.replace('​', '').replace('﻿', '').replace(' ', ' ').replace('\xad', '')
    if drop_from:
        text = re.split(re.escape(drop_from), text)[0]
    nt = norm_key(title)
    if src_type == "md":                                            # md：作者换行即分段
        segs = [ln.strip() for ln in text.split('\n') if ln.strip()]
    else:                                                           # pdf：先剔除标题行，再按句末标点分段
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        while lines:                                                # pdftotext 把标题断成几行，逐行剔除
            k = norm_key(lines[0])
            if k and k in nt and len(k) < 40:
                lines.pop(0)
            else:
                break
        segs, cur = [], ""
        for ln in lines:
            if not cur and is_head(ln):                             # 行首小标题单独成段
                segs.append(ln); continue
            cur += ln
            if re.search(r'[。！？]$', cur) or cur.endswith(('”', '」', '』', '…')):
                segs.append(cur); cur = ""
        if cur:
            segs.append(cur)
    out, started = [], False
    for seg in segs:
        is_md_h = seg.lstrip().startswith('#')
        is_bold_h = bool(re.match(r'^\*\*[^*]+\*\*$', seg.strip()))
        body = clean_inline(re.sub(r'^#{1,6}\s*', '', seg))
        if not body:
            continue
        if not started:                                             # 跳过开头与标题重复的段
            k = norm_key(body)
            if k and (k in nt or nt in k) and len(k) < 60:
                continue
            started = True
        if is_md_h or is_bold_h or is_head(body):
            out.append('<h4>%s</h4>' % html.escape(body))
        else:
            out.append('<p>%s</p>' % html.escape(body))
    return '\n'.join(out)

cards, arts = [], []
for a in ARTICLES:
    body = to_html(read_src(a), a["title"], a["type"], a.get("drop_from"))
    cards.append('<div class="文章项" data-article="%s"><span class="标">%s</span>'
                 '<strong>%s</strong><p>%s</p><span class="读">点开读全文 →</span></div>'
                 % (a["id"], html.escape(a["tag"]), html.escape(a["title"]), html.escape(a["intro"])))
    arts.append('<article data-id="%s" data-title="%s" data-tag="%s">\n%s\n</article>'
                % (a["id"], html.escape(a["title"]), html.escape(a["tag"]), body))

with open(HOME + "/_模板.html", encoding="utf-8") as f:
    tpl = f.read()
tpl = tpl.replace("<!--CARDS-->", "\n".join(cards)).replace("<!--ARTICLES-->", "\n".join(arts))
with open(HOME + "/index.html", "w", encoding="utf-8") as f:
    f.write(tpl)
print("OK 共 %d 篇；index.html = %d 字节" % (len(ARTICLES), os.path.getsize(HOME + "/index.html")))
