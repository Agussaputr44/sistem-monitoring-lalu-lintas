part of 'traffic_bloc.dart';

sealed class TrafficState extends Equatable {
  const TrafficState();

  @override
  List<Object> get props => [];
}

/// State awal saat belum ada data
final class TrafficInitial extends TrafficState {}

/// State saat sedang mengambil data
final class TrafficLoading extends TrafficState {}

/// State saat data berhasil diambil
final class TrafficLoaded extends TrafficState {
  final List<Traffic> data;
  const TrafficLoaded(this.data);

  @override
  List<Object> get props => [data];
}

/// State saat polling berjalan
final class TrafficPolling extends TrafficState {
  final List<Traffic> data;
  const TrafficPolling(this.data);

  @override
  List<Object> get props => [data];
}

/// State jika terjadi error
final class TrafficError extends TrafficState {
  final String message;
  const TrafficError(this.message);

  @override
  List<Object> get props => [message];
}

/// State ketika polling dihentikan
final class TrafficStopped extends TrafficState {}
