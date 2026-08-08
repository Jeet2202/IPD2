import 'package:flutter/material.dart';
import '../../../services/notification_service.dart';
import '../../l10n/app_translations.dart';

class NotificationPreferencesScreen extends StatefulWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  State<NotificationPreferencesScreen> createState() => _NotificationPreferencesScreenState();
}

class _NotificationPreferencesScreenState extends State<NotificationPreferencesScreen> {
  bool _isLoading = true;
  String? _errorMessage;

  bool _promotional = true;
  bool _booking = true;
  bool _messages = true;
  bool _system = true;
  bool _quietHoursEnabled = false;
  String _quietHoursStart = '22:00';
  String _quietHoursEnd = '07:00';

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    try {
      final data = await NotificationService.instance.getPreferences();
      if (!mounted) return;
      setState(() {
        // Backend field names: booking_notifications, chat_notifications,
        // promotional_notifications, quiet_hours_enabled, quiet_hours_start, quiet_hours_end
        _promotional = data['promotional_notifications'] as bool? ?? true;
        _booking = data['booking_notifications'] as bool? ?? true;
        _messages = data['chat_notifications'] as bool? ?? true;
        _system = data['ai_notifications'] as bool? ?? true;
        _quietHoursEnabled = data['quiet_hours_enabled'] as bool? ?? false;
        _quietHoursStart = data['quiet_hours_start'] as String? ?? '22:00';
        _quietHoursEnd = data['quiet_hours_end'] as String? ?? '07:00';
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _savePreferences() async {
    try {
      await NotificationService.instance.updatePreferences({
        // Backend field names must match PreferencesUpdate schema
        'promotional_notifications': _promotional,
        'booking_notifications': _booking,
        'chat_notifications': _messages,
        'ai_notifications': _system,
        'quiet_hours_enabled': _quietHoursEnabled,
        'quiet_hours_start': _quietHoursStart,
        'quiet_hours_end': _quietHoursEnd,
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('preferences_saved_successfully'.tr(context)),
            backgroundColor: Color(0xFF10B981),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save preferences: $e'),
            backgroundColor: const Color(0xFFEF4444),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        title: Text('notification_preferences'.tr(context),
          style: TextStyle(color: Color(0xFF0F172A), fontSize: 18, fontWeight: FontWeight.w700),
        ),
        iconTheme: const IconThemeData(color: Color(0xFF0F172A)),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : _errorMessage != null
              ? Center(child: Text('Error: $_errorMessage', style: TextStyle(color: Colors.red)))
              : ListView(
                  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 24),
                  children: [
                    _buildSectionHeader('Notification Types'),
                    _buildSwitchTile('Booking Updates', 'Status changes and reminders', _booking, (val) {
                      setState(() => _booking = val);
                      _savePreferences();
                    }),
                    _buildSwitchTile('Messages', 'New messages and media', _messages, (val) {
                      setState(() => _messages = val);
                      _savePreferences();
                    }),
                    _buildSwitchTile('System Alerts', 'Account security and system info', _system, (val) {
                      setState(() => _system = val);
                      _savePreferences();
                    }),
                    _buildSwitchTile('Promotions', 'Offers and recommendations', _promotional, (val) {
                      setState(() => _promotional = val);
                      _savePreferences();
                    }),
                    SizedBox(height: 32),
                    _buildSectionHeader('Quiet Hours'),
                    _buildSwitchTile('Enable Quiet Hours', 'Mute non-system notifications during these hours', _quietHoursEnabled, (val) {
                      setState(() => _quietHoursEnabled = val);
                      _savePreferences();
                    }),
                    if (_quietHoursEnabled) ...[
                      SizedBox(height: 16),
                      _buildTimeSelector('Start Time', _quietHoursStart, (val) {
                        setState(() => _quietHoursStart = val);
                        _savePreferences();
                      }),
                      _buildTimeSelector('End Time', _quietHoursEnd, (val) {
                        setState(() => _quietHoursEnd = val);
                        _savePreferences();
                      }),
                    ],
                  ],
                ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Color(0xFF64748B),
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  Widget _buildSwitchTile(String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: SwitchListTile(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        title: Text(title, style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF0F172A))),
        subtitle: Text(subtitle, style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
        value: value,
        activeColor: const Color(0xFF2563EB),
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildTimeSelector(String label, String time, ValueChanged<String> onTimeSelected) {
    return Container(
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF0F172A))),
          InkWell(
            onTap: () async {
              final timeParts = time.split(':');
              final initialTime = TimeOfDay(hour: int.parse(timeParts[0]), minute: int.parse(timeParts[1]));
              final selected = await showTimePicker(context: context, initialTime: initialTime);
              if (selected != null) {
                final hh = selected.hour.toString().padLeft(2, '0');
                final mm = selected.minute.toString().padLeft(2, '0');
                onTimeSelected('$hh:$mm');
              }
            },
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                time,
                style: TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
