part of 'statistic_bloc.dart';

sealed class StatisticEvent extends Equatable {
  const StatisticEvent();

  @override
  List<Object> get props => [];
}

// Event untuk memanggil data dari API
class FetchStatisticData extends StatisticEvent {}