import 'package:dartz/dartz.dart';
import 'package:dashboard_app/common/exception.dart';
import 'package:dashboard_app/data/datasources/statistic_remote_datasources.dart';
import '../../common/failure.dart';
import '../../domain/entities/vehicle_statistic.dart';
import '../../domain/repositories/statistic_repository.dart';

class StatisticRepositoryImpl implements StatisticRepository {
  final StatisticRemoteDatasources remoteDataSource;

  // Constructor
  StatisticRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, List<VehicleStatistic>>> getVehicleStatistic() async {
    try {
      final remoteData = await remoteDataSource.getVehicleStatistics();

      final entities = remoteData.map((model) => model.toEntity()).toList();

      return Right(entities);
    } on ServerException {
      return const Left(ServerFailure('Gagal terhubung ke server'));
    } on Exception catch (e) {
      return Left(ServerFailure(e.toString()));
    }
  }
}
