# 獨立審查紀錄

## 方案審查

- 角色：獨立 Rubber Duck；只讀審查，未操作網站、未編輯產品。
- 結果：無 Blocking，通過真實表單與 CLI subprocess 比較的方案。
- 補強：保留完整英吋字串與原始輸出、跨導航時鐘校正、區分顯示與分類一致性、HTTP成功與計算成功、揭露快取與無法量測項目。
- 方案審查時網站行為尚未實測，未宣稱網站分類規則已被確認。

## 最終獨立複查

- 範圍：比較報告、兩批瀏覽器結果、CLI結果、網路索引、擷取摘錄、摘要、量測與報告腳本。
- 結果：**無 Blocking**；未修改檔案、未重跑網站或報告產生工具；通過範圍凍結。
- 確認有效案例數值30/30在±0.05內，分類24/30一致；六筆差異為B01、B05、B06、B07、P02、P03。
- 確認76個GET／POST階段與資源URL集合，正式946筆、累計960筆；時間公式、nearest-rank p95、平均與中位數、位元組加總均吻合。
- 查詢逐筆提供Navigation／ResourceTiming，未量測逐筆trace／INP與iframe條件等限制已揭露。
- gzip trace可解析，共6664 events；未檢出session Cookie／Authorization值或VIEWSTATE。這是有限字串與內容檢查，不是完整資安稽核。

Reviewer使用PowerShell唯讀檢查：`Get-Content | ConvertFrom-Json`、`Compare-Object`、`Measure-Object`、`.NET GZipStream`、`Get-FileHash`。

```text
PASS: numeric=30/30; classification=24/30
PASS: 76 GET/POST phase mappings; formal 946
PASS: all summary fields; nearest-rank p95
Trace parse PASS; events=6664
PASS: unchanged SHA256: 51 doc files
```

當時16個本地連結僅本審查紀錄尚未建立，屬已知收尾，不列Blocking；本文件建立後另執行最終連結檢查。既有pytest測試由主執行者執行為7 passed，Reviewer未重跑。

## 限制與延後項目

- 四筆alert的摘錄、CLI JSON與request ID一致，且主執行者以MCP get_network_request確認原文；但交付證據未保存完整response body／四筆inlineScripts，Reviewer無法只靠保存檔案再次獨立核對原文。
- 這是非Blocking的證據追溯性補強建議；本次不重跑網站或新增測試範圍。
- 產品修正、完整跨裝置效能與資安稽核不在此次交付範圍。

## Reviewer資格

兩輪Reviewer均為工具可用的GitHub Copilot，角色為獨立Rubber Duck。工具無法指定或確認底層模型、effort與跨供應商條件，依使用者規則降級，未宣稱符合指定模型／high effort資格。未使用已知被禁止的模型名稱。

## 完成狀態

實測比較與文件完成；產品程式未變更。已確認Blocking：無；未解限制如上。正式報告：[bmi-comparison.md](../bmi-comparison.md)；證據索引：[README.md](README.md)。