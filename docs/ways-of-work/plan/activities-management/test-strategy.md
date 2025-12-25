# Test Strategy: Mergington High School Activities Management System

## 1. Test Strategy Overview

### Testing Scope

該測試策略涵蓋 Mergington High School 課外活動管理系統的全面質量驗證，包括：

- **活動管理功能**（查看、篩選、報名、撤銷報名）
- **教師身份認證**（登入、會話驗證）
- **校園公告管理**（建立、編輯、刪除、有效期管理）
- **API 端點與整合**
- **數據持久化與完整性**

### Quality Objectives

| 目標 | 目標值 | 驗證方法 |
|------|-------|---------|
| 代碼覆蓋率 | >80% 行覆蓋、>90% 關鍵路徑分支覆蓋 | 自動化測試 + 代碼分析 |
| 功能完整性 | 100% 受理準則驗證 | 功能與端到端測試 |
| 缺陷發現率 | >95% 生產前缺陷發現 | 多層級測試 |
| 性能基準 | API 響應時間 <200ms | 性能測試 |
| 安全驗證 | 100% 認證/授權場景覆蓋 | 安全性測試 |
| WCAG 合規性 | WCAG 2.1 AA 級標準 | 可訪問性測試 |

### Risk Assessment

#### 識別的關鍵風險

| 風險 | 嚴重性 | 可能性 | 優先級 | 緩解策略 |
|------|-------|-------|--------|---------|
| 密碼驗證失敗導致未授權訪問 | 關鍵 | 高 | P1 | 單元測試 + 安全測試 + 密碼哈希驗證 |
| 數據不一致導致報名重複 | 高 | 中 | P2 | 集成測試 + 併發測試 |
| 活動篩選邏輯錯誤 | 高 | 中 | P2 | 邊界值分析 + 決策表測試 |
| 公告有效期計算錯誤 | 中 | 低 | P3 | 狀態轉換測試 + 邊界日期測試 |
| 前後端集成失敗 | 高 | 中 | P2 | 端到端測試 + Playwright 自動化 |
| MongoDB 連接失敗 | 關鍵 | 低 | P1 | 集成測試 + 錯誤處理驗證 |

### Test Approach

本策略採用 **多層級風險導向的測試方法**，結合 ISTQB 框架與 ISO 25010 品質標準：

1. **單元測試**（開發階段）：90% 關鍵函數與路由的代碼覆蓋
2. **集成測試**（構建階段）：API 端點、數據庫交互、認證流程
3. **端到端測試**（系統級）：使用 Playwright 進行完整用戶工作流驗證
4. **性能測試**：API 響應時間、資料庫查詢效能
5. **安全性測試**：認證、授權、密碼驗證、SQL 注入
6. **迴歸測試**：代碼變更影響驗證

---

## 2. ISTQB Framework Implementation

### Test Design Techniques Selection

#### 2.1 等價分割 (Equivalence Partitioning)

**應用場景**：輸入參數與篩選條件驗證

| 測試對象 | 有效分割 | 無效分割 | 邊界值 |
|---------|---------|---------|--------|
| 日期篩選 (day) | Monday-Friday, 空值 | 無效日期 "abc" | 邊界天數 |
| 時間篩選 (start_time, end_time) | 00:00-23:59, 空值 | 無效格式 "25:00" | 午夜、正午 |
| 學生郵箱 (email) | 有效格式 "name@school.edu" | 格式錯誤 "invalid-email" | 邊界長度 |
| 活動名稱 (activity_name) | 已存在活動 | 未存在活動 | 特殊字元 |

**測試用例**：
- 有效日期範圍篩選應返回相應活動 ✓
- 無效日期字串應返回 400 錯誤 ✓
- 空值篩選應返回全部活動 ✓

#### 2.2 邊界值分析 (Boundary Value Analysis)

**應用場景**：時間、日期、數值邊界

