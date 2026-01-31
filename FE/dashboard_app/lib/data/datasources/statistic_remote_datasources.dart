import 'dart:convert';
import 'package:dashboard_app/common/exception.dart';
import 'package:http/http.dart' as http;
import 'package:dashboard_app/common/constants.dart';
import '../models/vehicle_statistic_model.dart';

abstract class StatisticRemoteDatasources {
  Future<List<VehicleStatisticModel>> getVehicleStatistics();
}

class StatisticRemoteDatasourcesImpl implements StatisticRemoteDatasources {
  final http.Client client;

  StatisticRemoteDatasourcesImpl({required this.client});

  @override
  Future<List<VehicleStatisticModel>> getVehicleStatistics() async {
    final uri = Uri.parse('$kUrl/api/traffic-classification'); 
    
    final response = await client.get(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      
      return data.map((e) => VehicleStatisticModel.fromJson(e)).toList();
    } else {
      throw ServerException(); 
    }
  }
}