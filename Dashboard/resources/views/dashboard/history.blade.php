<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Detection History - Bengkalis Traffic</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <style>
        body {
            background-color: #f8f9fa;
        }
        .card {
            border: none;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        }
        .vehicle-badge {
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
        }
        .speed-indicator {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .speed-low { background-color: #d4edda; color: #155724; }
        .speed-medium { background-color: #fff3cd; color: #856404; }
        .speed-high { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center py-3">
                    <div>
                        <h1 class="h3 mb-0 text-gray-800">
                            <i class="fas fa-history text-primary"></i>
                            History Deteksi Kendaraan
                        </h1>
                        <p class="text-muted">Data deteksi kendaraan dari sistem YOLO</p>
                    </div>
                    <div>
                        <a href="{{ route('dashboard') }}" class="btn btn-primary">
                            <i class="fas fa-dashboard"></i> Kembali ke Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filters -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-filter"></i> Filter Data
                        </h6>
                    </div>
                    <div class="card-body">
                        <form method="GET" action="{{ route('dashboard.history') }}">
                            <div class="row">
                                <div class="col-md-3">
                                    <label for="vehicle_type" class="form-label">Jenis Kendaraan</label>
                                    <select name="vehicle_type" id="vehicle_type" class="form-select">
                                        <option value="">Semua Kendaraan</option>
                                        @foreach($vehicleTypes as $type)
                                            <option value="{{ $type }}" {{ request('vehicle_type') == $type ? 'selected' : '' }}>
                                                {{ $type }}
                                            </option>
                                        @endforeach
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label for="date_from" class="form-label">Tanggal Dari</label>
                                    <input type="date" name="date_from" id="date_from" class="form-control" 
                                           value="{{ request('date_from') }}">
                                </div>
                                <div class="col-md-3">
                                    <label for="date_to" class="form-label">Tanggal Sampai</label>
                                    <input type="date" name="date_to" id="date_to" class="form-control" 
                                           value="{{ request('date_to') }}">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">&nbsp;</label>
                                    <div class="d-grid">
                                        <button type="submit" class="btn btn-primary">
                                            <i class="fas fa-search"></i> Filter
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="m-0 font-weight-bold text-primary">
                            <i class="fas fa-table"></i> Data Deteksi Kendaraan
                        </h6>
                        <div class="text-muted">
                            Total: {{ $detections->total() }} deteksi
                        </div>
                    </div>
                    <div class="card-body">
                        @if($detections->count() > 0)
                            <div class="table-responsive">
                                <table class="table table-bordered table-hover">
                                    <thead class="bg-light">
                                        <tr>
                                            <th width="5%">#</th>
                                            <th width="15%">Jenis Kendaraan</th>
                                            <th width="12%">Kecepatan</th>
                                            <th width="15%">Waktu Deteksi</th>
                                            <th width="15%">Lokasi</th>
                                            <th width="10%">Confidence</th>
                                            <th width="10%">Track ID</th>
                                            <th width="18%">Detail</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        @foreach($detections as $index => $detection)
                                            <tr>
                                                <td>{{ $detections->firstItem() + $index }}</td>
                                                <td>
                                                    <span class="vehicle-badge badge 
                                                        @if($detection->vehicle_type == 'Mobil') bg-primary
                                                        @elseif($detection->vehicle_type == 'Motor') bg-success
                                                        @elseif($detection->vehicle_type == 'Sepeda') bg-info
                                                        @elseif($detection->vehicle_type == 'Truk') bg-warning
                                                        @else bg-secondary
                                                        @endif">
                                                        @if($detection->vehicle_type == 'Mobil')
                                                            <i class="fas fa-car"></i>
                                                        @elseif($detection->vehicle_type == 'Motor')
                                                            <i class="fas fa-motorcycle"></i>
                                                        @elseif($detection->vehicle_type == 'Sepeda')
                                                            <i class="fas fa-bicycle"></i>
                                                        @elseif($detection->vehicle_type == 'Truk')
                                                            <i class="fas fa-truck"></i>
                                                        @elseif($detection->vehicle_type == 'Bus')
                                                            <i class="fas fa-bus"></i>
                                                        @endif
                                                        {{ $detection->vehicle_type }}
                                                    </span>
                                                </td>
                                                <td>
                                                    @if($detection->speed)
                                                        <span class="speed-indicator 
                                                            @if($detection->speed < 30) speed-low
                                                            @elseif($detection->speed < 60) speed-medium
                                                            @else speed-high
                                                            @endif">
                                                            {{ number_format($detection->speed, 1) }} km/h
                                                        </span>
                                                    @else
                                                        <span class="text-muted">-</span>
                                                    @endif
                                                </td>
                                                <td>
                                                    <div>
                                                        <strong>{{ $detection->detected_at->format('d/m/Y') }}</strong>
                                                        <br>
                                                        <small class="text-muted">{{ $detection->detected_at->format('H:i:s') }}</small>
                                                    </div>
                                                </td>
                                                <td>
                                                    <small class="text-muted">
                                                        <i class="fas fa-map-marker-alt"></i>
                                                        {{ $detection->location }}
                                                    </small>
                                                </td>
                                                <td>
                                                    @if($detection->confidence > 0)
                                                        <div class="progress" style="height: 20px;">
                                                            <div class="progress-bar 
                                                                @if($detection->confidence >= 0.8) bg-success
                                                                @elseif($detection->confidence >= 0.6) bg-warning
                                                                @else bg-danger
                                                                @endif" 
                                                                role="progressbar" 
                                                                style="width: {{ $detection->confidence * 100 }}%">
                                                                {{ round($detection->confidence * 100) }}%
                                                            </div>
                                                        </div>
                                                    @else
                                                        <span class="text-muted">-</span>
                                                    @endif
                                                </td>
                                                <td>
                                                    @if($detection->track_id)
                                                        <code>#{{ $detection->track_id }}</code>
                                                    @else
                                                        <span class="text-muted">-</span>
                                                    @endif
                                                </td>
                                                <td>
                                                    <div class="d-flex gap-1">
                                                        <button class="btn btn-sm btn-outline-info" 
                                                                onclick="showDetails({{ $detection->id }})"
                                                                title="Detail">
                                                            <i class="fas fa-info-circle"></i>
                                                        </button>
                                                        @if($detection->additional_data)
                                                            <button class="btn btn-sm btn-outline-secondary" 
                                                                    onclick="showAdditionalData({{ json_encode($detection->additional_data) }})"
                                                                    title="Data Tambahan">
                                                                <i class="fas fa-code"></i>
                                                            </button>
                                                        @endif
                                                    </div>
                                                </td>
                                            </tr>
                                        @endforeach
                                    </tbody>
                                </table>
                            </div>

                            <!-- Pagination -->
                            <div class="d-flex justify-content-center">
                                {{ $detections->withQueryString()->links() }}
                            </div>
                        @else
                            <div class="text-center py-5">
                                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                                <h5 class="text-muted">Tidak ada data deteksi</h5>
                                <p class="text-muted">Coba ubah filter atau periksa kembali sistem deteksi.</p>
                            </div>
                        @endif
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Detail Modal -->
    <div class="modal fade" id="detailModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Detail Deteksi Kendaraan</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body" id="detailModalBody">
                    <!-- Content will be loaded here -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Additional Data Modal -->
    <div class="modal fade" id="additionalDataModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Data Tambahan</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <pre id="additionalDataContent" class="bg-light p-3 rounded"></pre>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Tutup</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        function showDetails(detectionId) {
            // In a real implementation, you would fetch detailed data via AJAX
            document.getElementById('detailModalBody').innerHTML = 
                '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Memuat detail...</div>';
            
            const modal = new bootstrap.Modal(document.getElementById('detailModal'));
            modal.show();
            
            // Simulate API call
            setTimeout(() => {
                document.getElementById('detailModalBody').innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Informasi Dasar</h6>
                            <p><strong>ID Deteksi:</strong> #${detectionId}</p>
                            <p><strong>Status:</strong> <span class="badge bg-success">Berhasil</span></p>
                        </div>
                        <div class="col-md-6">
                            <h6>Metadata</h6>
                            <p><strong>Algoritma:</strong> YOLOv8</p>
                            <p><strong>Model:</strong> yolov8n.pt</p>
                        </div>
                    </div>
                `;
            }, 500);
        }

        function showAdditionalData(data) {
            document.getElementById('additionalDataContent').textContent = JSON.stringify(data, null, 2);
            const modal = new bootstrap.Modal(document.getElementById('additionalDataModal'));
            modal.show();
        }

        // Auto-set today's date as default if no dates are selected
        document.addEventListener('DOMContentLoaded', function() {
            const dateFrom = document.getElementById('date_from');
            const dateTo = document.getElementById('date_to');
            
            if (!dateFrom.value && !dateTo.value) {
                const today = new Date().toISOString().split('T')[0];
                dateTo.value = today;
                
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                dateFrom.value = weekAgo.toISOString().split('T')[0];
            }
        });
    </script>
</body>
</html>