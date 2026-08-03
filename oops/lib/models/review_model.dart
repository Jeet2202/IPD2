class ReviewModel {
  final String id;
  final String bookingId;
  final String workerId;
  final String customerId;
  final double overallRating;
  final double punctualityRating;
  final double qualityRating;
  final double professionalismRating;
  final double communicationRating;
  final String? reviewTitle;
  final String? reviewComment;
  final bool wouldRecommend;
  final List<String> attachments;
  final String createdAt;
  final String updatedAt;

  const ReviewModel({
    required this.id,
    required this.bookingId,
    required this.workerId,
    required this.customerId,
    required this.overallRating,
    required this.punctualityRating,
    required this.qualityRating,
    required this.professionalismRating,
    required this.communicationRating,
    this.reviewTitle,
    this.reviewComment,
    this.wouldRecommend = true,
    this.attachments = const [],
    required this.createdAt,
    required this.updatedAt,
  });

  factory ReviewModel.fromJson(Map<String, dynamic> json) {
    final raw = (json['data'] is Map<String, dynamic>) ? json['data'] as Map<String, dynamic> : json;

    return ReviewModel(
      id: raw['id'] as String? ?? '',
      bookingId: raw['booking_id'] as String? ?? '',
      workerId: raw['worker_id'] as String? ?? '',
      customerId: raw['customer_id'] as String? ?? '',
      overallRating: (raw['overall_rating'] as num?)?.toDouble() ?? 5.0,
      punctualityRating: (raw['punctuality_rating'] as num?)?.toDouble() ?? 5.0,
      qualityRating: (raw['quality_rating'] as num?)?.toDouble() ?? 5.0,
      professionalismRating: (raw['professionalism_rating'] as num?)?.toDouble() ?? 5.0,
      communicationRating: (raw['communication_rating'] as num?)?.toDouble() ?? 5.0,
      reviewTitle: raw['review_title'] as String?,
      reviewComment: raw['review_comment'] as String?,
      wouldRecommend: raw['would_recommend'] as bool? ?? true,
      attachments: (raw['attachments'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: raw['created_at'] as String? ?? '',
      updatedAt: raw['updated_at'] as String? ?? '',
    );
  }
}
