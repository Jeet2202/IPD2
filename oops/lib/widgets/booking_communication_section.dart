import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../app/theme/app_colors.dart';
import '../../models/booking_model.dart';
import '../../services/booking_chat_service.dart';
import 'booking_chat_bottom_sheet.dart';
import '../l10n/app_translations.dart';

class BookingCommunicationSection extends StatefulWidget {
  final BookingModel booking;
  final String currentUserId;
  final bool isWorker;

  const BookingCommunicationSection({
    super.key,
    required this.booking,
    required this.currentUserId,
    this.isWorker = false,
  });

  @override
  State<BookingCommunicationSection> createState() => _BookingCommunicationSectionState();
}

class _BookingCommunicationSectionState extends State<BookingCommunicationSection> {
  BookingChatService? _chatService;

  @override
  void initState() {
    super.initState();
    _chatService = BookingChatService(
      bookingId: widget.booking.id,
      currentUserId: widget.currentUserId,
    );
  }

  @override
  void dispose() {
    _chatService?.dispose();
    super.dispose();
  }

  bool _isCommunicationActive() {
    final status = widget.booking.status.toLowerCase();
    return ['assigned', 'accepted', 'worker_en_route', 'arrived', 'in_progress'].contains(status);
  }

  bool _isWorkerEnRoute() {
    return widget.booking.status.toLowerCase() == 'worker_en_route';
  }

  bool _isPending() {
    return widget.booking.status.toLowerCase() == 'pending';
  }

  Future<void> _makePhoneCall(String phoneNumber) async {
    final cleanPhone = phoneNumber.trim();
    if (cleanPhone.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('phone_number_not_available'.tr(context))),
        );
      }
      return;
    }

    // 1. Copy phone number to clipboard
    await Clipboard.setData(ClipboardData(text: cleanPhone));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Copied phone number ($cleanPhone) to clipboard! Opening phone app...'),
          backgroundColor: const Color(0xFF10B981),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }

    // 2. Open phone app via tel: URL scheme
    final Uri launchUri = Uri(
      scheme: 'tel',
      path: cleanPhone,
    );
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('phone_number_copied_but_could'.tr(context))),
        );
      }
    }
  }

  void _openChat() {
    if (_chatService != null) {
      BookingChatBottomSheet.show(context, chatService: _chatService!, isActive: _isCommunicationActive());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.isWorker ? 'Connect with Customer' : 'Connect with your Worker',
            style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800),
          ),
          SizedBox(height: 12),

          if (_isPending()) ...[
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFF1F5F9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(Icons.hourglass_empty_rounded, color: Color(0xFF64748B), size: 20),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text('waiting_for_a_worker_communication'.tr(context),
                      style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                    ),
                  ),
                ],
              ),
            ),
          ] else if (_isCommunicationActive()) ...[
            // Chat Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _openChat,
                icon: Icon(Icons.chat_bubble_rounded, size: 20),
                label: Text(widget.isWorker ? 'Chat with Customer' : 'Chat with Worker'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
              ),
            ),
            SizedBox(height: 12),

            // Call Button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: OutlinedButton.icon(
                onPressed: () {
                  final phone = widget.isWorker 
                      ? widget.booking.addressSnapshot.phone
                      : (widget.booking.workerPhone ?? '');
                  _makePhoneCall(phone);
                },
                icon: Icon(Icons.phone_rounded, size: 20),
                label: Text(widget.isWorker ? 'Call Customer' : 'Call Worker'),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Color(0xFFCBD5E1)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),

            // Live Tracking (Only if Customer and Worker is En Route)
            if (!widget.isWorker && _isWorkerEnRoute()) ...[
              SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                height: 48,
                child: OutlinedButton.icon(
                  onPressed: () {
                    // Navigate to Live Tracking screen (Phase 4 / Phase 7.1)
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('live_tracking_will_be_launched'.tr(context))),
                    );
                  },
                  icon: Icon(Icons.location_on_rounded, size: 20, color: Color(0xFF0D9488)),
                  label: Text('live_track_worker'.tr(context)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF0D9488),
                    side: BorderSide(color: Color(0xFF99F6E4)),
                    backgroundColor: const Color(0xFFF0FDFA),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ]
        ],
      ),
    );
  }
}
