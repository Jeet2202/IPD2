// File: lib/customer/address/add_edit_address_screen.dart
//
// Phase 4.3.3 — Address Form with integrated Location Services.
//
// Location features added:
//   • "Use Current Location" button — GPS + Nominatim autofill
//   • "Pick on Map" button — opens MapPickerScreen → returns coordinates
//   • Coordinates stored as _latitude/_longitude → sent to backend
//   • Location preview card shown after coordinate selection
//   • Loading states for GPS acquisition
//
// All existing functionality preserved:
//   • Add mode (null existingAddress) → POST /customer/addresses
//   • Edit mode (existingAddress set) → PUT /customer/addresses/{id}
//   • Form validation + backend 422 field errors
//   • Returns true to caller on success (triggers list refresh)

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../app/routes/app_routes.dart';
import '../../models/address_model.dart';
import '../../services/address_service.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import 'map_picker_screen.dart';

class AddEditAddressScreen extends StatefulWidget {
  /// Pass an existing [AddressModel] to pre-populate the form for editing.
  /// Leave null to open in Add mode.
  final AddressModel? existingAddress;

  const AddEditAddressScreen({super.key, this.existingAddress});

  @override
  State<AddEditAddressScreen> createState() => _AddEditAddressScreenState();
}

class _AddEditAddressScreenState extends State<AddEditAddressScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;
  bool _isGettingLocation = false;
  String? _globalError;

  // ── Label ────────────────────────────────────────────────────────────
  String _selectedLabel = 'Home';
  final _labels = ['Home', 'Office', 'Other'];

  // ── Text Controllers ─────────────────────────────────────────────────
  late final TextEditingController _fullNameCtrl;
  late final TextEditingController _phoneCtrl;
  late final TextEditingController _addressLine1Ctrl;
  late final TextEditingController _addressLine2Ctrl;
  late final TextEditingController _landmarkCtrl;
  late final TextEditingController _cityCtrl;
  late final TextEditingController _stateCtrl;
  late final TextEditingController _countryCtrl;
  late final TextEditingController _postalCodeCtrl;

  // ── Location state ────────────────────────────────────────────────────
  double? _latitude;
  double? _longitude;

  // ── Field errors from backend 422 ───────────────────────────────────
  Map<String, String> _fieldErrors = {};

  // ── Colour palette ────────────────────────────────────────────────
  static const _blue = Color(0xFF2563EB);
  static const _darkText = Color(0xFF0F172A);
  static const _mutedText = Color(0xFF64748B);
  static const _border = Color(0xFFE2E8F0);

  bool get _isEditMode => widget.existingAddress != null;
  bool get _hasLocation => _latitude != null && _longitude != null;

  @override
  void initState() {
    super.initState();
    final a = widget.existingAddress;
    _selectedLabel = a?.label ?? 'Home';
    _fullNameCtrl    = TextEditingController(text: a?.fullName ?? '');
    _phoneCtrl       = TextEditingController(text: a?.phone ?? '');
    _addressLine1Ctrl = TextEditingController(text: a?.addressLine1 ?? '');
    _addressLine2Ctrl = TextEditingController(text: a?.addressLine2 ?? '');
    _landmarkCtrl    = TextEditingController(text: a?.landmark ?? '');
    _cityCtrl        = TextEditingController(text: a?.city ?? '');
    _stateCtrl       = TextEditingController(text: a?.state ?? '');
    _countryCtrl     = TextEditingController(text: a?.country ?? 'India');
    _postalCodeCtrl  = TextEditingController(text: a?.postalCode ?? '');
    // Initialize location from existing address
    _latitude  = a?.latitude;
    _longitude = a?.longitude;
  }

  @override
  void dispose() {
    _fullNameCtrl.dispose();
    _phoneCtrl.dispose();
    _addressLine1Ctrl.dispose();
    _addressLine2Ctrl.dispose();
    _landmarkCtrl.dispose();
    _cityCtrl.dispose();
    _stateCtrl.dispose();
    _countryCtrl.dispose();
    _postalCodeCtrl.dispose();
    super.dispose();
  }

  // ── Location: Use Current GPS ─────────────────────────────────────────

  Future<void> _useCurrentLocation() async {
    setState(() {
      _isGettingLocation = true;
      _globalError = null;
    });

    try {
      final loc = await LocationService.instance.getCurrentLocation();
      final geo = await LocationService.instance.reverseGeocode(loc);

      if (!mounted) return;

      setState(() {
        _latitude  = loc.latitude;
        _longitude = loc.longitude;
        _isGettingLocation = false;
      });

      _autofillFromGeocode(geo);
      _showSnack('Location detected and address filled.', isSuccess: true);
    } on LocationException catch (e) {
      if (!mounted) return;
      setState(() => _isGettingLocation = false);
      _showLocationErrorDialog(e);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isGettingLocation = false;
        _globalError = 'Failed to get current location.';
      });
    }
  }

  // ── Location: Map Picker ──────────────────────────────────────────────

  Future<void> _openMapPicker() async {
    final initialLoc = _hasLocation
        ? LatLng(_latitude!, _longitude!)
        : null;

    final result = await Navigator.pushNamed(
      context,
      AppRoutes.mapPicker,
      arguments: initialLoc,
    );

    if (result is MapPickerResult) {
      setState(() {
        _latitude  = result.location.latitude;
        _longitude = result.location.longitude;
      });
      _autofillFromGeocode(result.address);
      _showSnack('Location updated from map.', isSuccess: true);
    }
  }

  // ── Autofill fields from geocode result ───────────────────────────────

  void _autofillFromGeocode(ReverseGeocodeResult geo) {
    if (!mounted) return;

    if (geo.addressLine != null && geo.addressLine!.isNotEmpty) {
      // Only autofill line 1 if it's empty (don't overwrite user input)
      if (_addressLine1Ctrl.text.trim().isEmpty) {
        _addressLine1Ctrl.text = geo.addressLine!;
      }
    }
    if (geo.city != null && geo.city!.isNotEmpty) {
      _cityCtrl.text = geo.city!;
    }
    if (geo.state != null && geo.state!.isNotEmpty) {
      _stateCtrl.text = geo.state!;
    }
    if (geo.country != null && geo.country!.isNotEmpty) {
      _countryCtrl.text = geo.country!;
    }
    if (geo.postalCode != null && geo.postalCode!.isNotEmpty) {
      // Validate it's a 6-digit Indian PIN before autofilling
      if (RegExp(r'^\d{6}$').hasMatch(geo.postalCode!)) {
        _postalCodeCtrl.text = geo.postalCode!;
      }
    }
  }

  // ── Validation ─────────────────────────────────────────────────────

  String? _validateRequired(String? v, String fieldName, {int minLen = 2}) {
    if (v == null || v.trim().isEmpty) return '$fieldName is required.';
    if (v.trim().length < minLen) return '$fieldName must be at least $minLen characters.';
    return null;
  }

  String? _validatePhone(String? v) {
    if (v == null || v.trim().isEmpty) return 'Phone number is required.';
    final pattern = RegExp(r'^\+91[6-9]\d{9}$');
    if (!pattern.hasMatch(v.trim())) {
      return 'Enter a valid phone number in +91XXXXXXXXXX format.';
    }
    return null;
  }

  String? _validatePostalCode(String? v) {
    if (v == null || v.trim().isEmpty) return 'Postal code is required.';
    if (!RegExp(r'^\d{6}$').hasMatch(v.trim())) {
      return 'Enter a valid 6-digit PIN code.';
    }
    return null;
  }

  String? _validateAddressLine1(String? v) {
    if (v == null || v.trim().isEmpty) return 'Address Line 1 is required.';
    if (v.trim().length < 5) return 'Address Line 1 must be at least 5 characters.';
    return null;
  }

  // ── Submit ─────────────────────────────────────────────────────────

  Future<void> _submit() async {
    setState(() {
      _fieldErrors = {};
      _globalError = null;
    });

    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    final payload = <String, dynamic>{
      'label': _selectedLabel,
      'full_name': _fullNameCtrl.text.trim(),
      'phone': _phoneCtrl.text.trim(),
      'address_line_1': _addressLine1Ctrl.text.trim(),
      if (_addressLine2Ctrl.text.trim().isNotEmpty)
        'address_line_2': _addressLine2Ctrl.text.trim(),
      if (_landmarkCtrl.text.trim().isNotEmpty)
        'landmark': _landmarkCtrl.text.trim(),
      'city': _cityCtrl.text.trim(),
      'state': _stateCtrl.text.trim(),
      'country': _countryCtrl.text.trim().isNotEmpty
          ? _countryCtrl.text.trim()
          : 'India',
      'postal_code': _postalCodeCtrl.text.trim(),
      // Location — sent as flat lat/lng; backend converts to GeoJSON
      if (_hasLocation) 'latitude': _latitude,
      if (_hasLocation) 'longitude': _longitude,
    };

    try {
      if (_isEditMode) {
        await AddressService.instance.updateAddress(
          widget.existingAddress!.id,
          payload,
        );
      } else {
        await AddressService.instance.createAddress(payload);
      }

      if (mounted) {
        _showSnack(
          _isEditMode
              ? 'Address updated successfully.'
              : 'Address added successfully.',
          isSuccess: true,
        );
        Navigator.pop(context, true); // Signal list to refresh
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          if (e.fieldErrors.isNotEmpty) {
            _fieldErrors = e.fieldErrors;
            _globalError = 'Please correct the errors below.';
          } else {
            _globalError = _friendlyApiError(e);
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _globalError = 'An unexpected error occurred. Please try again.';
        });
      }
    }
  }

  // ── Error Helpers ─────────────────────────────────────────────────

  String _friendlyApiError(ApiException e) {
    if (e.statusCode == 408) return 'Request timed out. Check your internet connection.';
    if (e.statusCode == 503) return 'Server unavailable. Please try again later.';
    if (e.statusCode == 401) return 'Session expired. Please log in again.';
    if (e.statusCode == 403) return 'You do not have permission to perform this action.';
    return e.message;
  }

  void _showSnack(String message, {bool isSuccess = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isSuccess ? Icons.check_circle_rounded : Icons.error_outline_rounded,
              color: Colors.white,
              size: 18,
            ),
            const SizedBox(width: 10),
            Expanded(child: Text(message, style: const TextStyle(fontSize: 13))),
          ],
        ),
        backgroundColor: isSuccess ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  void _showLocationErrorDialog(LocationException e) {
    if (!mounted) return;
    final isPermanent = e.code == LocationErrorCode.permissionPermanentlyDenied;
    final isDisabled = e.code == LocationErrorCode.serviceDisabled;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        icon: Container(
          padding: const EdgeInsets.all(12),
          decoration: const BoxDecoration(
            color: Color(0xFFFEF2F2),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.location_off_rounded, color: Color(0xFFDC2626), size: 28),
        ),
        title: Text(
          isDisabled ? 'GPS Disabled' : 'Location Permission',
          textAlign: TextAlign.center,
          style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
        ),
        content: Text(
          e.message,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 14, color: _mutedText, height: 1.5),
        ),
        actionsPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
        actions: [
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.pop(ctx),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    side: const BorderSide(color: _border),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: const Text('Cancel',
                      style: TextStyle(color: _mutedText, fontWeight: FontWeight.w700)),
                ),
              ),
              const SizedBox(width: 12),
              if (isPermanent)
                Expanded(
                  child: ElevatedButton(
                    onPressed: () async {
                      Navigator.pop(ctx);
                      await LocationService.instance.openAppSettings();
                    },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      backgroundColor: _blue,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text('Settings', style: TextStyle(fontWeight: FontWeight.w700)),
                  ),
                )
              else if (isDisabled)
                Expanded(
                  child: ElevatedButton(
                    onPressed: () async {
                      Navigator.pop(ctx);
                      await LocationService.instance.openLocationSettings();
                    },
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      backgroundColor: _blue,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Text('Enable GPS', style: TextStyle(fontWeight: FontWeight.w700)),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: _darkText),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          _isEditMode ? 'Edit Address' : 'Add New Address',
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: _darkText,
          ),
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: _border),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Global error banner ──────────────────────────────
                if (_globalError != null) ...[
                  _ErrorBanner(message: _globalError!),
                  const SizedBox(height: 16),
                ],

                // ── Location Buttons ──────────────────────────────────
                _SectionHeader(icon: Icons.my_location_rounded, title: 'Detect Location'),
                const SizedBox(height: 10),
                Row(
                  children: [
                    // Use Current Location
                    Expanded(
                      child: _LocationButton(
                        icon: Icons.gps_fixed_rounded,
                        label: 'Use Current\nLocation',
                        isLoading: _isGettingLocation,
                        isActive: _hasLocation,
                        onTap: _useCurrentLocation,
                      ),
                    ),
                    const SizedBox(width: 12),
                    // Pick on Map
                    Expanded(
                      child: _LocationButton(
                        icon: Icons.map_rounded,
                        label: 'Pick on\nMap',
                        isLoading: false,
                        isActive: false,
                        onTap: _openMapPicker,
                      ),
                    ),
                  ],
                ),

                // ── Location Preview Card ─────────────────────────────
                if (_hasLocation) ...[
                  const SizedBox(height: 12),
                  _LocationPreviewCard(
                    latitude: _latitude!,
                    longitude: _longitude!,
                    onClear: () => setState(() {
                      _latitude = null;
                      _longitude = null;
                    }),
                  ),
                ],

                const SizedBox(height: 28),

                // ── Label Selector ────────────────────────────────────
                _SectionHeader(icon: Icons.label_outline_rounded, title: 'Address Label'),
                const SizedBox(height: 10),
                Row(
                  children: _labels.map((label) {
                    final isSelected = _selectedLabel == label;
                    return Expanded(
                      child: GestureDetector(
                        onTap: () => setState(() => _selectedLabel = label),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          margin: const EdgeInsets.only(right: 8),
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            color: isSelected ? _blue : Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: isSelected ? _blue : _border,
                              width: isSelected ? 2 : 1,
                            ),
                            boxShadow: isSelected
                                ? [
                                    BoxShadow(
                                      color: _blue.withValues(alpha: 0.2),
                                      blurRadius: 8,
                                      offset: const Offset(0, 2),
                                    )
                                  ]
                                : [],
                          ),
                          child: Column(
                            children: [
                              Icon(
                                label == 'Home'
                                    ? Icons.home_rounded
                                    : label == 'Office'
                                        ? Icons.work_rounded
                                        : Icons.place_rounded,
                                size: 20,
                                color: isSelected ? Colors.white : _mutedText,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                label,
                                style: TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w700,
                                  color: isSelected ? Colors.white : _mutedText,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),

                const SizedBox(height: 28),

                // ── Contact Info ──────────────────────────────────────
                _SectionHeader(icon: Icons.person_outline_rounded, title: 'Contact Details'),
                const SizedBox(height: 12),
                _FormField(
                  controller: _fullNameCtrl,
                  label: 'Full Name',
                  hint: 'e.g. Rajesh Kumar',
                  icon: Icons.badge_outlined,
                  backendError: _fieldErrors['full_name'],
                  validator: (v) => _validateRequired(v, 'Full Name'),
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 14),
                _FormField(
                  controller: _phoneCtrl,
                  label: 'Phone Number',
                  hint: '+91XXXXXXXXXX',
                  icon: Icons.phone_outlined,
                  backendError: _fieldErrors['phone'],
                  validator: _validatePhone,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[+\d]'))],
                  maxLength: 13,
                ),

                const SizedBox(height: 28),

                // ── Address Info ──────────────────────────────────────
                _SectionHeader(icon: Icons.location_on_outlined, title: 'Address Details'),
                const SizedBox(height: 12),
                _FormField(
                  controller: _addressLine1Ctrl,
                  label: 'Address Line 1',
                  hint: 'Flat / House no., Building, Street',
                  icon: Icons.home_work_outlined,
                  backendError: _fieldErrors['address_line_1'],
                  validator: _validateAddressLine1,
                  maxLines: 2,
                  textCapitalization: TextCapitalization.sentences,
                ),
                const SizedBox(height: 14),
                _FormField(
                  controller: _addressLine2Ctrl,
                  label: 'Address Line 2 (Optional)',
                  hint: 'Area, Locality, Colony',
                  icon: Icons.signpost_outlined,
                  backendError: _fieldErrors['address_line_2'],
                  isRequired: false,
                  textCapitalization: TextCapitalization.sentences,
                ),
                const SizedBox(height: 14),
                _FormField(
                  controller: _landmarkCtrl,
                  label: 'Landmark (Optional)',
                  hint: 'Near Metro Station, etc.',
                  icon: Icons.push_pin_outlined,
                  backendError: _fieldErrors['landmark'],
                  isRequired: false,
                  textCapitalization: TextCapitalization.sentences,
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: _FormField(
                        controller: _cityCtrl,
                        label: 'City',
                        hint: 'Mumbai',
                        icon: Icons.location_city_outlined,
                        backendError: _fieldErrors['city'],
                        validator: (v) => _validateRequired(v, 'City'),
                        textCapitalization: TextCapitalization.words,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: _FormField(
                        controller: _postalCodeCtrl,
                        label: 'PIN Code',
                        hint: '400001',
                        icon: Icons.pin_drop_outlined,
                        backendError: _fieldErrors['postal_code'],
                        validator: _validatePostalCode,
                        keyboardType: TextInputType.number,
                        inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                        maxLength: 6,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                _FormField(
                  controller: _stateCtrl,
                  label: 'State',
                  hint: 'Maharashtra',
                  icon: Icons.map_outlined,
                  backendError: _fieldErrors['state'],
                  validator: (v) => _validateRequired(v, 'State'),
                  textCapitalization: TextCapitalization.words,
                ),
                const SizedBox(height: 14),
                _FormField(
                  controller: _countryCtrl,
                  label: 'Country',
                  hint: 'India',
                  icon: Icons.public_outlined,
                  backendError: _fieldErrors['country'],
                  validator: (v) => _validateRequired(v, 'Country'),
                  textCapitalization: TextCapitalization.words,
                ),

                const SizedBox(height: 36),

                // ── Submit Button ─────────────────────────────────────
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _blue,
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: _blue.withValues(alpha: 0.5),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2.5,
                            ),
                          )
                        : Text(
                            _isEditMode ? 'Update Address' : 'Save Address',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Location Button
// ══════════════════════════════════════════════════════════════════════════════

class _LocationButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isLoading;
  final bool isActive;
  final VoidCallback onTap;

  const _LocationButton({
    required this.icon,
    required this.label,
    required this.isLoading,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    const blue = Color(0xFF2563EB);

    return GestureDetector(
      onTap: isLoading ? null : onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFFEFF6FF) : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isActive ? blue : const Color(0xFFE2E8F0),
            width: isActive ? 2 : 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (isLoading)
              const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: blue),
              )
            else
              Icon(icon, size: 18, color: isActive ? blue : const Color(0xFF64748B)),
            const SizedBox(width: 8),
            Flexible(
              child: Text(
                label,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: isActive ? blue : const Color(0xFF64748B),
                  height: 1.3,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Location Preview Card
// ══════════════════════════════════════════════════════════════════════════════

class _LocationPreviewCard extends StatelessWidget {
  final double latitude;
  final double longitude;
  final VoidCallback onClear;

  const _LocationPreviewCard({
    required this.latitude,
    required this.longitude,
    required this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFBFDBFE)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: const BoxDecoration(
              color: Color(0xFF2563EB),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.location_on_rounded, color: Colors.white, size: 14),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Location Pinned',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF1E3A8A),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '${latitude.toStringAsFixed(5)}, ${longitude.toStringAsFixed(5)}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF1E40AF),
                    fontFamily: 'monospace',
                  ),
                ),
              ],
            ),
          ),
          GestureDetector(
            onTap: onClear,
            child: Container(
              padding: const EdgeInsets.all(4),
              child: const Icon(Icons.close_rounded, size: 16, color: Color(0xFF64748B)),
            ),
          ),
        ],
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Section Header (unchanged)
// ══════════════════════════════════════════════════════════════════════════════

class _SectionHeader extends StatelessWidget {
  final IconData icon;
  final String title;

  const _SectionHeader({required this.icon, required this.title});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: const Color(0xFFEFF6FF),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 16, color: const Color(0xFF2563EB)),
        ),
        const SizedBox(width: 10),
        Text(
          title,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0F172A),
          ),
        ),
      ],
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Form Field Widget (unchanged)
// ══════════════════════════════════════════════════════════════════════════════

