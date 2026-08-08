import 'package:flutter/material.dart';
import '../models/booking_model.dart';
import '../l10n/app_translations.dart';

class BookingLifecycleStepper extends StatelessWidget {
  final BookingModel booking;

  const BookingLifecycleStepper({
    super.key,
    required this.booking,
  });

  int _getCurrentStep() {
    switch (booking.status.toLowerCase()) {
      case 'pending':
        return 0;
      case 'assigned':
      case 'accepted':
        return 1;
      case 'worker_en_route':
        return 2;
      case 'arrived':
        return 3;
      case 'in_progress':
        return 4;
      case 'work_completed':
        return 5;
      case 'customer_confirmed':
      case 'completed':
        return 6;
      case 'cancelled':
        return -1;
      default:
        return 0;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentStep = _getCurrentStep();

    if (currentStep == -1) {
      return Card(
        color: Colors.red.shade50,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(color: Colors.red.shade200),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Icon(Icons.cancel_rounded, color: Colors.red.shade700, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('statuscancelled'.tr(context).tr(context),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade900,
                      ),
                    ),
                    if (booking.cancellationReason != null)
                      Text(
                        '${'status_cancelled'.tr(context)}: ${booking.cancellationReason}',
                        style: theme.textTheme.bodySmall?.copyWith(color: Colors.red.shade800),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
    }

    final steps = [
      {'title': 'status_pending'.tr(context), 'subtitle': 'status_pending'.tr(context)},
      {'title': 'status_assigned'.tr(context), 'subtitle': 'worker_assigned'.tr(context)},
      {'title': 'status_en_route'.tr(context), 'subtitle': 'status_en_route'.tr(context)},
      {'title': 'status_arrived'.tr(context), 'subtitle': 'status_arrived'.tr(context)},
      {'title': 'status_in_progress'.tr(context), 'subtitle': 'status_in_progress'.tr(context)},
      {'title': 'status_work_completed'.tr(context), 'subtitle': 'status_work_completed'.tr(context)},
      {'title': 'status_completed'.tr(context), 'subtitle': 'status_completed'.tr(context)},
    ];

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('bookingdetails'.tr(context).tr(context),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getStatusColor(booking.status).withOpacity(0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _getStatusText(context, booking.status),
                    style: TextStyle(
                      color: _getStatusColor(booking.status),
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: steps.length,
              itemBuilder: (context, index) {
                final isDone = index <= currentStep;
                final isCurrent = index == currentStep;

                Color circleColor = Colors.grey.shade300;
                IconData iconData = Icons.circle_outlined;
                Color textColor = Colors.grey.shade600;

                if (isDone) {
                  circleColor = isCurrent ? theme.primaryColor : Colors.green;
                  iconData = isCurrent ? Icons.play_arrow_rounded : Icons.check_rounded;
                  textColor = isCurrent ? theme.primaryColor : Colors.black87;
                }

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Column(
                      children: [
                        Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: isDone ? circleColor : Colors.transparent,
                            border: Border.all(color: circleColor, width: 2),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            iconData,
                            size: 16,
                            color: isDone ? Colors.white : Colors.grey.shade400,
                          ),
                        ),
                        if (index < steps.length - 1)
                          Container(
                            width: 2,
                            height: 24,
                            color: (index < currentStep) ? Colors.green : Colors.grey.shade300,
                          ),
                      ],
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Padding(
                        padding: const EdgeInsets.only(top: 2.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              steps[index]['title']!,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                                color: textColor,
                              ),
                            ),
                            Text(
                              steps[index]['subtitle']!,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: Colors.grey.shade600,
                                fontSize: 11,
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Colors.orange;
      case 'assigned':
      case 'accepted':
        return Colors.blue;
      case 'worker_en_route':
        return Colors.indigo;
      case 'arrived':
        return Colors.purple;
      case 'in_progress':
        return Colors.amber.shade800;
      case 'work_completed':
        return Colors.teal;
      case 'customer_confirmed':
      case 'completed':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  String _getStatusText(BuildContext context, String status) {
    switch (status.toLowerCase()) {
      case 'pending': return 'status_pending'.tr(context);
      case 'assigned':
      case 'accepted': return 'status_assigned'.tr(context);
      case 'worker_en_route': return 'status_en_route'.tr(context);
      case 'arrived': return 'status_arrived'.tr(context);
      case 'in_progress': return 'status_in_progress'.tr(context);
      case 'work_completed': return 'status_work_completed'.tr(context);
      case 'completed': return 'status_completed'.tr(context);
      case 'cancelled': return 'status_cancelled'.tr(context);
      default: return status.toUpperCase().replaceAll('_', ' ');
    }
  }
}
