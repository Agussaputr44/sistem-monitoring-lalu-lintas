<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\DashboardController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
*/

Route::get('/', function () {
    return redirect('/dashboard');
});
Route::post('/dashboard/reset', [DashboardController::class, 'resetData'])->name('dashboard.reset');
Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
Route::get('/dashboard/data', [DashboardController::class, 'getDashboardData'])->name('dashboard.data');
Route::get('/dashboard/history', [DashboardController::class, 'history'])->name('dashboard.history');

// Report Routes
Route::prefix('dashboard/reports')->group(function () {
    Route::get('/', [ReportController::class, 'index'])->name('dashboard.reports');
    Route::post('/generate', [ReportController::class, 'generateReport'])->name('reports.generate');
    Route::get('/export/pdf', [ReportController::class, 'exportPDF'])->name('reports.export.pdf');
    Route::get('/export/excel', [ReportController::class, 'exportExcel'])->name('reports.export.excel');
    Route::get('/summary', [ReportController::class, 'getSummary'])->name('reports.summary');
});
Route::get('/dashboard/settings', [DashboardController::class, 'settings'])->name('dashboard.settings');