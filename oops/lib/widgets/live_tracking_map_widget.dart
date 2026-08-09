import 'package:flutter/material.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/services.dart';
import '../l10n/app_translations.dart';

class LiveTrackingMapWidget extends StatefulWidget {
  final double customerLat;
  final double customerLng;
  final double? workerLat;
  final double? workerLng;
  final int? etaMinutes;
  final double? distanceMeters;
  final String? lastUpdated;

  const LiveTrackingMapWidget({
    super.key,
    required this.customerLat,
    required this.customerLng,
    this.workerLat,
    this.workerLng,
    this.etaMinutes,
    this.distanceMeters,
    this.lastUpdated,
  });

  @override
  State<LiveTrackingMapWidget> createState() => _LiveTrackingMapWidgetState();
}

class _LiveTrackingMapWidgetState extends State<LiveTrackingMapWidget> {
  MapboxMap? _mapboxMap;
  PointAnnotationManager? _pointAnnotationManager;
  PointAnnotation? _workerAnnotation;
  PointAnnotation? _customerAnnotation;

  @override
  void initState() {
    super.initState();
    final token = dotenv.env['MAPBOX_PUBLIC_TOKEN'] ?? 'YOUR_MAPBOX_PUBLIC_TOKEN_HERE';
    MapboxOptions.setAccessToken(token);
  }

  void _onMapCreated(MapboxMap mapboxMap) async {
    _mapboxMap = mapboxMap;
    
    _pointAnnotationManager = await mapboxMap.annotations.createPointAnnotationManager();

    // Create Customer Annotation
    _customerAnnotation = await _pointAnnotationManager!.create(PointAnnotationOptions(
      geometry: Point(coordinates: Position(widget.customerLng, widget.customerLat)).toJson(),
      iconImage: 'marker-15', // Built-in mapbox marker
    ));

    // Create Worker Annotation if exists
    if (widget.workerLat != null && widget.workerLng != null) {
      _createOrUpdateWorkerAnnotation(widget.workerLat!, widget.workerLng!);
    }
  }

  Future<void> _createOrUpdateWorkerAnnotation(double lat, double lng) async {
    if (_pointAnnotationManager == null) return;
    
    final point = Point(coordinates: Position(lng, lat)).toJson();
    
    if (_workerAnnotation == null) {
        _workerAnnotation = await _pointAnnotationManager!.create(PointAnnotationOptions(
            geometry: point,
            iconImage: 'car-15', // Built-in mapbox car icon
            iconSize: 2.0,
        ));
    } else {
        _workerAnnotation!.geometry = point;
        _pointAnnotationManager!.update(_workerAnnotation!);
    }
    _fitCamera(lat, lng);
  }

  void _fitCamera(double workerLat, double workerLng) {
     if (_mapboxMap == null) return;
     // To fit both, calculate bounds
     final swLat = workerLat < widget.customerLat ? workerLat : widget.customerLat;
     final neLat = workerLat > widget.customerLat ? workerLat : widget.customerLat;
     final swLng = workerLng < widget.customerLng ? workerLng : widget.customerLng;
     final neLng = workerLng > widget.customerLng ? workerLng : widget.customerLng;

     // Add padding
     final latDiff = neLat - swLat;
     final lngDiff = neLng - swLng;

     final paddedSwLat = swLat - (latDiff * 0.2);
     final paddedNeLat = neLat + (latDiff * 0.2);
     final paddedSwLng = swLng - (lngDiff * 0.2);
     final paddedNeLng = neLng + (lngDiff * 0.2);

     final cameraOptions = _mapboxMap!.cameraForCoordinateBounds(
         CoordinateBounds(
             southwest: Point(coordinates: Position(paddedSwLng, paddedSwLat)).toJson(),
             northeast: Point(coordinates: Position(paddedNeLng, paddedNeLat)).toJson(),
             infiniteBounds: false,
         ),
         MbxEdgeInsets(top: 50.0, left: 50.0, bottom: 50.0, right: 50.0),
         0.0, // bearing
         0.0  // pitch
     );
     
     cameraOptions.then((options) {
        _mapboxMap!.setCamera(options);
     });
  }

  @override
  void didUpdateWidget(covariant LiveTrackingMapWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.workerLat != oldWidget.workerLat || widget.workerLng != oldWidget.workerLng) {
      if (widget.workerLat != null && widget.workerLng != null) {
        _createOrUpdateWorkerAnnotation(widget.workerLat!, widget.workerLng!);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final hasWorkerLocation = widget.workerLat != null && widget.workerLng != null;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            color: const Color(0xFFF8FAFC),
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.location_on_rounded, color: Color(0xFF2563EB), size: 20),
                const SizedBox(width: 8),
                Text('live_worker_location'.tr(context),
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
                ),
                const Spacer(),
                if (widget.etaMinutes != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFFDBEAFE),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      'ETA: ${widget.etaMinutes} min',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF1E40AF),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          
          // Map Area
          SizedBox(
            height: 250,
            child: Stack(
              children: [
                MapWidget(
                  onMapCreated: _onMapCreated,
                  cameraOptions: CameraOptions(
                      center: Point(coordinates: Position(
                          hasWorkerLocation ? widget.workerLng! : widget.customerLng, 
                          hasWorkerLocation ? widget.workerLat! : widget.customerLat
                      )).toJson(),
                      zoom: 14.0,
                  ),
                ),
                
                // Offline overlay / waiting
                if (!hasWorkerLocation)
                  Container(
                    color: Colors.white.withOpacity(0.8),
                    alignment: Alignment.center,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.location_off_rounded, color: Color(0xFF94A3B8), size: 32),
                        const SizedBox(height: 8),
                        Text(
                          widget.lastUpdated != null
                              ? 'Location unavailable.\nLast updated: ${widget.lastUpdated}'
                              : 'Waiting for worker to start travelling...',
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: Color(0xFF64748B),
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
          
          // Footer / Details
          if (hasWorkerLocation && widget.distanceMeters != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Distance: ${(widget.distanceMeters! / 1000).toStringAsFixed(1)} km',
                    style: const TextStyle(fontSize: 13, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
                  ),
                  if (widget.lastUpdated != null)
                    Text(
                      'Updated: ${widget.lastUpdated}',
                      style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                    ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
