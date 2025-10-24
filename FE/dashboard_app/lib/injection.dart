import 'package:dashboard_app/data/datasources/traffic_remote_datasources.dart';
import 'package:dashboard_app/data/repositories/traffic_repository_impl.dart';
import 'package:dashboard_app/domain/repositories/traffic_repository.dart';
import 'package:dashboard_app/domain/usecases/get_traffic_history.dart';
import 'package:dashboard_app/presentation/bloc/traffic_bloc.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;

final locator = GetIt.instance; 

Future<void> init() async {
  //! Features - Traffic Monitoring

  // Bloc
   locator.registerFactory(() => TrafficBloc(getTrafficHistory: locator()));


  // Use cases
  locator.registerLazySingleton(() => GetTrafficHistory(locator()));

  // // Repository
  locator.registerLazySingleton<TrafficRepository>(
      () => TrafficRepositoryImpl(locator()));

  // // Data sources
  locator.registerLazySingleton<TrafficRemoteDataSource>(
      () => TrafficRemoteDataSourceImpl(client: locator()));

  //! External
  locator.registerLazySingleton(() => http.Client());
}
