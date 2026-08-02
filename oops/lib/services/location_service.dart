// File: lib/services/location_service.dart
//
// Phase 4.3.3 — LocationService abstraction.
//
// Architecture:
//   LocationService (abstract interface)
//       └── OsmLocationService (concrete impl using geolocator + Nominatim)
//
// Future migration path:
//   To switch to Google Maps or Mapbox:
//     1. Create GoogleLocationService implements LocationService
//     2. Change LocationService.instance assignment below
//     3. No other code changes needed — all callers use LocationService.instance
//
// Design principles:
//   - No flutter_map imports in this file — purely business logic
//   - All callers depend on LocationService, not OsmLocationService
//   - Nominatim HTTP calls are isolated here; easy to swap geocoder
//   - GPS is cached while address screen is open (see currentPosition)

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;

// ══════════════════════════════════════════════════════════════════════════════
// Data Models
// ══════════════════════════════════════════════════════════════════════════════

/// Location coordinate pair — used throughout the app.
/// Keeps lat/lng together to avoid argument-order bugs.
class LatLng {
  final double latitude;
  final double longitude;

  const LatLng(this.latitude, this.longitude);

  @override
  String toString() => 'LatLng($latitude, $longitude)';
}

/// Result of reverse geocoding a coordinate pair.
/// All fields are nullable — allow manual editing if unavailable.
class ReverseGeocodeResult {
  final String? addressLine;
  final String? city;
  final String? state;
  final String? country;
  final String? postalCode;
  final String? displayName; // Full human-readable address for map preview

  const ReverseGeocodeResult({
    this.addressLine,
    this.city,
    this.state,
    this.country,
    this.postalCode,
    this.displayName,
  });

  bool get hasData =>
      addressLine != null ||
      city != null ||
      state != null ||
      postalCode != null;
}

/// Structured permission/location error codes.
enum LocationErrorCode {
  serviceDisabled,
  permissionDenied,
  permissionPermanentlyDenied,
  timeout,
  noInternet,
  geocodingFailed,
  unknown,
}

/// Strongly-typed location exception.
class LocationException implements Exception {
  final LocationErrorCode code;
  final String message;

  const LocationException({required this.code, required this.message});

  @override
  String toString() => 'LocationException(${code.name}): $message';
}

// ══════════════════════════════════════════════════════════════════════════════
// Abstract Interface
// ══════════════════════════════════════════════════════════════════════════════

/// Abstract location service interface.
///
/// All location-dependent code in the app depends on this interface.
/// Swap the implementation (OSM → Google → Mapbox) by changing [instance].
abstract class LocationService {
  /// Singleton accessor — change the assignment to swap providers.
  static LocationService instance = OsmLocationService();

  /// Request location permission from the OS.
  /// Returns true if granted.
  Future<bool> requestPermission();

  /// Check if location permission is currently granted.
  Future<LocationPermissionStatus> checkPermission();

  /// Check if location services (GPS) are enabled on the device.
  Future<bool> isLocationServiceEnabled();

  /// Get the current GPS position.
  ///
  /// Throws [LocationException] on service disabled / permission denied / timeout.
  Future<LatLng> getCurrentLocation({Duration timeout = const Duration(seconds: 15)});

  /// Open the device location settings (useful when permission permanently denied).
  Future<void> openLocationSettings();

  /// Open the app settings (for permanently denied permission).
  Future<void> openAppSettings();

  /// Reverse geocode coordinates to an address.
  ///
  /// Returns [ReverseGeocodeResult] with as many fields as the provider returns.
  /// Never throws — returns empty result on failure.
  Future<ReverseGeocodeResult> reverseGeocode(LatLng location);
}

/// Permission status enumeration (provider-agnostic).
enum LocationPermissionStatus {
  granted,
  denied,
  permanentlyDenied,
  restricted, // iOS only
}

// ══════════════════════════════════════════════════════════════════════════════
// OpenStreetMap / Nominatim Implementation
// ══════════════════════════════════════════════════════════════════════════════

/// Concrete location service using:
///   - geolocator for GPS + permission management
///   - Nominatim (OpenStreetMap) for reverse geocoding — no API key required
///
/// Nominatim usage policy:
///   - Max 1 request/second (enforced by user interaction, not polling)
///   - Must include a User-Agent identifying the app
///   - Suitable for student/production projects under normal usage
///
/// To migrate to Google:
///   Create GoogleLocationService that calls Google Geocoding API
///   and set LocationService.instance = GoogleLocationService().
class OsmLocationService implements LocationService {
  static const _nominatimBase = 'https://nominatim.openstreetmap.org';
  static const _userAgent = 'KaamSetu/1.0 (student project; contact@kaamsetu.app)';
  static const _timeout = Duration(seconds: 10);