class _FormField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final IconData icon;
  final String? backendError;
  final String? Function(String?)? validator;
  final TextInputType keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final int maxLines;
  final int? maxLength;
  final bool isRequired;
  final TextCapitalization textCapitalization;

  const _FormField({
    required this.controller,
    required this.label,
    required this.hint,
    required this.icon,
    this.backendError,
    this.validator,
    this.keyboardType = TextInputType.text,
    this.inputFormatters,
    this.maxLines = 1,
    this.maxLength,
    this.isRequired = true,
    this.textCapitalization = TextCapitalization.none,
  });

  @override
  Widget build(BuildContext context) {
    const blue = Color(0xFF2563EB);
    const border = Color(0xFFE2E8F0);
    const mutedText = Color(0xFF64748B);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        RichText(
          text: TextSpan(
            text: label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: Color(0xFF374151),
            ),
            children: isRequired
                ? [
                    const TextSpan(
                      text: ' *',
                      style: TextStyle(color: Color(0xFFDC2626)),
                    ),
                  ]
                : [],
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          keyboardType: keyboardType,
          inputFormatters: inputFormatters,
          maxLines: maxLines,
          maxLength: maxLength,
          textCapitalization: textCapitalization,
          validator: backendError != null
              ? (_) => backendError
              : (isRequired ? validator : null),
          autovalidateMode: AutovalidateMode.onUserInteraction,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: TextStyle(
              fontSize: 13,
              color: mutedText.withValues(alpha: 0.6),
            ),
            prefixIcon: Icon(icon, size: 18, color: mutedText),
            counterText: '',
            filled: true,
            fillColor: Colors.white,
            contentPadding: EdgeInsets.symmetric(
              horizontal: 16,
              vertical: maxLines > 1 ? 14 : 0,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: blue, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFDC2626)),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFDC2626), width: 2),
            ),
          ),
        ),
      ],
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Error Banner (unchanged)
// ══════════════════════════════════════════════════════════════════════════════

class _ErrorBanner extends StatelessWidget {
  final String message;

  const _ErrorBanner({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: Color(0xFFDC2626), size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                fontSize: 13,
                color: Color(0xFFDC2626),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
