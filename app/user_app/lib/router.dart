import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'features/voice/ui/voice_page.dart';

class AppRouter {
  AppRouter._();
  static final GoRouter router = GoRouter(
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (BuildContext context, GoRouterState state) => const VoicePage(),
      ),
    ],
  );
}


