# -*- coding: utf-8 -*-
"""贵金属全景图 · GitHub Actions 构建脚本（v3：品牌更名适配）
从 kimi.link 拉取的 base.html（自包含单文件，含内嵌 echarts + 旧数据），
把其中的数据块整体替换为：SNAP_INDEX + BOARD_NEWS（rawdata/news.json）+ 新 data/dashboard.js。
"""
import sys, os, json

base = open("base.html", encoding="utf-8").read()
dj = open("data/dashboard.js", encoding="utf-8").read().replace("</script", "<\\/script")

news_js = "{}"
if os.path.exists("rawdata/news.json"):
    news_js = open("rawdata/news.json", encoding="utf-8").read().strip().replace("</script", "<\\/script")
    json.loads(news_js)  # 校验合法 JSON

snap_idx = "[]"
if os.path.exists("rawdata/snap_index.json"):
    snap_idx = open("rawdata/snap_index.json", encoding="utf-8").read().strip()
    json.loads(snap_idx)

i = base.find("window.DASHBOARD_DATA=")
if i < 0:
    sys.exit("base.html 中未找到 window.DASHBOARD_DATA 数据块，终止")
s = base.rindex("<script>", 0, i)
e = base.index("</script>", i)
block = ("window.SNAP_INDEX = " + snap_idx + ";\n"
         "window.BOARD_NEWS = " + news_js + ";\n" + dj)
out = base[:s] + "<script>\n" + block + "\n" + base[e:]

assert "<title>贵金属全景图" in out, "标题断言失败"
open("index.html", "w", encoding="utf-8").write(out)
print("index.html written,", len(out), "bytes")
