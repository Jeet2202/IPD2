import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart' as ll;
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
  late final MapController _mapController;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(covariant LiveTrackingMapWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.workerLat != oldWidget.workerLat || widget.workerLng != oldWidget.workerLng) {
      if (widget.workerLat != null && widget.workerLng != null) {
        _fitBounds();
      }
    }
  }

  void _fitBounds() {
    if (widget.workerLat == null || widget.workerLng == null) return;
    
    final bounds = LatLngBounds.fromPoints([
      ll.LatLng(widget.customerLat, widget.customerLng),
      ll.LatLng(widget.workerLat!, widget.workerLng!),
    ]);

    // Add padding around the bounds
    _mapController.fitCamera(
      CameraFit.bounds(
        bounds: bounds,
        padding: const EdgeInsets.all(50.0),
      ),
    );
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
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF0F172A)),
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
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: hasWorkerLocation 
                        ? ll.LatLng(widget.workerLat!, widget.workerLng!)
                        : ll.LatLng(widget.customerLat, widget.customerLng),
                    initialZoom: 14.0,
                    onMapReady: () {
                      if (hasWorkerLocation) {
                        _fitBounds();
                      }
                    },
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.ally.app',
                      maxZoom: 19,
                    ),
                    if (hasWorkerLocation)
                      PolylineLayer(
                        polylines: [
                          Polyline(
                            points: [
                              ll.LatLng(widget.workerLat!, widget.workerLng!),
                              ll.LatLng(widget.customerLat, widget.customerLng),
                            ],
                            strokeWidth: 3.0,
                            color: const Color(0xFF2563EB).withOpacity(0.5),
                          ),
                        ],
                      ),
                    MarkerLayer(
                      markers: [
                        // Customer Marker
                        Marker(
                          point: ll.LatLng(widget.customerLat, widget.customerLng),
                          width: 40,
                          height: 40,
                          child: const Icon(Icons.home_rounded, color: Color(0xFFEF4444), size: 30),
                        ),
                        // Worker Marker
                        if (hasWorkerLocation)
                          Marker(
                            point: ll.LatLng(widget.workerLat!, widget.workerLng!),
                            width: 40,
                            height: 40,
                            child: const Icon(Icons.directions_car_rounded, color: Color(0xFF2563EB), size: 30),
                          ),
                      ],
                    ),
                  ],
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
