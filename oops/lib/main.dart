import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'app/routes/app_router.dart';
import 'app/theme/app_theme.dart';
import 'config/app_config.dart';
import 'config/environment.dart';
import 'customer/splash/splash_screen.dart';
import 'services/language_service.dart';
import 'utils/token_storage.dart';
import 'services/push_notification_service.dart';
import 'services/in_app_notification_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load environment variables via flutter_dotenv
  await EnvironmentConfig.initialize();

  // Load persistent authentication session tokens
  await TokenStorage.init();

  // Load persistent language preferences
  await LanguageService.instance.init();

  // Initialize push notifications & real-time in-app alerts if token exists
  if (TokenStorage.accessToken.isNotEmpty) {
    try {
      await PushNotificationService.instance.initialize();
      InAppNotificationService.instance.startPolling();
    } catch (e) {
      debugPrint('Init ignored during startup: $e');
    }
  }

  // Lock orientation to portrait
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Status bar styling
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const HireMeApp());
}

class HireMeApp extends StatelessWidget {
  const HireMeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<Locale>(
      valueListenable: LanguageService.instance.currentLocale,
      builder: (context, locale, child) {
        return MaterialApp(
          title: AppConfig.appName,
          debugShowCheckedModeBanner: false,
          navigatorKey: AppRouter.navigatorKey,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: ThemeMode.light,
          locale: locale,
          supportedLocales: const [
            Locale('en', ''),
            Locale('hi', ''),
            Locale('mr', ''),
          ],
          localizationsDelegates: const [
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          onGenerateRoute: AppRouter.generateRoute,
          home: const SplashScreen(),
        );
      },
    );
  }
}
