class UserModel {
  final String id;
  final String name;
  final String email;
  final String phone;
  final String role;
  final String? avatar;
  final bool isVerified;
  final DateTime createdAt;

  const UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    this.avatar,
    this.isVerified = false,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        id:         json['_id'] as String,
        name:       json['name'] as String,
        email:      json['email'] as String,
        phone:      json['phone'] as String,
        role:       json['role'] as String,
        avatar:     json['avatar'] as String?,
        isVerified: json['isVerified'] as bool? ?? false,
        createdAt:  DateTime.parse(json['createdAt'] as String),
      );

  Map<String, dynamic> toJson() => {
        '_id':        id,
        'name':       name,
        'email':      email,
        'phone':      phone,
        'role':       role,
        'avatar':     avatar,
        'isVerified': isVerified,
        'createdAt':  createdAt.toIso8601String(),
      };

  UserModel copyWith({
    String? id, String? name, String? email,
    String? phone, String? role, String? avatar, bool? isVerified,
  }) =>
      UserModel(
        id:         id ?? this.id,
        name:       name ?? this.name,
        email:      email ?? this.email,
        phone:      phone ?? this.phone,
        role:       role ?? this.role,
        avatar:     avatar ?? this.avatar,
        isVerified: isVerified ?? this.isVerified,
        createdAt:  createdAt,
      );
}
