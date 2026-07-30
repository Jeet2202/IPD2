class ServiceModel {
  final String id;
  final String categoryId;
  final String name;
  final String description;
  final String image;
  final double basePrice;
  final String unit; // e.g. "per visit", "per hour"
  final double rating;
  final int reviewCount;
  final bool isActive;

  const ServiceModel({
    required this.id,
    required this.categoryId,
    required this.name,
    required this.description,
    required this.image,
    required this.basePrice,
    required this.unit,
    this.rating = 0.0,
    this.reviewCount = 0,
    this.isActive = true,
  });

  factory ServiceModel.fromJson(Map<String, dynamic> json) => ServiceModel(
        id:          json['_id'] as String,
        categoryId:  json['categoryId'] as String,
        name:        json['name'] as String,
        description: json['description'] as String,
        image:       json['image'] as String,
        basePrice:   (json['basePrice'] as num).toDouble(),
        unit:        json['unit'] as String,
        rating:      (json['rating'] as num?)?.toDouble() ?? 0.0,
        reviewCount: json['reviewCount'] as int? ?? 0,
        isActive:    json['isActive'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        '_id':         id,
        'categoryId':  categoryId,
        'name':        name,
        'description': description,
        'image':       image,
        'basePrice':   basePrice,
        'unit':        unit,
        'rating':      rating,
        'reviewCount': reviewCount,
        'isActive':    isActive,
      };
}
