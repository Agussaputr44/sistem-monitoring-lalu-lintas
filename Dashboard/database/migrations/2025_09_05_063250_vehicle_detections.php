<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('vehicle_detections', function (Blueprint $table) {
            $table->id();
            $table->string('vehicle_type'); // Sepeda, Mobil, Motor, Truk, Bus
            $table->decimal('speed', 5, 1)->nullable(); // Kecepatan dalam km/h
            $table->timestamp('detected_at'); // Waktu deteksi
            $table->string('location')->default('Bengkalis Traffic Cam'); // Lokasi kamera
            $table->decimal('confidence', 3, 2)->default(0.00); // Confidence score 0.00-1.00
            $table->integer('track_id')->nullable(); // ID tracking dari YOLO
            $table->json('additional_data')->nullable(); // Data tambahan jika diperlukan
            $table->timestamps();

            // Indexes untuk performa query
            $table->index('vehicle_type');
            $table->index('detected_at');
            $table->index('location');
            $table->index(['vehicle_type', 'detected_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('vehicle_detections');
    }
};