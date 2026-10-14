import gzip
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

from bmi_calculator.app import _calculate_bmi


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def number(value):
    return f"{value:.2f}" if value is not None else "N/A"


def table(headers, rows):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(cell(value) for value in row) + " |" for row in rows),
    ])


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, __import__("math").ceil(len(ordered) * fraction) - 1)]


def main():
    main_batch, probes = load("browser-results.json"), load("browser-probes.json")
    notes, environment = load("capture-notes.json"), load("environment.json")
    records = main_batch["records"] + probes["records"]
    assert main_batch["done"] and probes["done"] and len(records) == 38
    assert len({record["id"] for record in records}) == 38
    requests = {}
    for name in ("network-page-1.txt", "network-page-2-overlap.txt"):
        for request_id, method, url, status in re.findall(
            r"reqid=(\d+) (\S+) (\S+) \[([^\]]+)\]", (HERE / name).read_text(encoding="utf-8")
        ):
            requests[int(request_id)] = {"id": int(request_id), "method": method, "url": url, "status": status}
    ordered_requests = sorted(requests.values(), key=lambda entry: entry["id"])
    assert len(ordered_requests) == 960
    formal_requests = [entry for entry in ordered_requests if entry["id"] >= 68]
    posts = [entry for entry in formal_requests if entry["method"] == "POST"]
    gets = [entry for entry in formal_requests if entry["method"] == "GET" and entry["url"].endswith("BmiCalculate.aspx")]
    assert len(posts) == len(gets) == len(records)
    category_map = {"體位過輕": "Underweight", "體位正常": "Normal weight", "體位過重": "Overweight", "體位超重": "Obesity"}
    results = []
    for record, post, get in zip(records, posts, gets):
        height = record["heightCm"]
        try:
            inches = repr(float(height) / 2.54)
        except ValueError:
            inches = height
        stdin = record["weightKg"] + "\n" + inches + "\n"
        started = time.perf_counter()
        process = subprocess.run(
            [sys.executable, "app.py"], cwd=ROOT, input=stdin,
            text=True, encoding="utf-8", capture_output=True, timeout=10,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        elapsed = (time.perf_counter() - started) * 1000
        match = re.search(r"Your BMI is (.+?)\. You are classified as (.+?)\.", process.stdout)
        text = record["result"]["text"]
        web_bmi = re.search(r"BMI值：([^\n]+)", text)
        web_category = re.search(r"「([^」]+)」", text)
        error = re.search(r"(\w+Error): ([^\n]+)", process.stderr)
        raw = None
        if match:
            raw = _calculate_bmi(float(record["weightKg"]), float(inches))
        nav = record["result"]["navigation"][0]
        assert nav["responseStatus"] == int(post["status"])
        assert nav["loadEventEnd"] > 0 and record["result"]["clickToDomMs"] >= 0
        positive = not record["id"].startswith("I")
        result = {
            "id": record["id"], "heightCm": height, "weightKg": record["weightKg"],
            "heightInchesInput": inches, "stdin": stdin, "command": ["<project-venv-python>", "app.py"],
            "timestamp": datetime.now(timezone.utc).isoformat(), "durationMs": elapsed,
            "stdout": process.stdout, "stderr": process.stderr, "exitCode": process.returncode,
            "cliBmi": match[1] if match else None, "cliCategory": match[2] if match else None,
            "rawBmi": raw, "exception": error[0] if error else None,
            "webBmi": web_bmi[1] if web_bmi else None,
            "webCategory": web_category[1] if web_category else None,
            "alert": notes["alerts"].get(record["id"], {}).get("message"),
            "getRequestId": get["id"], "postRequestId": post["id"], "positive": positive,
        }
        if positive:
            assert raw is not None and result["webCategory"] in category_map
            result["withinDisplayPrecision"] = abs(float(result["webBmi"]) - raw) <= 0.050000001
            result["categoryMatches"] = result["cliCategory"] == category_map[result["webCategory"]]
        results.append(result)
    (HERE / "cli-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "network-index.json").write_text(json.dumps(ordered_requests, ensure_ascii=False, indent=2), encoding="utf-8")
    positive = [result for result in results if result["positive"]]
    differences = [result for result in positive if not result["categoryMatches"]]
    timings = {
        "POST request 到第一個回應位元組": [record["result"]["navigation"][0]["responseStart"] - record["result"]["navigation"][0]["requestStart"] for record in records],
        "送出到 DOMContentLoaded": [record["result"]["clickToDomMs"] for record in records],
        "送出到 load": [record["result"]["clickToLoadMs"] for record in records],
        "CLI 程序總時間（含啟動）": [result["durationMs"] for result in results],
    }
    resource_entries = [entry for record in records for phase in ("inputPage", "result") for entry in record[phase]["resources"]]
    documents = [record[phase]["navigation"][0] for record in records for phase in ("inputPage", "result")]
    assert len(resource_entries) + len(documents) == len(formal_requests)
    resources_by_url = defaultdict(list)
    for entry in resource_entries:
        resources_by_url[entry["name"]].append(entry)
    trace_text = gzip.open(HERE / "initial-load-trace.json.gz", "rt", encoding="utf-8").read()
    assert "ASP.NET_SessionId=" not in trace_text, "Trace contains a session cookie; redact before publishing"
    assert "__VIEWSTATE" not in trace_text, "Trace contains hidden form state; redact before publishing"
    headers = notes["headerSample"]
    sections = [
        "# 本地 CLI 與國健署成人版 BMI 計算機實測比較\n",
        "## 結論\n",
        f"本次完成 **38 筆正式案例**（30 筆有效正數、8 筆無效／非生理輸入）。有效案例的 BMI 數值 **{sum(result['withinDisplayPrecision'] for result in positive)}/30** 在網站顯示精度 ±0.05 內吻合；分類 **{sum(result['categoryMatches'] for result in positive)}/30** 一致、**{len(differences)} 筆不同**。因此不能判定兩者執行結果完全相符。網站顯示最多一位小數；本地固定兩位，文字不應直接逐字比對。\n",
        "網站實測分類為「體位過輕／體位正常／體位過重／體位超重」。本報告依本次門檻案例將其分別對照 Underweight／Normal weight／Overweight／Obesity；這是比較用標籤映射，不表示「體位超重」是 Obesity 的逐字翻譯，也不代表網站後端實作已被取得。\n",
        "## 環境與範圍\n",
        f"- 日期：2026-10-14；主批次 UTC {main_batch['started']}～{main_batch['finished']}；補充批次 UTC {probes['started']}～{probes['finished']}。台灣時間為 UTC+8。\n- 網站：https://www.hpa.gov.tw/Obesity/BmiCalculate.aspx\n- 瀏覽器：{environment['ua']}\n- 視窗：{environment['viewport']}；CPU 1x、無網路節流、online={environment['online']}。\n- CLI：Python {sys.version.split()[0]}，使用 uv 專案環境；未修改任何產品程式。\n",
        "初始確認使用 Chrome DevTools MCP 的 fill_form／click；正式 38 筆使用 evaluate_script 在同來源、全視窗 iframe 內填寫原有表單並呼叫原按鈕 click()，由瀏覽器真正執行 GET／POST，不以 fetch 或重寫公式取代網站結果。iframe 的 DOM、網路與時序都取自其自己的文件；初始完整頁面 trace 與 iframe 查詢不可視為完全相同的呈現條件。\n",
        "每筆先 GET 輸入頁，填入 30 歲男性（S01 女性、S02 65 歲），再 POST 取得全新結果文件；等待 load 後 350 ms 取樣資源與結果文字。350 ms 是採集等待，不加進 click→DOMContentLoaded／load 數值。腳本點擊為非 trusted event，未量測每筆 INP。每筆均有 15 秒網頁 timeout；CLI timeout 10 秒，無觸發。\n",
        "身高以公分 / 2.54 轉為完整浮點數英吋字串；無法轉數字的 abc、空白原樣送入 CLI。CLI 真正以 subprocess 執行根目錄入口，不僅呼叫 helper；原始 BMI helper 僅作額外診斷。英吋、stdin、stdout、stderr、exit code、時間均保留於 [cli-results.json](bmi-evidence/cli-results.json)。\n",
        "來源：[CLI 輸入與換算](../src/bmi_calculator/app.py#L10)、[未四捨五入分類](../src/bmi_calculator/app.py#L42)、[兩位小數顯示](../src/bmi_calculator/app.py#L57)、[根目錄入口](../app.py#L3)。既有 tests 只涵蓋 helper，CLI 比較由本次額外執行補足。\n",
        "## 有效案例詳細比較\n",
        "N=一般值；B=18.5／24／27 邊界及30／35；R=同輸入重複；S=性別／年齡；P=補充探測。BMI 原始欄顯示至 8 位，完整 Python float 在 JSON。所有有效案例 exit code=0。\n",
        table(["ID", "cm", "kg", "CLI 原始 BMI", "CLI 顯示", "CLI 分類", "網站 BMI", "網站分類", "分類相符"], [
            [result["id"], result["heightCm"], result["weightKg"], f"{result['rawBmi']:.8f}", result["cliBmi"], result["cliCategory"], result["webBmi"], result["webCategory"], "是" if result["categoryMatches"] else "否"] for result in positive
        ]),
        "\n## 分類差異與判讀\n",
        table(["ID", "原始 BMI", "CLI 分類", "網站顯示／分類"], [[result["id"], f"{result['rawBmi']:.8f}", result["cliCategory"], f"{result['webBmi']}／{result['webCategory']}"] for result in differences]),
        "\n- 18.49 與 18.45：CLI 仍屬過輕，網站顯示 18.5 並判為正常。\n- 24.00、24.01、24.04：CLI 判為 Overweight，網站顯示 24 並判為正常；24.05 顯示 24.1、判為過重。精確 24 的差異即使不涉及顯示誤差仍存在。\n- 26.99：CLI 為 Overweight，網站顯示 27、判為體位超重；27.00 以上兩邊對照一致。\n- 30／35 不是本地額外分類邊界；網站本次也均顯示體位超重，沒有額外細分。S01／S02 與 N01 本次結果相同，但不能外推所有性別年齡。\n- **推測**：網站可能先將 BMI 取一位小數再分類，且正常上界包含顯示值 24。觀測支持此解釋，但未取得伺服器原始碼，無法斷言演算法或所有小數捨入規則。\n",
        "## 無效與非生理輸入\n",
        table(["ID", "cm", "kg", "CLI 結果", "exit", "網站結果／警示", "HTTP"], [
            [result["id"], result["heightCm"] or "空白", result["weightKg"] or "空白", result["exception"] or f"{result['cliBmi']}／{result['cliCategory']}", result["exitCode"], result["alert"] or f"{result['webBmi']}／{result['webCategory']}", "200"] for result in results if not result["positive"]
        ]),
        "\nHTTP 200 只代表回應成功，不代表有效 BMI。網站對零身高產生 ∞，本地拋出 ZeroDivisionError；兩者都接受負身高、零體重與負體重，這些結果不能當成醫療或有效輸入。網站對 abc／空白用 alert 退回輸入頁，CLI 則為未攔截的 ValueError；本次網站未出現 HTTP 4xx／5xx。alert 原文由 MCP get_network_request 核對，見 [capture-notes.json](bmi-evidence/capture-notes.json)。\n",
        "## 初始完整頁面效能\n",
        "量測為先前已開啟頁面的 reload，**不是保證冷快取**。單次 Chrome trace：LCP 242 ms、CLS 0.00、TTFB 約 60 ms。LCP 圖像為 adultBmiPic-05.png；其分解為 TTFB 60／發現延遲42／下載4／呈現延遲135 ms，四捨五入可能不等於總和。\n",
        "DocumentLatency insight：無重新導向、伺服器回應快速、HTML 未壓縮；RenderBlocking／Cache／DocumentLatency 預估 FCP、LCP 節省均為 0 ms，因此未據此主張有明顯瓶頸。MCP 摘要另附 CrUX p75 LCP 385 ms、INP35 ms、CLS0，但它是外部群體資料，不是本次38筆量測、不是本次查詢 INP。TBT、Speed Index、每次查詢 LCP／CLS／INP：N/A，未量測或無法在此條件可靠取得。\n",
        "原始 [trace](bmi-evidence/initial-load-trace.json.gz)、[MCP 摘要](bmi-evidence/trace-summary.txt)、[Navigation／Resource Timing](bmi-evidence/initial-load.json)。\n",
        "## 每次查詢效能\n",
        "單位均為 ms。TTFB=requestStart→responseStart（含網路及伺服器，不能解讀成純後端 CPU）；下載=responseEnd−responseStart；DOM／load 從按鈕送出前的 epoch 高解析度時間算到新文件事件。FCP 若 iframe 未提供則 N/A。這是瀏覽器事件時間，不是人工目視結果完成時間，也不含 MCP 往返。\n",
        table(["ID", "POST TTFB", "下載", "送出→DOM", "送出→load", "FCP", "CLI總時間"], [
            [record["id"], number(record["result"]["navigation"][0]["responseStart"] - record["result"]["navigation"][0]["requestStart"]), number(record["result"]["navigation"][0]["responseEnd"] - record["result"]["navigation"][0]["responseStart"]), number(record["result"]["clickToDomMs"]), number(record["result"]["clickToLoadMs"]), number(next((entry["startTime"] for entry in record["result"]["paint"] if entry["name"] == "first-contentful-paint"), None)), number(result["durationMs"])] for record, result in zip(records, results)
        ]),
        "\n### 統計\n",
        "全38筆含無效輸入；p95 採 nearest-rank（排序後第 ceil(n×0.95) 筆），不是跨使用者或多日服務指標。CLI 包含 Python 程序啟動且量測不同工作，不用來直接排名網頁快慢。\n",
        table(["指標", "n", "最小", "平均", "中位數", "p95", "最大"], [[name, len(values), number(min(values)), number(statistics.mean(values)), number(statistics.median(values)), number(percentile(values, 0.95)), number(max(values))] for name, values in timings.items()]),
        "\n### 相同輸入重複量測\n",
        table(["ID", "送出→load ms", "網站結果"], [[record["id"], number(record["result"]["clickToLoadMs"]), "22.5／體位正常"] for record in records if record["id"] in {"N01", "R01", "R02", "R03"}]),
        "\n## 每次查詢網路狀態\n",
        f"MCP 累積清單去重後960筆；正式38案例為 **{len(formal_requests)} 筆**，其中GET輸入文件38、POST結果文件38、子資源{len(resource_entries)}。餘下{len(ordered_requests)-len(formal_requests)}筆屬前置父頁POST與資源。所有MCP列出狀態均200；它們包含快取資源項目，不等於相同數量的實體網路往返。\n",
        "以下資源數／transfer包含該案例GET與POST兩份文件及所有觀測到的子資源。POST本文是 encodedBodySize；transferSize是瀏覽器估計、含回應標頭額外量，不是封包擷取的精確線上位元組，也不含上傳 request body。快取候選指 transferSize=0 且 encodedBodySize>0 的同來源子資源；零值不直接代表沒有資源，無法區分memory/disk cache。\n",
        table(["ID", "GET reqid", "POST reqid", "GET/POST", "協定", "POST本文 B", "子資源數", "快取候選", "合計transfer B"], [
            [record["id"], result["getRequestId"], result["postRequestId"], f"{record['inputPage']['navigation'][0]['responseStatus']}/{record['result']['navigation'][0]['responseStatus']}", record["result"]["navigation"][0]["nextHopProtocol"], record["result"]["navigation"][0]["encodedBodySize"], len(record["inputPage"]["resources"]) + len(record["result"]["resources"]), sum(entry["transferSize"] == 0 and entry["encodedBodySize"] > 0 for phase in ("inputPage", "result") for entry in record[phase]["resources"]), sum(entry["transferSize"] for phase in ("inputPage", "result") for entry in record[phase]["navigation"] + record[phase]["resources"])] for record, result in zip(records, results)
        ]),
        "\n### 資源彙總\n",
        table(["資源 URL", "觀測次數", "平均duration ms", "encoded合計 B", "transfer合計 B", "快取候選數"], [[url, len(entries), number(statistics.mean(entry["duration"] for entry in entries)), sum(entry["encodedBodySize"] for entry in entries), sum(entry["transferSize"] for entry in entries), sum(entry["transferSize"] == 0 and entry["encodedBodySize"] > 0 for entry in entries)] for url, entries in sorted(resources_by_url.items())]),
        f"\n文件encoded本文總計 {sum(entry['encodedBodySize'] for entry in documents)} B；子資源encoded總計 {sum(entry['encodedBodySize'] for entry in resource_entries)} B；文件與子資源transfer總計 {sum(entry['transferSize'] for entry in documents + resource_entries)} B。\n",
        "### 標頭與console\n",
        f"標頭是N01／reqid={headers['requestId']}的**抽樣**，並未逐筆取得全部標頭：POST application/x-www-form-urlencoded、request content-length=6672 B；回應 cache-control=private、content-length=9656 B、text/html; charset=utf-8，未見Content-Encoding。HSTS max-age=480、nosniff、CORP/COOP same-origin。private不等於禁止瀏覽器快取，也不能由此推論所有靜態資源的快取政策。詳見[capture-notes.json](bmi-evidence/capture-notes.json)。\n",
        "MCP累積console有一種error：`Ignoring duplicate Content-Security-Policy directive 'frame-src'.`，重複79次。這是父頁及iframe跨導航累積計數，**無法可靠分配成每案例的錯誤數**，不能填每筆0。未列出其他console訊息不等於已完成完整JavaScript錯誤或安全稽核。CSP允許同來源frame，本次iframe表單可正常載入；未改動網站CSP。\n",
        "[網路索引](bmi-evidence/network-index.json)記錄全部reqid／method／URL／status；[原始清單1](bmi-evidence/network-page-1.txt)及[原始清單2](bmi-evidence/network-page-2-overlap.txt)有重疊，統計以reqid去重。各URL的DNS／connect／TLS／requestStart／responseStart／responseEnd／protocol／bytes／redirectCount／deliveryType原始欄位見兩份browser JSON；TLS或DNS為0不能推論無加密，可能是已重用連線。未進行HAR或封包擷取。\n",
        "## 驗證與重現\n",
        "```powershell\nuv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ pytest -vv -ra --tb=long --showlocals\nuv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ python doc/bmi-evidence/build-report.py\n```\n",
        "既有測試實測：`7 passed in 0.05s`（Python3.13.15、pytest9.1.1、exit0）；報告工具另實際執行38次 `sys.executable app.py`，檢查唯一案例、完成旗標、38筆GET/POST對應、HTTP狀態、導覽事件與資源總數。stdout／stderr詳見CLI JSON；重跑會覆寫CLI時間與報告，但不重新查詢網站。\n",
        "重新測網站須使用Chrome DevTools MCP：開啟同一網站後，將[browser-runner.js](bmi-evidence/browser-runner.js)函式內容交給evaluate_script呼叫；預設是30筆，補充8筆定義見[browser-probes.json](bmi-evidence/browser-probes.json)的cases。MCP輸出另存檔案；量測腳本只保存合成身高體重與結果，不保存cookie、VIEWSTATE等隱藏欄位。初始trace已檢查未含本次session cookie欄位或VIEWSTATE。\n",
        "## 限制與建議\n",
        "- 這是單台Windows／單一時段、小樣本、已有連線與快取的實測，沒有控制WAN路由、伺服器負載或其他背景程序；不同輸入不可當作相同輸入的效能比較。未測手機、離線、節流、多瀏覽器、兒童年齡或所有極端值。\n- 350 ms採樣窗可能漏掉更晚才開始的非同步請求；本次頁面無額外計算API證據。未量測每案例CPU、記憶體、long tasks或INP；N/A不是0。輸入錯誤的alert可能由工具自動接受，所列load時序可能包含當次對話框處理，不代表純計算時間。\n- 早期跨頁注入未延續的試跑、人工確認與正式38筆分開，不計入有效／無效比率。批次iframe不是一般頂層使用流程，故另保留人工頂層170cm/65kg結果作交叉確認，不外推所有渲染效能。\n- 建議保留本地既定未捨入分類與門檻，先釐清是否真的要仿網站邊界行為；本次不修改產品。直接改成網站顯示值分類會違反目前專案規格，因此未採用。\n- 零值與負值驗證值得另開變更，但不屬本次比較文件範圍；延後項目：產品修正與完整跨裝置效能稽核。\n",
        "## 審查與完成狀態\n",
        "方案已由獨立Rubber Duck審查，無Blocking；最終文件審查結果另存[review.md](bmi-evidence/review.md)。Reviewer為可用GitHub Copilot，工具無法確認底層模型、effort或跨供應商條件，已依使用者規則降級而不宣稱符合資格。完成範圍為實測比較與Markdown證據；產品程式未變更。\n",
    ]
    report = "\n".join(sections) + "\n"
    (HERE.parent / "bmi-comparison.md").write_text(report, encoding="utf-8")
    summary = {
        "cases": len(results), "positive": len(positive),
        "numericWithinPrecision": sum(result["withinDisplayPrecision"] for result in positive),
        "classificationMatches": sum(result["categoryMatches"] for result in positive),
        "classificationDifferenceIds": [result["id"] for result in differences],
        "cliExitCodes": dict(Counter(result["exitCode"] for result in results)),
        "formalNetworkEntries": len(formal_requests), "mcpNetworkEntries": len(requests),
    }
    (HERE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Evidence and report checks: PASS")


if __name__ == "__main__":
    main()