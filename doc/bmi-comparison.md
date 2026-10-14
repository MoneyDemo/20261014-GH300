# 本地 CLI 與國健署成人版 BMI 計算機實測比較

## 結論

本次完成 **38 筆正式案例**（30 筆有效正數、8 筆無效／非生理輸入）。有效案例的 BMI 數值 **30/30** 在網站顯示精度 ±0.05 內吻合；分類 **24/30** 一致、**6 筆不同**。因此不能判定兩者執行結果完全相符。網站顯示最多一位小數；本地固定兩位，文字不應直接逐字比對。

網站實測分類為「體位過輕／體位正常／體位過重／體位超重」。本報告依本次門檻案例將其分別對照 Underweight／Normal weight／Overweight／Obesity；這是比較用標籤映射，不表示「體位超重」是 Obesity 的逐字翻譯，也不代表網站後端實作已被取得。

## 環境與範圍

- 日期：2026-10-14；主批次 UTC 2026-10-14T06:50:12.373Z～2026-10-14T06:50:36.925Z；補充批次 UTC 2026-10-14T06:51:58.238Z～2026-10-14T06:52:04.599Z。台灣時間為 UTC+8。
- 網站：https://www.hpa.gov.tw/Obesity/BmiCalculate.aspx
- 瀏覽器：Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36
- 視窗：{'width': 798, 'height': 875, 'dpr': 1.5}；CPU 1x、無網路節流、online=True。
- CLI：Python 3.13.15，使用 uv 專案環境；未修改任何產品程式。

初始確認使用 Chrome DevTools MCP 的 fill_form／click；正式 38 筆使用 evaluate_script 在同來源、全視窗 iframe 內填寫原有表單並呼叫原按鈕 click()，由瀏覽器真正執行 GET／POST，不以 fetch 或重寫公式取代網站結果。iframe 的 DOM、網路與時序都取自其自己的文件；初始完整頁面 trace 與 iframe 查詢不可視為完全相同的呈現條件。

每筆先 GET 輸入頁，填入 30 歲男性（S01 女性、S02 65 歲），再 POST 取得全新結果文件；等待 load 後 350 ms 取樣資源與結果文字。350 ms 是採集等待，不加進 click→DOMContentLoaded／load 數值。腳本點擊為非 trusted event，未量測每筆 INP。每筆均有 15 秒網頁 timeout；CLI timeout 10 秒，無觸發。

身高以公分 / 2.54 轉為完整浮點數英吋字串；無法轉數字的 abc、空白原樣送入 CLI。CLI 真正以 subprocess 執行根目錄入口，不僅呼叫 helper；原始 BMI helper 僅作額外診斷。英吋、stdin、stdout、stderr、exit code、時間均保留於 [cli-results.json](bmi-evidence/cli-results.json)。

