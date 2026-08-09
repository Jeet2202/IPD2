// File: lib/customer/address/map_picker_screen.dart
import 'package:flutter/material.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart' hide Size;
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:latlong2/latlong.dart' as ll;

import '../../services/location_service.dart';
import '../../l10n/app_translations.dart';

class MapPickerResult {
  final ll.LatLng location;
  final ReverseGeocodeResult address;

  const MapPickerResult({required this.location, required this.address});
}

class MapPickerScreen extends StatefulWidget {
  final ll.LatLng? initialLocation;

  const MapPickerScreen({super.key, this.initialLocation});

  @override
  State<MapPickerScreen> createState() => _MapPickerScreenState();
}

class _MapPickerScreenState extends State<MapPickerScreen> {
  static const _blue = Color(0xFF2563EB);
  static const _darkText = Color(0xFF0F172A);
  static const _mutedText = Color(0xFF64748B);
  static const _border = Color(0xFFE2E8F0);

  static const _defaultCenter = ll.LatLng(19.0760, 72.8777);

  MapboxMap? _mapboxMap;
  late ll.LatLng _selectedLocation;

  bool _isGeocodingLoading = false;
  bool _isLocatingGps = false;
  String? _previewAddress;

  DateTime _lastGeocode = DateTime(0);
  double _currentZoom = 15.0;

  @override
  void initState() {
    super.initState();
    _selectedLocation = widget.initialLocation ?? _defaultCenter;
    final token = dotenv.env['MAPBOX_PUBLIC_TOKEN'] ?? 'YOUR_MAPBOX_PUBLIC_TOKEN_HERE';
    MapboxOptions.setAccessToken(token);
    _geocodeSelected();
  }

  void _onMapCreated(MapboxMap mapboxMap) {
    _mapboxMap = mapboxMap;
  }

  Future<void> _fetchCenterAndGeocode() async {
    if (_mapboxMap == null) return;
    try {
      final cameraState = await _mapboxMap!.getCameraState();
      
      // Parse GeoJSON Point map to get coordinates
      final centerPoint = cameraState.center;
      if (centerPoint != null) {
          final lng = centerPoint.coordinates.lng.toDouble();
          final lat = centerPoint.coordinates.lat.toDouble();
          
          setState(() {
            _selectedLocation = ll.LatLng(lat, lng);
            _currentZoom = (cameraState.zoom as num).toDouble();
          });
          
          _geocodeSelected();
      }
    } catch (e) {
      debugPrint("Error fetching map center: $e");
    }
  }

  Future<void> _goToCurrentLocation() async {
    setState(() {
      _isLocatingGps = true;
    });

    try {
      final loc = await LocationService.instance.getCurrentLocation();
      if (!mounted) return;

      setState(() {
        _selectedLocation = ll.LatLng(loc.latitude, loc.longitude);
        _isLocatingGps = false;
      });

      if (_mapboxMap != null) {
        _mapboxMap!.setCamera(CameraOptions(
            center: Point(coordinates: Position(loc.longitude, loc.latitude)),
            zoom: 16.0,
        ));
      }
      await _geocodeSelected();
    } on LocationException catch (e) {
      if (!mounted) return;
      setState(() {
        _isLocatingGps = false;
      });
      _showLocationErrorDialog(e);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLocatingGps = false;
      });
    }
  }

  Future<void> _geocodeSelected() async {
    final now = DateTime.now();
    if (now.difference(_lastGeocode).inMilliseconds < 1500) return;
    _lastGeocode = now;

    setState(() {
      _isGeocodingLoading = true;
    });

    final result = await LocationService.instance.reverseGeocode(
      LatLng(_selectedLocation.latitude, _selectedLocation.longitude)
    );

    if (!mounted) return;
    setState(() {
      _isGeocodingLoading = false;
      _previewAddress = result.displayName ??
          [result.addressLine, result.city, result.state]
              .where((s) => s != null && s.isNotEmpty)
              .join(', ');
      if (_previewAddress?.isEmpty ?? true) {
        _previewAddress = '${_selectedLocation.latitude.toStringAsFixed(5)}, '
            '${_selectedLocation.longitude.toStringAsFixed(5)}';
      }
    });
  }

  Future<void> _confirm() async {
    final result = await LocationService.instance.reverseGeocode(
      LatLng(_selectedLocation.latitude, _selectedLocation.longitude)
    );
    if (!mounted) return;
    Navigator.pop(
      context,
      MapPickerResult(location: _selectedLocation, address: result),
    );
  }

  String _friendlyLocationError(LocationException e) {
    switch (e.code) {
      case LocationErrorCode.serviceDisabled:
        return 'GPS is disabled. Please enable location services.';
      case LocationErrorCode.permissionDenied:
        return 'Location permission denied.';
      case LocationErrorCode.permissionPermanentlyDenied:
        return 'Location permission permanently denied. Go to Settings.';
      case LocationErrorCode.timeout:
        return 'GPS timed out. Try again.';
      case LocationErrorCode.noInternet:
        return 'No internet connection.';
      default:
        return 'Location unavailable.';
    }
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
          style: const TextStyle(fontWeight: FontWeight.w800),
        ),
        content: Text(
          _friendlyLocationError(e),
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 14, color: _mutedText),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('cancel'.tr(context), style: const TextStyle(color: _mutedText)),
          ),
          if (isPermanent)
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                await LocationService.instance.openAppSettings();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: _blue,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: Text('open_settings'.tr(context)),
            )
          else if (isDisabled)
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(ctx);
                await LocationService.instance.openLocationSettings();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: _blue,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: Text('enable_gps'.tr(context)),
            ),
        ],
      ),
    );
  }

  void _zoomIn() {
    if (_mapboxMap != null) {
      _currentZoom = (_currentZoom + 1).clamp(4.0, 19.0);
      _mapboxMap!.setCamera(CameraOptions(zoom: _currentZoom));
    }
  }

  void _zoomOut() {
    if (_mapboxMap != null) {
      _currentZoom = (_currentZoom - 1).clamp(4.0, 19.0);
      _mapboxMap!.setCamera(CameraOptions(zoom: _currentZoom));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: _darkText),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('select_location'.tr(context),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _darkText),
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: _border),
        ),
      ),
      body: Stack(
        children: [
          // ── Mapbox Map ────────────────────────────────────────────
          MapWidget(
            onMapCreated: _onMapCreated,
            cameraOptions: CameraOptions(
                center: Point(coordinates: Position(
                    _selectedLocation.longitude, 
                    _selectedLocation.latitude
                )),
                zoom: _currentZoom,
            ),
            onCameraChangeListener: (CameraChangedEventData event) {
                _fetchCenterAndGeocode();
            },
          ),

          // ── Center Marker (always points at selected location) ───────
          const Center(
            child: Padding(
              padding: EdgeInsets.only(bottom: 40), // offset for pin drop effect
              child: _MapMarker(),
            ),
          ),

          // ── Current Location FAB ─────────────────────────────────────
          Positioned(
            right: 16,
            bottom: 200,
            child: _LocationFab(
              isLoading: _isLocatingGps,
              onPressed: _goToCurrentLocation,
            ),
          ),

          // ── Zoom Controls ────────────────────────────────────────────
          Positioned(
            right: 16,
            bottom: 280,
            child: _ZoomControls(
              onZoomIn: _zoomIn,
              onZoomOut: _zoomOut,
            ),
          ),

          // ── Bottom Address Preview + Confirm ─────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: _BottomPanel(
              isLoading: _isGeocodingLoading,
              address: _previewAddress,
              onConfirm: _confirm,
            ),
          ),
        ],
      ),
    );
  }
}