| 測試對象 | 邊界值 | 預期結果 |
|---------|--------|---------|
| 開始時間 | 00:00, 23:59 | 包含邊界時間的活動 |
| 結束時間 | 00:00, 23:59 | 包含邊界時間的活動 |
| 最大參與人數 | 0, 1, max_int | 正確驗證容量 |
| 日期邊界 | 當日日期、過期日期 | 正確的有效期計算 |

**測試用例**：
- 搜尋 start_time="00:00" 的活動 ✓
- 搜尋 end_time="23:59" 的活動 ✓
- 當日期等於過期日期時，公告應顯示 ✓
- 當日期超過過期日期時，公告不應顯示 ✓

#### 2.3 決策表測試 (Decision Table Testing)

**應用場景**：複雜的業務規則（報名邏輯、公告可見性）

**報名驗證決策表**：

| 教師已驗證 | 活動存在 | 學生未報名 | 人數未滿 | 預期結果 | 狀態碼 |
|----------|--------|---------|--------|---------|--------|
| T | T | T | T | 報名成功 | 200 |
| T | T | T | F | 人數已滿 | 400 |
| T | T | F | T | 已報名 | 400 |
| T | F | T | T | 活動不存在 | 404 |
| F | T | T | T | 未授權 | 401 |
| T | T | F | F | 已報名 + 人數已滿 | 400 |

**公告可見性決策表**：

| 當前日期 >= 開始日期 | 當前日期 <= 過期日期 | active_only=true | 預期結果 |
|------------------|------------------|-----------------|---------|
| T | T | T | 顯示 |
| T | F | T | 不顯示 |
| F | T | T | 不顯示 |
| F | F | T | 不顯示 |
| T | T | F | 顯示 |
| T | F | F | 顯示 |
| F | T | F | 顯示 |

#### 2.4 狀態轉換測試 (State Transition Testing)

**應用場景**：公告狀態轉換、使用者認證狀態

**公告狀態轉換圖**：

```
        建立            發佈              有效             過期
未發佈 -----> 草稿 -----> 已發佈 -----> 可見 -----> 已過期 -----> 隱藏
       編輯↻        編輯↻
       刪除↓        刪除↓
        無效          無效
```

**狀態轉換測試用例**：
- 建立新公告 → 發佈 → 檢查可見性 ✓
- 建立 → 編輯過期日期 → 確認狀態更新 ✓
- 已過期公告刪除 → 確認無法訪問 ✓

#### 2.5 經驗式測試 (Experience-Based Testing)

**應用場景**：探索性測試、錯誤猜測

- 同時提交多個報名請求的併發情況
- 活動已滿時新的報名請求
- 無效的日期格式組合（"2025-13-45" 等）
- 非 ASCII 字元在郵箱或活動名稱中的處理
- 長字串輸入的邊界（>5000 字符）
- 數據庫連接中斷時的錯誤處理

---

## 3. ISO 25010 Quality Characteristics Assessment

### Quality Characteristics Prioritization Matrix

| 品質特性 | 優先級 | 驗證方法 | 驗收標準 |
|---------|--------|---------|---------|
| **功能適合性** | P1 - 關鍵 | 功能測試、端到端測試 | 100% 受理準則通過 |
| **性能效率** | P2 - 高 | 性能測試、負載測試 | API 響應 <200ms, DB 查詢 <100ms |
| **相容性** | P2 - 高 | 瀏覽器測試、集成測試 | Chrome, Firefox, Safari, Edge 支持 |
| **易用性** | P2 - 高 | 可訪問性測試、UI 測試 | WCAG 2.1 AA 合規性 |
| **可靠性** | P1 - 關鍵 | 可靠性測試、恢復測試 | 99.5% 可用性、<0.01% 數據丟失率 |
| **安全性** | P1 - 關鍵 | 安全測試、滲透測試 | 0 個關鍵/高嚴重性漏洞 |
| **可維護性** | P3 - 中 | 代碼品質分析、可測試性 | >80% 代碼覆蓋率、<10% 圈複雜度 |
| **可移植性** | P3 - 中 | 跨平台測試、部署驗證 | 支持 Linux/Windows/macOS |

