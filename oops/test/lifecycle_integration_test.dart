import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oops/models/booking_model.dart';
import 'package:oops/models/review_model.dart';
import 'package:oops/widgets/booking_lifecycle_stepper.dart';
import 'package:oops/widgets/booking_timeline_widget.dart';

void main() {
  group('Phase 4.7.7 Flutter Lifecycle Integration Tests', () {
    test('BookingModel status getters and execution fields', () {
      final json = {
        'id': '6a70ad3af880b54aa83e79d0',
        'booking_number': 'KS202600100',
        'customer_id': 'cust123',
        'booking_type': 'normal_service',
        'status': 'work_completed',
        'service_snapshot': {'name': 'AC Servicing'},
        'address_snapshot': {'full_name': 'Test User'},
        'completion_notes': 'Refilled gas',
        'work_summary': 'Done',
        'before_photos': ['http://img1.jpg'],
        'after_photos': ['http://img2.jpg'],
        'timeline': [
          {
            'event_id': 'e1',
            'status': 'work_completed',
            'title': 'Work Completed',
            'actor_id': 'w1',
            'actor_role': 'worker',
            'timestamp': '2026-08-03T12:00:00Z',
          }
        ]
      };

      final booking = BookingModel.fromJson(json);
      expect(booking.isWorkCompleted, isTrue);
      expect(booking.completionNotes, equals('Refilled gas'));
      expect(booking.beforePhotos.length, equals(1));
      expect(booking.timeline.length, equals(1));
      expect(booking.timeline.first.title, equals('Work Completed'));
    });

    test('ReviewModel deserialization', () {
      final json = {
        'id': 'rev123',
        'booking_id': 'b123',
        'worker_id': 'w123',
        'customer_id': 'c123',
        'overall_rating': 5.0,
        'punctuality_rating': 5.0,
        'quality_rating': 4.5,
        'professionalism_rating': 5.0,
        'communication_rating': 5.0,
        'review_title': 'Excellent Work',
        'review_comment': 'Great job done!',
        'would_recommend': true,
        'created_at': '2026-08-03T14:00:00Z',
        'updated_at': '2026-08-03T14:00:00Z',
      };

      final review = ReviewModel.fromJson(json);
      expect(review.overallRating, equals(5.0));
      expect(review.wouldRecommend, isTrue);
      expect(review.reviewTitle, equals('Excellent Work'));
    });

    testWidgets('BookingLifecycleStepper renders without error', (WidgetTester tester) async {
      final booking = BookingModel(
        id: '1',
        bookingNumber: 'KS100',
        customerId: 'c1',
        bookingType: 'normal_service',
        status: 'in_progress',
        serviceSnapshot: ServiceSnapshotModel.fromJson(const {'service_id': 's1', 'name': 'Plumbing'}),
        addressSnapshot: AddressSnapshotModel.fromJson(const {'address_id': 'a1', 'full_name': 'John'}),
        createdAt: '2026-08-03',
        updatedAt: '2026-08-03',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BookingLifecycleStepper(booking: booking),
          ),
        ),
      );

      expect(find.text('Service Journey'), findsOneWidget);
      expect(find.text('In-Progress'), findsOneWidget);
    });

    testWidgets('BookingTimelineWidget renders without error', (WidgetTester tester) async {
      final events = [
        const BookingTimelineEventModel(
          eventId: 'e1',
          status: 'assigned',
          title: 'Worker Assigned',
          actorId: 'w1',
          actorRole: 'system',
          timestamp: '2026-08-03T10:00:00Z',
        ),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BookingTimelineWidget(events: events),
          ),
        ),
      );

      expect(find.text('Audit Activity Timeline'), findsOneWidget);
      expect(find.text('Worker Assigned'), findsOneWidget);
    });
  });
}
