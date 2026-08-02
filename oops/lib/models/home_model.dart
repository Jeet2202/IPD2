import 'category_model.dart';
import 'service_model.dart';

class HomeModel {
  final List<CategoryModel> featuredCategories;
  final List<ServiceModel> featuredServices;
  final List<ServiceModel> popularServices;
  final List<ServiceModel> recommendedServices;
  final List<ServiceModel> recentServices;

  const HomeModel({
    this.featuredCategories = const [],
    this.featuredServices = const [],
    this.popularServices = const [],
    this.recommendedServices = const [],
    this.recentServices = const [],
  });

  factory HomeModel.fromJson(Map<String, dynamic> json) {
    return HomeModel(
      featuredCategories: (json['featured_categories'] as List? ?? [])
          .map((e) => CategoryModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      featuredServices: (json['featured_services'] as List? ?? [])
          .map((e) => ServiceModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      popularServices: (json['popular_services'] as List? ?? [])
          .map((e) => ServiceModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendedServices: (json['recommended_services'] as List? ?? [])
          .map((e) => ServiceModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      recentServices: (json['recent_services'] as List? ?? [])
          .map((e) => ServiceModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'featured_categories': featuredCategories.map((e) => e.toJson()).toList(),
        'featured_services': featuredServices.map((e) => e.toJson()).toList(),
        'popular_services': popularServices.map((e) => e.toJson()).toList(),
        'recommended_services': recommendedServices.map((e) => e.toJson()).toList(),
        'recent_services': recentServices.map((e) => e.toJson()).toList(),
      };
}
