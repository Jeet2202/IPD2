// File: lib/worker/profile/service_area/service_area_screen.dart

import 'package:flutter/material.dart';

class WorkerServiceAreaScreen extends StatefulWidget {
  const WorkerServiceAreaScreen({super.key});

  @override
  State<WorkerServiceAreaScreen> createState() =>
      _WorkerServiceAreaScreenState();
}

class _WorkerServiceAreaScreenState extends State<WorkerServiceAreaScreen> {
  double _radius = 12.0; // in km
  double _maxDistance = 25.0; // in km
  bool _chargeTravelFee = true;

  final List<Map<String, String>> _savedAreas = [
    {'name': 'Connaught Place, New Delhi', 'pincode': '110001', 'type': 'Primary'},
    {'name': 'South Extension, New Delhi', 'pincode': '110049', 'type': 'Secondary'},
    {'name': 'Lajpat Nagar, New Delhi', 'pincode': '110024', 'type': 'Secondary'},
  ];

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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Google Map Placeholder Card
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
                    // Grid map pattern placeholder
                    Opacity(
                      opacity: 0.15,
                      child: GridView.builder(
                        physics: const NeverScrollableScrollPhysics(),
                        gridDelegate:
                            const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 6,
                        ),
                        itemBuilder: (ctx, idx) => Container(
                          margin: const EdgeInsets.all(1),
                          color: Colors.blueGrey,
                        ),
                      ),
                    ),

                    // Radius circle visualization
                    Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF2563EB).withOpacity(0.15),
                        border: Border.all(
                            color: const Color(0xFF2563EB), width: 2),
                      ),
                    ),

                    // Center Pin Marker
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0xFF2563EB),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.my_location_rounded,
                        color: Colors.white,
                        size: 22,
                      ),
                    ),

                    Positioned(
                      bottom: 12,
                      right: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 8,
                            ),
                          ],
                        ),
                        child: Text(
                          'Coverage: ${_radius.round()} km radius',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Location Permission Status Card
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFD1FAE5),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.verified_user_rounded,
                        color: Color(0xFF10B981), size: 20),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'GPS Location Permission Granted (High Accuracy)',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF065F46),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // Service Radius Slider Card
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
                          style: TextStyle(
                            fontSize: 13,
                            color: Color(0xFF64748B),
                          ),
                        ),
                        Text(
                          '${_radius.round()} Km',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF2563EB),
                          ),
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
                        onChanged: (val) {
                          setState(() {
                            _radius = val;
                          });
                        },
                      ),
                    ),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('2 km',
                            style: TextStyle(
                                fontSize: 11, color: Color(0xFF94A3B8))),
                        Text('40 km',
                            style: TextStyle(
                                fontSize: 11, color: Color(0xFF94A3B8))),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Saved Service Areas List
              _buildCardSection(
                title: 'Saved Service Localities',
                child: Column(
                  children: [
                    ..._savedAreas.map((area) {
                      final isPrimary = area['type'] == 'Primary';
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.location_on_rounded,
                              color: isPrimary
                                  ? const Color(0xFF2563EB)
                                  : const Color(0xFF64748B),
                              size: 20,
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    area['name']!,
                                    style: const TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w700,
                                      color: Color(0xFF0F172A),
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    'PIN: ${area['pincode']} • ${area['type']}',
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: Color(0xFF64748B),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.delete_outline_rounded,
                                  size: 18, color: Color(0xFFEF4444)),
                              onPressed: () {
                                setState(() {
                                  _savedAreas.remove(area);
                                });
                              },
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: () {
                        setState(() {
                          _savedAreas.add({
                            'name': 'Uttam Nagar, New Delhi',
                            'pincode': '110059',
                            'type': 'Secondary'
                          });
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Added "Uttam Nagar, New Delhi" to service areas'),
                            backgroundColor: Color(0xFF10B981),
                          ),
                        );
                      },
                      icon: const Icon(Icons.add_location_alt_outlined, size: 18),
                      label: const Text('Add Area / Locality'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2563EB),
                        side: const BorderSide(color: Color(0xFF2563EB)),
                        minimumSize: const Size(double.infinity, 44),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Travel Settings Card
              _buildCardSection(
                title: 'Travel & Distance Limits',
                child: Column(
                  children: [
                    _buildSwitchTile(
                      title: 'Charge Travel Allowance',
                      subtitle: 'Add standard ₹50 travel fee for jobs beyond 10km',
                      value: _chargeTravelFee,
                      onChanged: (val) =>
                          setState(() => _chargeTravelFee = val),
                    ),
                    const Divider(height: 24, color: Color(0xFFF1F5F9)),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Max Travel Distance',
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            SizedBox(height: 2),
                            Text(
                              'Hard limit for job requests',
                              style: TextStyle(
                                fontSize: 12,
                                color: Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${_maxDistance.round()} Km',
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Save Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Service area updated successfully!'),
                        backgroundColor: Color(0xFF10B981),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Text(
                    'Save Service Area',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
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

  Widget _buildCardSection({
    required String title,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
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
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF0F172A),
                ),
              ),
              const SizedBox(height: 3),
              Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 12,
                  color: Color(0xFF64748B),
                ),
              ),
            ],
          ),
        ),
        Switch(
          value: value,
          activeColor: const Color(0xFF2563EB),
          onChanged: onChanged,
        ),
      ],
    );
  }
}
