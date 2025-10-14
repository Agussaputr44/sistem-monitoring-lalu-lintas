<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Detection Dashboard - Bengkalis Traffic</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        body {
            background-color: #f8f9fa;
        }
        .card {
            border: none;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
            margin-bottom: 1.5rem;
        }
        .card-header {
            background-color: #f8f9fc;
            border-bottom: 1px solid #e3e6f0;
        }
        .stat-card {
            background: linear-gradient(45deg, #4e73df, #224abe);
            color: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .stat-card.success {
            background: linear-gradient(45deg, #1cc88a, #17a673);
        }
        .stat-card.warning {
            background: linear-gradient(45deg, #f6c23e, #dda20a);
        }
        .stat-card.info {
            background: linear-gradient(45deg, #36b9cc, #258391);
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #28a745;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .chart-container {
            position: relative;
            height: 300px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center py-3">
                    <h1 class="h3 mb-0 text-gray-800">
                        <i class="fas fa-traffic-light text-primary"></i>
                        Vehicle Detection Dashboard
                    </h1>
                    <div class="text-muted">
                        <span class="live-indicator"></span>
                        Live Data | Last Update: <span id="lastUpdate"><?php echo e(now()->format('H:i:s')); ?></span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-xl-3 col-md-6">
                <div class="stat-card">
                    <div class="card-body">
                        <h5><i class="fas fa-calendar-day"></i> Hari Ini</h5>
                        <h2 id="todayCount"><?php echo e($totalToday); ?></h2>
                        <p class="mb-0">Total Kendaraan</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="stat-card success">
                    <div class="card-body">
                        <h5><i class="fas fa-calendar-week"></i> Minggu Ini</h5>
                        <h2 id="weekCount"><?php echo e($totalWeek); ?></h2>
                        <p class="mb-0">Total Kendaraan</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="stat-card warning">
                    <div class="card-body">
                        <h5><i class="fas fa-calendar-alt"></i> Bulan Ini</h5>
                        <h2 id="monthCount"><?php echo e($totalMonth); ?></h2>
                        <p class="mb-0">Total Kendaraan</p>
                    </div>
                </div>
            </div>
            <div class="col-xl-3 col-md-6">
                <div class="stat-card info">
                    <div class="card-body">
                        <h5><i class="fas fa-clock"></i> Live Data</h5>
                        <h2 id="liveCount">0</h2>
                        <p class="mb-0">Deteksi Terbaru</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row mb-4">
            <!-- Vehicle Distribution Chart -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-chart-pie"></i> Distribusi Kendaraan Hari Ini
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="vehicleDistributionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Hourly Traffic Chart -->
            <div class="col-lg-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-chart-line"></i> Lalu Lintas Per Jam
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="hourlyTrafficChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Speed Statistics and Recent Detections -->
        <div class="row mb-4">
            <!-- Speed Statistics -->
            <div class="col-lg-8">
                <div class="card">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-tachometer-alt"></i> Statistik Kecepatan
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-bordered" id="speedStatsTable">
                                <thead class="bg-light">
                                    <tr>
                                        <th>Jenis Kendaraan</th>
                                        <th>Rata-rata (km/h)</th>
                                        <th>Minimum (km/h)</th>
                                        <th>Maximum (km/h)</th>
                                        <th>Total Deteksi</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Data akan diisi via JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Detections -->
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-clock"></i> Deteksi Terbaru (5 menit)
                        </h6>
                    </div>
                    <div class="card-body">
                        <div id="recentDetections">
                            <!-- Data akan diisi via JavaScript -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Action Buttons -->
        <div class="row">
            <div class="col-12 text-center">
                <a href="<?php echo e(route('dashboard.history')); ?>" class="btn btn-primary btn-lg me-3">
                    <i class="fas fa-history"></i> Lihat History Lengkap
                </a>
                <button class="btn btn-success btn-lg" onclick="refreshDashboard()">
                    <i class="fas fa-sync-alt"></i> Refresh Data
                </button>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // Chart variables
        let vehicleDistributionChart;
        let hourlyTrafficChart;

        // Initial data
        const todayStats = <?php echo json_encode($todayStats, 15, 512) ?>;
        
        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            refreshDashboard();
            
            
            setInterval(refreshDashboard, 5000);
        });

        function initializeCharts() {
            // Vehicle Distribution Chart
            const ctx1 = document.getElementById('vehicleDistributionChart').getContext('2d');
            vehicleDistributionChart = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: todayStats.map(item => item.vehicle_type),
                    datasets: [{
                        data: todayStats.map(item => item.count),
                        backgroundColor: [
                            '#4e73df',
                            '#1cc88a',
                            '#f6c23e',
                            '#e74a3b',
                            '#36b9cc'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // Hourly Traffic Chart
            const ctx2 = document.getElementById('hourlyTrafficChart').getContext('2d');
            hourlyTrafficChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: Array.from({length: 24}, (_, i) => i + ':00'),
                    datasets: [{
                        label: 'Total Kendaraan',
                        data: new Array(24).fill(0),
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }

        function refreshDashboard() {

            showLoading();
            fetch('/dashboard/data')
                .then(response => response.json())
                .then(data => {
                    updateDashboardData(data);
                    document.getElementById('lastUpdate').textContent = data.timestamp;
                })
                .catch(error => {
                    console.error('Error refreshing dashboard:', error);
                });
        }
            function showLoading() {
                document.getElementById('lastUpdate').innerHTML = 
                    '<i class="fas fa-spinner fa-spin text-primary"></i> updating...';
}

        function updateDashboardData(data) {
            // Update live count
            const liveTotal = data.recent_detections.reduce((sum, item) => sum + item.count, 0);
            document.getElementById('liveCount').textContent = liveTotal;
            document.getElementById('todayCount').textContent = data.today_total;
            document.getElementById('weekCount').textContent = data.week_total;
            document.getElementById('monthCount').textContent = data.month_total;


            // Update recent detections display
            updateRecentDetections(data.recent_detections);

            // Update speed statistics table
            updateSpeedStatsTable(data.speed_statistics);

            // Update hourly chart
            updateHourlyChart(data.hourly_data);

            updateVehicleDistributionChart(data.today_distribution);
        }

        function updateRecentDetections(recentDetections) {
            const container = document.getElementById('recentDetections');
            
            if (recentDetections.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">Tidak ada deteksi dalam 5 menit terakhir</p>';
                return;
            }

            let html = '';
            recentDetections.forEach(detection => {
                const avgSpeed = detection.avg_speed ? parseFloat(detection.avg_speed).toFixed(1) : '0.0';
                html += `
                    <div class="d-flex justify-content-between align-items-center border-bottom py-2">
                        <div>
                            <strong>${detection.vehicle_type}</strong>
                            <br>
                            <small class="text-muted">${avgSpeed} km/h rata-rata</small>
                        </div>
                        <span class="badge bg-primary">${detection.count}</span>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        function updateSpeedStatsTable(speedStats) {
            const tbody = document.querySelector('#speedStatsTable tbody');
            
            if (speedStats.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Tidak ada data kecepatan</td></tr>';
                return;
            }

            let html = '';
            speedStats.forEach(stat => {
                html += `
                    <tr>
                        <td><strong>${stat.vehicle_type}</strong></td>
                        <td>${parseFloat(stat.avg_speed).toFixed(1)}</td>
                        <td>${parseFloat(stat.min_speed).toFixed(1)}</td>
                        <td>${parseFloat(stat.max_speed).toFixed(1)}</td>
                        <td><span class="badge bg-info">${stat.total_count}</span></td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
        }

        function updateHourlyChart(hourlyData) {
            // Group data by hour
            const hourlyCount = new Array(24).fill(0);
            
            hourlyData.forEach(data => {
                const hour = parseInt(data.hour);
                hourlyCount[hour] += data.count;
            });

            // Update chart data
            hourlyTrafficChart.data.datasets[0].data = hourlyCount;
            hourlyTrafficChart.update();
        }

        function updateVehicleDistributionChart(todayDistribution) {
            const labels = todayDistribution.map(item => item.vehicle_type);
            const counts = todayDistribution.map(item => item.count);

            vehicleDistributionChart.data.labels = labels;
            vehicleDistributionChart.data.datasets[0].data = counts;
            vehicleDistributionChart.update();
}


        // Vehicle type icons mapping
        function getVehicleIcon(vehicleType) {
            const icons = {
                'Mobil': 'fas fa-car',
                'Motor': 'fas fa-motorcycle', 
                'Sepeda': 'fas fa-bicycle',
                'Truk': 'fas fa-truck',
                'Bus': 'fas fa-bus'
            };
            return icons[vehicleType] || 'fas fa-vehicle';
        }

        // Export data function
        function exportData() {
            window.open('/dashboard/export', '_blank');
        }

        // Show loading state
        function showLoading() {
            document.getElementById('lastUpdate').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Memuat...';
        }
    </script>
</body>
</html><?php /**PATH C:\Coolyeah\Final Project\monitoring-lalu-lintas\Dashboard\resources\views/dashboard/index.blade.php ENDPATH**/ ?>