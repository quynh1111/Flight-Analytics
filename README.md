
# ✈️ Flight Analytics — Phân tích & Trực quan hóa Dữ liệu Hàng không  
_(Google Colab + Databricks + FastAPI + MongoDB + ngrok)_

---

## 🎯 Mục tiêu dự án  
Dự án này mô phỏng toàn bộ quy trình của một hệ thống dữ liệu hiện đại:  
- Thu thập & xử lý dữ liệu chuyến bay bằng **PySpark trên Databricks**  
- Tính toán các chỉ số vận hành (KPI) của hãng hàng không  
- Lưu kết quả lên **MongoDB Atlas**  
- Xây dựng ứng dụng web + API với **FastAPI** để truy xuất và trực quan hóa  
- Triển khai nhanh trên **Google Colab** bằng **ngrok** để demo  

---

## 🧠 Kỹ năng thể hiện  
- **Data Engineering**: Làm sạch, chuẩn hóa và tổng hợp dữ liệu lớn với PySpark  
- **API Development**: Thiết kế RESTful API chuẩn với FastAPI  
- **NoSQL Database**: Thiết kế & thao tác với MongoDB Atlas  
- **Cloud Integration**: Kết nối Databricks ↔ MongoDB, triển khai trên Colab/ngrok  

---

## 📦 Cấu trúc dự án  

flight_analytics/
│
├── BTL_BigData.ipynb # Notebook xử lý dữ liệu (Databricks)
├── PigData_API_BTL.ipynb/ # Ứng dụng FastAPI (UI + API) chạy trên Colab
└── README.md # Tài liệu mô tả dự án

---

## ⚙️ Công nghệ & Công cụ  
| Công nghệ | Mục đích sử dụng |
|------------|------------------|
| **Databricks / PySpark** | Xử lý dữ liệu lớn, ETL pipeline |
| **MongoDB Atlas** | Lưu trữ dữ liệu tổng hợp |
| **FastAPI + Uvicorn** | Xây dựng REST API và backend |
| **Jinja2 + Chart.js** | Trực quan hóa dữ liệu và UI |
| **ngrok** | Tạo public URL để demo |
| **Google Colab** | Môi trường thực thi và chia sẻ dự án |

---

## 🧮 Pipeline xử lý dữ liệu  
1. Đọc dữ liệu CSV (`airlines`, `airports`, `flights`)  
2. Làm sạch & chuẩn hóa: chuyển kiểu dữ liệu, `fillna`, chuyển thời gian từ `HHMM → phút`  
3. Tạo các cột mới: `IS_DELAYED`, `DELAY_CATEGORY`, `PEAK_PERIOD`, `TIME_OF_DAY`  
4. Join với bảng `airlines` & `airports` để làm giàu dữ liệu  
5. Tính KPI cho từng hãng bay: tổng chuyến bay, tỷ lệ đúng giờ, tỷ lệ hủy, độ trễ trung bình, top sân bay...  
6. Ghi kết quả sang **MongoDB** dạng JSON document  
7. Ứng dụng **FastAPI** đọc dữ liệu từ MongoDB, hiển thị qua web UI & API endpoint  

---

## 💻 Hướng dẫn chạy dự án  

### **1️⃣ Xử lý dữ liệu trên Databricks**
- Tạo **Notebook mới** trên Databricks và upload file `BTL_BigData.ipynb`
- Cấu hình kết nối MongoDB (URI, user, password)
- Chạy toàn bộ các cell để xử lý và ghi dữ liệu sang MongoDB

### **2️⃣ Chạy ứng dụng API & Dashboard trên Colab**
!pip install fastapi uvicorn nest_asyncio pyngrok pymongo jinja2
!ngrok config add-authtoken <YOUR_NGROK_TOKEN>
Mở file mainAPI.ipynb hoặc script tương ứng

Khởi chạy FastAPI server

Ngrok sẽ tạo một link public:

🌍 Ứng dụng chạy tại: https://xxxx.ngrok-free.app

Truy cập đường link này để mở Dashboard hoặc test API.

### 🚀 Hướng phát triển tiếp theo
Hỗ trợ load incremental qua Delta Lake

Dashboard nâng cao bằng Streamlit hoặc Dash

Triển khai thật lên Render / Railway / AWS Lambda

Thêm JWT Authentication cho API

Tích hợp CI/CD & Unit Test cho pipeline
---
### 👤 Tác giả
Đinh Trọng Quỳnh
💼 Data Engineer
Lê Tuấn Dũng
💼 AI Engineer

⭐ Nếu bạn thấy dự án hữu ích, hãy để lại một ⭐ trên GitHub nhé!
