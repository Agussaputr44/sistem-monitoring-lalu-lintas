import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:http/http.dart' as http;

import '../../common/constants.dart'; 
import '../../domain/entities/traffic.dart';
import '../bloc/traffic_bloc.dart';
import '../bloc/statistic_bloc.dart'; 

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

  @override
  void initState() {
    super.initState();
    
    context.read<StatisticBloc>().add(FetchStatisticData());

    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (mounted) {
        context.read<TrafficBloc>().add(FetchTrafficData());
        context.read<StatisticBloc>().add(FetchStatisticData());
      }
    });

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
      Future.delayed(const Duration(milliseconds: 300), () {
        if (mounted) setState(() => _isLoadingMore = false);
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
      appBar: _buildAppBar(),
      body: BlocBuilder<TrafficBloc, TrafficState>(
        builder: (context, state) {
          // Update cache jika data loaded
          if (state is TrafficLoaded) {
            _cachedTraffics = state.data;
          }

          if (_cachedTraffics.isNotEmpty || state is TrafficLoaded) {
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
                      const SizedBox(height: 16),
                      
                      // Bagian KPI Utama (Total & Avg Speed)
                      _buildMainKpiRow(traffics),
                      const SizedBox(height: 12),
                      
                      // Bagian KPI Per Tipe Kendaraan (Grid)
                      _buildTypeKpiRow(traffics),
                      const SizedBox(height: 16),
                      
                      // CCTV Stream
                      const _MjpegStreamPlayer(url: '$kUrl/api/video_feed'),
                      const SizedBox(height: 12),
                      
                      // Filters & Charts
                      _buildVehicleTypeFilter(),
                      const SizedBox(height: 12),
                      _buildFilterSection(context),
                      const SizedBox(height: 16),
                      _buildVehicleVolumeChart(traffics),
                      const SizedBox(height: 16),
                      
                      // Header List
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text("Riwayat Traffic Terkini", style: kHeading6.copyWith(fontSize: 16)),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(color: kPrimaryTeal.withOpacity(0.2), borderRadius: BorderRadius.circular(12)),
                            child: Text("${traffics.length} items filtered", style: kSubtitle.copyWith(fontSize: 11, color: kPrimaryTeal, fontWeight: FontWeight.w600)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                    ]),
                  ),
                ),
                SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  sliver: _buildOptimizedTrafficList(traffics),
                ),
                const SliverPadding(padding: EdgeInsets.only(bottom: 80)),
              ],
            );
          } else if (state is TrafficError) {
            return _buildErrorView(state.message);
          } else {
            return const Center(child: CircularProgressIndicator(color: kPrimaryTeal));
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: kPrimaryTeal,
        onPressed: () {
          context.read<TrafficBloc>().add(FetchTrafficData());
          context.read<StatisticBloc>().add(FetchStatisticData());
        },
        child: const Icon(Icons.refresh, color: Colors.white),
      ),
    );
  }

  // --- WIDGET BUILDERS ---

  AppBar _buildAppBar() {
    return AppBar(
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
                  width: 8, height: 8,
                  decoration: BoxDecoration(
                    color: kSuccessGreen,
                    shape: BoxShape.circle,
                    boxShadow: [BoxShadow(color: kSuccessGreen.withOpacity(0.5), blurRadius: 4, spreadRadius: 1)],
                  ),
                ),
                const SizedBox(width: 6),
                Text("Live", style: kSubtitle.copyWith(fontSize: 12, color: kSuccessGreen)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // INTEGRASI STATISTIC BLOC DI SINI (Total Count)
  Widget _buildMainKpiRow(List<Traffic> traffics) {
    final totalLocal = traffics.length;
    final avgSpeed = traffics.isNotEmpty ? traffics.map((t) => t.speedKmph).reduce((a, b) => a + b) / totalLocal : 0.0;
    final avgConfidence = traffics.isNotEmpty ? traffics.map((t) => t.confidence).reduce((a, b) => a + b) / totalLocal : 0.0;

    return BlocBuilder<StatisticBloc, StatisticState>(
      builder: (context, state) {
        String totalDisplay = "$totalLocal"; 
        
        if (state.state == RequestState.Loaded) {
          final totalFromApi = state.statistics.fold(0, (sum, item) => sum + item.count);
          totalDisplay = "$totalFromApi";
        } else if (state.state == RequestState.Loading) {
          totalDisplay = "...";
        }

        return Row(
          children: [
            Expanded(child: _buildKpiCard("Total Kendaraan", totalDisplay, Icons.directions_car, kPrimaryTeal)),
            const SizedBox(width: 8),
            Expanded(child: _buildKpiCard("Avg Speed", "${avgSpeed.toStringAsFixed(1)} km/h", Icons.speed, kSecondaryBlue)),
            const SizedBox(width: 8),
            Expanded(child: _buildKpiCard("Confidence", "${(avgConfidence * 100).toStringAsFixed(0)}%", Icons.verified, kSuccessGreen)),
          ],
        );
      },
    );
  }

  Widget _buildTypeKpiRow(List<Traffic> traffics) {
    return BlocBuilder<StatisticBloc, StatisticState>(
      builder: (context, state) {
        Map<String, int> dataCountMap = {};

        if (state.state == RequestState.Loaded) {
          for (var item in state.statistics) {
            dataCountMap[item.vehicleType.toLowerCase()] = item.count;
          }
        } else {
          for (var t in traffics) {
            dataCountMap[t.vehicleType.toLowerCase()] = (dataCountMap[t.vehicleType.toLowerCase()] ?? 0) + 1;
          }
        }

        // Config UI
        final vehicleData = [
          {'type': 'car', 'label': 'MOBIL', 'icon': Icons.directions_car, 'color': Colors.lightBlueAccent},
          {'type': 'motorcycle', 'label': 'MOTOR', 'icon': Icons.motorcycle, 'color': Colors.purpleAccent},
          {'type': 'pickup', 'label': 'PICKUP', 'icon': Icons.front_loader, 'color': Colors.orangeAccent},
          {'type': 'truck', 'label': 'TRUK', 'icon': Icons.local_shipping, 'color': Colors.redAccent},
          {'type': 'bus', 'label': 'BUS', 'icon': Icons.directions_bus, 'color': Colors.greenAccent},
        ];

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2, crossAxisSpacing: 8, mainAxisSpacing: 8, childAspectRatio: 2.2
          ),
          itemCount: vehicleData.length,
          itemBuilder: (context, index) {
            final data = vehicleData[index];
            final typeKey = data['type'] as String;
            final count = dataCountMap[typeKey] ?? 0;
            
            return _buildCompactKpiCard(
              data['label'] as String, 
              "$count", 
              data['icon'] as IconData, 
              data['color'] as Color
            );
          },
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
            Text(label, style: kSubtitle.copyWith(fontSize: 11), textAlign: TextAlign.center, maxLines: 1),
            const SizedBox(height: 2),
            Text(value, style: kHeading6.copyWith(color: color, fontSize: 14), maxLines: 1),
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
                  Text(value, style: kHeading6.copyWith(color: color, fontSize: 16))
                ]
              )
            ),
          ],
        ),
      ),
    );
  }

  // --- FILTERS & CHARTS & LIST LOGIC ---

  List<Traffic> _filterTraffics(List<Traffic> traffics) {
    var filtered = traffics;
    if (_selectedTimeRange != 'all') {
      final now = DateTime.now();
      DateTime cutoffTime;
      switch (_selectedTimeRange) {
        case '15min': cutoffTime = now.subtract(const Duration(minutes: 15)); break;
        case '30min': cutoffTime = now.subtract(const Duration(minutes: 30)); break;
        case '1hour': cutoffTime = now.subtract(const Duration(hours: 1)); break;
        case '3hours': cutoffTime = now.subtract(const Duration(hours: 3)); break;
        case 'today': cutoffTime = DateTime(now.year, now.month, now.day); break;
        default: cutoffTime = DateTime(2000);
      }
      filtered = filtered.where((t) => t.detectedAt.isAfter(cutoffTime)).toList();
    }
    if (_selectedVehicleType != 'all') filtered = filtered.where((t) => t.vehicleType.toLowerCase() == _selectedVehicleType).toList();
    if (selectedRange != null) {
      filtered = filtered.where((t) {
        final date = t.detectedAt;
        return date.isAfter(selectedRange!.start.subtract(const Duration(days: 1))) && date.isBefore(selectedRange!.end.add(const Duration(days: 1)));
      }).toList();
    }
    if (filtered.length < _displayedItemCount) _displayedItemCount = 20;
    return filtered;
  }

  Widget _buildTimeRangeFilter() {
    final timeRanges = {'all': 'Semua Waktu', '15min': '15 Menit', '30min': '30 Menit', '1hour': '1 Jam', '3hours': '3 Jam', 'today': 'Hari Ini'};
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Rentang Waktu", style: kSubtitle.copyWith(fontSize: 12, color: Colors.white54)),
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
                  label: Text(entry.value, style: kSubtitle.copyWith(fontSize: 12, color: isSelected ? Colors.white : Colors.white70)),
                  backgroundColor: kSurfaceDark,
                  selectedColor: kPrimaryTeal.withOpacity(0.3),
                  checkmarkColor: kPrimaryTeal,
                  side: BorderSide(color: isSelected ? kPrimaryTeal : Colors.white24, width: 1),
                  onSelected: (selected) => setState(() {_selectedTimeRange = entry.key; if (entry.key != 'all') selectedRange = null;}),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildVehicleTypeFilter() {
    final vehicleTypes = {
      'all': {'label': 'Semua', 'icon': Icons.dashboard, 'color': kTextPrimary},
      'car': {'label': 'Mobil', 'icon': Icons.directions_car, 'color': Colors.lightBlueAccent},
      'motorcycle': {'label': 'Motor', 'icon': Icons.motorcycle, 'color': Colors.purpleAccent},
      'truck': {'label': 'Truk', 'icon': Icons.local_shipping, 'color': Colors.redAccent},
      'pickup': {'label': 'Pickup', 'icon': Icons.front_loader, 'color': Colors.orangeAccent},
      'bus': {'label': 'Bus', 'icon': Icons.directions_bus, 'color': Colors.greenAccent},
    };
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("Filter Jenis Kendaraan", style: kSubtitle.copyWith(fontSize: 12, color: Colors.white54)),
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
                  avatar: Icon(data['icon'] as IconData, size: 16, color: isSelected ? Colors.white : (data['color'] as Color)),
                  label: Text(data['label'] as String, style: kSubtitle.copyWith(fontSize: 12, color: isSelected ? Colors.white : Colors.white70)),
                  backgroundColor: kSurfaceDark,
                  selectedColor: (data['color'] as Color).withOpacity(0.4),
                  checkmarkColor: Colors.white,
                  side: BorderSide(color: isSelected ? data['color'] as Color : Colors.white24, width: 1),
                  onSelected: (selected) => setState(() => _selectedVehicleType = entry.key),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildFilterSection(BuildContext context) {
    final rangeText = selectedRange == null ? "Pilih rentang tanggal kustom" : "${DateFormat('dd MMM').format(selectedRange!.start)} - ${DateFormat('dd MMM').format(selectedRange!.end)}";
    return InkWell(
      onTap: () async {
        final now = DateTime.now();
        final picked = await showDateRangePicker(context: context, firstDate: DateTime(now.year - 1), lastDate: DateTime(now.year + 1), currentDate: now, saveText: "Terapkan", builder: (context, child) => Theme(data: ThemeData.dark().copyWith(colorScheme: const ColorScheme.dark(primary: kPrimaryTeal, surface: kSurfaceDark)), child: child!));
        if (picked != null) setState(() {selectedRange = picked; _selectedTimeRange = 'all';});
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(color: kSurfaceDark, borderRadius: BorderRadius.circular(12), border: Border.all(color: kPrimaryTeal.withOpacity(0.3))),
        child: Row(
          children: [
            Icon(Icons.calendar_today, color: kPrimaryTeal, size: 18),
            const SizedBox(width: 8),
            Text(rangeText, style: kSubtitle.copyWith(fontSize: 13)),
            const Spacer(),
            if (selectedRange != null) GestureDetector(onTap: () => setState(() => selectedRange = null), child: Icon(Icons.close, color: kDangerRed, size: 18)) else const Icon(Icons.arrow_drop_down, color: Colors.white70),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleVolumeChart(List<Traffic> traffics) {
    if (traffics.isEmpty) return const SizedBox.shrink();
    final grouped = <int, int>{};
    for (var t in traffics) { grouped[t.detectedAt.hour] = (grouped[t.detectedAt.hour] ?? 0) + 1; }
    final sortedEntries = grouped.entries.toList()..sort((a, b) => a.key.compareTo(b.key));
    final maxY = sortedEntries.isNotEmpty ? sortedEntries.map((e) => e.value).reduce((a, b) => a > b ? a : b).toDouble() : 1.0;
    
    return Card(
      color: kSurfaceDark,
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Volume per Jam (Filtered)", style: kHeading6.copyWith(fontSize: 14, color: kTextSecondary)),
            const SizedBox(height: 20),
            SizedBox(
              height: 180,
              child: LineChart(LineChartData(
                maxY: maxY + (maxY * 0.1), minY: 0,
                gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: maxY > 5 ? (maxY / 4).ceilToDouble() : 1, getDrawingHorizontalLine: (value) => FlLine(color: Colors.white.withOpacity(0.05), strokeWidth: 1)),
                titlesData: FlTitlesData(show: true, bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, getTitlesWidget: (value, meta) => Padding(padding: const EdgeInsets.only(top: 8), child: Text("${value.toInt()}:00", style: kSubtitle.copyWith(fontSize: 10, color: Colors.white24))), reservedSize: 24, interval: 2)), leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, interval: maxY > 5 ? (maxY / 4).ceilToDouble() : 1, reservedSize: 28, getTitlesWidget: (value, meta) {if (value == 0) return const SizedBox.shrink(); return Text(value.toInt().toString(), style: kSubtitle.copyWith(fontSize: 10, color: Colors.white24));})), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false))),
                borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: Colors.white.withOpacity(0.1), width: 1), left: BorderSide(color: Colors.white.withOpacity(0.1), width: 1))),
                lineBarsData: [LineChartBarData(spots: sortedEntries.map((e) => FlSpot(e.key.toDouble(), e.value.toDouble())).toList(), isCurved: true, gradient: LinearGradient(colors: [kPrimaryTeal, kPrimaryTeal.withOpacity(0.5)], begin: Alignment.centerLeft, end: Alignment.centerRight), barWidth: 3, isStrokeCapRound: true, dotData: FlDotData(show: true, getDotPainter: (spot, percent, bar, index) => FlDotCirclePainter(radius: 3, color: kPrimaryTeal, strokeWidth: 0)), belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [kPrimaryTeal.withOpacity(0.15), kPrimaryTeal.withOpacity(0.0)], begin: Alignment.topCenter, end: Alignment.bottomCenter)))],
              )),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOptimizedTrafficList(List<Traffic> traffics) {
    final displayCount = _displayedItemCount > traffics.length ? traffics.length : _displayedItemCount;
    final hasMore = displayCount < traffics.length;
    return SliverList(
      delegate: SliverChildBuilderDelegate((context, index) {
        if (index == displayCount) return Padding(padding: const EdgeInsets.symmetric(vertical: 20), child: Center(child: Column(children: [SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2, color: kPrimaryTeal)), const SizedBox(height: 8), Text("Memuat riwayat lainnya...", style: kSubtitle.copyWith(fontSize: 11))])));
        final t = traffics[index];
        final iconData = _getVehicleIcon(t.vehicleType);
        final iconColor = _getVehicleColor(t.vehicleType);
        return Card(
          color: kSurfaceDark, elevation: 1, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)), margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            dense: true, contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            leading: CircleAvatar(backgroundColor: iconColor.withOpacity(0.15), child: Icon(iconData, color: iconColor, size: 20)),
            title: Row(children: [Text(t.vehicleType.toUpperCase(), style: kBodyText.copyWith(fontWeight: FontWeight.bold, fontSize: 13, color: iconColor)), const SizedBox(width: 8), Text("•  ${t.speedKmph.toStringAsFixed(1)} km/h", style: kBodyText.copyWith(fontWeight: FontWeight.w600, fontSize: 13))]),
            subtitle: Padding(padding: const EdgeInsets.only(top: 4), child: Row(children: [Icon(Icons.location_on, size: 12, color: kTextSecondary), const SizedBox(width: 4), Expanded(child: Text(t.location, style: kSubtitle.copyWith(fontSize: 11), overflow: TextOverflow.ellipsis)), Text(DateFormat('dd/MM HH:mm:ss').format(t.detectedAt.toLocal()), style: kSubtitle.copyWith(fontSize: 11, color: kTextSecondary))])),
            trailing: Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [Text("Confidence", style: kSubtitle.copyWith(fontSize: 9)), Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2), decoration: BoxDecoration(color: kSuccessGreen.withOpacity(0.15), borderRadius: BorderRadius.circular(6)), child: Text("${(t.confidence * 100).toStringAsFixed(0)}%", style: kSubtitle.copyWith(color: kSuccessGreen, fontSize: 11, fontWeight: FontWeight.bold)))]),
          ),
        );
      }, childCount: hasMore ? displayCount + 1 : displayCount),
    );
  }

  Widget _buildErrorView(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: kDangerRed, size: 48),
          const SizedBox(height: 16),
          Text(message, style: kBodyText, textAlign: TextAlign.center),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => context.read<TrafficBloc>().add(FetchTrafficData()),
            style: ElevatedButton.styleFrom(backgroundColor: kPrimaryTeal),
            child: const Text("Coba Lagi"),
          )
        ],
      ),
    );
  }

  IconData _getVehicleIcon(String type) {
    switch (type.toLowerCase()) {
      case 'truck': return Icons.local_shipping;
      case 'pickup': return Icons.front_loader;
      case 'motorcycle': return Icons.motorcycle;
      case 'bus': return Icons.directions_bus;
      default: return Icons.directions_car;
    }
  }

  Color _getVehicleColor(String type) {
    switch (type.toLowerCase()) {
      case 'truck': return Colors.redAccent;
      case 'pickup': return Colors.orangeAccent;
      case 'motorcycle': return Colors.purpleAccent;
      case 'bus': return Colors.greenAccent;
      case 'car': return Colors.lightBlueAccent;
      default: return kTextSecondary;
    }
  }
}

