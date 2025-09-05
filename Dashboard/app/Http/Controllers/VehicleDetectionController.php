<?php

namespace App\Http\Controllers;

use App\Models\VehicleDetection;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Validator;
use Carbon\Carbon;

class VehicleDetectionController extends Controller
{
    /**
     * Display a listing of vehicle detections
     */
    public function index(Request $request): JsonResponse
    {
        $query = VehicleDetection::query();

        // Filter by date range
        if ($request->has('start_date')) {
            $query->whereDate('detected_at', '>=', $request->start_date);
        }
        
        if ($request->has('end_date')) {
            $query->whereDate('detected_at', '<=', $request->end_date);
        }

        // Filter by vehicle type
        if ($request->has('vehicle_type')) {
            $query->byVehicleType($request->vehicle_type);
        }

        // Filter by location
        if ($request->has('location')) {
            $query->byLocation($request->location);
        }

        // Pagination
        $perPage = $request->get('per_page', 15);
        $detections = $query->orderBy('detected_at', 'desc')->paginate($perPage);

        return response()->json([
            'success' => true,
            'data' => $detections,
            'message' => 'Vehicle detections retrieved successfully'
        ]);
    }

    /**
     * Store a single vehicle detection
     */
    public function store(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'vehicle_type' => 'required|string|max:255',
            'speed' => 'nullable|numeric|min:0|max:200',
            'detected_at' => 'required|date',
            'location' => 'nullable|string|max:255',
            'confidence' => 'nullable|numeric|min:0|max:1',
            'track_id' => 'nullable|integer',
            'additional_data' => 'nullable|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $detection = VehicleDetection::create([
                'vehicle_type' => $request->vehicle_type,
                'speed' => $request->speed,
                'detected_at' => Carbon::parse($request->detected_at),
                'location' => $request->location ?? 'Bengkalis Traffic Cam',
                'confidence' => $request->confidence ?? 0,
                'track_id' => $request->track_id,
                'additional_data' => $request->additional_data
            ]);

            return response()->json([
                'success' => true,
                'data' => $detection,
                'message' => 'Vehicle detection saved successfully'
            ], 201);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to save vehicle detection',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Store multiple vehicle detections in batch
     */
    public function storeBatch(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'detections' => 'required|array|min:1|max:100',
            'detections.*.vehicle_type' => 'required|string|max:255',
            'detections.*.speed' => 'nullable|numeric|min:0|max:200',
            'detections.*.detected_at' => 'required|date',
            'detections.*.location' => 'nullable|string|max:255',
            'detections.*.confidence' => 'nullable|numeric|min:0|max:1',
            'detections.*.track_id' => 'nullable|integer',
            'detections.*.additional_data' => 'nullable|array'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $detections = collect($request->detections)->map(function ($detection) {
                return [
                    'vehicle_type' => $detection['vehicle_type'],
                    'speed' => $detection['speed'] ?? null,
                    'detected_at' => Carbon::parse($detection['detected_at']),
                    'location' => $detection['location'] ?? 'Bengkalis Traffic Cam',
                    'confidence' => $detection['confidence'] ?? 0,
                    'track_id' => $detection['track_id'] ?? null,
                    'additional_data' => $detection['additional_data'] ?? null,
                    'created_at' => now(),
                    'updated_at' => now()
                ];
            });

            VehicleDetection::insert($detections->toArray());

            return response()->json([
                'success' => true,
                'message' => 'Batch vehicle detections saved successfully',
                'count' => count($request->detections)
            ], 201);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to save batch vehicle detections',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Display the specified vehicle detection
     */
    public function show(string $id): JsonResponse
    {
        try {
            $detection = VehicleDetection::findOrFail($id);
            
            return response()->json([
                'success' => true,
                'data' => $detection,
                'message' => 'Vehicle detection retrieved successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Vehicle detection not found'
            ], 404);
        }
    }

    /**
     * Remove the specified vehicle detection
     */
    public function destroy(string $id): JsonResponse
    {
        try {
            $detection = VehicleDetection::findOrFail($id);
            $detection->delete();

            return response()->json([
                'success' => true,
                'message' => 'Vehicle detection deleted successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to delete vehicle detection'
            ], 500);
        }
    }

    /**
     * Get general statistics
     */
    public function statistics(): JsonResponse
    {
        try {
            $today = VehicleDetection::getVehicleDistribution('today');
            $thisWeek = VehicleDetection::getVehicleDistribution('week');
            $thisMonth = VehicleDetection::getVehicleDistribution('month');
            $speedStats = VehicleDetection::getSpeedStats();

            $totalToday = $today->sum('count');
            $totalThisWeek = $thisWeek->sum('count');
            $totalThisMonth = $thisMonth->sum('count');

            return response()->json([
                'success' => true,
                'data' => [
                    'totals' => [
                        'today' => $totalToday,
                        'this_week' => $totalThisWeek,
                        'this_month' => $totalThisMonth
                    ],
                    'distribution' => [
                        'today' => $today,
                        'this_week' => $thisWeek,
                        'this_month' => $thisMonth
                    ],
                    'speed_statistics' => $speedStats,
                    'last_updated' => now()->toDateTimeString()
                ],
                'message' => 'Statistics retrieved successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to retrieve statistics',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get hourly statistics
     */
    public function hourlyStatistics(Request $request): JsonResponse
    {
        try {
            $date = $request->get('date', Carbon::today()->toDateString());
            $hourlyStats = VehicleDetection::getHourlyStats($date);

            // Group by hour for easier frontend consumption
            $groupedStats = $hourlyStats->groupBy('hour')->map(function ($items, $hour) {
                return [
                    'hour' => $hour,
                    'vehicles' => $items->mapWithKeys(function ($item) {
                        return [$item->vehicle_type => [
                            'count' => $item->count,
                            'avg_speed' => round($item->avg_speed, 1),
                            'max_speed' => $item->max_speed
                        ]];
                    })
                ];
            })->values();

            return response()->json([
                'success' => true,
                'data' => [
                    'date' => $date,
                    'hourly_stats' => $groupedStats
                ],
                'message' => 'Hourly statistics retrieved successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to retrieve hourly statistics',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get daily statistics
     */
    public function dailyStatistics(Request $request): JsonResponse
    {
        try {
            $days = $request->get('days', 7);
            $dailyStats = VehicleDetection::getDailyStats($days);

            // Group by date for easier frontend consumption
            $groupedStats = $dailyStats->groupBy('date')->map(function ($items, $date) {
                return [
                    'date' => $date,
                    'vehicles' => $items->mapWithKeys(function ($item) {
                        return [$item->vehicle_type => [
                            'count' => $item->count,
                            'avg_speed' => round($item->avg_speed, 1),
                            'max_speed' => $item->max_speed
                        ]];
                    }),
                    'total' => $items->sum('count')
                ];
            })->values();

            return response()->json([
                'success' => true,
                'data' => [
                    'period_days' => $days,
                    'daily_stats' => $groupedStats
                ],
                'message' => 'Daily statistics retrieved successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to retrieve daily statistics',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get live count (for real-time dashboard updates)
     */
    public function liveCount(Request $request): JsonResponse
    {
        try {
            $minutes = $request->get('minutes', 5); // Default last 5 minutes
            
            $recentDetections = VehicleDetection::where('detected_at', '>=', 
                Carbon::now()->subMinutes($minutes))
                ->selectRaw('
                    vehicle_type,
                    COUNT(*) as count,
                    AVG(speed) as avg_speed
                ')
                ->groupBy('vehicle_type')
                ->get();

            $totalRecent = $recentDetections->sum('count');

            return response()->json([
                'success' => true,
                'data' => [
                    'time_period_minutes' => $minutes,
                    'total_detections' => $totalRecent,
                    'vehicle_counts' => $recentDetections,
                    'timestamp' => now()->toDateTimeString()
                ],
                'message' => 'Live count retrieved successfully'
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to retrieve live count',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}