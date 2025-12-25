<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;

class VehicleDetection extends Model
{
    use HasFactory;

    protected $fillable = [
        'vehicle_type',
        'speed',
        'detected_at',
        'location',
        'confidence',
        'track_id',
        'additional_data'
    ];

    protected $casts = [
        'detected_at' => 'datetime',
        'speed' => 'decimal:1',
        'confidence' => 'decimal:2',
        'additional_data' => 'array'
    ];

    /**
     * Scope untuk filter berdasarkan tanggal
     */
    public function scopeToday($query)
    {
        return $query->whereDate('detected_at', Carbon::today());
    }

    public function scopeThisWeek($query)
    {
        return $query->whereBetween('detected_at', [
            Carbon::now()->startOfWeek(),
            Carbon::now()->endOfWeek()
        ]);
    }

    public function scopeThisMonth($query)
    {
        return $query->whereMonth('detected_at', Carbon::now()->month)
                    ->whereYear('detected_at', Carbon::now()->year);
    }

    public function scopeByVehicleType($query, $type)
    {
        return $query->where('vehicle_type', $type);
    }

    public function scopeByLocation($query, $location)
    {
        return $query->where('location', $location);
    }

    /**
     * Get hourly statistics
     */
    public static function getHourlyStats($date = null)
    {
        $date = $date ? Carbon::parse($date) : Carbon::today();
        
        return self::whereDate('detected_at', $date)
            ->selectRaw('
                HOUR(detected_at) as hour,
                vehicle_type,
                COUNT(*) as count,
                AVG(speed) as avg_speed,
                MAX(speed) as max_speed
            ')
            ->groupBy('hour', 'vehicle_type')
            ->orderBy('hour')
            ->get();
    }

    /**
     * Get daily statistics for a period
     */
    public static function getDailyStats($days = 7)
    {
        return self::whereBetween('detected_at', [
                Carbon::now()->subDays($days),
                Carbon::now()
            ])
            ->selectRaw('
                DATE(detected_at) as date,
                vehicle_type,
                COUNT(*) as count,
                AVG(speed) as avg_speed,
                MAX(speed) as max_speed
            ')
            ->groupBy('date', 'vehicle_type')
            ->orderBy('date')
            ->get();
    }

    /**
     * Get vehicle type distribution
     */
    public static function getVehicleDistribution($period = 'today')
    {
        $query = self::query();
        
        switch ($period) {
            case 'today':
                $query->today();
                break;
            case 'week':
                $query->thisWeek();
                break;
            case 'month':
                $query->thisMonth();
                break;
        }
        
        return $query->selectRaw('
                vehicle_type,
                COUNT(*) as count,
                AVG(speed) as avg_speed,
                AVG(confidence) as avg_confidence
            ')
            ->groupBy('vehicle_type')
            ->orderBy('count', 'desc')
            ->get();
    }

    /**
     * Get speed statistics by vehicle type
     */
    public static function getSpeedStats()
    {
        return self::selectRaw('
                vehicle_type,
                AVG(speed) as avg_speed,
                MIN(speed) as min_speed,
                MAX(speed) as max_speed,
                COUNT(*) as total_count
            ')
            ->whereNotNull('speed')
            ->where('speed', '>', 0)
            ->groupBy('vehicle_type')
            ->get();
    }
}