  final http.Client _httpClient;

  OsmLocationService({http.Client? httpClient})
      : _httpClient = httpClient ?? http.Client();

  // ── Permission ──────────────────────────────────────────────────────────

  @override
  Future<bool> requestPermission() async {
    final status = await Geolocator.requestPermission();
    return status == LocationPermission.always ||
        status == LocationPermission.whileInUse;
  }

  @override
  Future<LocationPermissionStatus> checkPermission() async {
    final status = await Geolocator.checkPermission();
    switch (status) {
      case LocationPermission.always:
      case LocationPermission.whileInUse:
        return LocationPermissionStatus.granted;
      case LocationPermission.denied:
        return LocationPermissionStatus.denied;
      case LocationPermission.deniedForever:
        return LocationPermissionStatus.permanentlyDenied;
      case LocationPermission.unableToDetermine:
        return LocationPermissionStatus.restricted;
    }
  }

  @override
  Future<bool> isLocationServiceEnabled() async {
    return Geolocator.isLocationServiceEnabled();
  }

  @override
  Future<void> openLocationSettings() async {
    await Geolocator.openLocationSettings();
  }

  @override
  Future<void> openAppSettings() async {
    await Geolocator.openAppSettings();
  }

  // ── GPS ─────────────────────────────────────────────────────────────────

  @override
  Future<LatLng> getCurrentLocation({
    Duration timeout = const Duration(seconds: 15),
  }) async {
    // 1. Check GPS enabled
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw const LocationException(
        code: LocationErrorCode.serviceDisabled,
        message: 'Location services are disabled. Please enable GPS in Settings.',
      );
    }

    // 2. Check / request permission
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw const LocationException(
          code: LocationErrorCode.permissionDenied,
          message: 'Location permission was denied. Please allow location access.',
        );
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw const LocationException(
        code: LocationErrorCode.permissionPermanentlyDenied,
        message: 'Location permission is permanently denied. Open Settings to enable it.',
      );
    }

    // 3. Get position
    try {
      final position = await Geolocator.getCurrentPosition(
        locationSettings: LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: timeout,
        ),
      );
      return LatLng(position.latitude, position.longitude);
    } on TimeoutException {
      throw const LocationException(
        code: LocationErrorCode.timeout,
        message: 'GPS timed out. Please try again or check your signal.',
      );
    } catch (e) {
      throw LocationException(
        code: LocationErrorCode.unknown,
        message: 'Failed to get location: ${e.toString()}',
      );
    }
  }

  // ── Reverse Geocoding (Nominatim) ────────────────────────────────────────

  @override
  Future<ReverseGeocodeResult> reverseGeocode(LatLng location) async {
    try {
      final uri = Uri.parse(
        '$_nominatimBase/reverse'
        '?lat=${location.latitude}'
        '&lon=${location.longitude}'
        '&format=json'
        '&addressdetails=1'
        '&accept-language=en',
      );

      final response = await _httpClient
          .get(uri, headers: {'User-Agent': _userAgent})
          .timeout(_timeout);

      if (response.statusCode != 200) {
        return const ReverseGeocodeResult();
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final addr = data['address'] as Map<String, dynamic>? ?? {};
      final displayName = data['display_name'] as String?;

      // Build address line from Nominatim fields
      final addressParts = <String>[];
      _addIfPresent(addressParts, addr['house_number'] as String?);
      _addIfPresent(addressParts, addr['road'] as String?);
      _addIfPresent(addressParts, addr['suburb'] as String?);
      final addressLine =
          addressParts.isNotEmpty ? addressParts.join(', ') : null;

      // City: try multiple field names Nominatim uses
      final city = _firstNonNull([
        addr['city'] as String?,
        addr['town'] as String?,
        addr['village'] as String?,
        addr['county'] as String?,
        addr['district'] as String?,
      ]);

      final state = addr['state'] as String?;
      final country = addr['country'] as String?;
      final postalCode = addr['postcode'] as String?;

      return ReverseGeocodeResult(
        addressLine: addressLine,
        city: city,
        state: state,
        country: country,
        postalCode: postalCode,
        displayName: displayName,
      );
    } on SocketException {
      return const ReverseGeocodeResult(); // No internet — silent fail, allow manual entry
    } on TimeoutException {
      return const ReverseGeocodeResult(); // Timeout — silent fail
    } catch (_) {
      return const ReverseGeocodeResult(); // Any other error — silent fail
    }
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  void _addIfPresent(List<String> parts, String? value) {
    if (value != null && value.isNotEmpty) parts.add(value);
  }

  String? _firstNonNull(List<String?> values) {
    for (final v in values) {
      if (v != null && v.isNotEmpty) return v;
    }
    return null;
  }
}
