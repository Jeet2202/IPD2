// File: lib/customer/support/help_support/help_support_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../app/routes/app_routes.dart';
import '../../../models/support_model.dart';
import '../../../services/support_service.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class HelpSupportScreen extends StatefulWidget {
  const HelpSupportScreen({super.key});

  @override
  State<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends State<HelpSupportScreen> {
  final SupportService _supportService = SupportService.instance;
  final TextEditingController _searchController = TextEditingController();

  bool _isLoading = true;
  String? _errorMessage;

  List<FAQModel> _faqs = [];
  List<FAQModel> _filteredFaqs = [];
  SupportTicketModel? _activeTicket;
  ContactInfoModel? _contactInfo;
  SOSConfigModel? _sosConfig;

  @override
  void initState() {
    super.initState();
    _loadSupportData();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadSupportData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final results = await Future.wait([
        _supportService.fetchFAQs(),
        _supportService.fetchUserTickets(),
        _supportService.fetchContactInfo(),
        _supportService.fetchSOSConfig(),
      ]);

      final allFaqs = results[0] as List<FAQModel>;
      final userTickets = results[1] as List<SupportTicketModel>;
      final contact = results[2] as ContactInfoModel;
      final sos = results[3] as SOSConfigModel;

      // Find open / in_progress ticket if available
      SupportTicketModel? openTicket;
      for (final t in userTickets) {
        if (t.isOpen) {
          openTicket = t;
          break;
        }
      }
      if (openTicket == null && userTickets.isNotEmpty) {
        openTicket = userTickets.first;
      }

      setState(() {
        _faqs = allFaqs;
        _filteredFaqs = allFaqs;
        _activeTicket = openTicket;
        _contactInfo = contact;
        _sosConfig = sos;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Failed to load support information. Please try again.';
      });
    }
  }

  void _onSearchChanged(String query) {
    if (query.trim().isEmpty) {
      setState(() => _filteredFaqs = _faqs);
      return;
    }

    final q = query.toLowerCase();
    setState(() {
      _filteredFaqs = _faqs.where((faq) {
        return faq.question.toLowerCase().contains(q) ||
            faq.answer.toLowerCase().contains(q) ||
            faq.category.toLowerCase().contains(q);
      }).toList();
    });
  }

  Future<void> _makePhoneCall(String? phoneNumber) async {
    final numberToCall = (phoneNumber != null && phoneNumber.trim().isNotEmpty)
        ? phoneNumber.trim()
        : '+919579601589';
    await Clipboard.setData(ClipboardData(text: numberToCall));

    final cleanNum = numberToCall.replaceAll(RegExp(r'[^0-9+]'), '');
    final uri = Uri.parse('tel:$cleanNum');
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri);
      }
      _showSnackBar('Number $numberToCall copied to clipboard & opening dialer.');
    } catch (_) {
      _showSnackBar('Number $numberToCall copied to clipboard.');
    }
  }

  void _showSnackBar(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(text), behavior: SnackBarBehavior.floating),
    );
  }

  void _showSOSModal() {
    final sos = _sosConfig;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
          ),
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFFCBD5E1),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              SizedBox(height: 16),
              Row(
                children: [
                  Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444), size: 28),
                  SizedBox(width: 10),
                  Text('emergency_assistance'.tr(context),
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF991B1B)),
                  ),
                ],
              ),
              SizedBox(height: 6),
              Text('if_you_are_in_immediate'.tr(context),
                style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
              ),
              SizedBox(height: 20),

              _EmergencyButton(
                icon: Icons.local_police_rounded,
                title: 'Police Helpline',
                number: sos?.policeHelpline ?? '112',
                color: const Color(0xFF1E3A8A),
                onTap: () => _makePhoneCall(sos?.policeHelpline ?? '112'),
              ),
              SizedBox(height: 10),
              _EmergencyButton(
                icon: Icons.female_rounded,
                title: 'Women Helpline',
                number: sos?.womenHelpline ?? '1091',
                color: const Color(0xFFBE185D),
                onTap: () => _makePhoneCall(sos?.womenHelpline ?? '1091'),
              ),
              SizedBox(height: 10),
              _EmergencyButton(
                icon: Icons.medical_services_rounded,
                title: 'Ambulance',
                number: sos?.ambulanceHelpline ?? '108',
                color: const Color(0xFFDC2626),
                onTap: () => _makePhoneCall(sos?.ambulanceHelpline ?? '108'),
              ),
              SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final ticket = _activeTicket;
    final contact = _contactInfo;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
            }
          },
        ),
        title: Text('helpsupport'.tr(context).tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          IconButton(
            icon: Icon(Icons.refresh_rounded, color: Color(0xFF0F172A)),
            onPressed: _loadSupportData,
          ),
        ],
      ),
      body: SafeArea(
        child: _isLoading
            ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
            : RefreshIndicator(
                onRefresh: _loadSupportData,
                color: const Color(0xFF2563EB),
                child: SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
                  padding: EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (_errorMessage != null) ...[
                        Container(
                          padding: EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEF2F2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFFCA5A5)),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.error_outline_rounded, color: Color(0xFFDC2626)),
                              SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  _errorMessage!,
                                  style: TextStyle(fontSize: 12, color: Color(0xFF991B1B)),
                                ),
                              ),
                            ],
                          ),
                        ),
                        SizedBox(height: 16),
                      ],

                      // ── Search Help Bar ──────────────────────────────────────
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.search_rounded, color: Color(0xFF2563EB)),
                            SizedBox(width: 10),
                            Expanded(
                              child: TextField(
                                controller: _searchController,
                                onChanged: _onSearchChanged,
                                decoration: const InputDecoration(
                                  hintText: 'Search help topics, FAQs, booking issues...',
                                  hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                                  border: InputBorder.none,
                                ),
                              ),
                            ),
                            if (_searchController.text.isNotEmpty)
                              IconButton(
                                icon: Icon(Icons.clear_rounded, size: 18, color: Color(0xFF94A3B8)),
                                onPressed: () {
                                  _searchController.clear();
                                  _onSearchChanged('');
                                },
                              ),
                          ],
                        ),
                      ),

                      SizedBox(height: 24),

                      // ── Active Support Ticket Card ───────────────────────────
                      Text('support_ticket_admin_chat'.tr(context),
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      SizedBox(height: 12),

                      GestureDetector(
                        onTap: () {
                          if (ticket != null) {
                            Navigator.pushNamed(
                              context,
                              AppRoutes.liveChat,
                              arguments: {'ticketId': ticket.ticketId},
                            ).then((_) => _loadSupportData());
                          } else {
                            Navigator.pushNamed(context, AppRoutes.raiseComplaint)
                                .then((_) => _loadSupportData());
                          }
                        },
                        child: Container(
                          padding: EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(22),
                            border: Border.all(
                              color: ticket != null ? const Color(0xFF3B82F6) : const Color(0xFFE2E8F0),
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.04),
                                blurRadius: 10,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Row(
                            children: [
                              Container(
                                padding: EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: ticket != null ? const Color(0xFFDBEAFE) : const Color(0xFFF1F5F9),
                                  shape: BoxShape.circle,
                                ),
                                child: Icon(
                                  ticket != null ? Icons.chat_rounded : Icons.add_comment_rounded,
                                  color: ticket != null ? const Color(0xFF2563EB) : const Color(0xFF64748B),
                                  size: 22,
                                ),
                              ),
                              SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          ticket != null ? '#${ticket.ticketId}' : 'Raise a Complaint / Ticket',
                                          style: TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w800,
                                            color: Color(0xFF0F172A),
                                          ),
                                        ),
                                        if (ticket != null)
                                          Container(
                                            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: ticket.isOpen ? const Color(0xFFFEF3C7) : const Color(0xFFDCFCE7),
                                              borderRadius: BorderRadius.circular(8),
                                            ),
                                            child: Text(
                                              ticket.status.toUpperCase(),
                                              style: TextStyle(
                                                fontSize: 10,
                                                fontWeight: FontWeight.w900,
                                                color: ticket.isOpen ? const Color(0xFFD97706) : const Color(0xFF16A34A),
                                              ),
                                            ),
                                          ),
                                      ],
                                    ),
                                    SizedBox(height: 4),
                                    Text(
                                      ticket != null
                                          ? ticket.subject
                                          : 'Tap here to raise a ticket and chat with Ally support team.',
                                      style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                                      overflow: TextOverflow.ellipsis,
                                      maxLines: 1,
                                    ),
                                  ],
                                ),
                              ),
                              SizedBox(width: 8),
                              Icon(Icons.arrow_forward_ios_rounded, size: 14, color: Color(0xFF94A3B8)),
                            ],
                          ),
                        ),
                      ),

                      SizedBox(height: 24),

                      // ── Direct Contact Row ───────────────────────────────────
                      Text('contact_support_247'.tr(context),
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      SizedBox(height: 12),

                      Row(
                        children: [
                          Expanded(
                            child: _ContactBox(
                              icon: Icons.headset_mic_rounded,
                              title: 'Live Chat',
                              sub: 'Chat with Admin',
                              color: const Color(0xFF2563EB),
                              onTap: () {
                                if (ticket != null) {
                                  Navigator.pushNamed(
                                    context,
                                    AppRoutes.liveChat,
                                    arguments: {'ticketId': ticket.ticketId},
                                  ).then((_) => _loadSupportData());
                                } else {
                                  Navigator.pushNamed(context, AppRoutes.raiseComplaint)
                                      .then((_) => _loadSupportData());
                                }
                              },
                            ),
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: _ContactBox(
                              icon: Icons.call_rounded,
                              title: 'Call Us',
                              sub: contact?.helplinePhone ?? '1800-123-4567',
                              color: const Color(0xFF16A34A),
                              onTap: () => _makePhoneCall(contact?.helplinePhone ?? '1800-123-4567'),
                            ),
                          ),
                        ],
                      ),

                      SizedBox(height: 24),

                      // ── Emergency SOS Banner ──────────────────────────────────
                      Container(
                        padding: EdgeInsets.all(18),
                        decoration: BoxDecoration(
                          color: const Color(0xFFFEF2F2),
                          borderRadius: BorderRadius.circular(22),
                          border: Border.all(color: const Color(0xFFFCA5A5)),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444), size: 28),
                            SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('emergency_safety_sos'.tr(context),
                                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF991B1B)),
                                  ),
                                  SizedBox(height: 2),
                                  Text('immediate_assistance_for_active_safety'.tr(context),
                                    style: TextStyle(fontSize: 11, color: Color(0xFF7F1D1D)),
                                    overflow: TextOverflow.ellipsis,
                                    maxLines: 2,
                                  ),
                                ],
                              ),
                            ),
                            ElevatedButton(
                              onPressed: _showSOSModal,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFEF4444),
                                foregroundColor: Colors.white,
                                elevation: 0,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                              child: Text('sos'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900)),
                            ),
                          ],
                        ),
                      ),

                      SizedBox(height: 24),

                      // ── FAQs List ───────────────────────────────────────────
                      Text('frequently_asked_questions'.tr(context),
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                      ),
                      SizedBox(height: 12),

                      if (_filteredFaqs.isEmpty)
                        Container(
                          padding: EdgeInsets.all(20),
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: const Color(0xFFE2E8F0)),
                          ),
                          child: Center(
                            child: Text('no_faqs_found_matching_your'.tr(context),
                              style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                            ),
                          ),
                        )
                      else
                        ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          itemCount: _filteredFaqs.length,
                          itemBuilder: (context, index) {
                            final faq = _filteredFaqs[index];
                            return Container(
                              margin: EdgeInsets.only(bottom: 10),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(color: const Color(0xFFE2E8F0)),
                              ),
                              child: ExpansionTile(
                                shape: Border(),
                                title: Text(
                                  faq.question,
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
                                ),
                                children: [
                                  Padding(
                                    padding: EdgeInsets.fromLTRB(16, 0, 16, 16),
                                    child: Text(
                                      faq.answer,
                                      style: TextStyle(fontSize: 12, color: Color(0xFF475569), height: 1.5),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),

                      SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.06),
              blurRadius: 20,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: 2,
          onTap: (index) {
            if (index == 2) return;
            switch (index) {
              case 0:
                if (Navigator.canPop(context)) {
                  Navigator.pop(context);
                } else {
                  Navigator.pushReplacementNamed(context, AppRoutes.customerHome);
                }
                break;
              case 1:
                Navigator.pushReplacementNamed(context, AppRoutes.myBookings);
                break;
              case 3:
                Navigator.pushReplacementNamed(context, AppRoutes.customerProfile);
                break;
            }
          },
          type: BottomNavigationBarType.fixed,
          selectedItemColor: const Color(0xFF2563EB),
          unselectedItemColor: const Color(0xFF94A3B8),
          selectedLabelStyle: TextStyle(fontWeight: FontWeight.w700, fontSize: 12),
          unselectedLabelStyle: TextStyle(fontWeight: FontWeight.w500, fontSize: 12),
          elevation: 0,
          items: [
            BottomNavigationBarItem(
              icon: Icon(Icons.home_rounded),
              label: 'home'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.calendar_today_rounded),
              label: 'my_bookings'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.headset_mic_rounded),
              label: 'support'.tr(context),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_rounded),
              label: 'profile'.tr(context),
            ),
          ],
        ),
      ),
    );
  }
}

class _ContactBox extends StatelessWidget {
  final IconData icon;
  final String title;
  final String sub;
  final Color color;
  final VoidCallback onTap;

  const _ContactBox({
    required this.icon,
    required this.title,
    required this.sub,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: const Color(0xFFE2E8F0)),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 24),
            SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  SizedBox(height: 2),
                  Text(
                    sub,
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmergencyButton extends StatelessWidget {
  final IconData icon;
  final String title;
  final String number;
  final Color color;
  final VoidCallback onTap;

  const _EmergencyButton({
    required this.icon,
    required this.title,
    required this.number,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: color.withOpacity(0.06),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white, size: 20),
        ),
        title: Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
        subtitle: Text(number, style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.w700)),
        trailing: ElevatedButton.icon(
          onPressed: onTap,
          icon: Icon(Icons.call_rounded, size: 16),
          label: Text('call'.tr(context)),
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: Colors.white,
            elevation: 0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
        ),
      ),
    );
  }
}
