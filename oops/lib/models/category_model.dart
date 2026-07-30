class CategoryModel {
  final String id;
  final String name;
  final String icon;
  final String image;
  final int serviceCount;
  final bool isActive;

  const CategoryModel({
    required this.id,
    required this.name,
    required this.icon,
    required this.image,
    this.serviceCount = 0,
    this.isActive = true,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) => CategoryModel(
        id:           json['_id'] as String,
        name:         json['name'] as String,
        icon:         json['icon'] as String,
        image:        json['image'] as String,
        serviceCount: json['serviceCount'] as int? ?? 0,
        isActive:     json['isActive'] as bool? ?? true,
      );

  Map<String, dynamic> toJson() => {
        '_id':          id,
        'name':         name,
        'icon':         icon,
        'image':        image,
        'serviceCount': serviceCount,
        'isActive':     isActive,
      };
}