### 1. Functional Suitability（功能適合性）- P1 關鍵

**完整性驗證**：
- 所有 API 端點均已實現並可訪問 ✓
- 所有受理準則均有測試覆蓋 ✓
- 資料模型完整性驗證 ✓

**正確性驗證**：
- 活動篩選邏輯正確（日期、時間組合） ✓
- 報名邏輯無重複和丟失 ✓
- 公告有效期計算準確 ✓
- Argon2 密碼驗證正確實現 ✓

**適當性驗證**：
- API 響應格式符合規範 ✓
- 錯誤訊息清晰有幫助 ✓
- 狀態碼使用正確 ✓

### 2. Performance Efficiency（性能效率）- P2 高

**時間行為**：
- API 單個請求響應時間 <200ms（99 百分位）
- 資料庫查詢時間 <100ms（平均）
- 前端頁面加載時間 <2s

**資源利用**：
- 記憶體使用 <500MB（空閒）
- CPU 使用率 <30%（正常負載）
- 資料庫連接池優化 <10 個連接

**容量**：
- 支持 1000 個並發用戶
- 支持 10,000 個活動記錄
- 支持 100,000 個報名記錄

### 3. Compatibility（相容性）- P2 高

**共存性**：
- 支持 Chrome 最近 3 個版本
- 支持 Firefox 最近 3 個版本
- 支持 Safari 最近 2 個版本
- 支持 Edge 最近 3 個版本

**互操作性**：
- MongoDB 連接穩定性 99.9%
- 環境變數配置靈活性
- 跨域請求 (CORS) 正確配置

### 4. Usability（易用性）- P2 高

**使用者界面美觀性**：
- 響應式設計正確（移動、平板、桌面）
- 視覺層級清晰
- 色彩對比度 WCAG AA 級

**可訪問性**：
- ARIA 標籤完整 ✓
- 鍵盤導航支持 ✓
- 屏幕閱讀器相容性 ✓
- 文字縮放支持 ✓

**易學性/可操作性**：
- 直觀的導航流程
- 清晰的錯誤提示
- 幫助文檔完整

### 5. Reliability（可靠性）- P1 關鍵

**容錯性**：
- 資料庫連接失敗時優雅降級 ✓
- 無效輸入处理不崩潰 ✓
- 異常情況日誌記錄 ✓

**可恢復性**：
- 自動重試機制 ✓
- 事務一致性保證 ✓
- 故障轉移支持 ✓

**可用性**：
- 99.5% 运行时间目標
- <5 秒故障轉移時間
- 零資料丟失保證

### 6. Security（安全性）- P1 關鍵

**機密性**：
- HTTPS 加密傳輸 ✓
- 密碼使用 Argon2 加密存儲 ✓
- 敏感資訊不在日誌中暴露 ✓

**完整性**：
- 數據驗證與清理 ✓
- CSRF 保護 ✓
- 輸入驗證防止注入 ✓

**認證**：
- 密碼驗證準確 ✓
- 會話驗證機制 ✓
- 無硬編碼憑證 ✓

**授權**：
- 基於角色的訪問控制 ✓
- 教師限制操作驗證 ✓
- 權限檢查完整 ✓

### 7. Maintainability（可維護性）- P3 中

**模塊性**：
- 清晰的代碼結構（routers 分離） ✓
- 關注點分離 ✓
- 可測試的設計 ✓

**可重用性**：
- 通用函數提取 ✓
- 配置集中管理 ✓

**可測試性**：
- >80% 代碼覆蓋率 ✓
- 清晰的測試邊界 ✓

### 8. Portability（可移植性）- P3 中

**適應性**：
- 跨平台路徑處理 ✓
- 環境變數配置 ✓

**可安裝性**：
- Docker 支持 ✓
- 簡單的設置流程 ✓

