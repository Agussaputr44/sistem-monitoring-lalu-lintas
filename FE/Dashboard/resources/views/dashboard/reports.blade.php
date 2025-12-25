<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Laporan - YO-vehicle</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        /* Sidebar - Same as Dashboard */
        .sidebar {
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: white;
            box-shadow: 4px 0 10px rgba(0,0,0,0.1);
            padding: 30px 0;
            z-index: 1000;
        }

        .sidebar-brand {
            padding: 0 30px 30px;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 30px;
        }

        .sidebar-brand h3 {
            color: #667eea;
            font-weight: bold;
            font-size: 24px;
        }

        .sidebar-menu {
            list-style: none;
            padding: 0 15px;
        }

        .sidebar-menu li {
            margin-bottom: 5px;
        }

        .sidebar-menu a {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            color: #666;
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s;
        }

        .sidebar-menu a:hover,
        .sidebar-menu a.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .sidebar-menu i {
            margin-right: 15px;
            width: 20px;
            text-align: center;
        }

        .sidebar-user {
            position: absolute;
            bottom: 30px;
            left: 30px;
            right: 30px;
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .sidebar-user-info h6 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }

        .sidebar-user-info p {
            margin: 0;
            font-size: 12px;
            color: #999;
        }

        /* Main Content */
        .main-content {
            margin-left: 280px;
            padding: 30px;
        }

        /* Top Header */
        .top-header {
            background: white;
            padding: 20px 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .top-header h4 {
            margin: 0;
            color: #333;
            font-weight: 600;
        }

        .top-header p {
            margin: 5px 0 0;
            color: #999;
            font-size: 14px;
        }

        /* Report Filter Card */
        .report-filter-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .report-filter-card h5 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .report-type-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .report-type-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
            text-align: center;
        }

        .report-type-card:hover {
            background: rgba(102, 126, 234, 0.1);
            border-color: #667eea;
        }

        .report-type-card.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-color: #667eea;
        }

        .report-type-card i {
            font-size: 32px;
            margin-bottom: 10px;
            display: block;
        }

        .report-type-card h6 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }

        .form-label {
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 8px;
        }

        .form-control, .form-select {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 10px 15px;
            font-size: 14px;
        }

        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn-generate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-generate:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-export {
            background: linear-gradient(135deg, #1cc88a 0%, #17a673 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-export:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(28, 200, 138, 0.4);
        }

        /* Report Stats Cards */
        .report-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .report-stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
        }

        .report-stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
        }

        .report-stat-card.primary::before {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        .report-stat-card.success::before {
            background: linear-gradient(180deg, #1cc88a 0%, #17a673 100%);
        }

        .report-stat-card.warning::before {
            background: linear-gradient(180deg, #f6c23e 0%, #dda20a 100%);
        }

        .report-stat-card.info::before {
            background: linear-gradient(180deg, #36b9cc 0%, #258391 100%);
        }

        .report-stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 15px;
        }

        .report-stat-card.primary .report-stat-icon {
            background: rgba(102, 126, 234, 0.15);
            color: #667eea;
        }

        .report-stat-card.success .report-stat-icon {
            background: rgba(28, 200, 138, 0.15);
            color: #1cc88a;
        }

        .report-stat-card.warning .report-stat-icon {
            background: rgba(246, 194, 62, 0.15);
            color: #f6c23e;
        }

        .report-stat-card.info .report-stat-icon {
            background: rgba(54, 185, 204, 0.15);
            color: #36b9cc;
        }

        .report-stat-label {
            font-size: 13px;
            color: #999;
            margin-bottom: 5px;
        }

        .report-stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }

        /* Chart Cards */
        .chart-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .chart-card.full {
            grid-column: 1 / -1;
        }

        .chart-card h5 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-container {
            height: 300px;
            position: relative;
        }

        /* Table Report */
        .table-report {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }

        .table-report h5 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }

        .custom-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }

        .custom-table thead th {
            background: #f8f9fa;
            color: #666;
            font-weight: 600;
            font-size: 13px;
            padding: 15px;
            text-align: left;
            border-bottom: 2px solid #e0e0e0;
        }

        .custom-table tbody td {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
            color: #333;
        }

        .custom-table tbody tr:hover {
            background: #f8f9fa;
        }

        /* Loading State */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            display: none;
        }

        .loading-overlay.active {
            display: flex;
        }

        .loading-spinner {
            background: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
        }

        .loading-spinner i {
            font-size: 48px;
            color: #667eea;
            margin-bottom: 15px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            .main-content {
                margin-left: 0;
            }
            .chart-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p style="margin: 0; color: #666;">Generating Report...</p>
        </div>
    </div>

    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-brand">
            <h3><i class="fas fa-traffic-light"></i> YO-vehicle</h3>
            <small style="color: #999;">Admin</small>
        </div>
        
        <ul class="sidebar-menu">
            <li>
                <a href="/">
                    <i class="fas fa-home"></i>
                    <span>Dashboard</span>
                </a>
            </li>
            <li>
                <a href="/dashboard/history">
                    <i class="fas fa-history"></i>
                    <span>Riwayat Kendaraan</span>
                </a>
            </li>
            <li>
                <a href="/dashboard/reports" class="active">
                    <i class="fas fa-chart-bar"></i>
                    <span>Laporan</span>
                </a>
            </li>
            <li>
                <a href="#">
                    <i class="fas fa-cog"></i>
                    <span>Pengaturan</span>
                </a>
            </li>
        </ul>

        <div class="sidebar-user">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">A</div>
            <div class="sidebar-user-info">
                <h6>Aditya Riyap</h6>
                <p>Administrator</p>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Header -->
        <div class="top-header">
            <div>
                <h4><i class="fas fa-chart-bar"></i> Laporan Kendaraan</h4>
                <p>Generate dan export laporan deteksi kendaraan</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button class="btn-export" onclick="exportReport('pdf')">
                    <i class="fas fa-file-pdf"></i> Export PDF
                </button>
                <button class="btn-export" onclick="exportReport('excel')">
                    <i class="fas fa-file-excel"></i> Export Excel
                </button>
            </div>
        </div>

        <!-- Report Filter -->
        <div class="report-filter-card">
            <h5><i class="fas fa-sliders-h"></i> Pilih Jenis Laporan</h5>
            
            <div class="report-type-grid">
                <div class="report-type-card active" data-type="daily">
                    <i class="fas fa-calendar-day"></i>
                    <h6>Laporan Harian</h6>
                </div>
                <div class="report-type-card" data-type="weekly">
                    <i class="fas fa-calendar-week"></i>
                    <h6>Laporan Mingguan</h6>
                </div>
                <div class="report-type-card" data-type="monthly">
                    <i class="fas fa-calendar-alt"></i>
                    <h6>Laporan Bulanan</h6>
                </div>
                <div class="report-type-card" data-type="custom">
                    <i class="fas fa-calendar-check"></i>
                    <h6>Custom Range</h6>
                </div>
            </div>

            <div class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">Tanggal Mulai</label>
                    <input type="date" class="form-control" id="startDate">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Tanggal Akhir</label>
                    <input type="date" class="form-control" id="endDate">
                </div>
                <div class="col-md-3">
                    <label class="form-label">Jenis Kendaraan</label>
                    <select class="form-select" id="vehicleType">
                        <option value="">Semua Kendaraan</option>
                        <option value="Mobil">Mobil</option>
                        <option value="Motor">Motor</option>
                        <option value="Pickup">Pickup</option>
                        <option value="Truk">Truk</option>
                        <option value="Bus">Bus</option>
                        <option value="Sepeda">Sepeda</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label">&nbsp;</label>
                    <button class="btn-generate w-100" onclick="generateReport()">
                        <i class="fas fa-sync-alt"></i> Generate Report
                    </button>
                </div>
            </div>
        </div>

        <!-- Report Stats -->
        <div class="report-stats">
            <div class="report-stat-card primary">
                <div class="report-stat-icon">
                    <i class="fas fa-car"></i>
                </div>
                <div class="report-stat-label">Total Kendaraan</div>
                <div class="report-stat-value" id="totalVehicles">1,706</div>
            </div>

            <div class="report-stat-card success">
                <div class="report-stat-icon">
                    <i class="fas fa-tachometer-alt"></i>
                </div>
                <div class="report-stat-label">Kecepatan Rata-rata</div>
                <div class="report-stat-value" id="avgSpeed">66.6 <small style="font-size: 14px;">km/h</small></div>
            </div>

            <div class="report-stat-card warning">
                <div class="report-stat-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="report-stat-label">Jam Tersibuk</div>
                <div class="report-stat-value" id="peakHour">08:00</div>
            </div>

            <div class="report-stat-card info">
                <div class="report-stat-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="report-stat-label">Pertumbuhan</div>
                <div class="report-stat-value" id="growth">+12.5%</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="chart-grid">
            <div class="chart-card">
                <h5><i class="fas fa-chart-pie"></i> Distribusi Jenis Kendaraan</h5>
                <div class="chart-container">
                    <canvas id="vehicleTypeChart"></canvas>
                </div>
            </div>

            <div class="chart-card">
                <h5><i class="fas fa-chart-bar"></i> Kendaraan per Jam</h5>
                <div class="chart-container">
                    <canvas id="hourlyChart"></canvas>
                </div>
            </div>

            <div class="chart-card full">
                <h5><i class="fas fa-chart-area"></i> Trend Kendaraan (7 Hari Terakhir)</h5>
                <div class="chart-container">
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Table Report -->
        <div class="table-report">
            <h5><i class="fas fa-table"></i> Detail Laporan per Jenis Kendaraan</h5>
            <div style="overflow-x: auto;">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Jenis Kendaraan</th>
                            <th>Total Deteksi</th>
                            <th>Persentase</th>
                            <th>Kecepatan Rata-rata</th>
                            <th>Kecepatan Min</th>
                            <th>Kecepatan Max</th>
                            <th>Trend</th>
                        </tr>
                    </thead>
                    <tbody id="reportTableBody">
                        <!-- Data will be inserted here -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        let vehicleTypeChart, hourlyChart, trendChart;
        let currentReportType = 'daily';

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            setDefaultDates();
            setupReportTypeCards();
            generateReport();
        });

        // Setup Report Type Cards
        function setupReportTypeCards() {
            document.querySelectorAll('.report-type-card').forEach(card => {
                card.addEventListener('click', function() {
                    document.querySelectorAll('.report-type-card').forEach(c => c.classList.remove('active'));
                    this.classList.add('active');
                    currentReportType = this.dataset.type;
                    updateDateRange(currentReportType);
                });
            });
        }

        // Update Date Range based on Report Type
        function updateDateRange(type) {
            const today = new Date();
            const endDate = document.getElementById('endDate');
            const startDate = document.getElementById('startDate');
            
            endDate.value = today.toISOString().split('T')[0];

            if (type === 'daily') {
                startDate.value = today.toISOString().split('T')[0];
            } else if (type === 'weekly') {
                const weekAgo = new Date(today);
                weekAgo.setDate(weekAgo.getDate() - 7);
                startDate.value = weekAgo.toISOString().split('T')[0];
            } else if (type === 'monthly') {
                const monthAgo = new Date(today);
                monthAgo.setMonth(monthAgo.getMonth() - 1);
                startDate.value = monthAgo.toISOString().split('T')[0];
            }
        }

        // Set Default Dates
        function setDefaultDates() {
            const today = new Date();
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = today.toISOString().split('T')[0];
        }

        // Initialize Charts
        function initializeCharts() {
            // Vehicle Type Pie Chart
            const ctx1 = document.getElementById('vehicleTypeChart').getContext('2d');
            vehicleTypeChart = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Motor', 'Mobil', 'Pickup', 'Truk', 'Bus', 'Sepeda'],
                    datasets: [{
                        data: [1400, 240, 36, 12, 18, 0],
                        backgroundColor: [
                            '#667eea',
                            '#1cc88a',
                            '#f6c23e',
                            '#e74a3b',
                            '#36b9cc',
                            '#858796'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { padding: 15, font: { size: 12 } }
                        }
                    }
                }
            });

            // Hourly Bar Chart
            const ctx2 = document.getElementById('hourlyChart').getContext('2d');
            hourlyChart = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                    datasets: [{
                        label: 'Kendaraan',
                        data: generateRandomData(24, 20, 150),
                        backgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });

            // Trend Line Chart
            const ctx3 = document.getElementById('trendChart').getContext('2d');
            trendChart = new Chart(ctx3, {
                type: 'line',
                data: {
                    labels: getLast7Days(),
                    datasets: [{
                        label: 'Total Kendaraan',
                        data: [1200, 1350, 1400, 1500, 1450, 1600, 1706],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        // Generate Report
        function generateReport() {
            showLoading();

            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const vehicleType = document.getElementById('vehicleType').value;

            // Simulate API call
            setTimeout(() => {
                updateReportData();
                hideLoading();
            }, 1000);
        }

        // Update Report Data
        function updateReportData() {
            // Update stats
            document.getElementById('totalVehicles').textContent = '1,706';
            document.getElementById('avgSpeed').innerHTML = '66.6 <small style="font-size: 14px;">km/h</small>';
            document.getElementById('peakHour').textContent = '08:00';
            document.getElementById('growth').textContent = '+12.5%';

            // Update table
            const tableData = [
                { type: 'Motor', count: 1400, percent: 82.0, avg: 55.2, min: 25.0, max: 85.0, trend: '+15%' },
                { type: 'Mobil', count: 240, percent: 14.1, avg: 62.5, min: 30.0, max: 90.0, trend: '+8%' },
                { type: 'Pickup', count: 36, percent: 2.1, avg: 58.3, min: 35.0, max: 80.0, trend: '+5%' },
                { type: 'Truk', count: 12, percent: 0.7, avg: 48.7, min: 25.0, max: 65.0, trend: '+2%' },
                { type: 'Bus', count: 18, percent: 1.1, avg: 52.4, min: 30.0, max: 70.0, trend: '+3%' },
            ];

            const tbody = document.getElementById('reportTableBody');
            tbody.innerHTML = '';

            tableData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${row.type}</strong></td>
                    <td>${row.count.toLocaleString()}</td>
                    <td>${row.percent}%</td>
                    <td>${row.avg} km/h</td>
                    <td>${row.min} km/h</td>
                    <td>${row.max} km/h</td>
                    <td><span style="color: #1cc88a; font-weight: 600;">${row.trend}</span></td>
                `;
                tbody.appendChild(tr);
            });

            // Update charts
            vehicleTypeChart.data.datasets[0].data = tableData.map(r => r.count);
            vehicleTypeChart.update();

            hourlyChart.data.datasets[0].data = generateRandomData(24, 20, 150);
            hourlyChart.update();

            trendChart.data.datasets[0].data = [1200, 1350, 1400, 1500, 1450, 1600, 1706];
            trendChart.update();
        }

        // Export Report
        function exportReport(format) {
            showLoading();
            
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const vehicleType = document.getElementById('vehicleType').value;

            // Simulate export (in real app, call backend API)
            setTimeout(() => {
                hideLoading();
                
                if (format === 'pdf') {
                    alert(`Export PDF berhasil!\nPeriode: ${startDate} - ${endDate}\nFile: laporan_kendaraan_${startDate}_${endDate}.pdf`);
                    // In real app: window.open('/api/reports/export/pdf?start=...');
                } else if (format === 'excel') {
                    alert(`Export Excel berhasil!\nPeriode: ${startDate} - ${endDate}\nFile: laporan_kendaraan_${startDate}_${endDate}.xlsx`);
                    // In real app: window.open('/api/reports/export/excel?start=...');
                }
            }, 1500);
        }

        // Helper Functions
        function showLoading() {
            document.getElementById('loadingOverlay').classList.add('active');
        }

        function hideLoading() {
            document.getElementById('loadingOverlay').classList.remove('active');
        }

        function getLast7Days() {
            const days = [];
            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                days.push(date.toLocaleDateString('id-ID', { day: '2-digit', month: 'short' }));
            }
            return days;
        }

        function generateRandomData(length, min, max) {
            return Array.from({length}, () => Math.floor(Math.random() * (max - min + 1)) + min);
        }
    </script>
</body>
</html>