import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/env/env.dart';
import 'features/voice/state/voice_provider.dart';
import 'features/auth/state/auth_provider.dart';
import 'features/notification/state/notification_provider.dart';
import 'router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Load environment variables
  await AppEnv.load();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final ThemeData base = ThemeData(brightness: Brightness.dark);
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => VoiceProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
      ],
      child: MaterialApp.router(
        title: 'Voice Interface App',
        routerConfig: AppRouter.router,
        theme: base.copyWith(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark),
          scaffoldBackgroundColor: Colors.black,
          appBarTheme: const AppBarTheme(backgroundColor: Colors.black, foregroundColor: Colors.white70),
        ),
      ),
    );
  }
}
