// File: lib/customer/support/contact_support/contact_support_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../models/support_model.dart';
import '../../../services/support_service.dart';

class ContactSupportScreen extends StatefulWidget {
  const ContactSupportScreen({super.key});

  @override
  State<ContactSupportScreen> createState() => _ContactSupportScreenState();
}

class _ContactSupportScreenState extends State<ContactSupportScreen> {
  final SupportService _supportService = SupportService.instance;

  bool _isLoading = true;
  ContactInfoModel? _contactInfo;

  @override
  void initState() {
    super.initState();
    _loadContactInfo();
  }

  Future<void> _loadContactInfo() async {
    setState(() => _isLoading = true);
    try {
      final info = await _supportService.fetchContactInfo();
      setState(() {
        _contactInfo = info;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _makePhoneCall() async {
    const numberToCall = '+919579601589';
    await Clipboard.setData(const ClipboardData(text: numberToCall));

    final uri = Uri.parse('tel:$numberToCall');
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
      _showSnackBar('Number $numberToCall copied to clipboard & opening dialer.');
    } catch (_) {
      _showSnackBar('Number $numberToCall copied to clipboard.');
    }
  }

  Future<void> _launchUri(String uriString) async {
    final uri = Uri.parse(uriString);
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      } else {
        _showSnackBar('Could not launch $uriString');
      }
    } catch (_) {
      _showSnackBar('Could not perform action.');
    }
  }

  void _showSnackBar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final info = _contactInfo;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Contact Support',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
            : SingleChildScrollView(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header Banner
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: const Row(
                        children: [
                          CircleAvatar(
                            radius: 26,
                            backgroundColor: Colors.white24,
                            child: Icon(Icons.headset_mic_rounded, color: Colors.white, size: 28),
                          ),
                          SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'We are here to help!',
                                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Colors.white),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  'Reach out to our 24/7 Ally support team anytime.',
                                  style: TextStyle(fontSize: 12, color: Color(0xFFDBEAFE)),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Contact Options
                    _buildContactCard(
                      icon: Icons.call_rounded,
                      title: 'Helpline Phone',
                      value: info?.helplinePhone ?? '+919579601589',
                      color: const Color(0xFF16A34A),
                      actionLabel: 'Call Now',
                      onTap: _makePhoneCall,
                    ),
                    const SizedBox(height: 12),

                    _buildContactCard(
                      icon: Icons.email_rounded,
                      title: 'Support Email',
                      value: info?.email ?? 'support@kaamsetu.com',
                      color: const Color(0xFF2563EB),
                      actionLabel: 'Send Email',
                      onTap: () => _launchUri('mailto:${info?.email ?? 'support@kaamsetu.com'}'),
                    ),
                    const SizedBox(height: 12),

                    if (info?.whatsappNumber != null && info!.whatsappNumber!.isNotEmpty)
                      _buildContactCard(
                        icon: Icons.chat_rounded,
                        title: 'WhatsApp Support',
                        value: info.whatsappNumber!,
                        color: const Color(0xFF25D366),
                        actionLabel: 'Open Chat',
                        onTap: () {
                          final cleanNum = info.whatsappNumber!.replaceAll(RegExp(r'[^0-9]'), '');
                          _launchUri('https://wa.me/$cleanNum');
                        },
                      ),

                    const SizedBox(height: 24),

                    // Operating Hours & Address
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.access_time_rounded, color: Color(0xFF64748B), size: 20),
                              SizedBox(width: 10),
                              Text('Operating Hours', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            info?.operatingHours ?? 'Monday - Saturday: 9:00 AM - 8:00 PM IST',
                            style: const TextStyle(fontSize: 13, color: Color(0xFF475569)),
                          ),
                          if (info?.address != null && info!.address!.isNotEmpty) ...[
                            const Divider(height: 28),
                            const Row(
                              children: [
                                Icon(Icons.location_on_rounded, color: Color(0xFF64748B), size: 20),
                                SizedBox(width: 10),
                                Text('Office Address', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              info.address!,
                              style: const TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.4),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildContactCard({
    required IconData icon,
    required String title,
    required String value,
    required Color color,
    required String actionLabel,
    required VoidCallback onTap,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: color.withOpacity(0.1),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: onTap,
            style: ElevatedButton.styleFrom(
              backgroundColor: color,
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text(actionLabel, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }
}
