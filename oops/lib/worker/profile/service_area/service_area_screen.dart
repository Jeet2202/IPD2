// File: lib/worker/profile/service_area/service_area_screen.dart

import 'package:flutter/material.dart';
import '../../../services/auth_service.dart';
import '../../../services/api_service.dart';
import '../../../services/location_service.dart';

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
            _detectedAddress = 'Last saved location (${lat.toStringAsFixed(4)}, ${lng.toStringAsFixed(4)})';
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
            : 'Location detected (${loc.latitude.toStringAsFixed(4)}, ${loc.longitude.toStringAsFixed(4)})';
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(_detectedAddress ?? 'Location detected!'),
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
          const SnackBar(
            content: Text('Service area saved successfully!'),
            backgroundColor: Color(0xFF10B981),
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
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Service Area & Location',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Map Placeholder with radius visualization ────────────
                    Container(
                      height: 180,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E8F0),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: const Color(0xFFCBD5E1)),
                      ),
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Opacity(
                            opacity: 0.15,
                            child: GridView.builder(
                              physics: const NeverScrollableScrollPhysics(),
                              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: 6),
                              itemBuilder: (ctx, idx) => Container(margin: const EdgeInsets.all(1), color: Colors.blueGrey),
                            ),
                          ),
                          // Radius circle
                          Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: const Color(0xFF2563EB).withOpacity(0.15),
                              border: Border.all(color: const Color(0xFF2563EB), width: 2),
                            ),
                          ),
                          // Center pin
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: _detectedLocation != null ? const Color(0xFF10B981) : const Color(0xFF2563EB),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.my_location_rounded, color: Colors.white, size: 22),
                          ),
                          Positioned(
                            bottom: 12,
                            right: 12,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(10),
                                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 8)],
                              ),
                              child: Text(
                                'Coverage: ${_radius.round()} km radius',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    // ── Location Status / Detect Button ──────────────────────
                    _buildCardSection(
                      title: 'My Current Location',
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (_detectedAddress != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFFD1FAE5),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.location_on_rounded, color: Color(0xFF10B981), size: 18),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _detectedAddress!,
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF065F46)),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                          ] else ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFFFBEB),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFFFDE68A)),
                              ),
                              child: const Row(
                                children: [
                                  Icon(Icons.location_off_rounded, color: Color(0xFFD97706), size: 18),
                                  SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      'No location set. Detect your location to get nearby job alerts.',
                                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF92400E)),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                          ],
                          SizedBox(
                            width: double.infinity,
                            child: OutlinedButton.icon(
                              onPressed: _isDetectingLocation ? null : _detectMyLocation,
                              icon: _isDetectingLocation
                                  ? const SizedBox(
                                      width: 16, height: 16,
                                      child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF2563EB)),
                                    )
                                  : const Icon(Icons.gps_fixed_rounded, size: 18),
                              label: Text(_isDetectingLocation ? 'Detecting...' : 'Use My Current Location'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: const Color(0xFF2563EB),
                                side: const BorderSide(color: Color(0xFF2563EB)),
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 18),

                    // ── Service Radius Slider ────────────────────────────────
                    _buildCardSection(
                      title: 'Service Radius',
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Operating Radius',
                                style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                              ),
                              Text(
                                '${_radius.round()} Km',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                              ),
                            ],
                          ),
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
                          const Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('2 km', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                              Text('40 km', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 18),

                    // ── Travel Settings ──────────────────────────────────────
                    _buildCardSection(
                      title: 'Travel & Distance Settings',
                      child: _buildSwitchTile(
                        title: 'Charge Travel Allowance',
                        subtitle: 'Add standard ₹50 travel fee for jobs beyond 10km',
                        value: _chargeTravelFee,
                        onChanged: (val) => setState(() => _chargeTravelFee = val),
                      ),
                    ),

                    const SizedBox(height: 32),

                    // ── Info note ─────────────────────────────────────────────
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFFBFDBFE)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.info_outline_rounded, color: Color(0xFF2563EB), size: 18),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Only jobs within your radius will appear in your Incoming Jobs. Set your location and save to enable filtering.',
                              style: TextStyle(fontSize: 11, color: Color(0xFF1D4ED8), height: 1.4),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // ── Save Button ──────────────────────────────────────────
                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: _isSaving ? null : _saveServiceArea,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          disabledBackgroundColor: const Color(0xFFCBD5E1),
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        ),
                        child: _isSaving
                            ? const SizedBox(
                                width: 22, height: 22,
                                child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                              )
                            : const Text(
                                'Save Service Area',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                              ),
                      ),
                    ),

                    const SizedBox(height: 24),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildCardSection({required String title, required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF0F172A))),
              const SizedBox(height: 3),
              Text(subtitle, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
            ],
          ),
        ),
        Switch(value: value, activeColor: const Color(0xFF2563EB), onChanged: onChanged),
      ],
    );
  }
}
