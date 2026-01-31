import 'package:dartz/dartz.dart';
import 'package:dashboard_app/common/failure.dart';
import 'package:dashboard_app/domain/entities/vehicle_statistic.dart';
import 'package:dashboard_app/domain/repositories/statistic_repository.dart';

class GetVehicleStatistic {
  final StatisticRepository repository;
  GetVehicleStatistic(this.repository);

  Future<Either<Failure, List<VehicleStatistic>>> execute() {
    return repository.getVehicleStatistic();
  }

}