// === CUSTOM MJPEG STREAM WIDGET ===
class _MjpegStreamPlayer extends StatefulWidget {
  final String url;
  const _MjpegStreamPlayer({required this.url});

  @override
  State<_MjpegStreamPlayer> createState() => _MjpegStreamPlayerState();
}

class _MjpegStreamPlayerState extends State<_MjpegStreamPlayer> {
  Uint8List? _currentFrame;
  bool _isLoading = true;
  bool _hasError = false;
  String _errorMessage = '';
  StreamSubscription? _streamSubscription;
  String _streamKey = '0';

  @override
  void initState() {
    super.initState();
    _startStream();
  }

  void _startStream() {
    setState(() {
      _isLoading = true;
      _hasError = false;
      _currentFrame = null;
    });

    final request = http.Request('GET', Uri.parse(widget.url));
    request.headers['ngrok-skip-browser-warning'] = 'true';
    request.headers['User-Agent'] = 'Mozilla/5.0';

    http.Client().send(request).then((response) {
      if (response.statusCode == 200) {
        final boundary = _getBoundary(response.headers['content-type'] ?? '');
        if (boundary.isEmpty) {
          setState(() { _hasError = true; _errorMessage = 'Invalid stream'; _isLoading = false; });
          return;
        }

        List<int> buffer = [];
        _streamSubscription = response.stream.listen(
          (chunk) {
            buffer.addAll(chunk);
            final frame = _extractFrame(buffer, boundary);
            if (frame != null) {
              if (mounted) setState(() { _currentFrame = Uint8List.fromList(frame); _isLoading = false; });
              buffer.clear();
            }
          },
          onError: (e) { if (mounted) setState(() { _hasError = true; _errorMessage = '$e'; _isLoading = false; }); },
          onDone: () { if (mounted) setState(() { _hasError = true; _errorMessage = 'Done'; _isLoading = false; }); },
        );
      } else {
        if (mounted) setState(() { _hasError = true; _errorMessage = 'HTTP ${response.statusCode}'; _isLoading = false; });
      }
    }).catchError((e) {
      if (mounted) setState(() { _hasError = true; _errorMessage = '$e'; _isLoading = false; });
    });
  }

