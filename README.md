# Mergington High School 課外活動管理系統

<img src="https://octodex.github.com/images/Professortocat_v2.png" align="right" height="200px" />

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

應用程式將在 `http://localhost:8000` 啟動。

### 訪問應用程式

- **Web 介面**：http://localhost:8000
- **API 文件**：http://localhost:8000/docs
- **替代文件**：http://localhost:8000/redoc

## 📚 API 文件

詳見 [src/README.md](src/README.md) 了解完整的 API 端點文件。

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

## 📂 項目結構

```
.
├── src/
│   ├── app.py              # FastAPI 應用入口
│   ├── README.md           # API 詳細文件
│   ├── backend/
│   │   ├── database.py     # MongoDB 配置與初始數據
│   │   └── routers/
│   │       ├── activities.py    # 活動管理端點
│   │       ├── auth.py          # 身份驗證端點
│   │       └── announcements.py # 公告管理端點
│   └── static/
│       ├── index.html      # 前端頁面
│       ├── app.js          # 前端邏輯
│       └── styles.css      # 樣式
├── requirements.txt        # Python 依賴
└── README.md              # 此檔案
```

## 🔐 認證

該系統使用教師身份驗證：

1. 教師使用 username/password 登入 `/auth/login` 端點
2. 系統使用 Argon2 算法驗證密碼
3. 驗證成功後，教師信息存儲在瀏覽器 localStorage
4. 所有需要權限的操作（報名、公告管理）均需提供有效的 `teacher_username` 參數

### 預設測試帳戶

詳見 [src/backend/database.py](src/backend/database.py) 中的 `initial_teachers` 部分。

## 💾 數據模型

### Activities（活動）

- `_id`：活動名稱（唯一識別符）
- `description`：活動描述
- `schedule`：時間表文字說明
- `schedule_details`：詳細時間信息
  - `days`：活動日期陣列（Monday, Tuesday 等）
  - `start_time`：開始時間（24小時制，例如 "15:15"）
  - `end_time`：結束時間
- `max_participants`：最大參與人數
- `participants`：已報名學生郵箱列表

### Teachers（教師）

- `_id`：用戶名
- `username`：用戶名
- `display_name`：顯示名稱
- `password`：Argon2 雜湊後的密碼
- `role`：角色（"teacher" 或 "admin"）

### Announcements（公告）

- `_id`：ObjectId（唯一識別符）
- `message`：公告內容
- `start_date`：生效日期（YYYY-MM-DD 格式，可選）
- `expiration_date`：過期日期（YYYY-MM-DD 格式）

## 📖 使用指南

### 教師工作流程

1. **登入**：訪問首頁並使用教師帳號登入
2. **管理學生報名**：在活動列表中為學生報名或撤銷報名
3. **篩選活動**：按日期、時間或分類查看特定活動
4. **發布公告**：在公告管理界面建立和編輯校園公告

### 公告有效期機制

- 系統自動根據 `start_date` 和 `expiration_date` 判斷公告是否應顯示
- 公告只在「有效期內」時對用戶可見
- `/announcements` 端點默認返回僅有效期內的公告（`active_only=true`）

## 📦 需求

詳見 [requirements.txt](requirements.txt)
