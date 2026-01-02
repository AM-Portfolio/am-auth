import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:am_common_ui/am_common_ui.dart';
import 'package:am_diagnostic_ui/providers/test_provider.dart';
import 'package:am_diagnostic_ui/theme/app_colors.dart';
import 'package:am_diagnostic_ui/screens/dashboard_screen.dart';
import 'package:am_diagnostic_ui/screens/user_management_screen.dart';
import 'package:am_diagnostic_ui/screens/token_tools_screen.dart';
import 'package:am_diagnostic_ui/screens/user_analytics_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: AuthProviders.providers,
      child: MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => TestProvider()),
        ],
        child: MaterialApp(
          title: 'AM Diagnostic UI',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            useMaterial3: true,
            scaffoldBackgroundColor: AppColors.background,
            colorScheme: ColorScheme.fromSeed(
              seedColor: AppColors.primary,
              background: AppColors.background,
              surface: AppColors.surface,
            ),
            textTheme: GoogleFonts.interTextTheme(
              Theme.of(context).textTheme,
            ),
            cardTheme: CardThemeData(
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: const BorderSide(color: AppColors.border),
              ),
              color: AppColors.surface,
            ),
          ),
          home: const AuthWrapper(
            child: DiagnosticShell(),
          ),
        ),
      ),
    );
  }
}

class DiagnosticShell extends StatefulWidget {
  const DiagnosticShell({super.key});

  @override
  State<DiagnosticShell> createState() => _DiagnosticShellState();
}

class _DiagnosticShellState extends State<DiagnosticShell> {
  String _activeNavItem = 'Tests';

  @override
  Widget build(BuildContext context) {
    return AuthenticatedLayout(
      title: 'Diagnostic Tool',
      activeNavItem: _activeNavItem,
      sidebarItems: [
        SidebarItem(title: 'Tests', icon: Icons.analytics_outlined),
        SidebarItem(title: 'Analytics', icon: Icons.insights_outlined),
        SidebarItem(title: 'Users', icon: Icons.people_outline),
        SidebarItem(title: 'Tokens', icon: Icons.key_outlined),
      ],
      onNavigate: (navItem) {
        setState(() {
          _activeNavItem = navItem;
        });
      },
      child: _getBody(),
    );
  }

  Widget _getBody() {
    switch (_activeNavItem) {
      case 'Tests':
        return const DashboardScreen();
      case 'Analytics':
        return const UserAnalyticsScreen();
      case 'Users':
        return const UserManagementScreen();
      case 'Tokens':
        return const TokenToolsScreen();
      default:
        return const DashboardScreen();
    }
  }
}
