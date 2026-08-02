class UserModel {
  final String id;
  final String name;
  final String email;
  final String phone;
  final String role;
  final String? avatar;
  final bool isVerified;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final String accountStatus;
  final DateTime createdAt;

  const UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.role,
    this.avatar,
    this.isVerified = false,
    this.isEmailVerified = false,
    this.isPhoneVerified = false,
    this.accountStatus = 'active',
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    final String idVal = (json['id'] ?? json['_id'] ?? '') as String;
    final String nameVal = (json['full_name'] ?? json['name'] ?? '') as String;
    final String emailVal = (json['email'] ?? '') as String;
    final String phoneVal = (json['phone'] ?? '') as String;
    final String roleVal = (json['role'] is String
        ? json['role']
        : (json['role']?['value'] ?? json['role']?.toString() ?? 'customer')) as String;
    final bool isEmailVer = json['is_email_verified'] as bool? ?? false;
    final bool isPhoneVer = json['is_phone_verified'] as bool? ?? false;
    final bool isVer = json['isVerified'] as bool? ?? (isEmailVer || isPhoneVer);

    final String createdStr = (json['created_at'] ?? json['createdAt'] ?? DateTime.now().toIso8601String()) as String;

    return UserModel(
      id: idVal,
      name: nameVal,
      email: emailVal,
      phone: phoneVal,
      role: roleVal,
      avatar: json['avatar'] as String?,
      isVerified: isVer,
      isEmailVerified: isEmailVer,
      isPhoneVerified: isPhoneVer,
      accountStatus: json['account_status'] as String? ?? 'active',
      createdAt: DateTime.parse(createdStr),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'full_name': name,
        'email': email,
        'phone': phone,
        'role': role,
        'avatar': avatar,
        'is_email_verified': isEmailVerified,
        'is_phone_verified': isPhoneVerified,
        'account_status': accountStatus,
        'created_at': createdAt.toIso8601String(),
      };

  UserModel copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    String? role,
    String? avatar,
    bool? isVerified,
    bool? isEmailVerified,
    bool? isPhoneVerified,
    String? accountStatus,
  }) =>
      UserModel(
        id: id ?? this.id,
        name: name ?? this.name,
        email: email ?? this.email,
        phone: phone ?? this.phone,
        role: role ?? this.role,
        avatar: avatar ?? this.avatar,
        isVerified: isVerified ?? this.isVerified,
        isEmailVerified: isEmailVerified ?? this.isEmailVerified,
        isPhoneVerified: isPhoneVerified ?? this.isPhoneVerified,
        accountStatus: accountStatus ?? this.accountStatus,
        createdAt: createdAt,
      );
}
