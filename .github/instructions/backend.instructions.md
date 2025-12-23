---
applyTo: "backend/**/*,*.py"
---

## Backend Guidelines

- 所有 API 端點必須定義在 `routers` 資料夾中。
- 範例資料庫內容需從 `database.py` 檔案載入。
- 錯誤處理僅在伺服器端記錄日誌，不得傳遞至前端。
- 確保所有 API 都有清楚的文件說明。
- 驗證後端的變更是否已反映到前端（`src/static/**`）。若發現可能造成破壞性影響的變更，請主動告知開發人員。
