# Test Issues Checklist: Mergington High School Activities Management System

## 📋 Test Issues Creation and Prioritization

本檢查清單定義了該專案所需的全部測試 Issue，按照 ISTQB 框架與 ISO 25010 標準組織。

---

## 🎯 Test Level Issues

### ✅ Test Strategy Issue

- [ ] **建立 Test Strategy Issue**
  - 標籤：`test-strategy`, `istqb`, `iso25010`
  - 優先級：P1（關鍵）
  - 預估：2-3 story points
  - 依賴：無
  - **狀態**：已建立 ✓

### ✅ Unit Test Issues

#### Backend 單元測試

- [ ] **Unit Test: Activities Router**
  - 測試技術：等價分割 + 邊界值分析
  - 覆蓋範圍：
    - `get_activities()` - 篩選邏輯（day, start_time, end_time）
    - `get_available_days()` - 日期聚合
    - `signup_for_activity()` - 報名驗證
    - `cancel_signup()` - 撤銷報名
  - 標籤：`unit-test`, `backend-test`, `api-test`
  - 優先級：P1
  - 預估：2 story points
  - 驗收標準：
    - [ ] >90% 代碼覆蓋率
    - [ ] 所有邊界情況測試
    - [ ] 所有錯誤路徑驗證

- [ ] **Unit Test: Auth Router**
  - 測試技術：決策表測試 + 經驗式測試
  - 覆蓋範圍：
    - `login()` - Argon2 密碼驗證
    - `check_session()` - 會話驗證
  - 標籤：`unit-test`, `backend-test`, `security-test`
  - 優先級：P1
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] 密碼驗證正確性 100%
    - [ ] 會話檢查邏輯完整
    - [ ] 無權限繞過漏洞

- [ ] **Unit Test: Announcements Router**
  - 測試技術：狀態轉換測試 + 邊界值分析
  - 覆蓋範圍：
    - `get_announcements()` - 有效期過濾
    - `create_announcement()` - 日期驗證
    - `update_announcement()` - 狀態更新
    - `delete_announcement()` - 刪除驗證
  - 標籤：`unit-test`, `backend-test`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] 日期邊界測試完整
    - [ ] 狀態轉換正確
    - [ ] 無資料不一致

- [ ] **Unit Test: Database Module**
  - 測試技術：等價分割 + 經驗式測試
  - 覆蓋範圍：
    - `hash_password()` - Argon2 加密
    - `verify_password()` - 密碼驗證
    - `init_database()` - 資料初始化
  - 標籤：`unit-test`, `backend-test`, `database-test`, `security-test`
  - 優先級：P1
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] 密碼加密/驗證準確
    - [ ] 初始化幂等性
    - [ ] 無明文密碼洩露

#### Frontend 單元測試

- [ ] **Unit Test: Frontend JavaScript**
  - 測試技術：決策表 + 經驗式測試
  - 覆蓋範圍：
    - API 呼叫邏輯
    - 表單驗證
    - localStorage 管理
    - DOM 操作
  - 標籤：`unit-test`, `frontend-test`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] >80% 代碼覆蓋率
    - [ ] 所有分支邏輯驗證

---

### ✅ Integration Test Issues

- [ ] **Integration Test: Activities API Endpoints**
  - 測試技術：決策表 + 狀態轉換
  - 覆蓋範圍：
    - GET /activities 與資料庫互動
    - POST /activities/{name}/signup 與資料庫操作
    - DELETE /activities/{name}/signup 與資料庫一致性
  - 標籤：`integration-test`, `backend-test`, `api-test`, `database-test`
  - 優先級：P1
  - 預估：2 story points
  - 依賴：`unit-test-auth-router`（需要認證驗證）
  - 驗收標準：
    - [ ] 所有 API 端點正確呼叫資料庫
    - [ ] 資料一致性驗證
    - [ ] 事務完整性

- [ ] **Integration Test: Auth API Integration**
  - 測試技術：決策表 + 經驗式測試
  - 覆蓋範圍：
    - POST /auth/login 與 Teachers collection
    - GET /auth/check-session 與認證狀態
  - 標籤：`integration-test`, `backend-test`, `security-test`
  - 優先級：P1
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] 認證流程端到端正確
    - [ ] 會話狀態一致

