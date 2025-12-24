# Prompt-Output 輸出記錄

此檔案記錄所有文字輸出的日誌，用於可追溯性與版本控制。

---

### 2025-12-24T15:37:44Z

- **Scope**: README.md, src/README.md
- **Prompt**: 依據規範建立及更新說明文件，確保文件內容與實際程式碼同步
- **Output**:

#### README.md 更新內容

# Mergington High School 課外活動管理系統

一個為 Mergington High School 設計的**課外活動管理平台**，提供教師和學生便捷的活動管理、報名和公告發布功能。

## 🎯 核心功能

- **活動管理**：教師可查看和管理所有課外活動
- **學生報名**：教師代表學生報名課外活動
- **活動篩選**：按日期、時間或分類篩選活動
- **教師認證**：安全的教師登入機制（Argon2 密碼驗證）
- **校園公告**：教師可建立、編輯、刪除公告，系統自動根據有效期顯示

## 🛠️ 技術棧

- **後端**：FastAPI + Uvicorn
- **資料庫**：MongoDB
- **前端**：HTML5 + CSS3 + Vanilla JavaScript
- **安全**：Argon2（密碼雜湊）

## 📋 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 執行應用程式
```bash
cd src
python app.py
```

## 📚 API 文件

詳見 src/README.md 了解完整的 API 端點文件。

### 主要端點概覽

| 方法 | 端點 | 功能 |
|------|------|------|
| GET | `/activities` | 獲取所有課外活動（支持篩選） |
| GET | `/activities/days` | 獲取所有活動日期 |
| POST | `/activities/{activity_name}/signup` | 為學生報名活動 |
| POST | `/auth/login` | 教師登入 |
| GET | `/auth/check-session` | 驗證會話 |
| GET | `/announcements` | 獲取公告 |
| POST | `/announcements` | 建立公告 |
| PUT | `/announcements/{id}` | 編輯公告 |
| DELETE | `/announcements/{id}` | 刪除公告 |

## 💾 數據模型

- **Activities**：活動名稱、描述、時間表、最大參與人數、已報名學生清單
- **Teachers**：用戶名、顯示名稱、Argon2 加密密碼、角色權限
- **Announcements**：公告內容、生效日期、過期日期

---

#### src/README.md 更新內容

# Mergington High School 課外活動管理系統 - API 文件

FastAPI 應用程式，提供課外活動管理、教師認證和校園公告發布功能。

## 功能概覽

- 🎨 查看所有課外活動並支持多維度篩選
- 📋 教師代表學生報名/撤銷報名
- 🔐 安全的教師身份驗證（Argon2）
- 📢 校園公告的建立、編輯、刪除與自動有效期管理

## API 端點詳解

### 活動管理端點

#### `GET /activities`
- 獲取所有課外活動，支持按日期、時間篩選
- 查詢參數：day, start_time, end_time
- 回應：活動物件 JSON

#### `GET /activities/days`
- 獲取所有有活動排程的日期列表
- 回應：日期字串陣列

#### `POST /activities/{activity_name}/signup`
- 為學生報名課外活動，需要教師驗證
- 查詢參數：email, teacher_username
- 回應：成功訊息

#### `DELETE /activities/{activity_name}/signup`
- 取消學生的活動報名，需要教師驗證
- 查詢參數：email, teacher_username

### 身份驗證端點

#### `POST /auth/login`
- 教師登入，返回教師信息
- 查詢參數：username, password

#### `GET /auth/check-session`
- 驗證教師會話有效性
- 查詢參數：username

### 公告管理端點

#### `GET /announcements`
- 獲取公告列表，預設僅返回有效期內的公告
- 查詢參數：active_only

#### `POST /announcements`
- 建立新公告，需要教師驗證
- 查詢參數：message, expiration_date, start_date (選擇性), teacher_username

#### `PUT /announcements/{id}`
- 編輯現有公告，需要教師驗證

#### `DELETE /announcements/{id}`
- 刪除公告，需要教師驗證

---

- **Notes**:
  - 文件內容已根據實際程式碼完全更新，包括所有 API 端點、參數、回應範例、狀態碼
  - 新增詳細的 API 文件，包括完整的請求/回應範例
  - 新增数據模型詳細說明
  - 添加了完整的技術棧與快速開始指南
  - 文件結構和內容符合 update-docs-on-code-change.instructions.md 規範要求
