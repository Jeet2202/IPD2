import '../shared/utils/category_helper.dart';

class ServiceModel {
  final String id;
  final String categoryId;
  final String categorySlug;
  final String name;
  final String slug;
  final String shortDescription;
  final String description;
  final String image;
  final double basePrice;
  final String priceRangeDisplay;
  final String durationDisplay;
  final int estimatedDurationMinutes;
  final String unit;
  final double rating;
  final int reviewCount;
  final bool isFeatured;
  final bool isActive;
  final List<String> whatsIncluded;
  final List<String> whatsNotIncluded;

  const ServiceModel({
    required this.id,
    required this.categoryId,
    this.categorySlug = '',
    required this.name,
    this.slug = '',
    this.shortDescription = '',
    this.description = '',
    required this.image,
    required this.basePrice,
    this.priceRangeDisplay = '',
    this.durationDisplay = '',
    this.estimatedDurationMinutes = 0,
    this.unit = 'per service',
    this.rating = 4.8,
    this.reviewCount = 120,
    this.isFeatured = false,
    this.isActive = true,
    this.whatsIncluded = const [],
    this.whatsNotIncluded = const [],
  });

  String get resolvedImage => image.isNotEmpty ? image : CategoryHelper.getServiceImageUrl(slug, categorySlug, name);

  factory ServiceModel.fromJson(Map<String, dynamic> json) {
    final title = json['title'] as String? ?? json['name'] as String? ?? '';
    final basePrice = (json['base_price'] as num?)?.toDouble() ??
        (json['base_market_price'] as num?)?.toDouble() ??
        (json['basePrice'] as num?)?.toDouble() ??
        0.0;
    final image = json['service_image_url'] as String? ??
        json['service_image'] as String? ??
        json['image'] as String? ??
        '';
    final durationMin = json['estimated_duration_minutes'] as int? ?? 0;

    final rawInc = json['whats_included'] as List? ?? json['whatsIncluded'] as List? ?? [];
    final incList = rawInc.map((e) => e.toString()).toList();

    final rawExc = json['whats_not_included'] as List? ?? json['whatsNotIncluded'] as List? ?? [];
    final excList = rawExc.map((e) => e.toString()).toList();

    return ServiceModel(
      id: json['id'] as String? ?? json['_id'] as String? ?? '',
      categoryId: json['category_id'] as String? ?? json['categoryId'] as String? ?? '',
      categorySlug: json['category_slug'] as String? ?? '',
      name: title,
      slug: json['slug'] as String? ?? '',
      shortDescription: json['short_description'] as String? ?? '',
      description: json['description'] as String? ?? '',
      image: image,
      basePrice: basePrice,
      priceRangeDisplay: json['price_range_display'] as String? ?? '₹${basePrice.toStringAsFixed(0)}',
      durationDisplay: json['duration_display'] as String? ?? (durationMin > 0 ? '$durationMin min' : ''),
      estimatedDurationMinutes: durationMin,
      unit: json['unit'] as String? ?? 'per service',
      rating: (json['rating'] as num?)?.toDouble() ?? 4.8,
      reviewCount: json['review_count'] as int? ?? json['reviewCount'] as int? ?? 120,
      isFeatured: json['is_featured'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? json['isActive'] as bool? ?? true,
      whatsIncluded: incList,
      whatsNotIncluded: excList,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'category_id': categoryId,
        'category_slug': categorySlug,
        'title': name,
        'slug': slug,
        'short_description': shortDescription,
        'description': description,
        'service_image_url': image,
        'base_price': basePrice,
        'price_range_display': priceRangeDisplay,
        'duration_display': durationDisplay,
        'estimated_duration_minutes': estimatedDurationMinutes,
        'unit': unit,
        'rating': rating,
        'review_count': reviewCount,
        'is_featured': isFeatured,
        'is_active': isActive,
        'whats_included': whatsIncluded,
        'whats_not_included': whatsNotIncluded,
      };
}
