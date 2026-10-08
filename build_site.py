# -*- coding: utf-8 -*-
"""贵金属全景图 · GitHub Actions 构建脚本（v4：快照与日报归档）
从 kimi.link 拉取的 base.html，把数据块替换为：SNAP_INDEX + REPORT_INDEX + BOARD_NEWS + 新 dashboard.js；
并把当日 dashboard 存入 data/snapshots/、日报索引进 data/reports/（由 workflow 一并提交归档）。
"""
import sys, os, json

base = open("base.html", encoding="utf-8").read()
dj = open("data/dashboard.js", encoding="utf-8").read().replace("</script", "<\\/script")

news_js = "{}"
if os.path.exists("rawdata/news.json"):
    news_js = open("rawdata/news.json", encoding="utf-8").read().strip().replace("</script", "<\\/script")
    json.loads(news_js)

# ---- 快照归档：当日数据落 data/snapshots/dashboard_YYYY-MM-DD.json ----
snap_idx, rpt_idx = [], []
try:
    d = json.loads(dj.replace("window.DASHBOARD_DATA=", "").rstrip(";").replace("<\\/script", "</script"))
    day = d["meta"]["updated_at"][:10]
    os.makedirs("data/snapshots", exist_ok=True)
    json.dump(d, open(f"data/snapshots/dashboard_{day}.json", "w"), ensure_ascii=False)
except Exception as e:
    print("snapshot skipped:", e)
if os.path.isdir("data/snapshots"):
    snap_idx = sorted(f[len("dashboard_"):-5] for f in os.listdir("data/snapshots")
                      if f.startswith("dashboard_") and f.endswith(".json"))
    json.dump(snap_idx, open("data/snapshots/snap_index.json", "w"))
if os.path.isdir("data/reports"):
    rpt_idx = sorted(f[:-3] for f in os.listdir("data/reports") if f.endswith(".md"))
    json.dump(rpt_idx, open("data/reports/index.json", "w"))

i = base.find("window.DASHBOARD_DATA=")
if i < 0:
    sys.exit("base.html 中未找到 window.DASHBOARD_DATA 数据块，终止")
s = base.rindex("<script>", 0, i)
e = base.index("</script>", i)
block = ("window.REPORT_INDEX = " + json.dumps(rpt_idx) + ";\n"
         "window.SNAP_INDEX = " + json.dumps(snap_idx) + ";\n"
         "window.BOARD_NEWS = " + news_js + ";\n" + dj)
out = base[:s] + "<script>\n" + block + "\n" + base[e:]

assert "<title>贵金属全景图" in out, "标题断言失败"
open("index.html", "w", encoding="utf-8").write(out)
print("index.html written,", len(out), "bytes; snapshots:", len(snap_idx), "; reports:", len(rpt_idx))
