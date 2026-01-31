import 'package:dashboard_app/data/datasources/statistic_remote_datasources.dart';
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;

// Import Traffic (Existing)
import 'data/datasources/traffic_remote_datasources.dart';
import 'data/repositories/statistic_repository_impl.dart';
import 'data/repositories/traffic_repository_impl.dart';
import 'domain/repositories/statistic_repository.dart';
import 'domain/repositories/traffic_repository.dart';
import 'domain/usecases/get_traffic_history.dart';
import 'presentation/bloc/statistic_bloc.dart';
import 'presentation/bloc/traffic_bloc.dart';

final locator = GetIt.instance; 

Future<void> init() async {
  locator.registerFactory(() => TrafficBloc(getTrafficHistory: locator()));
  locator.registerLazySingleton(() => GetTrafficHistory(locator()));
  locator.registerLazySingleton<TrafficRepository>(
      () => TrafficRepositoryImpl(locator()));
  locator.registerLazySingleton<TrafficRemoteDataSource>(
      () => TrafficRemoteDataSourceImpl(client: locator()));


  //! Features - Vehicle Statistics (BARU)
  
  // Bloc
  // Menggunakan registerFactory karena Bloc memiliki state yang harus di-reset 
  // setiap kali halaman dibuka/ditutup.
  // Note: Kita inject Repository langsung (sesuai kode Bloc sebelumnya).
  locator.registerFactory(
    () => StatisticBloc(locator()), 
  );

  // Repository
  // Menggunakan registerLazySingleton agar instance di-cache (hemat memori)
  locator.registerLazySingleton<StatisticRepository>(
    () => StatisticRepositoryImpl(remoteDataSource: locator()),
  );

  // Data Sources
  locator.registerLazySingleton<StatisticRemoteDatasources>(
    () => StatisticRemoteDatasourcesImpl(client: locator()),
  );


  //! External
  // Pastikan Client diregister paling akhir atau paling awal (hanya sekali)
  if (!locator.isRegistered<http.Client>()) {
     locator.registerLazySingleton(() => http.Client());
  }
}