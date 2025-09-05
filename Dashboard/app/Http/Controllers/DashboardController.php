<?php

namespace App\Http\Controllers;

use App\Models\VehicleDetection;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Carbon\Carbon;

class DashboardController extends Controller
{
    /**
     * Display the dashboard view
     */
    public function index()
    {
        $todayStats = VehicleDetection::getVehicleDistribution('today');
        $weekStats = VehicleDetection::getVehicleDistribution('week');
        $monthStats = VehicleDetection::getVehicleDistribution('month');
        
        $totalToday = $todayStats->sum('count');
        $totalWeek = $weekStats->sum('count');
        $totalMonth = $monthStats->sum('count');

        return view('dashboard.index', compact(
            'todayStats', 'weekStats', 'monthStats', 
            'totalToday', 'totalWeek', 'totalMonth'
        ));
    }

    /**
     * Get dashboard data for AJAX updates
     */
    public function getDashboardData(): JsonResponse
    {
        try {
            // Hitung ulang total per hari/minggu/bulan
        $todayStats = VehicleDetection::getVehicleDistribution('today');
        $weekStats = VehicleDetection::getVehicleDistribution('week');
        $monthStats = VehicleDetection::getVehicleDistribution('month');
        
        $totalToday = $todayStats->sum('count');
        $totalWeek = $weekStats->sum('count');
        $totalMonth = $monthStats->sum('count');
            // Real-time counts (last 5 minutes)
            $recentDetections = VehicleDetection::where('detected_at', '>=', 
                Carbon::now()->subMinutes(5))
                ->selectRaw('
                    vehicle_type,
                    COUNT(*) as count,
                    AVG(speed) as avg_speed
                ')
                ->groupBy('vehicle_type')
                ->get();

            // Today's hourly data
            $hourlyData = VehicleDetection::getHourlyStats(Carbon::today());
            
            // Speed statistics
            $speedStats = VehicleDetection::getSpeedStats();

            // Daily trend (last 7 days)
            $dailyTrend = VehicleDetection::getDailyStats(7);

            return response()->json([
                'today_distribution' => $todayStats,
                'today_total' => $totalToday,
                'week_total' => $totalWeek,
                'month_total' => $totalMonth,
                'recent_detections' => $recentDetections,
                'hourly_data' => $hourlyData,
                'speed_statistics' => $speedStats,
                'daily_trend' => $dailyTrend,
                'timestamp' => now()->format('H:i:s')
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'error' => 'Failed to load dashboard data',
                'message' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display vehicle detection history
     */
    public function history(Request $request)
    {
        $query = VehicleDetection::query();

        // Apply filters
        if ($request->has('vehicle_type') && $request->vehicle_type != '') {
            $query->where('vehicle_type', $request->vehicle_type);
        }

        if ($request->has('date_from') && $request->date_from != '') {
            $query->whereDate('detected_at', '>=', $request->date_from);
        }

        if ($request->has('date_to') && $request->date_to != '') {
            $query->whereDate('detected_at', '<=', $request->date_to);
        }

        $detections = $query->orderBy('detected_at', 'desc')->paginate(20);
        $vehicleTypes = VehicleDetection::distinct()->pluck('vehicle_type');

        return view('dashboard.history', compact('detections', 'vehicleTypes'));
    }
}