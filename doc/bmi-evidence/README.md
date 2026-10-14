# BMI 比較原始證據

此目錄保存 Chrome DevTools MCP 的實測輸出、效能 trace 與本地 CLI 執行結果。
所有輸入均為合成測試資料；不保存 cookie 或 ASP.NET 隱藏狀態欄位。

## 文件索引

- [完整比較報告](../bmi-comparison.md)：38 筆比較、效能、網路統計及限制。
- [主批次瀏覽器原始結果](browser-results.json)：30 筆真實表單輸入與回應、Navigation／Resource Timing。
- [補充探測原始結果](browser-probes.json)：8 筆邊界與分類探測。
- [CLI 原始結果](cli-results.json)：38 次程序的完整 stdin、stdout、stderr、exit code、英吋換算與耗時。
- [結果摘要](summary.json)：統計與差異案例 ID。
- [環境](environment.json)：瀏覽器、viewport 與頁面參考連結。
- [網路索引](network-index.json)：960 筆累積項目，依 reqid 去重；正式38案例946筆。
- [MCP 原始網路清單1](network-page-1.txt)、[清單2](network-page-2-overlap.txt)：兩頁有重疊。
- [抽樣標頭與警示摘錄](capture-notes.json)：不含Cookie或隱藏狀態；不是完整response body。
- [初始完整頁面trace](initial-load-trace.json.gz)、[MCP trace摘要](trace-summary.txt)、[初始載入時序](initial-load.json)。
- [人工頂層操作結果](manual-case.json)：170cm／65kg；不納入正式38筆統計。
- [網站P08畫面](website-P08.png)：200cm／106kg，26.5／體位過重。
- [瀏覽器量測腳本](browser-runner.js)、[CLI比較與報告產生工具](build-report.py)。
- [獨立審查紀錄](review.md)。

## 使用說明

正式測試由 Chrome DevTools MCP 執行；瀏覽器腳本不能直接以 Node.js 查詢網站。
在專案根目錄執行以下命令，會重新啟動38次本地CLI，並依既存瀏覽器證據重新產生報告；不重新查詢網站，會更新CLI時間。

```powershell
uv run --locked --group test --default-index https://packagefeedproxy.microsoft.io/pypi/simple/ python doc/bmi-evidence/build-report.py
```

本次單次與統計時間不代表SLA；逐筆INP／CPU／記憶體未量測。