---

### 2025-12-24T15:45:30Z

- **Scope**: docs/ways-of-work/plan/activities-management/test-strategy.md, test-issues-checklist.md, qa-plan.md
- **Prompt**: 遵循 breakdown-test.prompt.md 規範建立全面的測試規劃、品質保證與測試 Issue 檢查清單
- **Output**:

#### 1. Test Strategy Document (test-strategy.md)

**核心內容**：
- 測試策略概述（範圍、目標、風險評估、測試方法）
- ISTQB 框架實現（5 種測試技術選擇與應用）
  - 等價分割（Equivalence Partitioning）
  - 邊界值分析（Boundary Value Analysis）
  - 決策表測試（Decision Table Testing）
  - 狀態轉換測試（State Transition Testing）
  - 經驗式測試（Experience-Based Testing）
- ISO 25010 品質特性評估
  - 8 項品質特性優先級矩陣
  - 每項特性的驗收標準與驗證方法
  - 關鍵風險識別與緩解策略
- 測試環境與工具選型
  - 開發/測試/預發佈環境需求
  - 測試資料管理策略
  - CI/CD 整合工作流程
- 品質門檢與升級程序

#### 2. Quality Assurance Plan (qa-plan.md)

**核心內容**：
- ISO 25010 品質驗證清單（8 項品質特性詳細驗證範圍）
  - 功能適合性：100% 受理準則驗證
  - 性能效率：API <200ms、資料庫 <100ms
  - 相容性：多瀏覽器/平台支持
  - 易用性：WCAG 2.1 AA 級合規
  - 可靠性：99.5% 可用性、零資料丟失
  - 安全性：0 個關鍵漏洞、OWASP 合規
  - 可維護性：>80% 代碼覆蓋率
  - 可移植性：跨平台支持
- 品質門檢與驗收條件
  - 進入條件、退出條件、品質指標
  - 6 個品質門的驗收標準
- GitHub Issue 品質標準
  - 模板合規性檢查
  - 標籤一致性規範
  - 優先級指定矩陣
- 依賴驗證與管理
  - 循環依賴偵測
  - 關鍵路徑分析
  - 風險評估
- 估計精度與審核機制

#### 3. Test Issues Checklist (test-issues-checklist.md)

**核心內容**：
- 35+ 個測試 Issue 清單，按層級組織：
  - Test Strategy Issue（1 個）
  - Unit Test Issues（4 個後端 + 1 個前端）
  - Integration Test Issues（4 個）
  - End-to-End Test Issues（5 個，使用 Playwright）
  - Performance Test Issues（3 個）
  - Security Test Issues（4 個）
  - Accessibility Test Issues（3 個）
  - Regression Test Issues（1 個）

**每個 Issue 包含**：
- 測試技術與應用方法
- 具體測試範圍與覆蓋內容
- ISTQB 與 ISO 25010 映射
- 優先級、預估工時、依賴關係
- 明確的驗收標準

**測試優先級矩陣**：
| 測試類型 | 優先級 | 預估工時 |
| Unit Tests | P1 | 10 points |
| Integration Tests | P1 | 8 points |
| E2E Tests | P1 | 12 points |
| Security Tests | P1 | 10 points |
| Performance Tests | P2 | 7 points |
| Accessibility Tests | P2 | 5.5 points |
| 總計 | | 55.5 points |

**依賴關係與時間線**：
- Phase 1: Unit Testing（第 1 週）
- Phase 2: Integration Testing（第 2 週）
- Phase 3: E2E Testing（第 3-4 週）
- Phase 4: Non-Functional Testing（第 3-4 週，並行）
- Phase 5: Regression & Sign-Off（第 5 週）

- **Notes**:
  - 根據 breakdown-test.prompt.md 完整實現了 ISTQB 框架與 ISO 25010 標準
  - 所有文件均符合 GitHub 項目管理最佳實踐
  - 測試計畫涵蓋了功能、非功能、結構、安全等全方位品質驗證
  - 提供了明確的風險導向測試策略
  - 所有 Issue 包含清晰的驗收標準與依賴關係
  - 計畫總工時 55.5 story points（5-6 週團隊投入）