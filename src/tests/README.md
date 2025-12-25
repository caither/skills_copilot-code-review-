# Mergington 高中社團活動 API 測試指南

本指南說明如何執行社團活動管理系統的完整 pytest 測試套件。

## 🧪 測試結構

測試套件按照 ISTQB 框架組織為多個層級：

```
src/tests/
├── conftest.py                 # Pytest 設定與 fixtures
├── unit/                       # 單元測試（隔離、快速）
│   ├── test_database.py        # 資料庫模組測試
│   ├── test_activities_router.py # 社團活動 API 測試
│   ├── test_auth_router.py      # 身分驗證 API 測試
│   └── test_announcements_router.py # 公告 API 測試
└── integration/                # 整合測試（工作流程）
    └── test_workflows.py       # 完整 API 工作流程
```

## 🚀 安裝

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

這會安裝：
- `pytest` - 測試框架
- `pytest-cov` - 程式碼覆蓋率測量
- `mongomock` - 用於測試的模擬 MongoDB
- `httpx` - 用於 FastAPI 測試的 HTTP 客戶端

### 2. 驗證安裝

```bash
pytest --version
```

## ▶️ 執行測試

### 執行所有測試

```bash
cd src
pytest
```

### 以詳細模式執行

```bash
pytest -v
```

### 執行並產生覆蓋率報告

```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

這會產生：
- 包含逐行覆蓋率的終端機報告
- 位於 `htmlcov/index.html` 的 HTML 報告

### 執行特定類型的測試

**僅執行單元測試：**
```bash
pytest -m unit
```

**僅執行整合測試：**
```bash
pytest -m integration
```

**僅執行安全性測試：**
```bash
pytest -m security
```

### 執行特定測試檔案

```bash
pytest tests/unit/test_database.py -v
```

### 執行特定測試類別

```bash
pytest tests/unit/test_database.py::TestPasswordHashing -v
```

### 執行特定測試案例

```bash
pytest tests/unit/test_database.py::TestPasswordHashing::test_hash_password_creates_valid_hash -v
```

## 📊 測試覆蓋率目標

根據測試策略，覆蓋率目標為：

| 指標 | 目標 |
|--------|--------|
| 行覆蓋率 | >80% |
| 分支覆蓋率 | >90%（關鍵路徑） |
| 功能覆蓋率 | 100%（驗收標準） |
| 風險覆蓋率 | 100%（高風險場景） |

## 🧬 應用的 ISTQB 測試設計技術

### 單元測試

1. **等價分割（Equivalence Partitioning）**
   - 有效/無效日期分割
   - 電子郵件格式驗證
   - 基於角色的存取分割

2. **邊界值分析（Boundary Value Analysis）**
   - 時間邊界（00:00、23:59）
   - 日期邊界（今天、過去、未來）
   - 容量邊界（0、最大值、溢位）

3. **決策表測試（Decision Table Testing）**
   - 登入組合（有效/無效使用者與密碼）
   - 報名驗證（教師、活動、學生、容量）
   - 公告可見性（日期在範圍內/外）

### 整合測試

4. **狀態轉換測試（State Transition Testing）**
   - 使用者身分驗證狀態
   - 公告可見性狀態
   - 報名生命週期

5. **經驗導向測試（Experience-Based Testing）**
   - 並行報名
   - 資料庫失敗
   - 無效輸入組合

## 🔒 包含的安全性測試

- ✅ 密碼雜湊驗證（Argon2）
- ✅ 身分驗證必要性驗證
- ✅ 授權檢查
- ✅ 回應中不揭露密碼
- ✅ SQL 注入防護
- ✅ 無效輸入處理

## 📈 測試統計

| 類別 | 數量 | 預估執行時間 |
|----------|-------|-------------------|
| 單元測試 | 45+ | < 5 秒 |
| 整合測試 | 8+ | 2-5 秒 |
| 總計 | 53+ | < 10 秒 |

## 🎯 品質驗收標準

測試必須通過以下條件：
- ✅ 0 個失敗
- ✅ 0 個錯誤
- ✅ >80% 程式碼覆蓋率
- ✅ <10 秒執行時間

## 🐛 疑難排解

### MongoMock 匯入錯誤

若出現 `ImportError: No module named 'mongomock'`：

```bash
pip install mongomock
```

### FastAPI TestClient 問題

請確保從 `src/` 目錄執行測試：

```bash
cd src
pytest
```

### 資料庫連線錯誤

測試使用 mongomock 進行模擬，而非真實的 MongoDB。若出現連線錯誤：

1. 清除 pytest 快取：
   ```bash
   pytest --cache-clear
   ```

2. 重新安裝相依套件：
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 📝 測試範例

### 範例 1：密碼雜湊測試

```python
def test_verify_password_matches_valid_password(self):
    """測試 verify_password 對於正確密碼回傳 True"""
    password = "SecurePass123"
    hashed = hash_password(password)

    result = verify_password(hashed, password)
    assert result is True
```

### 範例 2：API 端點測試

```python
def test_signup_for_valid_activity(self, test_client, mock_database):
    """測試成功報名有效的社團活動"""
    response = test_client.post(
        "/activities/Programming%20Class/signup",
        params={
            "email": "newstudent@mergington.edu",
            "teacher_username": "ms_rodriguez"
        }
    )

    assert response.status_code == 200
```

### 範例 3：整合測試

```python
def test_login_and_session_verification(self, test_client, mock_database):
    """測試完整的登入與工作階段驗證工作流程"""
    # 登入
    login_response = test_client.post(
        "/auth/login",
        params={"username": "ms_rodriguez", "password": "SecurePass123"}
    )
    assert login_response.status_code == 200

    # 驗證工作階段
    session_response = test_client.get(
        "/auth/check-session",
        params={"username": "ms_rodriguez"}
    )
    assert session_response.status_code == 200
```

## 📚 參考資料

- [pytest 文件](https://docs.pytest.org/)
- [ISTQB 測試設計技術](https://www.istqb.org/)
- [FastAPI 測試](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [mongomock 文件](https://mongomock.readthedocs.io/)

## ✅ CI/CD 整合

在 GitHub Actions 中使用：

```yaml
- name: 執行測試
  run: |
    cd src
    pip install -r requirements.txt
    pytest --cov=backend --cov-report=xml
```

## 💡 提示

1. **在提交前執行測試：**
   ```bash
   pytest && git commit
   ```

2. **即時監看測試結果：**
   ```bash
   pytest -v --tb=short
   ```

3. **產生 HTML 覆蓋率報告：**
   ```bash
   pytest --cov=backend --cov-report=html
   # 在瀏覽器中開啟 htmlcov/index.html
   ```

4. **平行執行測試（需要 pytest-xdist）：**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

## 📧 聯絡資訊

關於測試的問題，請參考：
- `docs/ways-of-work/plan/activities-management/test-strategy.md`
- `docs/ways-of-work/plan/activities-management/qa-plan.md`
- `docs/ways-of-work/plan/activities-management/test-issues-checklist.md`
