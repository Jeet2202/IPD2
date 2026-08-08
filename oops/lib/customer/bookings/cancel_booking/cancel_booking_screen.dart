// File:
// lib/customer/bookings/cancel_booking/cancel_booking_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class CancelBookingScreen extends StatefulWidget {
  const CancelBookingScreen({super.key});

  @override
  State<CancelBookingScreen> createState() => _CancelBookingScreenState();
}

class _CancelBookingScreenState extends State<CancelBookingScreen> {
  String _selectedReason = 'Booked by mistake';
  final TextEditingController _commentsController = TextEditingController();

  final List<String> _cancellationReasons = [
    'Booked by mistake',
    'Provider was delayed / unavailable',
    'Problem resolved on its own',
    'Found lower price elsewhere',
    'Plans changed / Emergency',
  ];

  @override
  void dispose() {
    _commentsController.dispose();
    super.dispose();
  }

  void _showCancellationDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: Text('cancel_booking'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
        content: Text('are_you_sure_you_want'.tr(context),
          style: TextStyle(fontSize: 13, color: Color(0xFF64748B), height: 1.4),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('keep_booking'.tr(context), style: TextStyle(color: Color(0xFF64748B), fontWeight: FontWeight.w700)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: Text('yes_cancel_now'.tr(context), style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('cancel_booking_2'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Refund Banner ──────────────────────────────────────
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCFCE7),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFF86EFAC)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.account_balance_wallet_rounded, color: Color(0xFF16A34A), size: 28),
                      SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('100_refund_eligible'.tr(context), style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF15803D))),
                            SizedBox(height: 2),
                            Text('full_4850_credited_to_ally'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF14532D))),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 24),

                // ── Select Reason ──────────────────────────────────────
                Text('reason_for_cancellation'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 12),

                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: Column(
                    children: _cancellationReasons.map((reason) {
                      final isSelected = _selectedReason == reason;
                      return RadioListTile<String>(
                        title: Text(reason, style: TextStyle(fontSize: 13, fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500, color: const Color(0xFF0F172A))),
                        value: reason,
                        groupValue: _selectedReason,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _selectedReason = val!),
                      );
                    }).toList(),
                  ),
                ),

                SizedBox(height: 20),

                // ── Additional Comments ────────────────────────────────
                Text('additional_comments_optional'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                SizedBox(height: 8),

                Container(
                  padding: EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE2E8F0)),
                  ),
                  child: TextField(
                    controller: _commentsController,
                    maxLines: 3,
                    style: TextStyle(fontSize: 13, color: Color(0xFF0F172A)),
                    decoration: const InputDecoration(
                      hintText: 'Tell us how we can improve our service...',
                      hintStyle: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                      border: InputBorder.none,
                    ),
                  ),
                ),

                SizedBox(height: 100),
              ],
            ),
          ),

          // ── Sticky Cancel Button ───────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 20, offset: const Offset(0, -4)),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: _showCancellationDialog,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFEF4444),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  ),
                  child: Text('confirm_cancellation'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
