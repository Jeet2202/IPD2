// File: lib/customer/normal_booking/booking_success_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../models/booking_model.dart';

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

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.close_rounded, color: AppColors.textPrimary),
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
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
        child: Column(
          children: [
            const SizedBox(height: 20),

            // Success Green Badge / Animation Placeholder
            Container(
              width: 88,
              height: 88,
              decoration: const BoxDecoration(
                color: Color(0xFFDCFCE7),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle_rounded,
                color: Color(0xFF16A34A),
                size: 56,
              ),
            ),

            const SizedBox(height: 20),

            const Text(
              'Booking Successful!',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w900,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Your booking request has been submitted successfully.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),

            const SizedBox(height: 24),

            // Booking Number Badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.divider),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Booking ID: ', style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
                  Text(
                    bookingNumber,
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: AppColors.primary),
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: bookingNumber));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Booking ID copied to clipboard')),
                      );
                    },
                    child: const Icon(Icons.copy_rounded, size: 16, color: AppColors.primary),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 28),

            // Booking Summary Details Card
            Container(
              padding: const EdgeInsets.all(20),
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
                  const Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.location_on_rounded,
                    label: 'Address',
                    value: addressLine,
                  ),
                  const Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.calendar_month_rounded,
                    label: 'Scheduled Date',
                    value: scheduledDate,
                  ),
                  const Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.access_time_rounded,
                    label: 'Scheduled Time',
                    value: scheduledTime,
                  ),
                  const Divider(height: 20, color: AppColors.divider),
                  _buildDetailRow(
                    icon: Icons.info_outline_rounded,
                    label: 'Status',
                    valueWidget: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFEF3C7),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        status,
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFD97706)),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 36),

            // Navigation Buttons
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pushNamed(context, AppRoutes.customerBookings);
                },
                icon: const Icon(Icons.list_alt_rounded),
                label: const Text('View My Bookings', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                ),
              ),
            ),

            const SizedBox(height: 12),

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
                icon: const Icon(Icons.home_rounded),
                label: const Text('Back to Home', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.textPrimary,
                  side: const BorderSide(color: AppColors.divider),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                ),
              ),
            ),

            const SizedBox(height: 24),
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
        const SizedBox(width: 10),
        Text(label, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
        const Spacer(),
        if (valueWidget != null)
          valueWidget
        else
          Expanded(
            child: Text(
              value ?? '',
              textAlign: TextAlign.end,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
          ),
      ],
    );
  }
}
