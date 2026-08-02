class CategoryModel {
  final String id;
  final String name;
  final String slug;
  final String icon;
  final String image;
  final int serviceCount;
  final bool isActive;

  const CategoryModel({
    required this.id,
    required this.name,
    this.slug = '',
    this.icon = '',
    this.image = '',
    this.serviceCount = 0,
    this.isActive = true,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) => CategoryModel(
        id: json['id'] as String? ?? json['_id'] as String? ?? '',
        name: json['name'] as String? ?? '',
        slug: json['slug'] as String? ?? '',
        icon: json['icon'] as String? ?? '',
        image: json['image_url'] as String? ?? json['image'] as String? ?? '',
        serviceCount: json['service_count'] as int? ?? json['serviceCount'] as int? ?? 0,
        isActive: json['is_active'] as bool? ?? json['isActive'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'slug': slug,
        'icon': icon,
        'image_url': image,
        'service_count': serviceCount,
        'is_active': isActive,
      };
}
