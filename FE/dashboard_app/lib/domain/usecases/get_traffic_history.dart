import 'package:dartz/dartz.dart';
import '../../common/failure.dart';
import '../entities/traffic.dart';

import '../repositories/traffic_repository.dart';

class GetTrafficHistory {

  final TrafficRepository repository;
  
  GetTrafficHistory(this.repository);

  Future<Either<Failure, List<Traffic>>> execute() {
    return repository.getTrafficHistory();
  }
}
