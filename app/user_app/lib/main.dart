import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/env/env.dart';
import 'features/voice/state/voice_provider.dart';
import 'router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Attempt to load dotenv only if flag set; failures are ignored in AppEnv
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
      ],
      child: MaterialApp.router(
        title: 'User Voice App',
        routerConfig: AppRouter.router,
        theme: base.copyWith(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.grey, brightness: Brightness.dark),
          scaffoldBackgroundColor: Colors.black,
          appBarTheme: const AppBarTheme(backgroundColor: Colors.black, foregroundColor: Colors.white70),
        ),
      ),
    );
  }
}