- [ ] **Integration Test: Announcements API Integration**
  - 測試技術：狀態轉換 + 邊界值分析
  - 覆蓋範圍：
    - 公告 CRUD 操作與資料庫
    - 有效期邏輯與日期處理
  - 標籤：`integration-test`, `backend-test`, `database-test`
  - 優先級：P2
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] 日期計算準確
    - [ ] 篩選邏輯正確

- [ ] **Integration Test: Frontend-Backend API Integration**
  - 測試技術：經驗式測試 + 決策表
  - 覆蓋範圍：
    - 前端 API 呼叫與後端端點
    - 請求/回應格式匹配
    - 錯誤處理流程
  - 標籤：`integration-test`, `api-test`, `frontend-test`
  - 優先級：P2
  - 預估：2 story points
  - 依賴：所有路由單元測試
  - 驗收標準：
    - [ ] 所有 API 呼叫成功
    - [ ] 回應格式符合規範

---

### ✅ End-to-End Test Issues

- [ ] **E2E Test: Teacher Login & Session Management**
  - 工具：Playwright
  - 覆蓋範圍：
    - 訪問首頁
    - 輸入教師賬號密碼
    - 登入後重定向
    - 會話驗證
    - 登出
  - 標籤：`e2e-test`, `frontend-test`, `security-test`
  - 優先級：P1
  - 預估：2 story points
  - 驗收標準：
    - [ ] 登入成功導向儀表板
    - [ ] 會話保持有效
    - [ ] 無授權訪問被阻止

- [ ] **E2E Test: Activity Viewing & Filtering**
  - 工具：Playwright
  - 覆蓋範圍：
    - 首頁加載活動列表
    - 按日期篩選
    - 按時間篩選
    - 篩選結果驗證
  - 標籤：`e2e-test`, `frontend-test`, `test-medium`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] 篩選結果準確
    - [ ] UI 回應正常

- [ ] **E2E Test: Student Signup Workflow**
  - 工具：Playwright
  - 覆蓋範圍：
    - 教師登入
    - 查看活動詳情
    - 代表學生報名
    - 驗證報名確認
    - 查看報名列表
  - 標籤：`e2e-test`, `frontend-test`, `business-critical`
  - 優先級：P1
  - 預估：2.5 story points
  - 依賴：`e2e-test-teacher-login`
  - 驗收標準：
    - [ ] 完整報名流程成功
    - [ ] 無重複報名
    - [ ] 容量檢查有效

- [ ] **E2E Test: Announcement Management Workflow**
  - 工具：Playwright
  - 覆蓋範圍：
    - 教師登入
    - 訪問公告管理界面
    - 建立新公告
    - 編輯公告
    - 刪除公告
    - 驗證有效期顯示
  - 標籤：`e2e-test`, `frontend-test`
  - 優先級：P2
  - 預估：2.5 story points
  - 依賴：`e2e-test-teacher-login`
  - 驗收標準：
    - [ ] CRUD 操作完整
    - [ ] 有效期邏輯正確
    - [ ] UI 狀態同步

- [ ] **E2E Test: Error Handling & Edge Cases**
  - 工具：Playwright
  - 覆蓋範圍：
    - 無效登入
    - 活動已滿
    - 重複報名
    - 網絡超時
    - 資料庫錯誤
  - 標籤：`e2e-test`, `frontend-test`, `error-handling`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] 所有錯誤場景有友好提示
    - [ ] 系統不崩潰

---

### ✅ Performance Test Issues

- [ ] **Performance Test: API Response Time**
  - 工具：Locust / Apache JMeter
  - 測試範圍：
    - GET /activities（含篩選）：<200ms
    - POST /auth/login：<150ms
    - GET /announcements：<150ms
    - POST /activities/{name}/signup：<200ms
  - 標籤：`performance-test`, `backend-test`, `test-critical`
  - 優先級：P2
  - 預估：3 story points
  - 負載配置：
    - 100 並發用戶
    - 5 分鐘持續時間
  - 驗收標準：
    - [ ] 99 百分位響應時間 <500ms
    - [ ] 95 百分位響應時間 <300ms
    - [ ] 錯誤率 <0.1%

