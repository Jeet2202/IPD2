// File: lib/worker/profile/service_area/service_area_screen.dart

import 'package:flutter/material.dart';
import '../../../services/auth_service.dart';
import '../../../services/api_service.dart';
import '../../../services/location_service.dart';
import '../../../widgets/location_search_bar.dart';
import '../../../customer/address/map_picker_screen.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerServiceAreaScreen extends StatefulWidget {
  const WorkerServiceAreaScreen({super.key});

  @override
  State<WorkerServiceAreaScreen> createState() =>
      _WorkerServiceAreaScreenState();
}

class _WorkerServiceAreaScreenState extends State<WorkerServiceAreaScreen> {
  double _radius = 10.0; // km
  bool _chargeTravelFee = true;

  bool _isLoading = false;
  bool _isDetectingLocation = false;
  bool _isSaving = false;

  LatLng? _detectedLocation;
  String? _detectedAddress;

  static const _presetDistances = [5, 10, 15, 20, 30, 40];

  @override
  void initState() {
    super.initState();
    _loadCurrentSettings();
  }

  /// Load worker's current radius + location from API
  Future<void> _loadCurrentSettings() async {
    setState(() => _isLoading = true);
    try {
      final res = await AuthService.instance.fetchWorkerProfile();
      final data = res['data'] as Map<String, dynamic>? ?? res;
      final radiusRaw = data['working_radius_km'];
      if (radiusRaw != null) {
        final r = (radiusRaw as num).toDouble();
        setState(() => _radius = r.clamp(2.0, 40.0));
      }
      // Load existing location if any
      final loc = data['current_location'] as Map<String, dynamic>?;
      if (loc != null) {
        final coords = loc['coordinates'] as List<dynamic>?;
        if (coords != null && coords.length >= 2) {
          final lng = (coords[0] as num).toDouble();
          final lat = (coords[1] as num).toDouble();
          setState(() {
            _detectedLocation = LatLng(lat, lng);
            _detectedAddress =
                '${'saved_location'.tr(context)} (${lat.toStringAsFixed(4)}, ${lng.toStringAsFixed(4)})';
          });
        }
      }
    } catch (_) {
      // Silently ignore — default values remain
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  /// GPS detect current location and reverse-geocode it
  Future<void> _detectMyLocation() async {
    setState(() => _isDetectingLocation = true);
    try {
      final loc = await LocationService.instance.getCurrentLocation();
      final geo = await LocationService.instance.reverseGeocode(loc);

      final addressParts = <String>[];
      if (geo.addressLine != null) addressParts.add(geo.addressLine!);
      if (geo.city != null) addressParts.add(geo.city!);
      if (geo.state != null) addressParts.add(geo.state!);

      setState(() {
        _detectedLocation = loc;
        _detectedAddress = addressParts.isNotEmpty
            ? addressParts.join(', ')
            : '${'location_detected'.tr(context)} (${loc.latitude.toStringAsFixed(4)}, ${loc.longitude.toStringAsFixed(4)})';
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_detectedAddress ?? '${'location_detected'.tr(context)}!'),
            backgroundColor: const Color(0xFF10B981),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } on LocationException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isDetectingLocation = false);
    }
  }

  /// Pick location interactively on Map
  Future<void> _pickOnMap() async {
    final MapPickerResult? result = await Navigator.push<MapPickerResult>(
      context,
      MaterialPageRoute(
        builder: (ctx) => MapPickerScreen(initialLocation: _detectedLocation),
      ),
    );

    if (result != null) {
      final addressLine = result.address.addressLine ??
          '${result.location.latitude.toStringAsFixed(4)}, ${result.location.longitude.toStringAsFixed(4)}';
      setState(() {
        _detectedLocation = result.location;
        _detectedAddress = addressLine;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${'map_location_selected'.tr(context)}$addressLine'),
            backgroundColor: const Color(0xFF10B981),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  /// Save radius to profile + location via PATCH endpoint
  Future<void> _saveServiceArea() async {
    setState(() => _isSaving = true);
    try {
      // 1. Update working radius on main profile
      await AuthService.instance.updateWorkerProfile({
        'working_radius_km': _radius.roundToDouble(),
      });

      // 2. If location was detected, save it separately
      if (_detectedLocation != null) {
        await ApiService.instance.patch('/worker/profile/location', {
          'latitude': _detectedLocation!.latitude,
          'longitude': _detectedLocation!.longitude,
        });
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('service_area_saved_success'.tr(context)),
            backgroundColor: const Color(0xFF10B981),
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pop(context);
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'service_area_location'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF0F172A)),
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(20.0),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Modern Hero Header Banner ────────────────────────────
                    _buildHeroHeader(),

                    SizedBox(height: 20),

                    // ── Location Search Bar ─────────────────────────────────
                    LocationSearchBar(
                      onLocationSelected: (location) {
                        setState(() {
                          _detectedLocation = LatLng(location.latitude, location.longitude);
                          _detectedAddress = location.displayName;
                        });
                      },
                    ),

                    SizedBox(height: 16),

                    // ── Quick Location Action Buttons (GPS & Map Picker) ───
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isDetectingLocation ? null : _detectMyLocation,
                            icon: _isDetectingLocation
                                ? SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Color(0xFF2563EB),
                                    ),
                                  )
                                : Icon(Icons.my_location_rounded, size: 18),
                            label: Text(_isDetectingLocation ? 'detecting_gps'.tr(context) : 'detect_gps'.tr(context)),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF2563EB),
                              side: BorderSide(color: Color(0xFF2563EB), width: 1.5),
                              padding: EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14),
                              ),
                            ),
                          ),
                        ),
                        SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: _pickOnMap,
                            icon: Icon(Icons.map_rounded, size: 18),
                            label: Text('pick_on_map'.tr(context)),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF1E293B),
                              foregroundColor: Colors.white,
                              padding: EdgeInsets.symmetric(vertical: 14),
                              elevation: 0,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(14),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),

                    SizedBox(height: 20),

                    // ── Map Preview & Service Radius Card ────────────────────
                    _buildMapVisualizerCard(),

                    SizedBox(height: 20),

                    // ── Active Selected Location Card ────────────────────────
                    _buildSelectedLocationCard(),

                    SizedBox(height: 20),

                    // ── Service Radius & Distance Chips Card ─────────────────
                    _buildRadiusControlCard(),

                    SizedBox(height: 20),

                    // ── Travel Settings Card ─────────────────────────────────
                    _buildCardContainer(
                      title: 'travel_allowance_preferences'.tr(context),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'charge_travel_allowance'.tr(context),
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  'standard_travel_fee_desc'.tr(context),
                                  style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                                ),
                              ],
                            ),
                          ),
                          Switch(
                            value: _chargeTravelFee,
                            activeTrackColor: const Color(0xFF2563EB),
                            onChanged: (val) => setState(() => _chargeTravelFee = val),
                          ),
                        ],
                      ),
                    ),

                    SizedBox(height: 24),

                    // ── Save Service Area Primary Action ─────────────────────
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: _isSaving ? null : _saveServiceArea,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          disabledBackgroundColor: const Color(0xFFCBD5E1),
                          elevation: 2,
                          shadowColor: const Color(0xFF2563EB).withValues(alpha: 0.3),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                        ),
                        child: _isSaving
                            ? SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                            : Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.check_circle_rounded, size: 20),
                                  SizedBox(width: 8),
                                  Text(
                                    'save_service_area_location'.tr(context),
                                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                                  ),
                                ],
                              ),
                      ),
                    ),

                    SizedBox(height: 24),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildHeroHeader() {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A8A), Color(0xFF2563EB)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2563EB).withValues(alpha: 0.25),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(Icons.radar_rounded, color: Colors.white, size: 24),
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'work_radius_coverage'.tr(context),
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white),
                    ),
                    SizedBox(height: 2),
                    Text(
                      '${'active_operating_zone_prefix'.tr(context)}${_radius.round()} ${'km_radius'.tr(context)}',
                      style: TextStyle(fontSize: 12, color: Color(0xFFDBEAFE)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          SizedBox(height: 12),
          Text(
            'set_location_radius_desc'.tr(context),
            style: TextStyle(fontSize: 12, color: Color(0xFFE0E7FF), height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildMapVisualizerCard() {
    return Container(
      height: 200,
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFCBD5E1)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background Map Pattern grid
          Opacity(
            opacity: 0.1,
            child: GridView.builder(
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 6),
              itemBuilder: (ctx, idx) => Container(margin: EdgeInsets.all(1), color: Colors.blueGrey),
            ),
          ),
          // Pulsing Radius Visualizer Circle
          AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: (100 + (_radius * 2)).clamp(90.0, 180.0),
            height: (100 + (_radius * 2)).clamp(90.0, 180.0),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF2563EB).withValues(alpha: 0.15),
              border: Border.all(color: const Color(0xFF2563EB), width: 2.5),
            ),
          ),
          // Location Pin Marker
          Container(
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _detectedLocation != null ? const Color(0xFF10B981) : const Color(0xFF2563EB),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Icon(Icons.place_rounded, color: Colors.white, size: 24),
          ),
          // Floating Coverage Badge
          Positioned(
            bottom: 14,
            right: 14,
            child: Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.08),
                    blurRadius: 8,
                  ),
                ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.share_location_rounded, size: 14, color: Color(0xFF2563EB)),
                  SizedBox(width: 6),
                  Text(
                    '${_radius.round()} ${'km_radius'.tr(context)}',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSelectedLocationCard() {
    return _buildCardContainer(
      title: 'current_operating_base'.tr(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_detectedAddress != null) ...[
            Container(
              padding: EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFECFDF5),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFA7F3D0)),
              ),
              child: Row(
                children: [
                  Icon(Icons.location_on_rounded, color: Color(0xFF059669), size: 22),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _detectedAddress!,
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF065F46), height: 1.3),
                    ),
                  ),
                ],
              ),
            ),
          ] else ...[
            Container(
              padding: EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBEB),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFFDE68A)),
              ),
              child: Row(
                children: [
                  Icon(Icons.location_off_rounded, color: Color(0xFFD97706), size: 22),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'no_location_set_desc'.tr(context),
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF92400E)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRadiusControlCard() {
    return _buildCardContainer(
      title: 'working_distance_radius'.tr(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'max_coverage_radius'.tr(context),
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF64748B)),
              ),
              Text(
                '${_radius.round()} ${'km'.tr(context)}',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: Color(0xFF2563EB)),
              ),
            ],
          ),
          SizedBox(height: 12),

          // Presets Chips
          Wrap(
            spacing: 8,
            children: _presetDistances.map((dist) {
              final isSelected = _radius.round() == dist;
              return ChoiceChip(
                label: Text('$dist${'km'.tr(context)}'),
                selected: isSelected,
                selectedColor: const Color(0xFF2563EB),
                backgroundColor: const Color(0xFFF1F5F9),
                labelStyle: TextStyle(
                  color: isSelected ? Colors.white : const Color(0xFF475569),
                  fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                  fontSize: 12,
                ),
                onSelected: (val) {
                  if (val) setState(() => _radius = dist.toDouble());
                },
              );
            }).toList(),
          ),

          SizedBox(height: 12),

          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: const Color(0xFF2563EB),
              inactiveTrackColor: const Color(0xFFE2E8F0),
              thumbColor: const Color(0xFF2563EB),
            ),
            child: Slider(
              value: _radius,
              min: 2,
              max: 40,
              divisions: 38,
              onChanged: (val) => setState(() => _radius = val),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('2 ${'km'.tr(context)}', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
              Text('40 ${'km'.tr(context)}', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCardContainer({required String title, required Widget child}) {
    return Container(
      padding: EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFE2E8F0), width: 1.2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
          ),
          SizedBox(height: 14),
          child,
        ],
      ),
    );
  }
}
