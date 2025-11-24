import os
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from urllib.parse import quote_plus
import json

USER = quote_plus("tyanzuq_2811")
PASSWORD = quote_plus("")
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@cluster0.gbghetv.mongodb.net/"
DB_NAME = "flight_analytics"
COLLECTION_NAME = "airline_performance"

app = FastAPI()

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# ==== GIAO DIỆN MỚI (TAILWIND CSS + MODERN UI) ====
html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airline Analytics Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        primary: '#2563eb',
                        secondary: '#475569',
                        success: '#10b981',
                        danger: '#ef4444',
                        warning: '#f59e0b',
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #f1f5f9; }
        .card-hover:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }
        .loader {
            border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%;
            width: 30px; height: 30px; animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        #loadingOverlay { display: none; }
    </style>
</head>
<body class="text-slate-800 antialiased">

    <!-- Loading Overlay -->
    <div id="loadingOverlay" class="fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center backdrop-blur-sm">
        <div class="bg-white p-6 rounded-lg shadow-xl flex items-center space-x-4">
            <div class="loader"></div>
            <span class="text-lg font-semibold text-gray-700">Đang phân tích dữ liệu...</span>
        </div>
    </div>

    <!-- Navbar -->
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <i class="fa-solid fa-plane-circle-check text-3xl text-primary mr-3"></i>
                    <h1 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-blue-400">
                        Flight Analytics
                    </h1>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Search Section -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-8 text-center bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100">
            <h2 class="text-3xl font-bold text-gray-800 mb-2">Tra cứu hiệu suất hãng hàng không</h2>
            <p class="text-gray-500 mb-6">Nhập mã IATA của hãng bay để xem báo cáo chi tiết (VD: AA, DL, UA...)</p>
            
            <form method="post" class="flex justify-center max-w-lg mx-auto relative" onsubmit="document.getElementById('loadingOverlay').style.display = 'flex'">
                <div class="relative w-full">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fa-solid fa-magnifying-glass text-gray-400"></i>
                    </div>
                    <input type="text" name="code" 
                           class="block w-full pl-10 pr-24 py-4 border-none rounded-full shadow-md focus:ring-2 focus:ring-primary focus:outline-none sm:text-sm text-lg" 
                           placeholder="Nhập mã hãng (VD: AA)..." 
                           value="{{ code if code else '' }}" required autocomplete="off">
                    <button type="submit" 
                            class="absolute right-2 top-2 bottom-2 bg-primary hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-full transition duration-300">
                        Tìm kiếm
                    </button>
                </div>
            </form>
        </div>

        {% if airline %}
        
        <!-- Header Info -->
        <div class="flex flex-col md:flex-row justify-between items-end mb-6 border-b pb-4 border-gray-200">
            <div>
                <div class="flex items-center gap-3">
                    <span class="bg-primary text-white text-xl font-bold px-3 py-1 rounded-lg shadow">{{ airline.airline_code }}</span>
                    <h2 class="text-3xl font-bold text-gray-900">{{ airline.airline_name }}</h2>
                </div>
                <p class="text-gray-500 mt-1"><i class="fa-regular fa-clock mr-1"></i> Cập nhật lần cuối: {{ airline.last_updated }}</p>
            </div>
            <div class="mt-4 md:mt-0">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <span class="w-2 h-2 mr-2 bg-green-500 rounded-full"></span> Active Data
                </span>
            </div>
        </div>

        <!-- Key Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <!-- Total Flights -->
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500 card-hover transition duration-300">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-gray-500 uppercase">Tổng chuyến bay</p>
                    <div class="p-2 bg-blue-100 rounded-lg"><i class="fa-solid fa-plane-departure text-blue-600"></i></div>
                </div>
                <p class="text-3xl font-bold text-gray-800">{{ "{:,}".format(airline.metrics.total_flights) }}</p>
            </div>

            <!-- On Time Rate -->
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500 card-hover transition duration-300">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-gray-500 uppercase">Tỷ lệ đúng giờ</p>
                    <div class="p-2 bg-green-100 rounded-lg"><i class="fa-regular fa-clock text-green-600"></i></div>
                </div>
                <p class="text-3xl font-bold text-gray-800">{{ airline.metrics.on_time_rate }}%</p>
                <div class="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                    <div class="bg-green-500 h-1.5 rounded-full" style="width: {{ airline.metrics.on_time_rate }}%"></div>
                </div>
            </div>

            <!-- Cancellation Rate -->
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500 card-hover transition duration-300">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-gray-500 uppercase">Tỷ lệ hủy chuyến</p>
                    <div class="p-2 bg-red-100 rounded-lg"><i class="fa-solid fa-ban text-red-600"></i></div>
                </div>
                <p class="text-3xl font-bold text-gray-800">{{ airline.metrics.cancellation_rate }}%</p>
            </div>

            <!-- Avg Delay -->
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-yellow-500 card-hover transition duration-300">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-gray-500 uppercase">Trễ trung bình</p>
                    <div class="p-2 bg-yellow-100 rounded-lg"><i class="fa-solid fa-hourglass-half text-yellow-600"></i></div>
                </div>
                <p class="text-3xl font-bold text-gray-800">{{ airline.metrics.avg_delay_minutes }} <span class="text-sm font-normal text-gray-500">phút</span></p>
            </div>
        </div>

        <!-- Charts Row 1: Flight Types & Cancel Reasons -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <!-- Flight Classification -->
            <div class="bg-white rounded-xl shadow-md p-6 lg:col-span-2">
                <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                    <i class="fa-solid fa-chart-pie mr-2 text-primary"></i> Phân loại chuyến bay
                </h3>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Số lượng</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Biểu đồ</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            {% for key, value in airline.metrics.flight_counts.items() %}
                            {% set percent = (value / airline.metrics.total_flights * 100) if airline.metrics.total_flights > 0 else 0 %}
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">{{ key.replace('_',' ') }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-bold">{{ "{:,}".format(value) }}</td>
                                <td class="px-6 py-4 whitespace-nowrap w-1/3">
                                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                                        <div class="bg-indigo-600 h-2.5 rounded-full" style="width: {{ percent }}%"></div>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Cancellation Reasons -->
            <div class="bg-white rounded-xl shadow-md p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4 text-center">Nguyên nhân hủy chuyến</h3>
                <div class="relative h-64">
                    <canvas id="cancelChart"></canvas>
                </div>
                <div class="mt-4 text-center text-sm text-gray-500">
                    *Biểu đồ thể hiện tỷ trọng các lý do gây hủy chuyến
                </div>
            </div>
        </div>

        <!-- Operations Stats -->
        <h3 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <i class="fa-solid fa-cogs mr-2 text-gray-600"></i> Hiệu quả vận hành
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-white p-5 rounded-xl shadow border border-gray-100">
                <p class="text-xs text-gray-500 uppercase font-semibold">Quãng đường TB</p>
                <p class="text-2xl font-bold text-gray-800 mt-1">{{ airline.metrics.operational.avg_distance_miles | round(1) }} <span class="text-sm font-normal text-gray-400">dặm</span></p>
            </div>
            <div class="bg-white p-5 rounded-xl shadow border border-gray-100">
                <p class="text-xs text-gray-500 uppercase font-semibold">Thời gian bay TB</p>
                <p class="text-2xl font-bold text-gray-800 mt-1">{{ airline.metrics.operational.avg_air_time_minutes | round(1) }} <span class="text-sm font-normal text-gray-400">phút</span></p>
            </div>
            <div class="bg-white p-5 rounded-xl shadow border border-gray-100">
                <p class="text-xs text-gray-500 uppercase font-semibold">Taxi Out TB</p>
                <p class="text-2xl font-bold text-gray-800 mt-1">{{ airline.metrics.operational.avg_taxi_out_minutes | round(1) }} <span class="text-sm font-normal text-gray-400">phút</span></p>
            </div>
            <div class="bg-white p-5 rounded-xl shadow border border-gray-100">
                <p class="text-xs text-gray-500 uppercase font-semibold">Trễ đến TB</p>
                <p class="text-2xl font-bold text-gray-800 mt-1">{{ airline.metrics.avg_arrival_delay_minutes | round(1) }} <span class="text-sm font-normal text-gray-400">phút</span></p>
            </div>
        </div>

        <!-- Charts Row 2: Top Routes -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-xl shadow-md p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                    <i class="fa-solid fa-plane-departure mr-2 text-blue-500"></i> Top 10 Sân bay Khởi hành
                </h3>
                <canvas id="originChart"></canvas>
            </div>
            <div class="bg-white rounded-xl shadow-md p-6">
                <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
                    <i class="fa-solid fa-plane-arrival mr-2 text-green-500"></i> Top 10 Sân bay Điểm đến
                </h3>
                <canvas id="destChart"></canvas>
            </div>
        </div>

        <script>
            // Common Chart Options
            Chart.defaults.font.family = "'Inter', sans-serif";
            Chart.defaults.color = '#64748b';

            // 1. Cancellation Chart (Doughnut)
            const cancelCtx = document.getElementById('cancelChart');
            const cancelData = {{ airline.metrics.cancellation_reasons | tojson }};
            new Chart(cancelCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Hãng bay', 'Thời tiết', 'Hệ thống QG', 'An ninh'],
                    datasets: [{
                        data: [
                            cancelData.airline.count, 
                            cancelData.weather.count, 
                            cancelData.national_air_system.count, 
                            cancelData.security.count
                        ],
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.8)',  // Blue
                            'rgba(245, 158, 11, 0.8)',  // Yellow
                            'rgba(239, 68, 68, 0.8)',   // Red
                            'rgba(16, 185, 129, 0.8)'   // Green
                        ],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } }
                    }
                }
            });

            // 2. Origin Chart (Bar)
            new Chart(document.getElementById('originChart'), {
                type: 'bar',
                data: {
                    labels: {{ airline.metrics.airport_info.top_origin | tojson }},
                    datasets: [{
                        label: 'Số chuyến bay',
                        data: {{ airline.metrics.airport_info.top_origin_count | tojson }},
                        backgroundColor: 'rgba(59, 130, 246, 0.7)',
                        borderRadius: 6,
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { borderDash: [2, 4], color: '#e2e8f0' } },
                        x: { grid: { display: false } }
                    }
                }
            });

            // 3. Destination Chart (Bar)
            new Chart(document.getElementById('destChart'), {
                type: 'bar',
                data: {
                    labels: {{ airline.metrics.airport_info.top_destination | tojson }},
                    datasets: [{
                        label: 'Số chuyến bay',
                        data: {{ airline.metrics.airport_info.top_destination_count | tojson }},
                        backgroundColor: 'rgba(16, 185, 129, 0.7)',
                        borderRadius: 6,
                    }]
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { borderDash: [2, 4], color: '#e2e8f0' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        </script>

        {% elif code %}
        <div class="max-w-2xl mx-auto mt-12 bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <div class="text-5xl mb-4">😕</div>
            <h3 class="text-xl font-bold text-red-600 mb-2">Không tìm thấy dữ liệu</h3>
            <p class="text-gray-600">Chúng tôi không tìm thấy thông tin cho mã hãng bay "<strong>{{ code }}</strong>".</p>
            <p class="text-gray-500 text-sm mt-4">Vui lòng thử lại với các mã phổ biến như: AA, DL, UA, WN...</p>
        </div>
        {% else %}
        <!-- Welcome State -->
        <div class="text-center mt-12 text-gray-500">
            <div class="inline-block p-6 bg-white rounded-full shadow-md mb-4">
                <i class="fa-solid fa-chart-line text-4xl text-blue-300"></i>
            </div>
            <p class="text-lg">Nhập mã hãng bay để bắt đầu phân tích dữ liệu.</p>
        </div>
        {% endif %}
        
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-12 py-8">
        <div class="max-w-7xl mx-auto px-4 text-center">
            <p class="text-gray-400 text-sm">&copy; 2025 Flight Analytics Dashboard. Powered by MongoDB & Spark.</p>
        </div>
    </footer>

</body>
</html>
"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# ==== LOGIC BACKEND (GIỮ NGUYÊN) ====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "airline": None, "code": None})

@app.post("/", response_class=HTMLResponse)
async def search(request: Request, code: str = Form(...)):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        doc = collection.find_one({"airline_code": code.upper()}, {"_id": 0})
        client.close()
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "airline": doc, 
            "code": code.upper()
        })
    except Exception as e:
        return HTMLResponse(f"<h3>Lỗi kết nối Database: {e}</h3>")

if __name__ == "__main__":
    print("Server đang chạy tại: http://127.0.0.1:4050")
    uvicorn.run(app, host="0.0.0.0", port=4050)