# Mergington High School 課外活動管理系統 - API 文件

FastAPI 應用程式，提供課外活動管理、教師認證和校園公告發布功能。

## 功能概覽

- 🎨 查看所有課外活動並支持多維度篩選
- 📋 教師代表學生報名/撤銷報名
- 🔐 安全的教師身份驗證（Argon2）
- 📢 校園公告的建立、編輯、刪除與自動有效期管理

## 快速開始

### 安裝依賴

```bash
pip install -r ../../requirements.txt
```

### 執行應用程式

```bash
python app.py
```

應用程式將在 `http://localhost:8000` 啟動。

### 訪問 API 文件

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

## 🔬 API 端點詳解

### 活動管理端點

#### `GET /activities`

獲取所有課外活動，支持按日期、時間篩選。

**查詢參數：**
- `day` (string, 選擇性)：按日期篩選（如 "Monday", "Tuesday"）
- `start_time` (string, 選擇性)：篩選在該時間或之後開始的活動（24小時制，如 "14:30"）
- `end_time` (string, 選擇性)：篩選在該時間或之前結束的活動（24小時制，如 "17:00"）

**回應範例：**

```json
{
  "Chess Club": {
    "description": "Learn strategies and compete in chess tournaments",
    "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
    "schedule_details": {
      "days": ["Monday", "Friday"],
      "start_time": "15:15",
      "end_time": "16:45"
    },
    "max_participants": 12,
    "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
  },
  "Programming Class": {
    "description": "Learn programming fundamentals and build software projects",
    "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
    "schedule_details": {
      "days": ["Tuesday", "Thursday"],
      "start_time": "07:00",
      "end_time": "08:00"
    },
    "max_participants": 20,
    "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
  }
}
```

**狀態碼：**
- `200`：成功

---

#### `GET /activities/days`

獲取所有有活動排程的日期列表。

**回應範例：**

```json
["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
```

**狀態碼：**
- `200`：成功

---

#### `POST /activities/{activity_name}/signup`

為學生報名課外活動。需要教師驗證。

**路徑參數：**
- `activity_name` (string, 必需)：活動名稱

**查詢參數：**
- `email` (string, 必需)：學生郵箱
- `teacher_username` (string, 必需)：教師用戶名（用於驗證）

**請求範例：**

```
POST /activities/Chess%20Club/signup?email=john@mergington.edu&teacher_username=ms_rodriguez
```

**回應範例：**

```json
{
  "message": "Successfully signed up for Chess Club"
}
```

**狀態碼：**
- `200`：報名成功
- `400`：學生已報名該活動
- `401`：教師驗證失敗或未提供
- `404`：活動不存在
- `500`：伺服器錯誤

---

#### `DELETE /activities/{activity_name}/signup`

取消學生的活動報名。需要教師驗證。

**路徑參數：**
- `activity_name` (string, 必需)：活動名稱

**查詢參數：**
- `email` (string, 必需)：學生郵箱
- `teacher_username` (string, 必需)：教師用戶名（用於驗證）

**請求範例：**

```
DELETE /activities/Chess%20Club/signup?email=john@mergington.edu&teacher_username=ms_rodriguez
```

**回應範例：**

```json
{
  "message": "Successfully removed from Chess Club"
}
```

**狀態碼：**
- `200`：取消報名成功
- `401`：教師驗證失敗或未提供
- `404`：活動不存在或學生未報名
- `500`：伺服器錯誤

---

### 身份驗證端點

#### `POST /auth/login`

教師登入端點。

**查詢參數：**
- `username` (string, 必需)：教師用戶名
- `password` (string, 必需)：教師密碼

**請求範例：**

```
POST /auth/login?username=ms_rodriguez&password=SecurePass123
```

**回應範例：**

```json
{
  "username": "ms_rodriguez",
  "display_name": "Ms. Rodriguez",
  "role": "teacher"
}
```

**狀態碼：**
- `200`：登入成功
- `401`：用戶名或密碼不正確

---

#### `GET /auth/check-session`

驗證教師會話有效性。

**查詢參數：**
- `username` (string, 必需)：教師用戶名

**請求範例：**

```
GET /auth/check-session?username=ms_rodriguez
```

**回應範例：**

