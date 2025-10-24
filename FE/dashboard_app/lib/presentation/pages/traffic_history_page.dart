import 'dart:async';
import 'package:dashboard_app/common/constants.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../domain/entities/traffic.dart';
import '../bloc/traffic_bloc.dart';

class TrafficHistoryPage extends StatefulWidget {
  const TrafficHistoryPage({super.key});

  @override
  State<TrafficHistoryPage> createState() => _TrafficHistoryPageState();
}

class _TrafficHistoryPageState extends State<TrafficHistoryPage> {
  DateTimeRange? selectedRange;
  Timer? _refreshTimer;
  final ScrollController _scrollController = ScrollController();
  List<Traffic> _cachedTraffics = []; // Cache data terakhir
  String _selectedTimeRange = 'all'; // 'all', '15min', '30min', '1hour', '3hours', 'today'
  String _selectedVehicleType = 'all'; // 'all', 'car', 'truck', 'motorcycle', 'bus'
  
  // Infinite scroll variables
  int _displayedItemCount = 20; // Mulai dengan 20 item
  static const int _itemsPerPage = 20;
  bool _isLoadingMore = false;

  @override
  void initState() {
    super.initState();
    // Auto refresh setiap 5 detik
    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (mounted) {
        context.read<TrafficBloc>().add(FetchTrafficData());
      }
    });
    
    // Scroll listener untuk infinite scroll
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200) {
      _loadMoreItems();
    }
  }

  void _loadMoreItems() {
    if (!_isLoadingMore) {
      setState(() {
        _isLoadingMore = true;
        _displayedItemCount += _itemsPerPage;
      });
      
      // Simulate loading delay
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
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kBackgroundDark,
      appBar: AppBar(
        backgroundColor: kSurfaceDark,
        elevation: 0,
        title: Text(
          "Traffic Monitoring Dashboard",
          style: kHeading6,
        ),
        actions: [
          // Indicator auto-refresh
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
                    style: kSubtitle.copyWith(fontSize: 12, color: kSuccessGreen),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      body: BlocBuilder<TrafficBloc, TrafficState>(
        builder: (context, state) {
          // Update cache saat data baru masuk
          if (state is TrafficLoaded) {
            _cachedTraffics = state.data;
          }
          
          // Selalu tampilkan data dari cache (tidak ada loading state)
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
                      _buildMainKpiRow(traffics),
                      const SizedBox(height: 12),
                      _buildTypeKpiRow(traffics),
                      const SizedBox(height: 16),
                      _buildTimeRangeFilter(),
                      const SizedBox(height: 12),
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
                            "Riwayat Traffic",
                            style: kHeading6.copyWith(fontSize: 16),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
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
                // Optimized list with lazy loading
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
            // Initial loading state - hanya muncul sekali di awal
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

  // Filter traffics berdasarkan date range, time range, dan vehicle type
  List<Traffic> _filterTraffics(List<Traffic> traffics) {
    var filtered = traffics;

    // Filter by time range
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

      filtered = filtered.where((t) => t.detectedAt.isAfter(cutoffTime)).toList();
    }

    // Filter by vehicle type
    if (_selectedVehicleType != 'all') {
      filtered = filtered.where((t) => t.vehicleType == _selectedVehicleType).toList();
    }

    // Filter by custom date range (dari date picker)
    if (selectedRange != null) {
      filtered = filtered.where((t) {
        final date = t.detectedAt;
        return date.isAfter(selectedRange!.start.subtract(const Duration(days: 1))) &&
            date.isBefore(selectedRange!.end.add(const Duration(days: 1)));
      }).toList();
    }

    // Reset displayed item count when filter changes
    if (filtered.length < _displayedItemCount) {
      _displayedItemCount = 20;
    }

    return filtered;
  }

  // 🧮 KPI Utama (Optimized)
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

  // 🚗 KPI per Jenis Kendaraan (Optimized Grid)
  Widget _buildTypeKpiRow(List<Traffic> traffics) {
    final grouped = <String, int>{};
    for (var t in traffics) {
      grouped[t.vehicleType] = (grouped[t.vehicleType] ?? 0) + 1;
    }

    final vehicleData = [
      {'type': 'car', 'icon': Icons.directions_car, 'color': Colors.lightBlueAccent},
      {'type': 'truck', 'icon': Icons.local_shipping, 'color': Colors.orange},
      {'type': 'motorcycle', 'icon': Icons.motorcycle, 'color': Colors.purpleAccent},
      {'type': 'bus', 'icon': Icons.directions_bus, 'color': Colors.greenAccent},
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
        final count = grouped[data['type']] ?? 0;
        return _buildCompactKpiCard(
          (data['type'] as String).toUpperCase(),
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

  Widget _buildCompactKpiCard(String label, String value, IconData icon, Color color) {
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

  // 🕐 Time Range Filter
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
                      // Reset custom date range jika memilih time range
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

  // 🚗 Vehicle Type Filter
  Widget _buildVehicleTypeFilter() {
    final vehicleTypes = {
      'all': {'label': 'Semua', 'icon': Icons.dashboard, 'color': kTextPrimary},
      'car': {'label': 'Mobil', 'icon': Icons.directions_car, 'color': Colors.lightBlueAccent},
      'truck': {'label': 'Truk', 'icon': Icons.local_shipping, 'color': Colors.orange},
      'motorcycle': {'label': 'Motor', 'icon': Icons.motorcycle, 'color': Colors.purpleAccent},
      'bus': {'label': 'Bus', 'icon': Icons.directions_bus, 'color': Colors.greenAccent},
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Jenis Kendaraan",
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
                    size: 18,
                    color: isSelected ? data['color'] as Color : Colors.white54,
                  ),
                  label: Text(
                    data['label'] as String,
                    style: kSubtitle.copyWith(
                      fontSize: 12,
                      color: isSelected ? Colors.white : Colors.white70,
                    ),
                  ),
                  backgroundColor: kSurfaceDark,
                  selectedColor: (data['color'] as Color).withOpacity(0.2),
                  checkmarkColor: data['color'] as Color,
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

  // 📅 Filter Section (Custom Date Range)
  Widget _buildFilterSection(BuildContext context) {
    final rangeText = selectedRange == null
        ? "Pilih rentang tanggal"
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
          setState(() => selectedRange = picked);
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

  // 📈 Line Chart Volume Kendaraan per Jam - Minimalist Design
Widget _buildVehicleVolumeChart(List<Traffic> traffics) {
  if (traffics.isEmpty) {
    return const SizedBox.shrink();
  }

  // Group by hour
  final grouped = <int, int>{};
  for (var t in traffics) {
    final hour = t.detectedAt.hour;
    grouped[hour] = (grouped[hour] ?? 0) + 1;
  }

  final sortedEntries = grouped.entries.toList()
    ..sort((a, b) => a.key.compareTo(b.key));
  final maxY = sortedEntries.map((e) => e.value).reduce((a, b) => a > b ? a : b).toDouble();

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
            "Volume per Jam",
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
                  horizontalInterval: maxY > 5 ? (maxY / 4).ceilToDouble() : 1,
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
                            "${value.toInt()}",
                            style: kSubtitle.copyWith(fontSize: 10, color: Colors.white24),
                          ),
                        );
                      },
                      reservedSize: 24,
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
                          style: kSubtitle.copyWith(fontSize: 10, color: Colors.white24),
                        );
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border(
                    bottom: BorderSide(color: Colors.white.withOpacity(0.1), width: 1),
                    left: BorderSide(color: Colors.white.withOpacity(0.1), width: 1),
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: sortedEntries
                        .map((e) => FlSpot(e.key.toDouble(), e.value.toDouble()))
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
                          kPrimaryTeal.withOpacity(0.0)
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
      delegate: SliverChildBuilderDelegate(
        (context, index) {
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
                      "Memuat lebih banyak...",
                      style: kSubtitle.copyWith(fontSize: 11),
                    ),
                  ],
                ),
              ),
            );
          }

          final t = traffics[index];
          final iconData = _getVehicleIcon(t.vehicleType);
          final iconColor = _getVehicleColor(t.vehicleType);

          return Card(
            color: kSurfaceDark,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              dense: true,
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              leading: CircleAvatar(
                backgroundColor: iconColor.withOpacity(0.2),
                child: Icon(iconData, color: iconColor, size: 20),
              ),
              title: Text(
                "${t.vehicleType.toUpperCase()} • ${t.speedKmph.toStringAsFixed(1)} km/h",
                style: kBodyText.copyWith(fontWeight: FontWeight.w600, fontSize: 13),
              ),
              subtitle: Text(
                "${t.location} • ${DateFormat('HH:mm').format(t.detectedAt.toLocal())}",
                style: kSubtitle.copyWith(fontSize: 11),
              ),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: kSuccessGreen.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  "${(t.confidence * 100).toStringAsFixed(0)}%",
                  style: kSubtitle.copyWith(color: kSuccessGreen, fontSize: 11),
                ),
              ),
            ),
          );
        },
        childCount: hasMore ? displayCount + 1 : displayCount, // +1 untuk loading indicator
      ),
    );
  }

  IconData _getVehicleIcon(String type) {
    switch (type.toLowerCase()) {
      case 'truck':
        return Icons.local_shipping;
      case 'motorcycle':
        return Icons.motorcycle;
      case 'bus':
        return Icons.directions_bus;
      default:
        return Icons.directions_car;
    }
  }

  Color _getVehicleColor(String type) {
    switch (type.toLowerCase()) {
      case 'truck':
        return Colors.orange;
      case 'motorcycle':
        return Colors.purpleAccent;
      case 'bus':
        return Colors.greenAccent;
      default:
        return kSecondaryBlue;
    }
  }
}