**可替換性**：
- MongoDB 版本兼容性 ✓
- Python 版本支持 3.8+ ✓

---

## 4. Test Environment and Data Strategy

### Test Environment Requirements

#### 開發環境 (Dev)
- Python 3.8+
- FastAPI 0.100+
- MongoDB 5.0+ (本地或 Docker)
- Node.js 18+ (前端開發)

#### 測試環境 (Test)
- 隔離的 MongoDB 實例
- 測試資料庫初始化腳本
- Mock 服務支持
- 性能監控工具

#### 預發佈環境 (Staging)
- 生產級 MongoDB 配置
- 完整的監控和日誌
- 負載測試工具
- 安全掃描工具

### Test Data Management

#### 測試資料準備策略

```yaml
Activities:
  - 標準活動集 (10-15 個)
  - 邊界情況（滿人數、無人報名）
  - 特殊字元活動名稱

Teachers:
  - 有效測試帳戶 (3-5 個)
  - 不同權限級別 (teacher, admin)
  - 無效密碼場景

Announcements:
  - 有效期內公告
  - 已過期公告
  - 尚未生效公告
```

#### 資料隱私考量
- 使用虛擬郵箱和姓名
- 不包含真實學生資訊
- 測試環境資料自動清理

### Tool Selection

| 工具 | 用途 | 安裝方式 |
|------|------|---------|
| **pytest** | 單元測試與集成測試 | `pip install pytest pytest-cov` |
| **Playwright** | 端到端自動化測試 | `pip install playwright && playwright install` |
| **locust** | 性能與負載測試 | `pip install locust` |
| **MongoDB** | 資料庫 | Docker: `docker run -d -p 27017:27017 mongo:latest` |
| **FastAPI TestClient** | API 測試 | 內建於 FastAPI |
| **axe-playwright** | 可訪問性測試 | `npm install @axe-core/playwright` |

### CI/CD Integration

#### GitHub Actions 工作流程

```yaml
name: Test Pipeline

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/unit --cov=src
      - run: pytest --cov-report=xml
      - uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
        options: >-
          --health-cmd mongosh
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/integration

  e2e-tests:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: playwright install
      - run: pytest tests/e2e/test_playwright.py

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install bandit safety
      - run: bandit -r src/
      - run: safety check
```

---

## 5. Quality Gates and Checkpoints

### 進入條件 (Entry Criteria)

**測試開始前必須滿足**：
- [ ] 功能實現已完成
- [ ] 代碼審核已通過
- [ ] 開發環境正常運行
- [ ] 測試環境已準備就緒
- [ ] 測試資料已初始化

### 退出條件 (Exit Criteria)

**測試完成前必須滿足**：
- [ ] 所有測試用例執行完成
- [ ] 代碼覆蓋率 >80%
- [ ] 無關鍵/高嚴重性缺陷
- [ ] 性能指標達成
- [ ] 安全掃描通過

### 質量指標 (Quality Metrics)

| 指標 | 目標 | 測量方式 |
|------|------|---------|
| 代碼覆蓋率 | >80% | pytest --cov |
| 缺陷密度 | <1 per KLOC | 自動化掃描 |
| 測試通過率 | >95% | CI/CD 報告 |
| 性能達成率 | 100% | 性能測試報告 |
| 安全合規性 | 100% | 安全掃描報告 |

### 升級程序 (Escalation)

**當品質問題發生時**：
1. 測試工程師記錄缺陷詳情
2. 評估缺陷嚴重性和影響
3. 如為關鍵/高級別：立即通知開發負責人
4. 如無法及時修復：評估延遲發佈的影響
5. 團隊會議決議最終方案

---

## Summary

本測試策略通過整合 ISTQB 框架與 ISO 25010 品質標準，為 Mergington High School 課外活動管理系統提供全面、多層級、風險導向的質量驗證方案。通過實施五層級的測試方法、明確的質量指標與自動化工具支持，確保交付高品質的系統。
