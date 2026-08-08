// File: lib/customer/normal_booking/booking_success_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../models/booking_model.dart';
import '../../l10n/app_translations.dart';

class BookingSuccessScreen extends StatelessWidget {
  final BookingModel? booking;

  const BookingSuccessScreen({
    super.key,
    this.booking,
  });

  @override
  Widget build(BuildContext context) {
    final routeArgs = ModalRoute.of(context)?.settings.arguments;
    BookingModel? b = booking;
    if (routeArgs is Map<String, dynamic> && routeArgs['booking'] is BookingModel) {
      b = routeArgs['booking'] as BookingModel;
    }

    final bookingNumber = b?.bookingNumber ?? 'KS202600001';
    final serviceName = b?.serviceSnapshot.name ?? 'Home Service';
    final addressLine = b?.addressSnapshot.shortAddress ?? 'Service Location';
    final scheduledDate = b?.scheduledDate ?? 'Today';
    final scheduledTime = b?.scheduledTime ?? 'Flexible';
    final status = (b?.status ?? 'pending').toUpperCase();

    return Scaffold(      appBar: AppBar(
        automaticallyImplyLeading: false,        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.close_rounded),
            onPressed: () => Navigator.pushNamedAndRemoveUntil(
              context,
              AppRoutes.customerHome,
              (route) => false,
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
        child: Column(
          children: [
            SizedBox(height: 20),

            // Success Green Badge / Animation Placeholder
            Container(
              width: 88,
              height: 88,
              decoration: BoxDecoration(
                color: Color(0xFFDCFCE7),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.check_circle_rounded,
                color: Color(0xFF16A34A),
                size: 56,
              ),
            ),

            SizedBox(height: 20),

            Text('booking_successful'.tr(context),
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w900,
              ),
            ),
            SizedBox(height: 6),
            Text('your_booking_request_has_been'.tr(context),
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13),
            ),

            SizedBox(height: 24),

            // Booking Number Badge
            Container(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.divider),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('booking_id_2'.tr(context), style: TextStyle(fontSize: 13)),
                  Text(
                    bookingNumber,
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: AppColors.primary),
                  ),
                  SizedBox(width: 8),
                  GestureDetector(
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: bookingNumber));
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('booking_id_copied_to_clipboard'.tr(context))),
                      );
                    },
                    child: Icon(Icons.copy_rounded, size: 16, color: AppColors.primary),
                  ),
                ],
              ),
            ),

            SizedBox(height: 28),

            // Booking Summary Details Card
            Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.divider),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  _buildDetailRow(
                    icon: Icons.build_circle_rounded,
                    label: 'Service',
                    value: serviceName,
                  ),
                  Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.location_on_rounded,
                    label: 'Address',
                    value: addressLine,
                  ),
                  Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.calendar_month_rounded,
                    label: 'Scheduled Date',
                    value: scheduledDate,
                  ),
                  Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.access_time_rounded,
                    label: 'Scheduled Time',
                    value: scheduledTime,
                  ),
                  Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.info_outline_rounded,
                    label: 'Status',
                    valueWidget: Container(
                      padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFEF3C7),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        status,
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFD97706)),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            SizedBox(height: 36),

            // Navigation Buttons
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pushNamed(context, AppRoutes.customerBookings);
                },
                icon: Icon(Icons.list_alt_rounded),
                label: Text('view_my_bookings'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                ),
              ),
            ),

            SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: OutlinedButton.icon(
                onPressed: () {
                  Navigator.pushNamedAndRemoveUntil(
                    context,
                    AppRoutes.customerHome,
                    (route) => false,
                  );
                },
                icon: Icon(Icons.home_rounded),
                label: Text('back_to_home'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Theme.of(context).dividerColor),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                ),
              ),
            ),

            SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow({
    required IconData icon,
    required String label,
    String? value,
    Widget? valueWidget,
  }) {
    return Row(
      children: [
        Icon(icon, size: 20, color: AppColors.primary),
        SizedBox(width: 10),
        Text(label, style: TextStyle(fontSize: 13)),
        Spacer(),
        if (valueWidget != null)
          valueWidget
        else
          Expanded(
            child: Text(
              value ?? '',
              textAlign: TextAlign.end,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
            ),
          ),
      ],
    );
  }
}
