<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\VehicleDetectionController;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

Route::middleware('api')->group(function () {
    // Vehicle Detection API Routes
    Route::prefix('vehicle-detections')->group(function () {
        Route::get('/', [VehicleDetectionController::class, 'index']);
        Route::post('/', [VehicleDetectionController::class, 'store']);
        Route::post('/batch', [VehicleDetectionController::class, 'storeBatch']);
        Route::get('/{id}', [VehicleDetectionController::class, 'show']);
        Route::delete('/{id}', [VehicleDetectionController::class, 'destroy']);
    });

    // Statistics Routes
    Route::get('/vehicle-statistics', [VehicleDetectionController::class, 'statistics']);
    Route::get('/vehicle-statistics/hourly', [VehicleDetectionController::class, 'hourlyStatistics']);
    Route::get('/vehicle-statistics/daily', [VehicleDetectionController::class, 'dailyStatistics']);

    // Real-time data for dashboard
    Route::get('/vehicle-live-count', [VehicleDetectionController::class, 'liveCount']);
});