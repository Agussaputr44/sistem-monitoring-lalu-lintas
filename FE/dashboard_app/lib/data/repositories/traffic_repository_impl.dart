import 'dart:io';

import 'package:dartz/dartz.dart';
import 'package:dashboard_app/common/exception.dart';
import 'package:dashboard_app/common/failure.dart';
import 'package:dashboard_app/data/datasources/traffic_remote_datasources.dart';
import 'package:dashboard_app/domain/entities/traffic.dart';
import 'package:dashboard_app/domain/repositories/traffic_repository.dart';

class TrafficRepositoryImpl implements TrafficRepository {
  final TrafficRemoteDataSource remoteDataSource;
  TrafficRepositoryImpl(this.remoteDataSource);

  @override
  Future<Either<Failure, List<Traffic>>> getTrafficHistory() async {
   try {
      final result = await remoteDataSource.GetTrafficHistory();
      return Right(result.map((model) => model.toEntity()).toList());
    } on ServerException {
      return Left(ServerFailure(''));
    } on SocketException {
      return Left(ConnectionFailure('Failed to connect to the network'));
    }

  }
}