import 'data/datasources/traffic_remote_datasources.dart';
import 'data/repositories/traffic_repository_impl.dart';
import 'domain/repositories/traffic_repository.dart';
import 'domain/usecases/get_traffic_history.dart';
import 'presentation/bloc/traffic_bloc.dart';
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
