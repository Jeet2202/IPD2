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
    final idVal = (json['id'] ?? json['_id'] ?? '').toString();
    final customerIdVal = (json['customer_id'] ?? json['customerId'] ?? '').toString();
    final labelVal = (json['label'] ?? 'Home').toString();
    final fullNameVal = (json['full_name'] ?? json['fullName'] ?? json['name'] ?? '').toString();
    final phoneVal = (json['phone'] ?? '').toString();
    final addressLine1Val = (json['address_line_1'] ?? json['addressLine1'] ?? json['address_line'] ?? json['address'] ?? '').toString();
    final addressLine2Val = json['address_line_2'] as String? ?? json['addressLine2'] as String?;
    final landmarkVal = json['landmark'] as String?;
    final cityVal = (json['city'] ?? '').toString();
    final stateVal = (json['state'] ?? '').toString();
    final countryVal = (json['country'] ?? 'India').toString();
    final postalCodeVal = (json['postal_code'] ?? json['postalCode'] ?? json['pincode'] ?? json['pin_code'] ?? '').toString();

    double? lat;
    if (json['latitude'] != null) {
      lat = double.tryParse(json['latitude'].toString());
    } else if (json['lat'] != null) {
      lat = double.tryParse(json['lat'].toString());
    }

    double? lng;
    if (json['longitude'] != null) {
      lng = double.tryParse(json['longitude'].toString());
    } else if (json['lng'] != null) {
      lng = double.tryParse(json['lng'].toString());
    }

    final isDefaultVal = json['is_default'] == true || json['isDefault'] == true;
    final isDeletedVal = json['is_deleted'] == true || json['isDeleted'] == true;
    final createdAtVal = (json['created_at'] ?? json['createdAt'] ?? DateTime.now().toIso8601String()).toString();
    final updatedAtVal = (json['updated_at'] ?? json['updatedAt'] ?? DateTime.now().toIso8601String()).toString();

    return AddressModel(
      id: idVal,
      customerId: customerIdVal,
      label: labelVal,
      fullName: fullNameVal,
      phone: phoneVal,
      addressLine1: addressLine1Val,
      addressLine2: addressLine2Val,
      landmark: landmarkVal,
      city: cityVal,
      state: stateVal,
      country: countryVal,
      postalCode: postalCodeVal,
      latitude: lat,
      longitude: lng,
      isDefault: isDefaultVal,
      isDeleted: isDeletedVal,
      createdAt: createdAtVal,
      updatedAt: updatedAtVal,
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
