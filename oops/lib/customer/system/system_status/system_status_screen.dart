// File:
// lib/customer/system/system_status/system_status_screen.dart

import 'package:flutter/material.dart';

enum SystemState {
  maintenance,
  serverError,
  notFound,
  comingSoon,
  forceUpdate,
  sessionExpired,
  paymentFailed,
}

class SystemStatusScreen extends StatefulWidget {
  final SystemState initialState;

  const SystemStatusScreen({super.key, this.initialState = SystemState.maintenance});

  @override
  State<SystemStatusScreen> createState() => _SystemStatusScreenState();
}

class _SystemStatusScreenState extends State<SystemStatusScreen> {
  late SystemState _currentState;

  @override
  void initState() {
    super.initState();
    _currentState = widget.initialState;
  }

  Map<String, dynamic> _getStateConfig() {
    switch (_currentState) {
      case SystemState.maintenance:
        return {
          'icon': Icons.engineering_rounded,
          'color': const Color(0xFFD97706),
          'title': 'Scheduled Maintenance',
          'desc': 'Ally is currently undergoing scheduled platform upgrades to serve you better. We will be back online shortly!',
          'primary': 'Check Status',
          'secondary': 'Contact Support',
        };
      case SystemState.serverError:
        return {
          'icon': Icons.dns_rounded,
          'color': const Color(0xFFEF4444),
          'title': '500 • Server Error',
          'desc': 'Something went wrong on our end. Our technical team has been notified.',
          'primary': 'Try Again',
          'secondary': 'Go to Home',
        };
      case SystemState.notFound:
        return {
          'icon': Icons.map_rounded,
          'color': const Color(0xFF64748B),
          'title': '404 • Page Not Found',
          'desc': 'The page or service screen you are looking for doesn\'t exist or has been moved.',
          'primary': 'Back to Home',
          'secondary': null,
        };
      case SystemState.comingSoon:
        return {
          'icon': Icons.auto_awesome_rounded,
          'color': const Color(0xFF2563EB),
          'title': 'Coming Soon! 🚀',
          'desc': 'We are expanding our services to your locality very soon! Stay tuned for launch updates.',
          'primary': 'Notify Me',
          'secondary': 'Explore Other Services',
        };
      case SystemState.forceUpdate:
        return {
          'icon': Icons.system_update_rounded,
          'color': const Color(0xFF16A34A),
          'title': 'App Update Required',
          'desc': 'A brand new version of Ally is available with enhanced safety features & faster technician dispatch.',
          'primary': 'Update Now',
          'secondary': null,
        };
      case SystemState.sessionExpired:
        return {
          'icon': Icons.lock_clock_rounded,
          'color': const Color(0xFF0EA5E9),
          'title': 'Session Expired',
          'desc': 'Your security session has expired. Please log in again to manage your bookings.',
          'primary': 'Log In Now',
          'secondary': null,
        };
      case SystemState.paymentFailed:
        return {
          'icon': Icons.payment_rounded,
          'color': const Color(0xFFEF4444),
          'title': 'Payment Failed',
          'desc': 'We were unable to charge your account. No money was deducted from your bank.',
          'primary': 'Retry Payment',
          'secondary': 'Change Payment Method',
        };
    }
  }

  @override
  Widget build(BuildContext context) {
    final cfg = _getStateConfig();
    final iconColor = cfg['color'] as Color;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text('System Status Demo', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              // ── State Selector Bar (For testing demo) ───────────────
              SizedBox(
                height: 36,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: SystemState.values.map((st) {
                    final isSel = _currentState == st;
                    return Padding(
                      padding: const EdgeInsets.only(right: 6),
                      child: ChoiceChip(
                        label: Text(st.name),
                        selected: isSel,
                        selectedColor: const Color(0xFF2563EB),
                        labelStyle: TextStyle(fontSize: 10, fontWeight: isSel ? FontWeight.w800 : FontWeight.w500, color: isSel ? Colors.white : const Color(0xFF475569)),
                        onSelected: (_) => setState(() => _currentState = st),
                      ),
                    );
                  }).toList(),
                ),
              ),

              const Spacer(),

              // ── Illustration Badge ──────────────────────────────────
              Container(
                width: 110,
                height: 110,
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(cfg['icon'] as IconData, color: iconColor, size: 52),
              ),

              const SizedBox(height: 28),

              Text(
                cfg['title'] as String,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF0F172A)),
              ),

              const SizedBox(height: 8),

              Text(
                cfg['desc'] as String,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
              ),

              const Spacer(),

              // ── Primary Action ─────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text(cfg['primary'] as String, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                ),
              ),

              if (cfg['secondary'] != null) ...[
                const SizedBox(height: 10),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: TextButton(
                    onPressed: () {},
                    child: Text(cfg['secondary'] as String, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF64748B))),
                  ),
                ),
              ],

              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }
}
