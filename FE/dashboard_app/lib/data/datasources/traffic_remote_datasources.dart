import 'dart:convert';

import 'package:dashboard_app/common/constants.dart';

import '../models/traffic_model.dart';
import 'package:http/http.dart' as http;

abstract class TrafficRemoteDataSource {
  Future<List<TrafficModel>> GetTrafficHistory();
}

class TrafficRemoteDataSourceImpl implements TrafficRemoteDataSource {
  final http.Client client;

  TrafficRemoteDataSourceImpl({required this.client});

  @override
  Future<List<TrafficModel>> GetTrafficHistory() async {
    final response = await client.get(
      Uri.parse('$kUrl/api/traffic-history'),
       headers: {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
      },
      );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((e) => TrafficModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to fetch traffic data');
    }
  }


}
