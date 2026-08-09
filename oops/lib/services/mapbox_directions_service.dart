import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class MapboxDirectionsService {
  MapboxDirectionsService._();
  static final MapboxDirectionsService instance = MapboxDirectionsService._();

  /// Fetches a route between two coordinates using Mapbox Directions API (Driving profile).
  /// Returns a list of [lng, lat] coordinate pairs that form the route geometry.
  Future<List<List<double>>> getRouteCoordinates(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) async {
    final token = dotenv.env['MAPBOX_PUBLIC_TOKEN'];
    if (token == null || token.isEmpty) {
      throw Exception('Mapbox token not found');
    }

    final url = Uri.parse(
        'https://api.mapbox.com/directions/v5/mapbox/driving/$startLng,$startLat;$endLng,$endLat?geometries=geojson&access_token=$token');

    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data['routes'] != null && data['routes'].isNotEmpty) {
        final geometry = data['routes'][0]['geometry'];
        final coordinates = geometry['coordinates'] as List;
        
        List<List<double>> polylineCoords = [];
        for (var coord in coordinates) {
          polylineCoords.add([
            (coord[0] as num).toDouble(), // lng
            (coord[1] as num).toDouble(), // lat
          ]);
        }
        return polylineCoords;
      }
      return [];
    } else {
      throw Exception('Failed to fetch route from Mapbox Directions API: ${response.statusCode}');
    }
  }
}