  String _getBoundary(String contentType) {
    final parts = contentType.split('boundary=');
    return parts.length > 1 ? parts[1].trim() : '';
  }

  List<int>? _extractFrame(List<int> buffer, String boundary) {
    final boundaryBytes = '--$boundary'.codeUnits;
    final startIndex = _indexOf(buffer, boundaryBytes);
    if (startIndex == -1) return null;
    final jpegStart = _indexOf(buffer, [0xFF, 0xD8], startIndex);
    final jpegEnd = _indexOf(buffer, [0xFF, 0xD9], jpegStart);
    if (jpegStart != -1 && jpegEnd != -1) return buffer.sublist(jpegStart, jpegEnd + 2);
    return null;
  }

  int _indexOf(List<int> data, List<int> pattern, [int start = 0]) {
    for (int i = start; i < data.length - pattern.length; i++) {
      bool match = true;
      for (int j = 0; j < pattern.length; j++) {
        if (data[i + j] != pattern[j]) { match = false; break; }
      }
      if (match) return i;
    }
    return -1;
  }

  void _reload() {
    _streamSubscription?.cancel();
    if (mounted) setState(() => _streamKey = DateTime.now().millisecondsSinceEpoch.toString());
    _startStream();
  }

  @override
  void dispose() {
    _streamSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      key: ValueKey(_streamKey),
      color: kSurfaceDark,
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Row(
              children: [
                Icon(Icons.videocam, color: kPrimaryTeal, size: 20),
                const SizedBox(width: 8),
                Text("Live CCTV Stream", style: kHeading6.copyWith(fontSize: 14, color: kTextSecondary)),
                const Spacer(),
                if (!_hasError && !_isLoading) _BlinkingLiveIndicator(),
                const SizedBox(width: 8),
                IconButton(icon: Icon(Icons.refresh, size: 18), color: kPrimaryTeal, onPressed: _reload, padding: EdgeInsets.zero, constraints: BoxConstraints(), tooltip: 'Reload'),
              ],
            ),
          ),
          Container(
            height: 220, width: double.infinity, margin: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: Colors.black, borderRadius: BorderRadius.circular(8)),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: _isLoading
                  ? Center(child: CircularProgressIndicator(color: kPrimaryTeal))
                  : _hasError
                      ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.videocam_off, color: Colors.white38, size: 48), Text(_errorMessage, style: TextStyle(color: Colors.white54, fontSize: 11)), TextButton(onPressed: _reload, child: Text("Retry"))]))
                      : Image.memory(_currentFrame!, fit: BoxFit.contain, gaplessPlayback: true),
            ),
          ),
        ],
      ),
    );
  }
}

class _BlinkingLiveIndicator extends StatefulWidget {
  @override
  State<_BlinkingLiveIndicator> createState() => _BlinkingLiveIndicatorState();
}

class _BlinkingLiveIndicatorState extends State<_BlinkingLiveIndicator> with SingleTickerProviderStateMixin {
  late AnimationController _c;
  @override
  void initState() { super.initState(); _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 800))..repeat(reverse: true); }
  @override
  void dispose() { _c.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) {
    return FadeTransition(opacity: _c, child: Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2), decoration: BoxDecoration(color: kDangerRed, borderRadius: BorderRadius.circular(4)), child: const Text("LIVE", style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold))));
  }
}