- [ ] **Performance Test: Database Query Performance**
  - 工具：MongoDB 性能分析
  - 測試範圍：
    - Activities 查詢：<100ms
    - Teachers 查詢：<50ms
    - Announcements 聚合：<200ms
  - 標籤：`performance-test`, `database-test`
  - 優先級：P2
  - 預估：2.5 story points
  - 驗收標準：
    - [ ] 平均查詢時間達成目標
    - [ ] 索引有效性驗證

- [ ] **Performance Test: Frontend Load Time**
  - 工具：Lighthouse / WebPageTest
  - 測試範圍：
    - 首頁加載時間：<2s
    - JavaScript 執行時間
    - 資源最優化
  - 標籤：`performance-test`, `frontend-test`
  - 優先級：P3
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] First Contentful Paint <1.5s
    - [ ] Largest Contentful Paint <2.5s

---

### ✅ Security Test Issues

- [ ] **Security Test: Authentication & Authorization**
  - 測試範圍：
    - 密碼驗證（Argon2）
    - 會話劫持防護
    - 未授權訪問防止
    - 密碼重置流程（若有）
  - 標籤：`security-test`, `backend-test`, `test-critical`
  - 優先級：P1
  - 預估：2.5 story points
  - 驗收標準：
    - [ ] 0 個認證繞過漏洞
    - [ ] 密碼安全存儲驗證
    - [ ] 會話管理安全

- [ ] **Security Test: Input Validation & Injection Prevention**
  - 測試範圍：
    - SQL 注入防止
    - XSS 防護
    - CSRF 保護
    - 命令注入防止
  - 標籤：`security-test`, `backend-test`
  - 優先級：P1
  - 預估：2.5 story points
  - 驗收標準：
    - [ ] 所有輸入正確清理
    - [ ] 無注入漏洞發現

- [ ] **Security Test: Data Protection & Privacy**
  - 測試範圍：
    - 敏感資訊不暴露在日誌中
    - HTTPS 加密傳輸
    - 資料庫連接安全
    - API 密鑰管理
  - 標籤：`security-test`, `backend-test`, `database-test`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] 無明文密碼或令牌洩露
    - [ ] HTTPS 強制使用

- [ ] **Security Test: OWASP Top 10 Compliance**
  - 測試範圍：
    - A1: 注入
    - A2: 認證失敗
    - A3: 數據洩露
    - A7: XSS
    - A9: 日誌和監控不足
  - 標籤：`security-test`, `compliance`
  - 優先級：P1
  - 預估：3 story points
  - 驗收標準：
    - [ ] OWASP Top 10 0 個發現
    - [ ] 高級漏洞掃描通過

---

### ✅ Accessibility Test Issues

- [ ] **Accessibility Test: WCAG 2.1 AA Compliance**
  - 工具：Axe DevTools / WAVE
  - 測試範圍：
    - 色彩對比度 AA 級
    - 標題結構
    - alt 文本完整性
    - 表單標籤關聯
  - 標籤：`accessibility-test`, `frontend-test`, `compliance`
  - 優先級：P2
  - 預估：2 story points
  - 驗收標準：
    - [ ] Axe 掃描 0 個違規
    - [ ] 手工審核通過

- [ ] **Accessibility Test: Keyboard Navigation**
  - 工具：Playwright + 手工測試
  - 測試範圍：
    - Tab 鍵導航順序
    - 焦點管理
    - 關鍵功能可達性
  - 標籤：`accessibility-test`, `frontend-test`
  - 優先級：P2
  - 預估：1.5 story points
  - 驗收標準：
    - [ ] 所有功能可通過鍵盤訪問
    - [ ] 焦點可見且邏輯正確

- [ ] **Accessibility Test: Screen Reader Compatibility**
  - 工具：NVDA / JAWS（手工測試）
  - 測試範圍：
    - 頁面結構可讀性
    - ARIA 標籤準確性
    - 動態內容通告
  - 標籤：`accessibility-test`, `frontend-test`
  - 優先級：P3
  - 預估：2 story points
  - 驗收標準：
    - [ ] 屏幕閱讀器用戶能獲取完整信息

