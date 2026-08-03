import '../models/review_model.dart';
import 'api_service.dart';

class ReviewService {
  final ApiService _apiService;

  ReviewService({ApiService? apiService}) : _apiService = apiService ?? ApiService.instance;

  /// Customer submits review for completed booking via POST /customer/reviews
  Future<ReviewModel> createReview({
    required String bookingId,
    required double overallRating,
    required double punctualityRating,
    required double qualityRating,
    required double professionalismRating,
    required double communicationRating,
    String? title,
    String? comment,
    bool wouldRecommend = true,
  }) async {
    final body = <String, dynamic>{
      'booking_id': bookingId,
      'overall_rating': overallRating,
      'punctuality_rating': punctualityRating,
      'quality_rating': qualityRating,
      'professionalism_rating': professionalismRating,
      'communication_rating': communicationRating,
      'would_recommend': wouldRecommend,
    };
    if (title != null && title.trim().isNotEmpty) {
      body['review_title'] = title.trim();
    }
    if (comment != null && comment.trim().isNotEmpty) {
      body['review_comment'] = comment.trim();
    }

    final res = await _apiService.post('/customer/reviews', body);
    return ReviewModel.fromJson(res as Map<String, dynamic>);
  }

  /// Get review submitted for a specific booking via GET /customer/reviews/{bookingId}
  Future<ReviewModel?> getReviewByBooking(String bookingId) async {
    try {
      final res = await _apiService.get('/customer/reviews/$bookingId');
      return ReviewModel.fromJson(res as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  /// Fetch paginated reviews for worker via GET /worker/reviews/{workerId}
  Future<Map<String, dynamic>> getWorkerReviews(String workerId, {int page = 1, int pageSize = 20}) async {
    final res = await _apiService.get(
      '/worker/reviews/$workerId',
      params: {
        'page': page.toString(),
        'page_size': pageSize.toString(),
      },
    );
    return res as Map<String, dynamic>;
  }
}
