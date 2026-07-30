class WorkerModel {
  final String id;
  final String userId;
  final String name;
  final String phone;
  final String? avatar;
  final List<String> skillIds;
  final double rating;
  final int completedJobs;
  final bool isAvailable;
  final bool isVerified;
  final double? distanceKm;

  const WorkerModel({
    required this.id,
    required this.userId,
    required this.name,
    required this.phone,
    this.avatar,
    required this.skillIds,
    this.rating = 0.0,
    this.completedJobs = 0,
    this.isAvailable = true,
    this.isVerified = false,
    this.distanceKm,
  });

  factory WorkerModel.fromJson(Map<String, dynamic> json) => WorkerModel(
        id:            json['_id'] as String,
        userId:        json['userId'] as String,
        name:          json['name'] as String,
        phone:         json['phone'] as String,
        avatar:        json['avatar'] as String?,
        skillIds:      List<String>.from(json['skillIds'] as List),
        rating:        (json['rating'] as num?)?.toDouble() ?? 0.0,
        completedJobs: json['completedJobs'] as int? ?? 0,
        isAvailable:   json['isAvailable'] as bool? ?? true,
        isVerified:    json['isVerified'] as bool? ?? false,
        distanceKm:    (json['distanceKm'] as num?)?.toDouble(),
      );

  Map<String, dynamic> toJson() => {
        '_id':          id,
        'userId':       userId,
        'name':         name,
        'phone':        phone,
        'avatar':       avatar,
        'skillIds':     skillIds,
        'rating':       rating,
        'completedJobs': completedJobs,
        'isAvailable':  isAvailable,
        'isVerified':   isVerified,
        'distanceKm':   distanceKm,
      };
}