```json
{
  "username": "ms_rodriguez",
  "display_name": "Ms. Rodriguez",
  "role": "teacher"
}
```

**狀態碼：**
- `200`：會話有效
- `404`：教師不存在

---

### 公告管理端點

#### `GET /announcements`

獲取公告列表。預設僅返回在有效期內的公告。

**查詢參數：**
- `active_only` (boolean, 默認 `true`)：是否僅返回有效期內的公告

**回應範例：**

```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "message": "Winter Sports Day on December 25th",
    "start_date": "2025-12-20",
    "expiration_date": "2025-12-26"
  },
  {
    "id": "507f1f77bcf86cd799439012",
    "message": "Holiday Break starts today",
    "expiration_date": "2026-01-05"
  }
]
```

**狀態碼：**
- `200`：成功

---

#### `POST /announcements`

建立新公告。需要教師驗證。

**查詢參數：**
- `message` (string, 必需)：公告內容
- `expiration_date` (string, 必需)：過期日期（YYYY-MM-DD 格式）
- `start_date` (string, 選擇性)：生效日期（YYYY-MM-DD 格式），不提供則立即生效
- `teacher_username` (string, 必需)：教師用戶名（用於驗證）

**請求範例：**

```
POST /announcements?message=New%20Club%20Fair%20This%20Saturday&expiration_date=2025-12-31&teacher_username=ms_rodriguez
```

**回應範例：**

```json
{
  "id": "507f1f77bcf86cd799439013",
  "message": "New Club Fair This Saturday",
  "expiration_date": "2025-12-31"
}
```

**狀態碼：**
- `200`：建立成功
- `400`：日期格式錯誤或 start_date > expiration_date
- `401`：教師驗證失敗或未提供

---

#### `PUT /announcements/{id}`

編輯現有公告。需要教師驗證。

**路徑參數：**
- `id` (string, 必需)：公告 ID

**查詢參數：**
- `message` (string, 選擇性)：新的公告內容
- `expiration_date` (string, 選擇性)：新的過期日期
- `start_date` (string, 選擇性)：新的生效日期
- `teacher_username` (string, 必需)：教師用戶名

**狀態碼：**
- `200`：編輯成功
- `400`：日期格式錯誤
- `401`：教師驗證失敗或未提供
- `404`：公告不存在

---

#### `DELETE /announcements/{id}`

刪除公告。需要教師驗證。

**路徑參數：**
- `id` (string, 必需)：公告 ID

**查詢參數：**
- `teacher_username` (string, 必需)：教師用戶名（用於驗證）

**請求範例：**

```
DELETE /announcements/507f1f77bcf86cd799439013?teacher_username=ms_rodriguez
```

**回應範例：**

```json
{
  "message": "Announcement deleted successfully"
}
```

**狀態碼：**
- `200`：刪除成功
- `401`：教師驗證失敗或未提供
- `404`：公告不存在

---

## 📊 數據模型

### Activities 集合

```json
{
  "_id": "活動名稱",
  "description": "活動描述",
  "schedule": "時間表文字說明",
  "schedule_details": {
    "days": ["Monday", "Friday"],
    "start_time": "15:15",
    "end_time": "16:45"
  },
  "max_participants": 12,
  "participants": ["email@mergington.edu"]
}
```

### Teachers 集合

```json
{
  "_id": "username",
  "username": "ms_rodriguez",
  "display_name": "Ms. Rodriguez",
  "password": "$argon2id$v=19$m=65540,t=3...",
  "role": "teacher"
}
```

密碼使用 Argon2 算法加密。

### Announcements 集合

```json
{
  "_id": "ObjectId",
  "message": "公告內容",
  "start_date": "2025-12-20",
  "expiration_date": "2025-12-26"
}
```

---

## 🔐 身份驗證

所有需要身份驗證的端點均要求提供有效的 `teacher_username` 查詢參數。系統會驗證該教師是否存在於數據庫中。

**需要身份驗證的操作：**
- 學生報名/撤銷報名
- 建立/編輯/刪除公告

---

## 💾 持久化

所有數據存儲在 MongoDB 中。應用程式啟動時，如果數據庫為空，會自動使用 [backend/database.py](backend/database.py) 中定義的初始數據進行初始化。
