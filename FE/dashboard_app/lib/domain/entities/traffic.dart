import 'package:equatable/equatable.dart';

class Traffic extends Equatable {
  final int id;
  final String vehicleType;
  final double speedKmph;
  final double confidence;
  final String location;
  final DateTime detectedAt;

  const Traffic({
    required this.id,
    required this.vehicleType,
    required this.speedKmph,
    required this.confidence,
    required this.location,
    required this.detectedAt,
  });

  @override
  List<Object?> get props => [id, vehicleType, speedKmph, confidence, location, detectedAt];
}
