import 'package:dartz/dartz.dart';
import '../entities/traffic.dart';

import '../../common/failure.dart';

abstract class TrafficRepository {
  Future<Either<Failure, List<Traffic>>> getTrafficHistory();
}