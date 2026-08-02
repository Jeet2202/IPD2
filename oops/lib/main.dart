import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'app/routes/app_router.dart';
import 'app/theme/app_theme.dart';
import 'config/app_config.dart';
import 'config/environment.dart';
import 'customer/splash/splash_screen.dart';
import 'utils/token_storage.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Load environment variables via flutter_dotenv
  await EnvironmentConfig.initialize();

  // Load persistent authentication session tokens
  await TokenStorage.init();

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
    return MaterialApp(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      onGenerateRoute: AppRouter.generateRoute,
      home: const SplashScreen(),
    );
  }
}
