import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'features/auth/ui/login_page.dart';
import 'features/auth/state/auth_provider.dart';
import 'features/voice/ui/voice_interface_page.dart';
import 'features/users/ui/users_list_page.dart';
import 'features/users/ui/user_detail_page.dart';
import 'features/emergency/ui/emergency_page.dart';
import 'features/items/ui/items_page.dart';
import 'features/messages/ui/messages_page.dart';
import 'features/voice/ui/tts_settings_page.dart';
import 'features/notification/ui/notification_list_page.dart';
import 'features/notification/ui/send_message_page.dart';

class AppRouter {
  AppRouter._();
  static final GoRouter router = GoRouter(
    routes: <RouteBase>[
      GoRoute(
        path: '/',
        builder: (BuildContext context, GoRouterState state) {
          return Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              if (authProvider.isLoggedIn) {
                return const VoiceInterfacePage();
              } else {
                return const LoginPage();
              }
            },
          );
        },
      ),
      GoRoute(
        path: '/login',
        builder: (BuildContext context, GoRouterState state) => const LoginPage(),
      ),
      GoRoute(
        path: '/voice',
        builder: (BuildContext context, GoRouterState state) => const VoiceInterfacePage(),
      ),
      GoRoute(
        path: '/users',
        builder: (BuildContext context, GoRouterState state) => const UsersListPage(),
      ),
      GoRoute(
        path: '/users/:userId',
        builder: (BuildContext context, GoRouterState state) {
          final userId = state.pathParameters['userId']!;
          return UserDetailPage(userId: userId);
        },
      ),
      GoRoute(
        path: '/emergency',
        builder: (BuildContext context, GoRouterState state) => const EmergencyPage(),
      ),
      GoRoute(
        path: '/items',
        builder: (BuildContext context, GoRouterState state) => const ItemsPage(),
      ),
      GoRoute(
        path: '/messages',
        builder: (BuildContext context, GoRouterState state) => const MessagesPage(),
      ),
      GoRoute(
        path: '/tts-settings',
        builder: (BuildContext context, GoRouterState state) => const TtsSettingsPage(),
      ),
      GoRoute(
        path: '/notifications',
        builder: (BuildContext context, GoRouterState state) => const NotificationListPage(),
      ),
      GoRoute(
        path: '/send-message',
        builder: (BuildContext context, GoRouterState state) => const SendMessagePage(),
      ),
    ],
  );
}


