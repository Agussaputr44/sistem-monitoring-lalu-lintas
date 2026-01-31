import 'package:equatable/equatable.dart';
import '../../domain/entities/vehicle_statistic.dart';

class VehicleStatisticModel extends Equatable {
  final String vehicleType;
  final int count;

  const VehicleStatisticModel({
    required this.vehicleType,
    required this.count,
  });

  factory VehicleStatisticModel.fromJson(Map<String, dynamic> json) {
    return VehicleStatisticModel(
      vehicleType: json['vehicle_type'] ?? 'unknown',
      count: (json['count'] as num?)?.toInt() ?? 0,
    );
  }

  Map<String, dynamic> toJson() => {
    'vehicle_type': vehicleType,
    'count': count,
  };

  VehicleStatistic toEntity() {
    return VehicleStatistic(
      vehicleType: vehicleType,
      count: count,
    );
  }

  @override
  List<Object?> get props => [vehicleType, count];
}