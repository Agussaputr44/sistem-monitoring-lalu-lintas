import 'dart:async';
import 'package:dashboard_app/common/constants.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../domain/entities/traffic.dart';
import '../bloc/traffic_bloc.dart';

// --- KONFIGURASI URL STREAM ---
const String _kWorkerApiBaseUrl = 'https://e94d13823346.ngrok-free.app';
// ------------------------------

class TrafficHistoryPage extends StatefulWidget {
  const TrafficHistoryPage({super.key});

  @override
  State<TrafficHistoryPage> createState() => _TrafficHistoryPageState();
}

class _TrafficHistoryPageState extends State<TrafficHistoryPage> {
  DateTimeRange? selectedRange;
  Timer? _refreshTimer;
  final ScrollController _scrollController = ScrollController();
  List<Traffic> _cachedTraffics = [];
  String _selectedTimeRange = 'all';
  String _selectedVehicleType = 'all';

  int _displayedItemCount = 20;
  static const int _itemsPerPage = 20;
  bool _isLoadingMore = false;

  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0x00000000))
      ..setNavigationDelegate(
        NavigationDelegate(
          onWebResourceError: (WebResourceError error) {
            debugPrint('Stream Error: ${error.description}');
          },
        ),
      )
      // TAMBAHKAN HEADER DI SINI
      ..loadRequest(Uri.parse('$_kWorkerApiBaseUrl/video_feed'));
    // Auto-refresh data setiap 5 detik
    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (mounted) {
        context.read<TrafficBloc>().add(FetchTrafficData());
      }
    });

    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      _loadMoreItems();
    }
  }

  void _loadMoreItems() {
    if (!_isLoadingMore) {
      setState(() {
        _isLoadingMore = true;
        _displayedItemCount += _itemsPerPage;
      });

      Future.delayed(const Duration(milliseconds: 300), () {
        if (mounted) {
          setState(() => _isLoadingMore = false);
        }
      });
    }
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _scrollController.dispose();
    // WebView controller tidak perlu didispose secara eksplisit di versi baru
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBackgroundDark,
      appBar: AppBar(
        backgroundColor: kSurfaceDark,
        elevation: 0,
        title: Text("Traffic Monitoring Dashboard", style: kHeading6),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: kSuccessGreen,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: kSuccessGreen.withOpacity(0.5),
                          blurRadius: 4,
                          spreadRadius: 1,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    "Live",
                    style: kSubtitle.copyWith(
                      fontSize: 12,
                      color: kSuccessGreen,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      body: BlocBuilder<TrafficBloc, TrafficState>(
        builder: (context, state) {
          if (state is TrafficLoaded) {
            _cachedTraffics = state.data;
          }

          if (_cachedTraffics.isNotEmpty) {
            final traffics = _filterTraffics(_cachedTraffics);
            return CustomScrollView(
              controller: _scrollController,
              physics: const ClampingScrollPhysics(),
              slivers: [
                SliverPadding(
                  padding: const EdgeInsets.all(16.0),
                  sliver: SliverList(
                    delegate: SliverChildListDelegate([
                      const SizedBox(height: 16),
                      _buildTimeRangeFilter(),
                      _buildMainKpiRow(traffics),
                      const SizedBox(height: 12),
                      // Grid KPI per Tipe Kendaraan (Updated)
                      _buildTypeKpiRow(traffics),
                      const SizedBox(height: 16),
                      // === VIDEO STREAM PLAYER ===
                      _buildVehicleStreamPlayer(),
                      // ===========================
                      const SizedBox(height: 12),
                      // Filter Tipe Kendaraan (Updated)
                      _buildVehicleTypeFilter(),
                      const SizedBox(height: 12),
                      _buildFilterSection(context),
                      const SizedBox(height: 16),
                      _buildVehicleVolumeChart(traffics),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "Riwayat Traffic Terkini",
                            style: kHeading6.copyWith(fontSize: 16),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: kPrimaryTeal.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              "${traffics.length} total",
                              style: kSubtitle.copyWith(
                                fontSize: 11,
                                color: kPrimaryTeal,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                    ]),
                  ),
                ),
                // List Riwayat (Optimized)
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  sliver: _buildOptimizedTrafficList(traffics),
                ),
                const SliverPadding(padding: EdgeInsets.only(bottom: 80)),
              ],
            );
          } else if (state is TrafficError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, color: kDangerRed, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    state.message,
                    style: kBodyText,
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            );
          } else {
            return const Center(
              child: CircularProgressIndicator(color: kPrimaryTeal),
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: kPrimaryTeal,
        onPressed: () {
          context.read<TrafficBloc>().add(FetchTrafficData());
        },
        child: const Icon(Icons.refresh, color: Colors.white),
      ),
    );
  }

  // --- WIDGET VIDEO STREAM ---
  Widget _buildVehicleStreamPlayer() {
    return Card(
      color: kSurfaceDark,
      elevation: 4, // Sedikit lebih menonjol
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Row(
              children: [
                Icon(Icons.videocam, color: kPrimaryTeal, size: 20),
                const SizedBox(width: 8),
                Text(
                  "Live CCTV Stream",
                  style: kHeading6.copyWith(
                    fontSize: 14,
                    color: kTextSecondary,
                  ),
                ),
                const Spacer(),
                // Indikator Live Berkedip
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: kDangerRed,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    "LIVE",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Container Video
          Container(
            height: 220,
            width: double.infinity,
            color: Colors.black,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                '$_kWorkerApiBaseUrl/video_feed',

                headers: const {
                  'ngrok-skip-browser-warning': 'any',
                  'bypass-tunnel-reminder': 'true',
                  'User-Agent': 'Mozilla/5.0',
                },

                fit: BoxFit.contain,
                // Placeholder saat koneksi sedang dibangun
                loadingBuilder: (context, child, loadingProgress) {
                  if (loadingProgress == null) return child;
                  return const Center(child: CircularProgressIndicator());
                },
                // Penanganan jika engine python mati atau error
                errorBuilder: (context, error, stackTrace) {
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: const [
                      Icon(Icons.videocam_off, color: Colors.white24, size: 48),
                      SizedBox(height: 8),
                      Text(
                        "Stream Offline",
                        style: TextStyle(color: Colors.white54),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  List<Traffic> _filterTraffics(List<Traffic> traffics) {
    var filtered = traffics;

    // Filter Waktu
    if (_selectedTimeRange != 'all') {
      final now = DateTime.now();
      DateTime cutoffTime;

      switch (_selectedTimeRange) {
        case '15min':
          cutoffTime = now.subtract(const Duration(minutes: 15));
          break;
        case '30min':
          cutoffTime = now.subtract(const Duration(minutes: 30));
          break;
        case '1hour':
          cutoffTime = now.subtract(const Duration(hours: 1));
          break;
        case '3hours':
          cutoffTime = now.subtract(const Duration(hours: 3));
          break;
        case 'today':
          cutoffTime = DateTime(now.year, now.month, now.day);
          break;
        default:
          cutoffTime = DateTime(2000);
      }
      filtered = filtered
          .where((t) => t.detectedAt.isAfter(cutoffTime))
          .toList();
    }

    // Filter Tipe Kendaraan (Case-Insensitive Comparison)
    if (_selectedVehicleType != 'all') {
      filtered = filtered
          .where((t) => t.vehicleType.toLowerCase() == _selectedVehicleType)
          .toList();
    }

    // Filter Custom Date Range
    if (selectedRange != null) {
      filtered = filtered.where((t) {
        final date = t.detectedAt;
        // Menambahkan buffer 1 hari agar mencakup seluruh tanggal start & end
        return date.isAfter(
              selectedRange!.start.subtract(const Duration(days: 1)),
            ) &&
            date.isBefore(selectedRange!.end.add(const Duration(days: 1)));
      }).toList();
    }

    // Reset pagination jika hasil filter sedikit
    if (filtered.length < _displayedItemCount) {
      _displayedItemCount = 20;
    }

    return filtered;
  }

  Widget _buildMainKpiRow(List<Traffic> traffics) {
    final total = traffics.length;
    final avgSpeed = traffics.isNotEmpty
        ? traffics.map((t) => t.speedKmph).reduce((a, b) => a + b) / total
        : 0.0;
    final avgConfidence = traffics.isNotEmpty
        ? traffics.map((t) => t.confidence).reduce((a, b) => a + b) / total
        : 0.0;

    return Row(
      children: [
        Expanded(
          child: _buildKpiCard(
            "Total Kendaraan",
            "$total",
            Icons.directions_car,
            kPrimaryTeal,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildKpiCard(
            "Avg Speed",
            "${avgSpeed.toStringAsFixed(1)} km/h",
            Icons.speed,
            kSecondaryBlue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildKpiCard(
            "Confidence",
            "${(avgConfidence * 100).toStringAsFixed(0)}%",
            Icons.verified,
            kSuccessGreen,
          ),
        ),
      ],
    );
  }

  // --- GRID KPI TIPE KENDARAAN (UPDATED) ---
  Widget _buildTypeKpiRow(List<Traffic> traffics) {
    final grouped = <String, int>{};
    for (var t in traffics) {
      // Gunakan lowercase untuk pengelompokan yang konsisten
      final type = t.vehicleType.toLowerCase();
      grouped[type] = (grouped[type] ?? 0) + 1;
    }

    // Data 5 Tipe Kendaraan
    final vehicleData = [
      {
        'type': 'mobil',
        'label': 'MOBIL',
        'icon': Icons.directions_car,
        'color': Colors.lightBlueAccent,
      },
      {
        'type': 'motor',
        'label': 'MOTOR',
        'icon': Icons.motorcycle,
        'color': Colors.purpleAccent,
      },
      {
        'type': 'truk',
        'label': 'TRUK',
        'icon': Icons.local_shipping,
        'color': Colors.redAccent,
      },
      {
        'type': 'pickup',
        'label': 'PICKUP',
        'icon': Icons.front_loader,
        'color': Colors.orangeAccent,
      },
      {
        'type': 'bus',
        'label': 'BUS',
        'icon': Icons.directions_bus,
        'color': Colors.greenAccent,
      },
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 2.2,
      ),
      itemCount: vehicleData.length,
      itemBuilder: (context, index) {
        final data = vehicleData[index];
        // Ambil jumlah berdasarkan key lowercase
        final count = grouped[data['type']] ?? 0;
        return _buildCompactKpiCard(
          data['label'] as String,
          "$count",
          data['icon'] as IconData,
          data['color'] as Color,
        );
      },
    );
  }

  Widget _buildKpiCard(String label, String value, IconData icon, Color color) {
    return Card(
      color: kSurfaceDark,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 4),
            Text(
              label,
              style: kSubtitle.copyWith(fontSize: 11),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              value,
              style: kHeading6.copyWith(color: color, fontSize: 14),
              maxLines: 1,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCompactKpiCard(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Card(
      color: kSurfaceDark,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Row(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: kSubtitle.copyWith(fontSize: 11)),
                  Text(
                    value,
                    style: kHeading6.copyWith(color: color, fontSize: 16),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeRangeFilter() {
    final timeRanges = {
      'all': 'Semua Waktu',
      '15min': '15 Menit Terakhir',
      '30min': '30 Menit Terakhir',
      '1hour': '1 Jam Terakhir',
      '3hours': '3 Jam Terakhir',
      'today': 'Hari Ini',
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Rentang Waktu",
          style: kSubtitle.copyWith(fontSize: 12, color: Colors.white54),
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: timeRanges.entries.map((entry) {
              final isSelected = _selectedTimeRange == entry.key;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: FilterChip(
                  selected: isSelected,
                  label: Text(
                    entry.value,
                    style: kSubtitle.copyWith(
                      fontSize: 12,
                      color: isSelected ? Colors.white : Colors.white70,
                    ),
                  ),
                  backgroundColor: kSurfaceDark,
                  selectedColor: kPrimaryTeal.withOpacity(0.3),
                  checkmarkColor: kPrimaryTeal,
                  side: BorderSide(
                    color: isSelected ? kPrimaryTeal : Colors.white24,
                    width: 1,
                  ),
                  onSelected: (selected) {
                    setState(() {
                      _selectedTimeRange = entry.key;
                      if (entry.key != 'all') {
                        selectedRange = null;
                      }
                    });
                  },
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  // --- FILTER CHIP TIPE KENDARAAN (UPDATED) ---
  Widget _buildVehicleTypeFilter() {
    final vehicleTypes = {
      'all': {'label': 'Semua', 'icon': Icons.dashboard, 'color': kTextPrimary},
      'mobil': {
        'label': 'Mobil',
        'icon': Icons.directions_car,
        'color': Colors.lightBlueAccent,
      },
      'motor': {
        'label': 'Motor',
        'icon': Icons.motorcycle,
        'color': Colors.purpleAccent,
      },
      'truk': {
        'label': 'Truk',
        'icon': Icons.local_shipping,
        'color': Colors.redAccent,
      },
      'pickup': {
        'label': 'Pickup',
        'icon': Icons.front_loader,
        'color': Colors.orangeAccent,
      },
      'bus': {
        'label': 'Bus',
        'icon': Icons.directions_bus,
        'color': Colors.greenAccent,
      },
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Filter Jenis Kendaraan",
          style: kSubtitle.copyWith(fontSize: 12, color: Colors.white54),
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: vehicleTypes.entries.map((entry) {
              final isSelected = _selectedVehicleType == entry.key;
              final data = entry.value;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: FilterChip(
                  selected: isSelected,
                  avatar: Icon(
                    data['icon'] as IconData,
                    size: 16,
                    // Warna icon putih jika dipilih, warna asli jika tidak
                    color: isSelected ? Colors.white : (data['color'] as Color),
                  ),
                  label: Text(
                    data['label'] as String,
                    style: kSubtitle.copyWith(
                      fontSize: 12,
                      color: isSelected ? Colors.white : Colors.white70,
                    ),
                  ),
                  backgroundColor: kSurfaceDark,
                  selectedColor: (data['color'] as Color).withOpacity(0.4),
                  checkmarkColor: Colors.white,
                  side: BorderSide(
                    color: isSelected ? data['color'] as Color : Colors.white24,
                    width: 1,
                  ),
                  onSelected: (selected) {
                    setState(() => _selectedVehicleType = entry.key);
                  },
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildFilterSection(BuildContext context) {
    final rangeText = selectedRange == null
        ? "Pilih rentang tanggal kustom"
        : "${DateFormat('dd MMM').format(selectedRange!.start)} - ${DateFormat('dd MMM').format(selectedRange!.end)}";

    return InkWell(
      onTap: () async {
        final now = DateTime.now();
        final picked = await showDateRangePicker(
          context: context,
          firstDate: DateTime(now.year - 1),
          lastDate: DateTime(now.year + 1),
          currentDate: now,
          saveText: "Terapkan",
          builder: (context, child) => Theme(
            data: ThemeData.dark().copyWith(
              colorScheme: const ColorScheme.dark(
                primary: kPrimaryTeal,
                surface: kSurfaceDark,
              ),
            ),
            child: child!,
          ),
        );
        if (picked != null) {
          setState(() {
            selectedRange = picked;
            _selectedTimeRange = 'all';
          });
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: kSurfaceDark,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: kPrimaryTeal.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, color: kPrimaryTeal, size: 18),
            const SizedBox(width: 8),
            Text(rangeText, style: kSubtitle.copyWith(fontSize: 13)),
            const Spacer(),
            if (selectedRange != null)
              GestureDetector(
                onTap: () => setState(() => selectedRange = null),
                child: Icon(Icons.close, color: kDangerRed, size: 18),
              )
            else
              const Icon(Icons.arrow_drop_down, color: Colors.white70),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleVolumeChart(List<Traffic> traffics) {
    if (traffics.isEmpty) {
      return const SizedBox.shrink();
    }

    final grouped = <int, int>{};
    for (var t in traffics) {
      final hour = t.detectedAt.hour;
      grouped[hour] = (grouped[hour] ?? 0) + 1;
    }

    final sortedEntries = grouped.entries.toList()
      ..sort((a, b) => a.key.compareTo(b.key));

    final maxY = sortedEntries.isNotEmpty
        ? sortedEntries
              .map((e) => e.value)
              .reduce((a, b) => a > b ? a : b)
              .toDouble()
        : 1.0;

    return Card(
      color: kSurfaceDark,
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Volume per Jam (Berdasarkan Filter)",
              style: kHeading6.copyWith(fontSize: 14, color: kTextSecondary),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 180,
              child: LineChart(
                LineChartData(
                  maxY: maxY + (maxY * 0.1),
                  minY: 0,
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: maxY > 5
                        ? (maxY / 4).ceilToDouble()
                        : 1,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: Colors.white.withOpacity(0.05),
                      strokeWidth: 1,
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(
                              "${value.toInt()}:00",
                              style: kSubtitle.copyWith(
                                fontSize: 10,
                                color: Colors.white24,
                              ),
                            ),
                          );
                        },
                        reservedSize: 24,
                        interval:
                            2, // Tampilkan label setiap 2 jam agar tidak penuh
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: maxY > 5 ? (maxY / 4).ceilToDouble() : 1,
                        reservedSize: 28,
                        getTitlesWidget: (value, meta) {
                          if (value == 0) return const SizedBox.shrink();
                          return Text(
                            value.toInt().toString(),
                            style: kSubtitle.copyWith(
                              fontSize: 10,
                              color: Colors.white24,
                            ),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border(
                      bottom: BorderSide(
                        color: Colors.white.withOpacity(0.1),
                        width: 1,
                      ),
                      left: BorderSide(
                        color: Colors.white.withOpacity(0.1),
                        width: 1,
                      ),
                    ),
                  ),
                  lineBarsData: [
                    LineChartBarData(
                      spots: sortedEntries
                          .map(
                            (e) => FlSpot(e.key.toDouble(), e.value.toDouble()),
                          )
                          .toList(),
                      isCurved: true,
                      gradient: LinearGradient(
                        colors: [kPrimaryTeal, kPrimaryTeal.withOpacity(0.5)],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      ),
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: FlDotData(
                        show: true,
                        getDotPainter: (spot, percent, bar, index) {
                          return FlDotCirclePainter(
                            radius: 3,
                            color: kPrimaryTeal,
                            strokeWidth: 0,
                          );
                        },
                      ),
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            kPrimaryTeal.withOpacity(0.15),
                            kPrimaryTeal.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 📋 Optimized Traffic List with Infinite Scroll
  Widget _buildOptimizedTrafficList(List<Traffic> traffics) {
    final displayCount = _displayedItemCount > traffics.length
        ? traffics.length
        : _displayedItemCount;

    final hasMore = displayCount < traffics.length;

    return SliverList(
      delegate: SliverChildBuilderDelegate((context, index) {
        // Loading indicator di akhir list
        if (index == displayCount) {
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 20),
            child: Center(
              child: Column(
                children: [
                  SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: kPrimaryTeal,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    "Memuat riwayat lainnya...",
                    style: kSubtitle.copyWith(fontSize: 11),
                  ),
                ],
              ),
            ),
          );
        }

        final t = traffics[index];
        // Helper functions untuk icon dan warna (Updated)
        final iconData = _getVehicleIcon(t.vehicleType);
        final iconColor = _getVehicleColor(t.vehicleType);

        return Card(
          color: kSurfaceDark,
          elevation: 1,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            dense: true,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 4,
            ),
            leading: CircleAvatar(
              backgroundColor: iconColor.withOpacity(0.15),
              child: Icon(iconData, color: iconColor, size: 20),
            ),
            title: Row(
              children: [
                Text(
                  t.vehicleType.toUpperCase(),
                  style: kBodyText.copyWith(
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    color: iconColor,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  "•  ${t.speedKmph.toStringAsFixed(1)} km/h",
                  style: kBodyText.copyWith(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
            subtitle: Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Row(
                children: [
                  Icon(Icons.location_on, size: 12, color: kTextSecondary),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      t.location,
                      style: kSubtitle.copyWith(fontSize: 11),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Text(
                    DateFormat('dd/MM HH:mm:ss').format(t.detectedAt.toLocal()),
                    style: kSubtitle.copyWith(
                      fontSize: 11,
                      color: kTextSecondary,
                    ),
                  ),
                ],
              ),
            ),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text("Confidence", style: kSubtitle.copyWith(fontSize: 9)),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: kSuccessGreen.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    "${(t.confidence * 100).toStringAsFixed(0)}%",
                    style: kSubtitle.copyWith(
                      color: kSuccessGreen,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      }, childCount: hasMore ? displayCount + 1 : displayCount),
    );
  }

  // --- HELPER ICON & WARNA (UPDATED) ---
  IconData _getVehicleIcon(String type) {
    switch (type.toLowerCase()) {
      case 'truk':
        return Icons.local_shipping;
      case 'pickup':
        return Icons.front_loader; // Icon yang cocok untuk pickup
      case 'motor':
        return Icons.motorcycle;
      case 'bus':
        return Icons.directions_bus;
      default:
        return Icons.directions_car; // Mobil & default
    }
  }

  Color _getVehicleColor(String type) {
    switch (type.toLowerCase()) {
      case 'truk':
        return Colors.redAccent;
      case 'pickup':
        return Colors.orangeAccent;
      case 'motor':
        return Colors.purpleAccent;
      case 'bus':
        return Colors.greenAccent;
      case 'mobil':
        return Colors.lightBlueAccent;
      default:
        return kTextSecondary;
    }
  }
}
