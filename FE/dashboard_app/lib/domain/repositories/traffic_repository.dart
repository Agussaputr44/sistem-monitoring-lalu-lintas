import 'package:dartz/dartz.dart';
import 'package:dashboard_app/domain/entities/traffic.dart';

import '../../common/failure.dart';

abstract class TrafficRepository {
  Future<Either<Failure, List<Traffic>>> getTrafficHistory();
}