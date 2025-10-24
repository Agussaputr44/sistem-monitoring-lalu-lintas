part of 'traffic_bloc.dart';

sealed class TrafficEvent extends Equatable {
  const TrafficEvent();

  @override
  List<Object> get props => [];
}

/// Ambil data lalu lintas sekali
class FetchTrafficData extends TrafficEvent {}

/// Mulai polling data berkala
class StartPollingTraffic extends TrafficEvent {
  final Duration interval;

  const StartPollingTraffic({this.interval = const Duration(seconds: 5)});

  @override
  List<Object> get props => [interval];
}

/// Hentikan polling data
class StopPollingTraffic extends TrafficEvent {}
