<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>Riwayat Kendaraan - YO-vehicle</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ffffffff 0%, #764ba2 100%);
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

        /* Filter Card */
        .filter-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 25px;
        }

        .filter-card h5 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
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

        .btn-filter {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-filter:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-reset {
            background: #f8f9fa;
            color: #666;
            border: 1px solid #e0e0e0;
            padding: 10px 25px;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .btn-reset:hover {
            background: #e9ecef;
        }

        /* Data Table Card */
        .table-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }

        .table-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }

        .table-card-header h5 {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }

        .table-stats {
            display: flex;
            gap: 20px;
            font-size: 13px;
        }

        .table-stats span {
            background: #f8f9fa;
            padding: 5px 12px;
            border-radius: 20px;
            color: #666;
        }

        /* Custom Table */
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

        .custom-table thead th:first-child {
            border-radius: 10px 0 0 0;
        }

        .custom-table thead th:last-child {
            border-radius: 0 10px 0 0;
        }

        .custom-table tbody tr {
            transition: all 0.3s;
        }

        .custom-table tbody tr:hover {
            background: #f8f9fa;
        }

        .custom-table tbody td {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
            color: #333;
        }

        /* Vehicle Badges */
        .vehicle-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-mobil {
            background: rgba(102, 126, 234, 0.15);
            color: #667eea;
        }

        .badge-motor {
            background: rgba(28, 200, 138, 0.15);
            color: #1cc88a;
        }

        .badge-pickup {
            background: rgba(246, 194, 62, 0.15);
            color: #f6c23e;
        }

        .badge-truk {
            background: rgba(231, 74, 59, 0.15);
            color: #e74a3b;
        }

        .badge-bus {
            background: rgba(54, 185, 204, 0.15);
            color: #36b9cc;
        }

        .badge-sepeda {
            background: rgba(133, 135, 150, 0.15);
            color: #858796;
        }

        /* Speed Indicator */
        .speed-badge {
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
        }

        .speed-low {
            background: rgba(28, 200, 138, 0.15);
            color: #1cc88a;
        }

        .speed-medium {
            background: rgba(246, 194, 62, 0.15);
            color: #f6c23e;
        }

        .speed-high {
            background: rgba(231, 74, 59, 0.15);
            color: #e74a3b;
        }

        /* Confidence Bar */
        .confidence-bar {
            width: 80px;
            height: 6px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
        }

        .confidence-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }

        .confidence-high {
            background: linear-gradient(90deg, #1cc88a, #17a673);
        }

        .confidence-medium {
            background: linear-gradient(90deg, #f6c23e, #dda20a);
        }

        .confidence-low {
            background: linear-gradient(90deg, #e74a3b, #be2617);
        }

        /* Action Buttons */
        .btn-action {
            padding: 6px 12px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-action-info {
            background: rgba(54, 185, 204, 0.15);
            color: #36b9cc;
        }

        .btn-action-info:hover {
            background: rgba(54, 185, 204, 0.3);
        }

        .btn-action-danger {
            background: rgba(231, 74, 59, 0.15);
            color: #e74a3b;
        }

        .btn-action-danger:hover {
            background: rgba(231, 74, 59, 0.3);
        }

        /* Pagination */
        .custom-pagination {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 25px;
        }

        .custom-pagination a,
        .custom-pagination span {
            padding: 8px 15px;
            border-radius: 8px;
            text-decoration: none;
            color: #666;
            font-size: 14px;
            transition: all 0.3s;
        }

        .custom-pagination a:hover {
            background: #f8f9fa;
        }

        .custom-pagination .active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        /* Empty State */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
        }

        .empty-state i {
            font-size: 64px;
            color: #e0e0e0;
            margin-bottom: 20px;
        }

        .empty-state h5 {
            color: #999;
            margin-bottom: 10px;
        }

        .empty-state p {
            color: #bbb;
            font-size: 14px;
        }

        /* Back Button */
        .btn-back {
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-back:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
            }
            .main-content {
                margin-left: 0;
            }
            .table-card {
                overflow-x: auto;
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
    <!-- Sidebar - Same as Dashboard -->
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
                <a href="/dashboard/history" class="active">
                    <i class="fas fa-history"></i>
                    <span>Riwayat Kendaraan</span>
                </a>
            
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
            <div>
                <h4><i class="fas fa-history"></i> Riwayat Deteksi Kendaraan</h4>
                <p>Data deteksi kendaraan dari sistem YOLO</p>
            </div>
            <a href="/" class="btn-back">
                <i class="fas fa-arrow-left"></i> Kembali ke Dashboard
            </a>
        </div>

        <!-- Filter Card -->
        <div class="filter-card">
            <h5><i class="fas fa-filter"></i> Filter Data</h5>
            <form method="GET" action="{{ route('dashboard.history') }}">
                <div class="row g-3">
                    <div class="col-md-3">
                        <label class="form-label">Jenis Kendaraan</label>
                        <select name="vehicle_type" class="form-select">
                            <option value="">Semua Kendaraan</option>
                            @foreach($vehicleTypes as $type)
                                <option value="{{ $type }}" {{ request('vehicle_type') == $type ? 'selected' : '' }}>
                                    {{ $type }}
                                </option>
                            @endforeach
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Tanggal Dari</label>
                        <input type="date" name="date_from" class="form-control" value="{{ request('date_from') }}">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Tanggal Sampai</label>
                        <input type="date" name="date_to" class="form-control" value="{{ request('date_to') }}">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">&nbsp;</label>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn-filter flex-grow-1">
                                <i class="fas fa-search"></i> Filter
                            </button>
                            <a href="{{ route('dashboard.history') }}" class="btn-reset">
                                <i class="fas fa-redo"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </form>
        </div>

        <!-- Data Table Card -->
        <div class="table-card">
            <div class="table-card-header">
                <h5><i class="fas fa-table"></i> Data Deteksi Kendaraan</h5>
                <div class="table-stats">
                    <span><i class="fas fa-database"></i> Total: {{ $detections->total() }} deteksi</span>
                    <span><i class="fas fa-file-alt"></i> Halaman: {{ $detections->currentPage() }} / {{ $detections->lastPage() }}</span>
                </div>
            </div>

            @if($detections->count() > 0)
                <div style="overflow-x: auto;">
                    <table class="custom-table">
                        <thead>
                            <tr>
                                <th width="5%">#</th>
                                <th width="15%">Jenis Kendaraan</th>
                                <th width="12%">Kecepatan</th>
                                <th width="15%">Waktu Deteksi</th>
                                <th width="15%">Lokasi</th>
                                <th width="12%">Confidence</th>
                                <th width="10%">Track ID</th>
                                <th width="16%">Aksi</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($detections as $index => $detection)
                                <tr>
                                    <td><strong>{{ $detections->firstItem() + $index }}</strong></td>
                                    <td>
                                        <span class="vehicle-badge 
                                            @if(str_contains(strtolower($detection->vehicle_type), 'mobil') || str_contains(strtolower($detection->vehicle_type), 'car')) badge-mobil
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'motor')) badge-motor
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'pickup')) badge-pickup
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'truk') || str_contains(strtolower($detection->vehicle_type), 'truck')) badge-truk
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'bus')) badge-bus
                                            @else badge-sepeda
                                            @endif">
                                            @if(str_contains(strtolower($detection->vehicle_type), 'mobil') || str_contains(strtolower($detection->vehicle_type), 'car'))
                                                <i class="fas fa-car"></i>
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'motor'))
                                                <i class="fas fa-motorcycle"></i>
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'pickup'))
                                                <i class="fas fa-truck-pickup"></i>
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'truk') || str_contains(strtolower($detection->vehicle_type), 'truck'))
                                                <i class="fas fa-truck"></i>
                                            @elseif(str_contains(strtolower($detection->vehicle_type), 'bus'))
                                                <i class="fas fa-bus"></i>
                                            @else
                                                <i class="fas fa-bicycle"></i>
                                            @endif
                                            {{ $detection->vehicle_type }}
                                        </span>
                                    </td>
                                    <td>
                                        @if($detection->speed)
                                            <span class="speed-badge 
                                                @if($detection->speed < 30) speed-low
                                                @elseif($detection->speed < 60) speed-medium
                                                @else speed-high
                                                @endif">
                                                <i class="fas fa-tachometer-alt"></i>
                                                {{ number_format($detection->speed, 1) }} km/h
                                            </span>
                                        @else
                                            <span style="color: #999;">-</span>
                                        @endif
                                    </td>
                                    <td>
                                        <div>
                                            <strong style="color: #333;">{{ $detection->detected_at->format('d/m/Y') }}</strong><br>
                                            <small style="color: #999;">{{ $detection->detected_at->format('H:i:s') }}</small>
                                        </div>
                                    </td>
                                    <td>
                                        <small style="color: #666;">
                                            <i class="fas fa-map-marker-alt" style="color: #667eea;"></i>
                                            {{ $detection->location }}
                                        </small>
                                    </td>
                                    <td>
                                        @if($detection->confidence > 0)
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <div class="confidence-bar">
                                                    <div class="confidence-fill 
                                                        @if($detection->confidence >= 0.65) confidence-high
                                                        @elseif($detection->confidence >= 0.45) confidence-medium
                                                        @else confidence-low
                                                        @endif" 
                                                        style="width: {{ $detection->confidence * 100 }}%">
                                                    </div>
                                                </div>
                                                <small style="color: #666; font-weight: 600;">{{ round($detection->confidence * 100) }}%</small>
                                            </div>
                                        @else
                                            <span style="color: #999;">-</span>
                                        @endif
                                    </td>
                                    <td>
                                        @if($detection->track_id)
                                            <code style="background: #f8f9fa; padding: 4px 8px; border-radius: 6px; font-size: 12px; color: #667eea;">#{{ $detection->track_id }}</code>
                                        @else
                                            <span style="color: #999;">-</span>
                                        @endif
                                    </td>
                                    <td>
                                        <div style="display: flex; gap: 6px;">
                                            <button class="btn-action btn-action-info" onclick="showDetails({{ $detection->id }})" title="Detail">
                                                <i class="fas fa-info-circle"></i>
                                            </button>
                                            <button class="btn-action btn-action-danger" onclick="confirmDelete({{ $detection->id }})" title="Hapus">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                <div class="custom-pagination">
                    {{ $detections->withQueryString()->links() }}
                </div>
            @else
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h5>Tidak ada data deteksi</h5>
                    <p>Coba ubah filter atau periksa kembali sistem deteksi.</p>
                </div>
            @endif
        </div>
    </div>

    <!-- Detail Modal -->
    <div class="modal fade" id="detailModal" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content" style="border-radius: 15px; border: none;">
                <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px 15px 0 0;">
                    <h5 class="modal-title"><i class="fas fa-info-circle"></i> Detail Deteksi Kendaraan</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="detailModalBody" style="padding: 30px;">
                    <!-- Content will be loaded here -->
                </div>
                <div class="modal-footer" style="border: none;">
                    <button type="button" class="btn-reset" data-bs-dismiss="modal">Tutup</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        function showDetails(detectionId) {
            document.getElementById('detailModalBody').innerHTML = 
                '<div class="text-center"><i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #667eea;"></i><p style="margin-top: 15px; color: #999;">Memuat detail...</p></div>';
            
            const modal = new bootstrap.Modal(document.getElementById('detailModal'));
            modal.show();
            
            // Simulate API call (in real app, fetch from server)
            setTimeout(() => {
                document.getElementById('detailModalBody').innerHTML = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                        <div>
                            <h6 style="color: #667eea; margin-bottom: 15px; font-weight: 600;"><i class="fas fa-info-circle"></i> Informasi Dasar</h6>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                                <p style="margin-bottom: 10px;"><strong>ID Deteksi:</strong> #${detectionId}</p>
                                <p style="margin-bottom: 10px;"><strong>Status:</strong> <span style="background: rgba(28, 200, 138, 0.15); color: #1cc88a; padding: 4px 10px; border-radius: 15px; font-size: 12px; font-weight: 600;">Berhasil</span></p>
                                <p style="margin-bottom: 0;"><strong>Proses:</strong> Real-time Detection</p>
                            </div>
                        </div>
                        <div>
                            <h6 style="color: #667eea; margin-bottom: 15px; font-weight: 600;"><i class="fas fa-cogs"></i> Metadata Teknis</h6>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                                <p style="margin-bottom: 10px;"><strong>Algoritma:</strong> YOLOv8</p>
                                <p style="margin-bottom: 10px;"><strong>Model:</strong> yolov8s.pt</p>
                                <p style="margin-bottom: 0;"><strong>Framework:</strong> Ultralytics</p>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 20px;">
                        <h6 style="color: #667eea; margin-bottom: 15px; font-weight: 600;"><i class="fas fa-chart-line"></i> Statistik</h6>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px;">
                            <p style="margin-bottom: 0;"><strong>Tracking:</strong> ByteTrack Algorithm | <strong>IOU Threshold:</strong> 0.4 | <strong>Confidence:</strong> 0.25+</p>
                        </div>
                    </div>
                `;
            }, 500);
        }

        function confirmDelete(detectionId) {
            if (confirm('Apakah Anda yakin ingin menghapus data deteksi ini?')) {
                // In real app, send DELETE request to server
                alert('Fitur hapus belum diimplementasikan. ID: ' + detectionId);
            }
        }

        // Auto-set date range on load
        document.addEventListener('DOMContentLoaded', function() {
            const dateFrom = document.querySelector('input[name="date_from"]');
            const dateTo = document.querySelector('input[name="date_to"]');
            
            // Set default to last 7 days if no filter
            if (!dateFrom.value && !dateTo.value) {
                const today = new Date();
                dateTo.value = today.toISOString().split('T')[0];
                
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                dateFrom.value = weekAgo.toISOString().split('T')[0];
            }
        });
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