來源：[CLI 輸入與換算](../src/bmi_calculator/app.py#L10)、[未四捨五入分類](../src/bmi_calculator/app.py#L42)、[兩位小數顯示](../src/bmi_calculator/app.py#L57)、[根目錄入口](../app.py#L3)。既有 tests 只涵蓋 helper，CLI 比較由本次額外執行補足。

## 有效案例詳細比較

N=一般值；B=18.5／24／27 邊界及30／35；R=同輸入重複；S=性別／年齡；P=補充探測。BMI 原始欄顯示至 8 位，完整 Python float 在 JSON。所有有效案例 exit code=0。

| ID | cm | kg | CLI 原始 BMI | CLI 顯示 | CLI 分類 | 網站 BMI | 網站分類 | 分類相符 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N01 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| N02 | 160 | 45 | 17.57812500 | 17.58 | Underweight | 17.6 | 體位過輕 | 是 |
| N03 | 180 | 100 | 30.86419753 | 30.86 | Obesity | 30.9 | 體位超重 | 是 |
| N04 | 150 | 35 | 15.55555556 | 15.56 | Underweight | 15.6 | 體位過輕 | 是 |
| B01 | 200 | 73.96 | 18.49000000 | 18.49 | Underweight | 18.5 | 體位正常 | 否 |
| B02 | 200 | 74 | 18.50000000 | 18.50 | Normal weight | 18.5 | 體位正常 | 是 |
| B03 | 200 | 74.04 | 18.51000000 | 18.51 | Normal weight | 18.5 | 體位正常 | 是 |
| B04 | 200 | 95.96 | 23.99000000 | 23.99 | Normal weight | 24 | 體位正常 | 是 |
| B05 | 200 | 96 | 24.00000000 | 24.00 | Overweight | 24 | 體位正常 | 否 |
| B06 | 200 | 96.04 | 24.01000000 | 24.01 | Overweight | 24 | 體位正常 | 否 |
| B07 | 200 | 107.96 | 26.99000000 | 26.99 | Overweight | 27 | 體位超重 | 否 |
| B08 | 200 | 108 | 27.00000000 | 27.00 | Obesity | 27 | 體位超重 | 是 |
| B09 | 200 | 108.04 | 27.01000000 | 27.01 | Obesity | 27 | 體位超重 | 是 |
| B10 | 200 | 119.96 | 29.99000000 | 29.99 | Obesity | 30 | 體位超重 | 是 |
| B11 | 200 | 120 | 30.00000000 | 30.00 | Obesity | 30 | 體位超重 | 是 |
| B12 | 200 | 139.96 | 34.99000000 | 34.99 | Obesity | 35 | 體位超重 | 是 |
| B13 | 200 | 140 | 35.00000000 | 35.00 | Obesity | 35 | 體位超重 | 是 |
| R01 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| R02 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| R03 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| S01 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| S02 | 170 | 65 | 22.49134948 | 22.49 | Normal weight | 22.5 | 體位正常 | 是 |
| P01 | 200 | 73.76 | 18.44000000 | 18.44 | Underweight | 18.4 | 體位過輕 | 是 |
| P02 | 200 | 73.8 | 18.45000000 | 18.45 | Underweight | 18.5 | 體位正常 | 否 |
| P03 | 200 | 96.16 | 24.04000000 | 24.04 | Overweight | 24 | 體位正常 | 否 |
| P04 | 200 | 96.2 | 24.05000000 | 24.05 | Overweight | 24.1 | 體位過重 | 是 |
| P05 | 200 | 96.4 | 24.10000000 | 24.10 | Overweight | 24.1 | 體位過重 | 是 |
| P06 | 200 | 100 | 25.00000000 | 25.00 | Overweight | 25 | 體位過重 | 是 |
| P07 | 200 | 104 | 26.00000000 | 26.00 | Overweight | 26 | 體位過重 | 是 |
| P08 | 200 | 106 | 26.50000000 | 26.50 | Overweight | 26.5 | 體位過重 | 是 |

## 分類差異與判讀

| ID | 原始 BMI | CLI 分類 | 網站顯示／分類 |
| --- | --- | --- | --- |
| B01 | 18.49000000 | Underweight | 18.5／體位正常 |
| B05 | 24.00000000 | Overweight | 24／體位正常 |
| B06 | 24.01000000 | Overweight | 24／體位正常 |
| B07 | 26.99000000 | Overweight | 27／體位超重 |
| P02 | 18.45000000 | Underweight | 18.5／體位正常 |
| P03 | 24.04000000 | Overweight | 24／體位正常 |

- 18.49 與 18.45：CLI 仍屬過輕，網站顯示 18.5 並判為正常。
- 24.00、24.01、24.04：CLI 判為 Overweight，網站顯示 24 並判為正常；24.05 顯示 24.1、判為過重。精確 24 的差異即使不涉及顯示誤差仍存在。
- 26.99：CLI 為 Overweight，網站顯示 27、判為體位超重；27.00 以上兩邊對照一致。
- 30／35 不是本地額外分類邊界；網站本次也均顯示體位超重，沒有額外細分。S01／S02 與 N01 本次結果相同，但不能外推所有性別年齡。
- **推測**：網站可能先將 BMI 取一位小數再分類，且正常上界包含顯示值 24。觀測支持此解釋，但未取得伺服器原始碼，無法斷言演算法或所有小數捨入規則。

## 無效與非生理輸入

| ID | cm | kg | CLI 結果 | exit | 網站結果／警示 | HTTP |
| --- | --- | --- | --- | --- | --- | --- |
| I01 | 0 | 65 | ZeroDivisionError: float division by zero | 1 | ∞／體位超重 | 200 |
| I02 | 170 | 0 | 0.00／Underweight | 0 | 0／體位過輕 | 200 |
| I03 | -170 | 65 | 22.49／Normal weight | 0 | 22.5／體位正常 | 200 |
| I04 | 170 | -65 | -22.49／Underweight | 0 | -22.5／體位過輕 | 200 |
| I05 | abc | 65 | ValueError: could not convert string to float: 'abc' | 1 | 請輸入正確身高數字!! | 200 |
| I06 | 170 | abc | ValueError: could not convert string to float: 'abc' | 1 | 請輸入正確體重數字!! | 200 |
| I07 | 空白 | 65 | ValueError: could not convert string to float: '' | 1 | 請輸入身高!! | 200 |
| I08 | 170 | 空白 | ValueError: could not convert string to float: '' | 1 | 請輸入體重!! | 200 |

HTTP 200 只代表回應成功，不代表有效 BMI。網站對零身高產生 ∞，本地拋出 ZeroDivisionError；兩者都接受負身高、零體重與負體重，這些結果不能當成醫療或有效輸入。網站對 abc／空白用 alert 退回輸入頁，CLI 則為未攔截的 ValueError；本次網站未出現 HTTP 4xx／5xx。alert 原文由 MCP get_network_request 核對，見 [capture-notes.json](bmi-evidence/capture-notes.json)。

## 初始完整頁面效能

量測為先前已開啟頁面的 reload，**不是保證冷快取**。單次 Chrome trace：LCP 242 ms、CLS 0.00、TTFB 約 60 ms。LCP 圖像為 adultBmiPic-05.png；其分解為 TTFB 60／發現延遲42／下載4／呈現延遲135 ms，四捨五入可能不等於總和。

DocumentLatency insight：無重新導向、伺服器回應快速、HTML 未壓縮；RenderBlocking／Cache／DocumentLatency 預估 FCP、LCP 節省均為 0 ms，因此未據此主張有明顯瓶頸。MCP 摘要另附 CrUX p75 LCP 385 ms、INP35 ms、CLS0，但它是外部群體資料，不是本次38筆量測、不是本次查詢 INP。TBT、Speed Index、每次查詢 LCP／CLS／INP：N/A，未量測或無法在此條件可靠取得。

原始 [trace](bmi-evidence/initial-load-trace.json.gz)、[MCP 摘要](bmi-evidence/trace-summary.txt)、[Navigation／Resource Timing](bmi-evidence/initial-load.json)。

## 每次查詢效能

單位均為 ms。TTFB=requestStart→responseStart（含網路及伺服器，不能解讀成純後端 CPU）；下載=responseEnd−responseStart；DOM／load 從按鈕送出前的 epoch 高解析度時間算到新文件事件。FCP 若 iframe 未提供則 N/A。這是瀏覽器事件時間，不是人工目視結果完成時間，也不含 MCP 往返。

| ID | POST TTFB | 下載 | 送出→DOM | 送出→load | FCP | CLI總時間 |
| --- | --- | --- | --- | --- | --- | --- |
| N01 | 38.80 | 0.40 | 52.00 | 53.90 | 80.00 | 88.63 |
| N02 | 18.70 | 0.30 | 29.30 | 30.50 | 56.00 | 76.45 |
| N03 | 31.90 | 0.50 | 45.40 | 47.90 | 64.00 | 88.56 |
| N04 | 35.30 | 0.50 | 48.70 | 49.80 | 76.00 | 108.17 |
| B01 | 21.00 | 0.50 | 37.50 | 40.00 | 56.00 | 111.71 |
| B02 | 19.70 | 0.50 | 31.50 | 32.90 | 48.00 | 109.32 |
| B03 | 19.20 | 0.50 | 32.90 | 34.20 | 64.00 | 87.82 |
| B04 | 62.20 | 0.70 | 76.60 | 78.10 | 100.00 | 80.20 |
| B05 | 26.20 | 0.50 | 38.00 | 39.20 | 60.00 | 83.89 |
| B06 | 26.40 | 0.60 | 37.30 | 38.30 | 60.00 | 86.19 |
| B07 | 20.20 | 0.40 | 33.30 | 34.40 | 52.00 | 86.10 |
| B08 | 87.40 | 1.00 | 107.40 | 107.50 | 120.00 | 80.88 |
| B09 | 45.50 | 0.70 | 62.40 | 64.60 | 92.00 | 88.42 |
| B10 | 280.30 | 0.50 | 291.90 | 293.00 | 316.00 | 124.29 |
| B11 | 24.10 | 0.40 | 36.60 | 38.10 | 56.00 | 110.40 |
| B12 | 24.60 | 0.40 | 36.70 | 37.90 | 68.00 | 102.20 |
| B13 | 24.30 | 0.50 | 35.10 | 36.00 | 60.00 | 91.48 |
| R01 | 31.40 | 0.40 | 43.90 | 45.80 | 72.00 | 91.28 |
| R02 | 24.50 | 0.40 | 34.80 | 35.80 | 56.00 | 88.40 |
| R03 | 20.20 | 0.50 | 35.70 | 35.70 | 48.00 | 74.89 |
| S01 | 36.40 | 0.70 | 51.90 | 54.70 | 80.00 | 84.58 |
| S02 | 22.80 | 0.50 | 37.40 | 39.60 | 52.00 | 80.82 |
| I01 | 18.10 | 0.70 | 34.40 | 36.60 | 52.00 | 90.60 |
| I02 | 24.80 | 0.60 | 37.20 | 38.30 | 68.00 | 72.48 |
| I03 | 21.30 | 0.50 | 35.00 | 36.10 | 60.00 | 71.08 |
| I04 | 21.70 | 1.00 | 35.30 | 36.60 | 68.00 | 68.94 |
| I05 | 36.40 | 7.20 | 61.00 | 63.80 | 92.00 | 78.39 |
| I06 | 21.50 | 7.90 | 41.00 | 43.60 | 64.00 | 81.38 |
| I07 | 24.20 | 6.80 | 41.20 | 44.40 | 56.00 | 85.28 |
| I08 | 24.10 | 5.70 | 40.60 | 42.90 | 64.00 | 85.76 |
| P01 | 19.20 | 0.70 | 36.30 | 37.70 | 64.00 | 64.94 |
| P02 | 24.90 | 0.60 | 40.90 | 42.10 | 72.00 | 66.38 |
| P03 | 43.50 | 0.50 | 58.80 | 60.50 | 88.00 | 68.39 |
| P04 | 20.70 | 0.60 | 36.60 | 37.90 | 68.00 | 78.18 |
| P05 | 18.20 | 0.60 | 33.10 | 34.80 | 52.00 | 68.05 |
| P06 | 20.10 | 0.50 | 37.40 | 37.50 | 48.00 | 69.38 |
| P07 | 20.10 | 0.60 | 34.50 | 35.60 | 64.00 | 71.51 |
| P08 | 38.10 | 0.80 | 52.80 | 53.90 | 76.00 | 61.38 |

### 統計

全38筆含無效輸入；p95 採 nearest-rank（排序後第 ceil(n×0.95) 筆），不是跨使用者或多日服務指標。CLI 包含 Python 程序啟動且量測不同工作，不用來直接排名網頁快慢。

| 指標 | n | 最小 | 平均 | 中位數 | p95 | 最大 |
| --- | --- | --- | --- | --- | --- | --- |
| POST request 到第一個回應位元組 | 38 | 18.10 | 35.21 | 24.25 | 87.40 | 280.30 |
| 送出到 DOMContentLoaded | 38 | 29.30 | 49.80 | 37.40 | 107.40 | 291.90 |
| 送出到 load | 38 | 30.50 | 51.32 | 38.75 | 107.50 | 293.00 |
| CLI 程序總時間（含啟動） | 38 | 61.38 | 84.39 | 84.23 | 111.71 | 124.29 |

### 相同輸入重複量測

| ID | 送出→load ms | 網站結果 |
| --- | --- | --- |
| N01 | 53.90 | 22.5／體位正常 |
| R01 | 45.80 | 22.5／體位正常 |
| R02 | 35.80 | 22.5／體位正常 |
| R03 | 35.70 | 22.5／體位正常 |

## 每次查詢網路狀態

MCP 累積清單去重後960筆；正式38案例為 **946 筆**，其中GET輸入文件38、POST結果文件38、子資源870。餘下14筆屬前置父頁POST與資源。所有MCP列出狀態均200；它們包含快取資源項目，不等於相同數量的實體網路往返。

以下資源數／transfer包含該案例GET與POST兩份文件及所有觀測到的子資源。POST本文是 encodedBodySize；transferSize是瀏覽器估計、含回應標頭額外量，不是封包擷取的精確線上位元組，也不含上傳 request body。快取候選指 transferSize=0 且 encodedBodySize>0 的同來源子資源；零值不直接代表沒有資源，無法區分memory/disk cache。

| ID | GET reqid | POST reqid | GET/POST | 協定 | POST本文 B | 子資源數 | 快取候選 | 合計transfer B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N01 | 68 | 80 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| N02 | 93 | 105 | 200/200 | h2 | 9693 | 23 | 23 | 26821 |
| N03 | 118 | 130 | 200/200 | h2 | 9676 | 23 | 23 | 26804 |
| N04 | 143 | 155 | 200/200 | h2 | 9693 | 23 | 23 | 26821 |
| B01 | 168 | 180 | 200/200 | h2 | 9659 | 23 | 23 | 26787 |
| B02 | 193 | 205 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| B03 | 218 | 230 | 200/200 | h2 | 9659 | 23 | 23 | 26787 |
| B04 | 243 | 255 | 200/200 | h2 | 9657 | 23 | 23 | 26785 |
| B05 | 268 | 280 | 200/200 | h2 | 9654 | 23 | 23 | 26782 |
| B06 | 293 | 305 | 200/200 | h2 | 9657 | 23 | 23 | 26785 |
| B07 | 318 | 330 | 200/200 | h2 | 9677 | 23 | 23 | 26805 |
| B08 | 343 | 355 | 200/200 | h2 | 9674 | 23 | 23 | 26802 |
| B09 | 368 | 380 | 200/200 | h2 | 9677 | 23 | 23 | 26805 |
| B10 | 393 | 405 | 200/200 | h2 | 9677 | 23 | 23 | 26805 |
| B11 | 418 | 430 | 200/200 | h2 | 9674 | 23 | 23 | 26802 |
| B12 | 443 | 455 | 200/200 | h2 | 9677 | 23 | 23 | 26805 |
| B13 | 468 | 480 | 200/200 | h2 | 9674 | 23 | 23 | 26802 |
| R01 | 493 | 505 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| R02 | 518 | 530 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| R03 | 543 | 555 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| S01 | 568 | 580 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| S02 | 593 | 605 | 200/200 | h2 | 9656 | 23 | 23 | 26784 |
| I01 | 618 | 630 | 200/200 | h2 | 9672 | 23 | 23 | 26800 |
| I02 | 643 | 655 | 200/200 | h2 | 9689 | 23 | 23 | 26817 |
| I03 | 668 | 680 | 200/200 | h2 | 9657 | 23 | 23 | 26785 |
| I04 | 693 | 705 | 200/200 | h2 | 9695 | 23 | 23 | 26823 |
| I05 | 718 | 730 | 200/200 | h2 | 16657 | 22 | 22 | 33785 |
| I06 | 742 | 754 | 200/200 | h2 | 16658 | 22 | 22 | 33786 |
| I07 | 766 | 778 | 200/200 | h2 | 16633 | 22 | 22 | 33761 |
| I08 | 790 | 802 | 200/200 | h2 | 16634 | 22 | 22 | 33762 |
| P01 | 814 | 826 | 200/200 | h2 | 9696 | 23 | 23 | 26824 |
| P02 | 839 | 851 | 200/200 | h2 | 9658 | 23 | 23 | 26786 |
| P03 | 864 | 876 | 200/200 | h2 | 9657 | 23 | 23 | 26785 |
| P04 | 889 | 901 | 200/200 | h2 | 9683 | 23 | 23 | 26811 |
| P05 | 914 | 926 | 200/200 | h2 | 9683 | 23 | 23 | 26811 |
| P06 | 939 | 951 | 200/200 | h2 | 9680 | 23 | 23 | 26808 |
| P07 | 964 | 976 | 200/200 | h2 | 9680 | 23 | 23 | 26808 |
| P08 | 989 | 1001 | 200/200 | h2 | 9682 | 23 | 23 | 26810 |

### 資源彙總

| 資源 URL | 觀測次數 | 平均duration ms | encoded合計 B | transfer合計 B | 快取候選數 |
| --- | --- | --- | --- | --- | --- |
| https://www.hpa.gov.tw/Obesity/css/inner.css | 76 | 0.00 | 1051156 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/css/layout.css | 76 | 0.00 | 140980 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/css/sport.css | 76 | 0.00 | 349600 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/bg/adultBmiBg.png | 76 | 0.00 | 75772 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/bg/adultBmiCTBg.jpg | 76 | 0.00 | 113240 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/bg/noteBg.png | 34 | 0.00 | 90746 | 0 | 34 |
| https://www.hpa.gov.tw/Obesity/images/pic/adultBmiPic-01.png | 76 | 0.00 | 1031396 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/pic/adultBmiPic-02.png | 76 | 0.00 | 3543880 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/pic/adultBmiPic-03.png | 76 | 0.00 | 996132 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/pic/adultBmiPic-04.png | 76 | 0.00 | 2904112 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/pic/adultBmiPic-05.png | 76 | 0.00 | 4921760 | 0 | 76 |
| https://www.hpa.gov.tw/Obesity/images/title/BMI.png | 42 | 0.03 | 495978 | 0 | 42 |
| https://www.hpa.gov.tw/Obesity/images/title/BMI_content.png | 34 | 0.00 | 318716 | 0 | 34 |

文件encoded本文總計 1023448 B；子資源encoded總計 16033468 B；文件與子資源transfer總計 1046248 B。

### 標頭與console

標頭是N01／reqid=80的**抽樣**，並未逐筆取得全部標頭：POST application/x-www-form-urlencoded、request content-length=6672 B；回應 cache-control=private、content-length=9656 B、text/html; charset=utf-8，未見Content-Encoding。HSTS max-age=480、nosniff、CORP/COOP same-origin。private不等於禁止瀏覽器快取，也不能由此推論所有靜態資源的快取政策。詳見[capture-notes.json](bmi-evidence/capture-notes.json)。

MCP累積console有一種error：`Ignoring duplicate Content-Security-Policy directive 'frame-src'.`，重複79次。這是父頁及iframe跨導航累積計數，**無法可靠分配成每案例的錯誤數**，不能填每筆0。未列出其他console訊息不等於已完成完整JavaScript錯誤或安全稽核。CSP允許同來源frame，本次iframe表單可正常載入；未改動網站CSP。

[網路索引](bmi-evidence/network-index.json)記錄全部reqid／method／URL／status；[原始清單1](bmi-evidence/network-page-1.txt)及[原始清單2](bmi-evidence/network-page-2-overlap.txt)有重疊，統計以reqid去重。各URL的DNS／connect／TLS／requestStart／responseStart／responseEnd／protocol／bytes／redirectCount／deliveryType原始欄位見兩份browser JSON；TLS或DNS為0不能推論無加密，可能是已重用連線。未進行HAR或封包擷取。

## 驗證與重現

```powershell
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ pytest -vv -ra --tb=long --showlocals
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ python doc/bmi-evidence/build-report.py
```

既有測試實測：`7 passed in 0.05s`（Python3.13.15、pytest9.1.1、exit0）；報告工具另實際執行38次 `sys.executable app.py`，檢查唯一案例、完成旗標、38筆GET/POST對應、HTTP狀態、導覽事件與資源總數。stdout／stderr詳見CLI JSON；重跑會覆寫CLI時間與報告，但不重新查詢網站。

重新測網站須使用Chrome DevTools MCP：開啟同一網站後，將[browser-runner.js](bmi-evidence/browser-runner.js)函式內容交給evaluate_script呼叫；預設是30筆，補充8筆定義見[browser-probes.json](bmi-evidence/browser-probes.json)的cases。MCP輸出另存檔案；量測腳本只保存合成身高體重與結果，不保存cookie、VIEWSTATE等隱藏欄位。初始trace已檢查未含本次session cookie欄位或VIEWSTATE。

## 限制與建議

- 這是單台Windows／單一時段、小樣本、已有連線與快取的實測，沒有控制WAN路由、伺服器負載或其他背景程序；不同輸入不可當作相同輸入的效能比較。未測手機、離線、節流、多瀏覽器、兒童年齡或所有極端值。
- 350 ms採樣窗可能漏掉更晚才開始的非同步請求；本次頁面無額外計算API證據。未量測每案例CPU、記憶體、long tasks或INP；N/A不是0。輸入錯誤的alert可能由工具自動接受，所列load時序可能包含當次對話框處理，不代表純計算時間。
- 早期跨頁注入未延續的試跑、人工確認與正式38筆分開，不計入有效／無效比率。批次iframe不是一般頂層使用流程，故另保留人工頂層170cm/65kg結果作交叉確認，不外推所有渲染效能。
- 建議保留本地既定未捨入分類與門檻，先釐清是否真的要仿網站邊界行為；本次不修改產品。直接改成網站顯示值分類會違反目前專案規格，因此未採用。
- 零值與負值驗證值得另開變更，但不屬本次比較文件範圍；延後項目：產品修正與完整跨裝置效能稽核。

## 審查與完成狀態

方案已由獨立Rubber Duck審查，無Blocking；最終文件審查結果另存[review.md](bmi-evidence/review.md)。Reviewer為可用GitHub Copilot，工具無法確認底層模型、effort或跨供應商條件，已依使用者規則降級而不宣稱符合資格。完成範圍為實測比較與Markdown證據；產品程式未變更。

