import 'package:dartz/dartz.dart';
import 'package:dashboard_app/domain/entities/vehicle_statistic.dart';
import '../../common/failure.dart';

abstract class StatisticRepository {
  Future<Either<Failure, List<VehicleStatistic>>> getVehicleStatistic();
}
