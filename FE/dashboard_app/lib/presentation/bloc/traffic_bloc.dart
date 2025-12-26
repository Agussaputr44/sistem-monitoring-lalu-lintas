import 'dart:async';
import '../../domain/usecases/get_traffic_history.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/traffic.dart';

part 'traffic_event.dart';
part 'traffic_state.dart';

class TrafficBloc extends Bloc<TrafficEvent, TrafficState> {
  final GetTrafficHistory getTrafficHistory;
  Timer? _timer;

  TrafficBloc({required this.getTrafficHistory}) : super(TrafficInitial()) {
    on<FetchTrafficData>(_onFetchTrafficData);
    on<StartPollingTraffic>(_onStartPolling);
    on<StopPollingTraffic>(_onStopPolling);
  }

  Future<void> _onFetchTrafficData(
      FetchTrafficData event, Emitter<TrafficState> emit) async {
    emit(TrafficLoading());
    final result = await getTrafficHistory.execute();
    result.fold(
      (failure) => emit(TrafficError('Failed to load traffic data')),
      (data) => emit(TrafficLoaded(data)),
    );
  }

  Future<void> _onStartPolling(
      StartPollingTraffic event, Emitter<TrafficState> emit) async {
    _timer?.cancel();
    _timer = Timer.periodic(event.interval, (_) async {
      final result = await getTrafficHistory.execute();
      result.fold(
        (failure) => emit(TrafficError('Polling failed')),
        (data) => emit(TrafficLoaded(data)),
      );
    });
  }

  void _onStopPolling(
      StopPollingTraffic event, Emitter<TrafficState> emit) {
    _timer?.cancel();
    emit(TrafficStopped());
  }

  @override
  Future<void> close() {
    _timer?.cancel();
    return super.close();
  }
}
