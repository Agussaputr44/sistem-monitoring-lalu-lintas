import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';

import '../../domain/entities/vehicle_statistic.dart';
import '../../domain/repositories/statistic_repository.dart';

part 'statistic_event.dart';
part 'statistic_state.dart';

class StatisticBloc extends Bloc<StatisticEvent, StatisticState> {
  final StatisticRepository repository;

  StatisticBloc(this.repository) : super(const StatisticState()) {
    
    on<FetchStatisticData>((event, emit) async {
      emit(state.copyWith(state: RequestState.Loading));

      final result = await repository.getVehicleStatistic();

      result.fold(
        (failure) {
          emit(state.copyWith(
            state: RequestState.Error,
            message: failure.message,
          ));
        },
        (data) {
          emit(state.copyWith(
            state: RequestState.Loaded,
            statistics: data,
          ));
        },
      );
    });
  }
}