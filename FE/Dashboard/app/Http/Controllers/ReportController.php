<?php

namespace App\Http\Controllers;

use App\Models\VehicleDetection;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;
use Barryvdh\DomPDF\Facade\Pdf; // composer require barryvdh/laravel-dompdf
use Maatwebsite\Excel\Facades\Excel; // composer require maatwebsite/excel

class ReportController extends Controller
{
    /**
     * Display the report page
     */
    public function index()
    {
        return view('dashboard.reports');
    }

    /**
     * Generate report data (AJAX)
     */
    public function generateReport(Request $request)
    {
        $startDate = $request->input('start_date', Carbon::today());
        $endDate = $request->input('end_date', Carbon::today());
        $vehicleType = $request->input('vehicle_type', null);

        try {
            $query = VehicleDetection::whereBetween('detected_at', [$startDate, $endDate]);
            
            if ($vehicleType) {
                $query->where('vehicle_type', $vehicleType);
            }

            // Total vehicles
            $totalVehicles = $query->count();

            // Average speed
            $avgSpeed = $query->avg('speed') ?? 0;

            // Peak hour (jam tersibuk)
            $peakHour = VehicleDetection::selectRaw('HOUR(detected_at) as hour, COUNT(*) as count')
                ->whereBetween('detected_at', [$startDate, $endDate])
                ->groupBy('hour')
                ->orderByDesc('count')
                ->first();

            // Growth calculation (compare with previous period)
            $periodDays = Carbon::parse($startDate)->diffInDays(Carbon::parse($endDate));
            $previousStartDate = Carbon::parse($startDate)->subDays($periodDays);
            $previousEndDate = Carbon::parse($startDate)->subDay();
            
            $previousTotal = VehicleDetection::whereBetween('detected_at', [$previousStartDate, $previousEndDate])->count();
            
            $growth = 0;
            if ($previousTotal > 0) {
                $growth = (($totalVehicles - $previousTotal) / $previousTotal) * 100;
            }

            // Vehicle type distribution
            $vehicleDistribution = $query->selectRaw('
                    vehicle_type,
                    COUNT(*) as count,
                    AVG(speed) as avg_speed,
                    MIN(speed) as min_speed,
                    MAX(speed) as max_speed
                ')
                ->groupBy('vehicle_type')
                ->get();

            // Hourly data
            $hourlyData = VehicleDetection::selectRaw('
                    HOUR(detected_at) as hour,
                    COUNT(*) as count
                ')
                ->whereBetween('detected_at', [$startDate, $endDate])
                ->groupBy('hour')
                ->orderBy('hour')
                ->get();

            // Daily trend (last 7 days)
            $dailyTrend = VehicleDetection::selectRaw('
                    DATE(detected_at) as date,
                    COUNT(*) as count
                ')
                ->whereBetween('detected_at', [Carbon::now()->subDays(7), Carbon::now()])
                ->groupBy('date')
                ->orderBy('date')
                ->get();

            return response()->json([
                'success' => true,
                'data' => [
                    'total_vehicles' => $totalVehicles,
                    'avg_speed' => round($avgSpeed, 1),
                    'peak_hour' => $peakHour ? sprintf('%02d:00', $peakHour->hour) : '00:00',
                    'growth' => round($growth, 1),
                    'vehicle_distribution' => $vehicleDistribution,
                    'hourly_data' => $hourlyData,
                    'daily_trend' => $dailyTrend,
                    'period' => [
                        'start' => $startDate,
                        'end' => $endDate
                    ]
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to generate report: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Export report to PDF
     */
    public function exportPDF(Request $request)
    {
        $startDate = $request->input('start_date', Carbon::today());
        $endDate = $request->input('end_date', Carbon::today());
        $vehicleType = $request->input('vehicle_type', null);

        try {
            $query = VehicleDetection::whereBetween('detected_at', [$startDate, $endDate]);
            
            if ($vehicleType) {
                $query->where('vehicle_type', $vehicleType);
            }

            $totalVehicles = $query->count();
            $avgSpeed = $query->avg('speed') ?? 0;

            $vehicleDistribution = $query->selectRaw('
                    vehicle_type,
                    COUNT(*) as count,
                    AVG(speed) as avg_speed,
                    MIN(speed) as min_speed,
                    MAX(speed) as max_speed
                ')
                ->groupBy('vehicle_type')
                ->get();

            $data = [
                'title' => 'Laporan Deteksi Kendaraan',
                'period' => Carbon::parse($startDate)->format('d/m/Y') . ' - ' . Carbon::parse($endDate)->format('d/m/Y'),
                'generated_at' => Carbon::now()->format('d/m/Y H:i:s'),
                'total_vehicles' => $totalVehicles,
                'avg_speed' => round($avgSpeed, 1),
                'vehicle_distribution' => $vehicleDistribution
            ];

            $pdf = Pdf::loadView('reports.pdf', $data);
            
            $filename = 'laporan_kendaraan_' . Carbon::parse($startDate)->format('Ymd') . '_' . Carbon::parse($endDate)->format('Ymd') . '.pdf';
            
            return $pdf->download($filename);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to export PDF: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Export report to Excel
     */
    public function exportExcel(Request $request)
    {
        $startDate = $request->input('start_date', Carbon::today());
        $endDate = $request->input('end_date', Carbon::today());
        $vehicleType = $request->input('vehicle_type', null);

        try {
            $query = VehicleDetection::whereBetween('detected_at', [$startDate, $endDate]);
            
            if ($vehicleType) {
                $query->where('vehicle_type', $vehicleType);
            }

            $detections = $query->orderBy('detected_at', 'desc')->get();

            $filename = 'laporan_kendaraan_' . Carbon::parse($startDate)->format('Ymd') . '_' . Carbon::parse($endDate)->format('Ymd') . '.xlsx';

            return Excel::download(new VehicleDetectionExport($detections), $filename);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to export Excel: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get summary statistics
     */
    public function getSummary(Request $request)
    {
        try {
            $today = VehicleDetection::whereDate('detected_at', Carbon::today())->count();
            $week = VehicleDetection::whereBetween('detected_at', [Carbon::now()->startOfWeek(), Carbon::now()->endOfWeek()])->count();
            $month = VehicleDetection::whereMonth('detected_at', Carbon::now()->month)->count();

            return response()->json([
                'success' => true,
                'data' => [
                    'today' => $today,
                    'week' => $week,
                    'month' => $month
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => $e->getMessage()
            ], 500);
        }
    }
}


// ========================================
// EXCEL EXPORT CLASS
// ========================================
namespace App\Exports;

use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;
use Maatwebsite\Excel\Concerns\WithStyles;
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class VehicleDetectionExport implements FromCollection, WithHeadings, WithMapping, WithStyles
{
    protected $detections;

    public function __construct($detections)
    {
        $this->detections = $detections;
    }

    public function collection()
    {
        return $this->detections;
    }

    public function headings(): array
    {
        return [
            'No',
            'Jenis Kendaraan',
            'Kecepatan (km/h)',
            'Tanggal',
            'Waktu',
            'Lokasi',
            'Confidence',
            'Track ID'
        ];
    }

    public function map($detection): array
    {
        static $no = 0;
        $no++;

        return [
            $no,
            $detection->vehicle_type,
            round($detection->speed, 1),
            $detection->detected_at->format('d/m/Y'),
            $detection->detected_at->format('H:i:s'),
            $detection->location,
            round($detection->confidence * 100, 0) . '%',
            $detection->track_id ?? '-'
        ];
    }

    public function styles(Worksheet $sheet)
    {
        return [
            1 => ['font' => ['bold' => true, 'size' => 12]],
        ];
    }
}