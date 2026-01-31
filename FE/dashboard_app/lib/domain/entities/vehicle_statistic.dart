import 'package:equatable/equatable.dart';

class VehicleStatistic extends Equatable {
  final String vehicleType;
  final int count;

  const VehicleStatistic({
    required this.vehicleType,
    required this.count,
  });

  @override
  List<Object?> get props => [vehicleType, count];
}