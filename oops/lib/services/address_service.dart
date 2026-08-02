// File: lib/services/address_service.dart
//
// Address API integration layer.
// Wraps all 6 address endpoints using the existing ApiService singleton.
// Follows the same pattern as AuthService — no business logic, just API calls.
//
// Endpoints:
//   GET    /customer/addresses              → listAddresses()
//   GET    /customer/addresses/{id}         → getAddress(id)
//   POST   /customer/addresses              → createAddress(payload)
//   PUT    /customer/addresses/{id}         → updateAddress(id, payload)
//   DELETE /customer/addresses/{id}         → deleteAddress(id)
//   PATCH  /customer/addresses/{id}/default → setDefaultAddress(id)

import '../constants/api_endpoints.dart';
import '../models/address_model.dart';
import 'api_service.dart';

class AddressService {
  AddressService._();
  static final AddressService instance = AddressService._();

  // ── List all active addresses ─────────────────────────────────────────────

  /// Returns a list of all non-deleted customer addresses.
  /// Default address is first in the list (backend-sorted).
  Future<List<AddressModel>> listAddresses() async {
    final res = await ApiService.instance.get(ApiEndpoints.customerAddresses);
    final addressList = res['addresses'] as List<dynamic>? ?? [];
    return addressList
        .map((e) => AddressModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  // ── Get single address ────────────────────────────────────────────────────

  /// Fetches a single address by ID. Throws [ApiException] on 404/403.
  Future<AddressModel> getAddress(String addressId) async {
    final res = await ApiService.instance.get(
      '${ApiEndpoints.customerAddresses}/$addressId',
    );
    return AddressModel.fromJson(res);
  }

  // ── Create address ────────────────────────────────────────────────────────

  /// Creates a new address. The backend auto-sets is_default=true if first address.
  /// [payload] must include all required fields per CreateAddressRequest schema.
  Future<AddressModel> createAddress(Map<String, dynamic> payload) async {
    final res = await ApiService.instance.post(
      ApiEndpoints.customerAddresses,
      payload,
    );
    return AddressModel.fromJson(res);
  }

  // ── Update address ────────────────────────────────────────────────────────

  /// Updates an existing address. Only provided fields are updated (PATCH semantics).
  Future<AddressModel> updateAddress(
    String addressId,
    Map<String, dynamic> payload,
  ) async {
    final res = await ApiService.instance.put(
      '${ApiEndpoints.customerAddresses}/$addressId',
      payload,
    );
    return AddressModel.fromJson(res);
  }

  // ── Delete address ────────────────────────────────────────────────────────

  /// Soft-deletes an address. If the deleted address was default, the backend
  /// auto-promotes the next oldest address to default.
  Future<void> deleteAddress(String addressId) async {
    await ApiService.instance.delete(
      '${ApiEndpoints.customerAddresses}/$addressId',
    );
  }

  // ── Set default address ───────────────────────────────────────────────────

  /// Sets the specified address as the customer's default.
  /// All other addresses have their default flag cleared (backend-enforced).
  /// Idempotent — calling on already-default address returns 200.
  Future<AddressModel> setDefaultAddress(String addressId) async {
    final res = await ApiService.instance.patch(
      '${ApiEndpoints.customerAddresses}/$addressId/default',
    );
    return AddressModel.fromJson(res);
  }
}