class _MapMarker extends StatelessWidget {
  const _MapMarker();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 46,
          height: 46,
          decoration: BoxDecoration(
            color: const Color(0xFF2563EB),
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 3),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF2563EB).withValues(alpha: 0.4),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: const Icon(Icons.location_on_rounded, color: Colors.white, size: 24),
        ),
        // Drop shadow triangle
        CustomPaint(
          size: const Size(12, 8),
          painter: _MarkerTrianglePainter(),
        ),
      ],
    );
  }
}

class _MarkerTrianglePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF2563EB)
      ..style = PaintingStyle.fill;
    final path = Path()
      ..moveTo(0, 0)
      ..lineTo(size.width / 2, size.height)
      ..lineTo(size.width, 0)
      ..close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _LocationFab extends StatelessWidget {
  final bool isLoading;
  final VoidCallback onPressed;

  const _LocationFab({required this.isLoading, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton(
      heroTag: 'map_location_fab',
      mini: true,
      foregroundColor: const Color(0xFF2563EB),
      elevation: 4,
      onPressed: isLoading ? null : onPressed,
      child: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFF2563EB),
              ),
            )
          : const Icon(Icons.my_location_rounded, size: 22),
    );
  }
}

class _ZoomControls extends StatelessWidget {
  final VoidCallback onZoomIn;
  final VoidCallback onZoomOut;

  const _ZoomControls({required this.onZoomIn, required this.onZoomOut});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _ZoomBtn(
          icon: Icons.add,
          onPressed: onZoomIn,
        ),
        const SizedBox(height: 4),
        _ZoomBtn(
          icon: Icons.remove,
          onPressed: onZoomOut,
        ),
      ],
    );
  }
}

class _ZoomBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;

  const _ZoomBtn({required this.icon, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(8),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.15),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(icon, size: 20, color: const Color(0xFF0F172A)),
      ),
    );
  }
}

class _BottomPanel extends StatelessWidget {
  final bool isLoading;
  final String? address;
  final VoidCallback onConfirm;

  const _BottomPanel({
    required this.isLoading,
    required this.address,
    required this.onConfirm,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.12),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Handle bar
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFE2E8F0),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          Row(
            children: [
              const Icon(Icons.location_on_rounded, color: Color(0xFF2563EB), size: 18),
              const SizedBox(width: 8),
              Text('selected_location'.tr(context),
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF64748B),
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          if (isLoading)
            Row(
              children: [
                const SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Color(0xFF2563EB),
                  ),
                ),
                const SizedBox(width: 10),
                Text('fetching_address'.tr(context),
                  style: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                ),
              ],
            )
          else
            Text(
              address ?? 'Move the map to select a location',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Color(0xFF0F172A),
                height: 1.4,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),

          const SizedBox(height: 20),

          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              onPressed: onConfirm,
              icon: const Icon(Icons.check_circle_outline_rounded, size: 20),
              label: Text('confirm_this_location'.tr(context),
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
