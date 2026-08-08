// File:
// lib/customer/inspection_booking/live_inspection_tracking/live_inspection_tracking_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class LiveInspectionTrackingScreen extends StatelessWidget {
  const LiveInspectionTrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      body: Stack(
        children: [
          // ── Map Canvas Canvas ─────────────────────────────────────
          Positioned.fill(
            child: Container(
              color: const Color(0xFFE2E8F0),
              child: Stack(
                children: [
                  Positioned.fill(child: CustomPaint(painter: _InspectorMapPainter())),
                  Positioned(
                    top: 48,
                    left: 20,
                    child: GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 10),
                          ],
                        ),
                        child: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A), size: 20),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 48,
                    right: 20,
                    child: Container(
                      padding: EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 10),
                        ],
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.search_rounded, size: 16, color: Color(0xFF2563EB)),
                          SizedBox(width: 6),
                          Text('12_km_est_10_mins'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Draggable Inspector Tracking Sheet ─────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 16, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: 24, offset: const Offset(0, -6)),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 36,
                      height: 4,
                      decoration: BoxDecoration(
                        color: const Color(0xFFCBD5E1),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('sunil_is_en_route_for'.tr(context), style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                          SizedBox(height: 2),
                          Text('carrying_diagnostic_multimeter_kit'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))),
                        ],
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                        child: Text('on_time'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                      ),
                    ],
                  ),
                  SizedBox(height: 16),
                  Divider(color: Color(0xFFF1F5F9), height: 1),
                  SizedBox(height: 14),

                  // Inspector Contact Card
                  Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: const Color(0xFFDBEAFE),
                          shape: BoxShape.circle,
                          border: Border.all(color: const Color(0xFF2563EB), width: 1.5),
                        ),
                        child: Icon(Icons.engineering_rounded, size: 28, color: Color(0xFF2563EB)),
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('sunil_verma'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                            SizedBox(height: 2),
                            Text('tvs_jupiter_ka03hl8812'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: Container(
                          padding: EdgeInsets.all(8),
                          decoration: BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                          child: Icon(Icons.call_rounded, color: Color(0xFF2563EB), size: 20),
                        ),
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('calling_inspector_sunil_verma_91'.tr(context)), backgroundColor: Color(0xFF16A34A)),
                          );
                        },
                      ),
                      IconButton(
                        icon: Container(
                          padding: EdgeInsets.all(8),
                          decoration: BoxDecoration(color: Color(0xFFEFF6FF), shape: BoxShape.circle),
                          child: Icon(Icons.chat_bubble_outline_rounded, color: Color(0xFF2563EB), size: 20),
                        ),
                        onPressed: () => Navigator.pushNamed(context, AppRoutes.customerChat),
                      ),
                    ],
                  ),

                  SizedBox(height: 18),

                  // Actions Row
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('inspection_tracking_link_copied_to'.tr(context))),
                            );
                          },
                          icon: Icon(Icons.share_location_rounded, size: 18),
                          label: Text('share_status'.tr(context)),
                          style: OutlinedButton.styleFrom(
                            padding: EdgeInsets.symmetric(vertical: 14),
                            side: BorderSide(color: Color(0xFFE2E8F0)),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        ),
                      ),
                      SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            showDialog(
                              context: context,
                              builder: (ctx) => AlertDialog(
                                title: Text('inspection_start_otp'.tr(context)),
                                content: Text('share_code_7391_with_inspector'.tr(context)),
                                actions: [
                                  TextButton(onPressed: () => Navigator.pop(ctx), child: Text('ok'.tr(context))),
                                ],
                              ),
                            );
                          },
                          icon: Icon(Icons.qr_code_rounded, size: 18),
                          label: Text('show_otp_7391'.tr(context)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            padding: EdgeInsets.symmetric(vertical: 14),
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InspectorMapPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = const Color(0xFFCBD5E1)
      ..strokeWidth = 1;
    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), gridPaint);
    }
    for (double j = 0; j < size.height; j += 30) {
      canvas.drawLine(Offset(0, j), Offset(size.width, j), gridPaint);
    }

    final routePaint = Paint()
      ..color = const Color(0xFF2563EB)
      ..strokeWidth = 5
      ..style = PaintingStyle.stroke;
    final path = Path()
      ..moveTo(size.width * 0.3, size.height * 0.35)
      ..lineTo(size.width * 0.45, size.height * 0.48)
      ..lineTo(size.width * 0.65, size.height * 0.65);
    canvas.drawPath(path, routePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
