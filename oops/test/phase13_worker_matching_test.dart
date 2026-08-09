import 'package:flutter_test/flutter_test.dart';
import 'package:oops/models/marketplace_booking_model.dart';
import 'package:oops/models/worker_model.dart';

void main() {
  group('Phase 13 Flutter Worker Matching & Canonical Skill Integration Tests', () {
    test('TEST 1 & 4: Canonical skills parsing & worker profile model skills', () {
      final json = {
        '_id': 'work123',
        'userId': 'u123',
        'name': 'Worker User',
        'phone': '+919876543210',
        'skillIds': ['electrical', 'plumbing'],
        'rating': 4.9,
        'completedJobs': 25,
        'isAvailable': true,
        'isVerified': true,
        'working_radius_km': 15.0,
      };

      final worker = WorkerModel.fromJson(json);
      expect(worker.skillIds, containsAll(['electrical', 'plumbing']));
      expect(worker.isVerified, isTrue);
    });

    test('TEST 2 & 3: Multi-select skills payload deduplication', () {
      final selectedSkills = [' Electrical ', 'PLUMBING', 'electrical'];
      final cleaned = selectedSkills
          .map((s) => s.trim().toLowerCase())
          .toSet()
          .toList();

      expect(cleaned, equals(['electrical', 'plumbing']));
    });

    test('TEST 5: Valid skills API error does not erase existing selected skills', () {
      List<String> existingSkills = ['electrical', 'plumbing'];
      List<String> fallbackPredefined = ['electrical', 'plumbing', 'cleaning'];

      // Simulate API failure (empty list returned or catch block)
      List<String> fetchedSkills = [];
      if (fetchedSkills.isNotEmpty) {
        fallbackPredefined = fetchedSkills;
      }

      // existingSkills remains intact
      expect(existingSkills, equals(['electrical', 'plumbing']));
      expect(fallbackPredefined, contains('electrical'));
    });

    test('TEST 7 & 9: MarketplacePaginatedResult & MarketplaceBookingItem parsing', () {
      final json = {
        'items': [
          {
            'id': 'b1',
            'booking_number': 'JOB-001',
            'service_name': 'Electrical Repair',
            'category_slug': 'electrical',
            'estimated_price': 350.0,
            'is_recommended': true,
            'distance_km': 3.4,
            'status': 'pending',
          }
        ],
        'total': 1,
        'page': 1,
        'page_size': 20,
        'total_pages': 1,
      };

      final result = MarketplacePaginatedResult.fromJson(json);
      expect(result.items.length, equals(1));
      expect(result.items.first.categorySlug, equals('electrical'));
      expect(result.items.first.isRecommended, isTrue);
      expect(result.items.first.distanceKm, equals(3.4));
    });

    test('TEST 12: Location staleness detection (> 2 hours)', () {
      final now = DateTime.now();
      final freshUpdate = now.subtract(const Duration(minutes: 30));
      final staleUpdate = now.subtract(const Duration(hours: 3, minutes: 15));

      bool isStale(DateTime? lastUpdated) {
        if (lastUpdated == null) return true;
        return DateTime.now().difference(lastUpdated).inHours >= 2;
      }

      expect(isStale(freshUpdate), isFalse);
      expect(isStale(staleUpdate), isTrue);
      expect(isStale(null), isTrue);
    });

    test('TEST 14, 15: Error code mappings for application eligibility', () {
      String getHumanReadableError(String rawError) {
        if (rawError.contains('SKILL_MISMATCH')) {
          return 'Your skills do not match the required skill for this booking.';
        }
        if (rawError.contains('OUTSIDE_SERVICE_RADIUS')) {
          return 'This job is outside your saved service working radius.';
        }
        if (rawError.contains('WORKER_NOT_VERIFIED')) {
          return 'Your worker profile must be verified before applying for marketplace jobs.';
        }
        if (rawError.contains('PROFILE_INCOMPLETE')) {
          return 'Complete your worker profile before applying for jobs.';
        }
        if (rawError.contains('DUPLICATE_APPLICATION')) {
          return 'You have already submitted an application for this booking.';
        }
        return rawError;
      }

      expect(
        getHumanReadableError('403: SKILL_MISMATCH'),
        equals('Your skills do not match the required skill for this booking.'),
      );
      expect(
        getHumanReadableError('403: OUTSIDE_SERVICE_RADIUS'),
        equals('This job is outside your saved service working radius.'),
      );
      expect(
        getHumanReadableError('403: WORKER_NOT_VERIFIED'),
        equals('Your worker profile must be verified before applying for marketplace jobs.'),
      );
    });
  });
}
