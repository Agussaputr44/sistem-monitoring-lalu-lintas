part of 'statistic_bloc.dart';

// Definisi Enum
enum RequestState { Empty, Loading, Loaded, Error }

class StatisticState extends Equatable {
  final RequestState state;
  final List<VehicleStatistic> statistics;
  final String message;

  const StatisticState({
    this.state = RequestState.Empty,
    this.statistics = const [],
    this.message = '',
  });

  StatisticState copyWith({
    RequestState? state,
    List<VehicleStatistic>? statistics,
    String? message,
  }) {
    return StatisticState(
      state: state ?? this.state,
      statistics: statistics ?? this.statistics,
      message: message ?? this.message,
    );
  }

  @override
  List<Object> get props => [state, statistics, message];
}