---

### ✅ Regression Test Issues

- [ ] **Regression Test: Features Baseline**
  - 測試範圍：
    - 所有已驗證的功能重新測試
    - 代碼變更影響分析
  - 標籤：`regression-test`, `backend-test`, `frontend-test`
  - 優先級：P1（每次代碼變更）
  - 預估：1-2 story points（每個週期）
  - 驗收標準：
    - [ ] 所有現存功能仍可用
    - [ ] 無新引入的缺陷

---

## 📊 Test Type Priority Matrix

| 測試類型 | 優先級 | 關鍵性 | 預估總工時 |
|---------|--------|--------|-----------|
| Unit Tests | P1 | 關鍵 | 10 story points |
| Integration Tests | P1 | 關鍵 | 8 story points |
| E2E Tests | P1 | 高 | 12 story points |
| Security Tests | P1 | 關鍵 | 10 story points |
| Performance Tests | P2 | 高 | 7 story points |
| Accessibility Tests | P2 | 中 | 5.5 story points |
| Regression Tests | P1 | 中 | 3-5 story points（重複） |
| **總計** | | | **55.5 story points** |

---

## ⚙️ Test Dependencies Map

```
1. Unit Tests (10 pts)
   ├── Unit Test: Activities Router
   ├── Unit Test: Auth Router ←-- MUST COMPLETE FIRST
   ├── Unit Test: Announcements Router
   └── Unit Test: Database Module

2. Integration Tests (8 pts)  ← 依賴: Unit Tests
   ├── Integration Test: Activities API
   ├── Integration Test: Auth API
   ├── Integration Test: Announcements API
   └── Integration Test: Frontend-Backend

3. E2E Tests (12 pts)  ← 依賴: Integration Tests
   ├── E2E: Teacher Login
   ├── E2E: Activity Filtering ← 依賴: Teacher Login
   ├── E2E: Signup Workflow ← 依賴: Teacher Login
   ├── E2E: Announcements ← 依賴: Teacher Login
   └── E2E: Error Handling

4. Security Tests (10 pts)  ← 可並行
   ├── Auth & Authorization
   ├── Input Validation
   ├── Data Protection
   └── OWASP Compliance

5. Performance Tests (7 pts)  ← 可並行（在 Integration 後）
   ├── API Response Time
   ├── Database Performance
   └── Frontend Load Time

6. Accessibility Tests (5.5 pts)  ← 可並行
   ├── WCAG Compliance
   ├── Keyboard Navigation
   └── Screen Reader

7. Regression Tests (重複)  ← 每次代碼變更
```

---

## 🎬 Implementation Timeline

### Phase 1: Unit Testing（第 1 週）
- 建立單元測試基礎設施
- 實現所有路由的單元測試
- 目標：>85% 代碼覆蓋率

### Phase 2: Integration Testing（第 2 週）
- 依賴于 Phase 1 完成
- API 集成測試
- 目標：所有端點驗證通過

### Phase 3: E2E Testing（第 3-4 週）
- 依賴于 Phase 2 完成
- Playwright 自動化測試
- 用戶工作流驗證

### Phase 4: Non-Functional Testing（第 3-4 週，並行）
- 性能、安全、可訪問性測試
- 獨立於功能測試流程

### Phase 5: Regression & Sign-Off（第 5 週）
- 最終迴歸測試
- 品質門檢查
- 發佈準備

---

## ✨ Success Criteria

此測試計畫成功的標準：

- ✅ 所有 Issue 已建立並標籤完整
- ✅ 所有單元測試覆蓋率 >80%
- ✅ 所有集成測試通過
- ✅ 所有 E2E 測試通過
- ✅ 安全掃描 0 個關鍵漏洞
- ✅ 性能測試指標達成
- ✅ 可訪問性 WCAG AA 合規
- ✅ 無迴歸缺陷

---

## 📝 Notes

本檢查清單基於 ISTQB 測試框架與 ISO 25010 品質標準，確保全面、系統化的質量驗證。所有 Issue 均包含明確的驗收標準、依賴關係和工時估計，便於項目管理和進度追蹤。
