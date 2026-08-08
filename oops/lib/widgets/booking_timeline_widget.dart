import 'package:flutter/material.dart';
import '../models/booking_model.dart';
import '../l10n/app_translations.dart';

class BookingTimelineWidget extends StatelessWidget {
  final List<BookingTimelineEventModel> events;

  const BookingTimelineWidget({
    super.key,
    required this.events,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (events.isEmpty) {
      return Card(
        elevation: 0,
        color: Colors.grey.shade50,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Center(
            child: Text('no_timeline_events_logged_yet'.tr(context),
              style: TextStyle(color: Colors.grey),
            ),
          ),
        ),
      );
    }

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history_rounded, color: theme.primaryColor),
                SizedBox(width: 8),
                Text('audit_activity_timeline'.tr(context),
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: events.length,
              separatorBuilder: (context, index) => Divider(height: 20),
              itemBuilder: (context, index) {
                final event = events[index];
                final roleBadgeColor = _getRoleColor(event.actorRole);

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: roleBadgeColor.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _getEventIcon(event.status),
                        size: 18,
                        color: roleBadgeColor,
                      ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Text(
                                  event.title,
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                              Container(
                                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: roleBadgeColor.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Text(
                                  event.actorRole.toUpperCase(),
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.bold,
                                    color: roleBadgeColor,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          if (event.description != null && event.description!.isNotEmpty) ...[
                            SizedBox(height: 4),
                            Text(
                              event.description!,
                              style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey.shade700),
                            ),
                          ],
                          SizedBox(height: 4),
                          Text(
                            _formatTimestamp(event.timestamp),
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: Colors.grey.shade500,
                              fontSize: 10,
                            ),
                          ),
                        ],
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

  Color _getRoleColor(String role) {
    switch (role.toLowerCase()) {
      case 'customer':
        return Colors.blue;
      case 'worker':
        return Colors.orange.shade800;
      case 'admin':
        return Colors.purple;
      default:
        return Colors.teal;
    }
  }

  IconData _getEventIcon(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return Icons.note_add_rounded;
      case 'assigned':
      case 'accepted':
        return Icons.person_add_rounded;
      case 'worker_en_route':
        return Icons.directions_car_rounded;
      case 'arrived':
        return Icons.location_on_rounded;
      case 'in_progress':
        return Icons.build_circle_rounded;
      case 'work_completed':
        return Icons.task_alt_rounded;
      case 'customer_confirmed':
      case 'completed':
        return Icons.verified_rounded;
      case 'cancelled':
        return Icons.cancel_rounded;
      default:
        return Icons.event_note_rounded;
    }
  }

  String _formatTimestamp(String ts) {
    if (ts.isEmpty) return '';
    try {
      final dt = DateTime.parse(ts).toLocal();
      return '${dt.day}/${dt.month}/${dt.year} at ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return ts;
    }
  }
}
