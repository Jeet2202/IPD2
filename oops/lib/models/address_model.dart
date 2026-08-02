// File: lib/models/address_model.dart
//
// Maps the backend AddressResponse schema (app/address/schemas.py).
// All fields match 1-to-1 with the Pydantic model.
//
// copyWith uses a sentinel object for nullable fields so callers can
// explicitly set them to null (e.g. to clear landmark or location).

// Sentinel for nullable fields in copyWith — distinguishes "not provided"
// from "explicitly set to null". Must be const to use as default parameter.
const _absent = Object();

class AddressModel {
  final String id;
  final String customerId;
  final String label;
  final String fullName;
  final String phone;
  final String addressLine1;
  final String? addressLine2;
  final String? landmark;
  final String city;
  final String state;
  final String country;
  final String postalCode;
  final double? latitude;
  final double? longitude;
  final bool isDefault;
  final bool isDeleted;
  final String createdAt;
  final String updatedAt;

  const AddressModel({
    required this.id,
    required this.customerId,
    required this.label,
    required this.fullName,
    required this.phone,
    required this.addressLine1,
    this.addressLine2,
    this.landmark,
    required this.city,
    required this.state,
    required this.country,
    required this.postalCode,
    this.latitude,
    this.longitude,
    required this.isDefault,
    required this.isDeleted,
    required this.createdAt,
    required this.updatedAt,
  });

  factory AddressModel.fromJson(Map<String, dynamic> json) {
    return AddressModel(
      id: json['id'] as String,
      customerId: json['customer_id'] as String,
      label: json['label'] as String,
      fullName: json['full_name'] as String,
      phone: json['phone'] as String,
      addressLine1: json['address_line_1'] as String,
      addressLine2: json['address_line_2'] as String?,
      landmark: json['landmark'] as String?,
      city: json['city'] as String,
      state: json['state'] as String,
      country: json['country'] as String? ?? 'India',
      postalCode: json['postal_code'] as String,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      isDefault: json['is_default'] as bool,
      isDeleted: json['is_deleted'] as bool,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'customer_id': customerId,
        'label': label,
        'full_name': fullName,
        'phone': phone,
        'address_line_1': addressLine1,
        if (addressLine2 != null) 'address_line_2': addressLine2,
        if (landmark != null) 'landmark': landmark,
        'city': city,
        'state': state,
        'country': country,
        'postal_code': postalCode,
        if (latitude != null) 'latitude': latitude,
        if (longitude != null) 'longitude': longitude,
        'is_default': isDefault,
        'is_deleted': isDeleted,
        'created_at': createdAt,
        'updated_at': updatedAt,
      };

  /// Returns a human-readable single-line address summary.
  String get shortAddress {
    final parts = <String>[addressLine1];
    if (addressLine2 != null && addressLine2!.isNotEmpty) parts.add(addressLine2!);
    parts.addAll([city, '$state - $postalCode']);
    return parts.join(', ');
  }

  /// Creates a copy of this model with the given fields replaced.
  ///
  /// Nullable optional fields (addressLine2, landmark, latitude, longitude)
  /// use a sentinel [_absent] default so that:
  ///   - Omitting the argument → keeps the existing value.
  ///   - Passing `null` explicitly → sets the field to null.
  ///
  /// Non-nullable required fields use the standard `?? this.x` pattern.
  AddressModel copyWith({
    String? id,
    String? customerId,
    String? label,
    String? fullName,
    String? phone,
    String? addressLine1,
    Object? addressLine2 = _absent,
    Object? landmark = _absent,
    String? city,
    String? state,
    String? country,
    String? postalCode,
    Object? latitude = _absent,
    Object? longitude = _absent,
    bool? isDefault,
    bool? isDeleted,
    String? createdAt,
    String? updatedAt,
  }) {
    return AddressModel(
      id: id ?? this.id,
      customerId: customerId ?? this.customerId,
      label: label ?? this.label,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      addressLine1: addressLine1 ?? this.addressLine1,
      addressLine2: identical(addressLine2, _absent)
          ? this.addressLine2
          : addressLine2 as String?,
      landmark: identical(landmark, _absent)
          ? this.landmark
          : landmark as String?,
      city: city ?? this.city,
      state: state ?? this.state,
      country: country ?? this.country,
      postalCode: postalCode ?? this.postalCode,
      latitude: identical(latitude, _absent)
          ? this.latitude
          : latitude as double?,
      longitude: identical(longitude, _absent)
          ? this.longitude
          : longitude as double?,
      isDefault: isDefault ?? this.isDefault,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
