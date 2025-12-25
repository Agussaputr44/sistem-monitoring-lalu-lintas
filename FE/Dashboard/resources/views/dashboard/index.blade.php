<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YO-vehicle Dashboard + Live Stream</title>
    
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
            background: linear-gradient(135deg, #e5dedeff 0%, #ffffffff 100%);
            min-height: 100vh;
        }

        /* Sidebar */
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

        .header-right {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        /* LIVE STREAM CARD - FEATURED! */
        .stream-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
            margin-bottom: 30px;
            border: 2px solid #667eea;
        }

        .stream-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .stream-header h5 {
            font-size: 18px;
            font-weight: 700;
            color: #333;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .live-badge {
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .stream-status {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #666;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #1cc88a;
            animation: blink 1.5s infinite;
        }

        .status-dot.offline {
            background: #e74a3b;
            animation: none;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .video-container {
            position: relative;
            width: 100%;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }

        .video-container img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
        }

        .video-placeholder {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: white;
        }

        .video-placeholder i {
            font-size: 64px;
            margin-bottom: 15px;
            opacity: 0.5;
        }

        .stream-controls {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }

        .btn-stream {
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-stream:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .btn-stream.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-stream.secondary {
            background: #f8f9fa;
            color: #666;
        }

        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        .stat-card.primary::before { background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); }
        .stat-card.success::before { background: linear-gradient(180deg, #1cc88a 0%, #17a673 100%); }
        .stat-card.warning::before { background: linear-gradient(180deg, #f6c23e 0%, #dda20a 100%); }

        .stat-card-header {
            font-size: 14px;
            color: #888;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-card-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }

        .stat-card-label {
            font-size: 13px;
            color: #999;
        }

        /* Chart Container */
        .chart-wrapper {
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

        .chart-card h5 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }

        .chart-container {
            height: 280px;
            position: relative;
        }

        /* Vehicle Sidebar */
        .vehicle-sidebar {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .vehicle-sidebar h5 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }

        .vehicle-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .vehicle-item:last-child {
            border-bottom: none;
        }

        .vehicle-info h6 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }

        .vehicle-info p {
            margin: 5px 0 0;
            font-size: 12px;
            color: #999;
        }

        .vehicle-count {
            font-size: 20px;
            font-weight: bold;
            color: #667eea;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            .main-content {
                margin-left: 0;
            }
            .chart-wrapper {
                grid-template-columns: 1fr;
            }
        }
        body.dark-mode {
    background: #1e1e2f;
    color: #eaeaea;
}

body.dark-mode .sidebar {
    background: #2b2b3c;
    color: white;
}

body.dark-mode .sidebar-menu a {
    color: #ccc;
}

body.dark-mode .sidebar-menu a.active,
body.dark-mode .sidebar-menu a:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    color: white;
}

body.dark-mode .main-content,
body.dark-mode .chart-card,
body.dark-mode .stat-card,
body.dark-mode .vehicle-sidebar,
body.dark-mode .stream-card {
    background: #2b2b3c;
    color: #eaeaea;
    box-shadow: 0 2px 8px rgba(255,255,255,0.05);
}

body.dark-mode .top-header {
    background: #2b2b3c;
    color: #eaeaea;
}

    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-brand">
            <h3><i class="fas fa-traffic-light"></i> YO-vehicle</h3>
            <small style="color: #999;">Admin</small>
        </div>
        
        <ul class="sidebar-menu">
            <li>
                <a href="#" class="active">
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
                <a href="/dashboard/settings">
                    <i class="fas fa-cog"></i>
                    <span>Pengaturan</span>
                </a>
            </li>
        </ul>

        <div class="sidebar-user">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">A</div>
            <div class="sidebar-user-info">
                <h6>Rizqo SP</h6>
                <p>Administrator</p>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Top Header -->
        <div class="top-header">
            <h4>Dashboard</h4>
            <div class="header-right">
                <button class="btn btn-light" style="border-radius: 10px;">
                    <i class="fas fa-bell"></i>
                </button>
            </div>
        </div>

        <!-- LIVE STREAM SECTION - HERO! -->
        <div class="stream-card">
            <div class="stream-header">
                <h5>
                    <i class="fas fa-video"></i>
                    Live CCTV Stream
                    <span class="live-badge" id="liveBadge">● LIVE</span>
                </h5>
                <div class="stream-status">
                    <div class="status-indicator">
                        <div class="status-dot" id="statusDot"></div>
                        <span id="streamStatus">Connecting...</span>
                    </div>
                    <div class="status-indicator">
                        <i class="fas fa-signal"></i>
                        <span id="streamFps">0 FPS</span>
                    </div>
                </div>
            </div>
            
            <div class="video-container" id="videoContainer">
                <div class="video-placeholder" id="placeholder">
                    <i class="fas fa-video-slash"></i>
                    <p>Menunggu stream dari Python...</p>
                    <small style="opacity: 0.7;">Port: 5001</small>
                </div>
                <img id="streamImage" style="display: none;" alt="Live Stream">
            </div>

            <div class="stream-controls">
                <button class="btn-stream primary" onclick="startStream()">
                    <i class="fas fa-play"></i> Start Stream
                </button>
                <button class="btn-stream secondary" onclick="stopStream()">
                    <i class="fas fa-stop"></i> Stop
                </button>
                <button class="btn-stream secondary" onclick="reconnectStream()">
                    <i class="fas fa-sync-alt"></i> Reconnect
                </button>
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="stat-card-header">
                    <i class="fas fa-calendar-day"></i>
                    Kendaraan Hari Ini
                </div>
                <div class="stat-card-value" id="todayCount">1.7K</div>
                <div class="stat-card-label">Total Kendaraan</div>
            </div>
            
            <div class="stat-card success">
                <div class="stat-card-header">
                    <i class="fas fa-tachometer-alt"></i>
                    Rata-rata Kecepatan
                </div>
                <div class="stat-card-value" id="avgSpeed">66.6 km/h</div>
                <div class="stat-card-label">Jam Padat</div>
            </div>
            
            <div class="stat-card warning">
                <div class="stat-card-header">
                    <i class="fas fa-car"></i>
                    Mobil yang Lewat
                </div>
                <div class="stat-card-value" id="carCount">5</div>
                <div class="stat-card-label">Kendaraan</div>
            </div>
        </div>

        <!-- Charts and Vehicle List -->
        <div class="row">
            <div class="col-lg-8">
                <!-- Line Chart -->
                <div class="chart-card" style="margin-bottom: 20px;">
                    <h5>Grafik Jumlah Kendaraan per Jam</h5>
                    <div class="chart-container">
                        <canvas id="hourlyTrafficChart"></canvas>
                    </div>
                </div>

                <!-- Pie Chart -->
                <div class="chart-card">
                    <h5>Distribusi Jenis Kendaraan</h5>
                    <div class="chart-container">
                        <canvas id="vehicleDistributionChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <!-- Jenis Kendaraan -->
                <div class="vehicle-sidebar">
                    <h5>Jenis Kendaraan</h5>
                    
                    <div class="vehicle-item">
                        <div class="vehicle-info">
                            <h6>Sepeda Motor</h6>
                            <p>1.2k per hari lalu</p>
                        </div>
                        <div class="vehicle-count" id="motorCount">1400</div>
                    </div>

                    <div class="vehicle-item">
                        <div class="vehicle-info">
                            <h6>Mobil</h6>
                            <p>190 per hari lalu</p>
                        </div>
                        <div class="vehicle-count" id="mobilCount">240</div>
                    </div>

                    <div class="vehicle-item">
                        <div class="vehicle-info">
                            <h6>Mobil Pickup</h6>
                            <p>31 per hari lalu</p>
                        </div>
                        <div class="vehicle-count" id="pickupCount">36</div>
                    </div>

                    <div class="vehicle-item">
                        <div class="vehicle-info">
                            <h6>Truk</h6>
                            <p>10 per hari lalu</p>
                        </div>
                        <div class="vehicle-count" id="trukCount">12</div>
                    </div>

                    <div class="vehicle-item">
                        <div class="vehicle-info">
                            <h6>Bus</h6>
                            <p>15 per hari lalu</p>
                        </div>
                        <div class="vehicle-count" id="busCount">18</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        let vehicleDistributionChart;
        let hourlyTrafficChart;
        let streamActive = false;
        let reconnectAttempts = 0;
        let fpsCounter = 0;
        let lastFrameTime = Date.now();

        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            refreshDashboard();
            setInterval(refreshDashboard, 5000);
            
            // Auto-start stream after 1 second
            setTimeout(() => {
                startStream();
            }, 1000);
        });

        // ===== STREAM FUNCTIONS =====
        function startStream() {
            const streamImage = document.getElementById('streamImage');
            const placeholder = document.getElementById('placeholder');
            const statusDot = document.getElementById('statusDot');
            const streamStatus = document.getElementById('streamStatus');
            const liveBadge = document.getElementById('liveBadge');
            
            // Update UI
            streamStatus.textContent = 'Connecting...';
            statusDot.classList.add('offline');
            
            // Set stream URL with cache-busting
            const timestamp = new Date().getTime();
            streamImage.src = `http://localhost:5001/video_feed?t=${timestamp}`;
            
            streamImage.onload = function() {
                streamActive = true;
                placeholder.style.display = 'none';
                streamImage.style.display = 'block';
                statusDot.classList.remove('offline');
                streamStatus.textContent = 'Connected';
                liveBadge.style.display = 'inline-block';
                reconnectAttempts = 0;
                
                // Calculate FPS
                updateFPS();
                
                console.log('✅ Stream connected successfully!');
            };
            
            streamImage.onerror = function() {
                streamActive = false;
                placeholder.style.display = 'block';
                streamImage.style.display = 'none';
                statusDot.classList.add('offline');
                streamStatus.textContent = 'Connection Failed';
                liveBadge.style.display = 'none';
                
                // Auto-reconnect
                if (reconnectAttempts < 5) {
                    reconnectAttempts++;
                    console.log(`⚠️ Reconnecting... (Attempt ${reconnectAttempts}/5)`);
                    setTimeout(startStream, 3000);
                } else {
                    streamStatus.textContent = 'Offline - Check Python App';
                }
            };
        }

        function stopStream() {
            const streamImage = document.getElementById('streamImage');
            const placeholder = document.getElementById('placeholder');
            const statusDot = document.getElementById('statusDot');
            const streamStatus = document.getElementById('streamStatus');
            const liveBadge = document.getElementById('liveBadge');
            
            streamImage.src = '';
            streamActive = false;
            placeholder.style.display = 'block';
            streamImage.style.display = 'none';
            statusDot.classList.add('offline');
            streamStatus.textContent = 'Stopped';
            liveBadge.style.display = 'none';
            document.getElementById('streamFps').textContent = '0 FPS';
            
            console.log('⏹️ Stream stopped');
        }

        function reconnectStream() {
            console.log('🔄 Manual reconnect...');
            reconnectAttempts = 0;
            stopStream();
            setTimeout(startStream, 500);
        }

        function updateFPS() {
            if (!streamActive) return;
            
            const now = Date.now();
            const timeDiff = (now - lastFrameTime) / 1000;
            const fps = timeDiff > 0 ? (1 / timeDiff).toFixed(1) : 0;
            
            document.getElementById('streamFps').textContent = `${fps} FPS`;
            lastFrameTime = now;
            
            setTimeout(updateFPS, 1000);
        }

        // ===== CHART INITIALIZATION =====
        function initializeCharts() {
            const ctx2 = document.getElementById('hourlyTrafficChart').getContext('2d');
            hourlyTrafficChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: Array.from({length: 24}, (_, i) => `${i}:00`),
                    datasets: [{
                        label: 'Total Kendaraan',
                        data: new Array(24).fill(0),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: { 
                        y: { 
                            beginAtZero: true,
                            grid: { color: '#f0f0f0' }
                        },
                        x: { grid: { display: false } }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            const ctx1 = document.getElementById('vehicleDistributionChart').getContext('2d');
            vehicleDistributionChart = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Motor', 'Mobil', 'Pickup', 'Truk', 'Bus'],
                    datasets: [{
                        data: [1400, 240, 36, 12, 18],
                        backgroundColor: ['#667eea', '#1cc88a', '#f6c23e', '#e74a3b', '#36b9cc']
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
        }

        function refreshDashboard() {
            fetch('/dashboard/data', { credentials: 'same-origin' })
                .then(response => response.json())
                .then(data => {
                    updateDashboardData(data);
                })
                .catch(error => console.error('Error:', error));
        }

        function updateDashboardData(data) {
            document.getElementById('todayCount').textContent = formatNumber(data.today_total || 0);
            
            const speedStats = data.speed_statistics || [];
            const totalSpeed = speedStats.reduce((sum, item) => sum + parseFloat(item.avg_speed || 0), 0);
            const avgSpeed = speedStats.length > 0 ? (totalSpeed / speedStats.length).toFixed(1) : 0;
            document.getElementById('avgSpeed').textContent = avgSpeed + ' km/h';

            const distribution = data.today_distribution || [];
            distribution.forEach(item => {
                const type = item.vehicle_type.toLowerCase();
                if (type.includes('motor')) {
                    document.getElementById('motorCount').textContent = item.count;
                } else if (type.includes('mobil') || type.includes('car')) {
                    document.getElementById('mobilCount').textContent = item.count;
                    document.getElementById('carCount').textContent = item.count;
                } else if (type.includes('pickup')) {
                    document.getElementById('pickupCount').textContent = item.count;
                } else if (type.includes('truk') || type.includes('truck')) {
                    document.getElementById('trukCount').textContent = item.count;
                } else if (type.includes('bus')) {
                    document.getElementById('busCount').textContent = item.count;
                }
            });

            updateHourlyChart(data.hourly_data || []);
            updateVehicleDistributionChart(data.today_distribution || []);
        }

        function updateHourlyChart(hourlyData) {
            const hourlyCount = new Array(24).fill(0);
            hourlyData.forEach(data => {
                const hour = parseInt(data.hour, 10);
                if (hour >= 0 && hour < 24) {
                    hourlyCount[hour] = parseInt(data.count || 0, 10);
                }
            });
            hourlyTrafficChart.data.datasets[0].data = hourlyCount;
            hourlyTrafficChart.update();
        }

        function updateVehicleDistributionChart(distribution) {
            const labels = distribution.map(item => item.vehicle_type);
            const counts = distribution.map(item => item.count || 0);
            vehicleDistributionChart.data.labels = labels;
            vehicleDistributionChart.data.datasets[0].data = counts;
            vehicleDistributionChart.update();
        }

        function formatNumber(num) {
            if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        }
        // === THEME SWITCHER ===
const themeToggle = document.getElementById('toggleTheme');
const currentTheme = localStorage.getItem('theme');

if (currentTheme === 'dark') {
    document.body.classList.add('dark-mode');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
}

themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    themeToggle.innerHTML = isDark 
        ? '<i class="fas fa-sun"></i>' 
        : '<i class="fas fa-moon"></i>';
});

    </script>
    
</body>
</html>