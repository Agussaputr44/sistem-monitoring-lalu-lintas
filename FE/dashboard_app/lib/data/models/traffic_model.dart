import 'package:equatable/equatable.dart';
import '../../domain/entities/traffic.dart';

class TrafficModel extends Equatable {
  final int id;
  final String vehicleType;
  final double speedKmph;
  final double confidence;
  final String location;
  final DateTime detectedAt;

  const TrafficModel({
    required this.id,
    required this.vehicleType,
    required this.speedKmph,
    required this.confidence,
    required this.location,
    required this.detectedAt,
  });

  factory TrafficModel.fromJson(Map<String, dynamic> json) {
    return TrafficModel(
      id: json['id'],
      vehicleType: json['vehicle_type'],
      speedKmph: (json['speed_kmph'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      location: json['location'],
      detectedAt: DateTime.parse(json['detected_at']),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'vehicle_type': vehicleType,
    'speed_kmph': speedKmph,
    'confidence': confidence,
    'location': location,
    'detected_at': detectedAt.toIso8601String(),
  };

  Traffic toEntity() {
    return Traffic(
      id: id,
      vehicleType: vehicleType,
      speedKmph: speedKmph,
      confidence: confidence,
      location: location,
      detectedAt: detectedAt,
    );
  }

  @override
  List<Object?> get props => [
    id,
    vehicleType,
    speedKmph,
    confidence,
    location,
    detectedAt,
  ];
}
