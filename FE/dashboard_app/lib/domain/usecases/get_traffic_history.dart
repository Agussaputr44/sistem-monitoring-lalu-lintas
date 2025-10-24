import 'package:dartz/dartz.dart';
import 'package:dashboard_app/common/failure.dart';
import 'package:dashboard_app/domain/entities/traffic.dart';

import '../repositories/traffic_repository.dart';

class GetTrafficHistory {

  final TrafficRepository repository;
  
  GetTrafficHistory(this.repository);

  Future<Either<Failure, List<Traffic>>> execute() {
    return repository.getTrafficHistory();
  }
}
