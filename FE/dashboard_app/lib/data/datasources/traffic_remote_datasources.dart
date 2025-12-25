import 'dart:convert';

import 'package:dashboard_app/data/models/traffic_model.dart';
import 'package:http/http.dart' as http;

abstract class TrafficRemoteDataSource {
  Future<List<TrafficModel>> GetTrafficHistory();
}

class TrafficRemoteDataSourceImpl implements TrafficRemoteDataSource {
  final http.Client client;
  static const BASE_URL = 'https://4c6b315fae0d.ngrok-free.app';

  TrafficRemoteDataSourceImpl({required this.client});

  @override
  Future<List<TrafficModel>> GetTrafficHistory() async {
    final response = await client.get(Uri.parse('$BASE_URL/api/traffic-history'));

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((e) => TrafficModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to fetch traffic data');
    }
  }
}
