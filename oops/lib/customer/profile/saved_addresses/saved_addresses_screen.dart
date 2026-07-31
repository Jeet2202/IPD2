// File:
// lib/customer/profile/saved_addresses/saved_addresses_screen.dart

import 'package:flutter/material.dart';

class SavedAddressesScreen extends StatefulWidget {
  const SavedAddressesScreen({super.key});

  @override
  State<SavedAddressesScreen> createState() => _SavedAddressesScreenState();
}

class _SavedAddressesScreenState extends State<SavedAddressesScreen> {
  int _defaultAddressIndex = 0;

  final List<Map<String, dynamic>> _addresses = [
    {
      'type': 'HOME',
      'title': 'Green Glen Heights',
      'address': 'Flat 402, Building 4, HSR Layout Sector 6, Bengaluru, Karnataka 560102',
      'contact': 'Rahul Sharma • 9876543210',
    },
    {
      'type': 'WORK',
      'title': 'Tech Park Office',
      'address': 'Floor 3, Block B, Embassy TechVillage, Outer Ring Road, Devarabeesanahalli, Bengaluru',
      'contact': 'Rahul Sharma • 9876543210',
    },
    {
      'type': 'OTHER',
      'title': 'Parents Residence',
      'address': 'House No 142, Indiranagar 100ft Road, Bengaluru, Karnataka 560038',
      'contact': 'Vijay Sharma • 9812345678',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Saved Addresses',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              // ── Use Current GPS Location Card ────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                      child: const Icon(Icons.my_location_rounded, color: Colors.white, size: 20),
                    ),
                    const SizedBox(width: 14),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Use Current Location', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF1E3A8A))),
                          SizedBox(height: 2),
                          Text('HSR Layout Sector 6, Bengaluru', style: TextStyle(fontSize: 12, color: Color(0xFF1E40AF))),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // ── Saved Address List ──────────────────────────────────
              Column(
                children: List.generate(_addresses.length, (index) {
                  final addr = _addresses[index];
                  final isDefault = _defaultAddressIndex == index;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: isDefault ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0), width: isDefault ? 2 : 1),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4)),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(8)),
                              child: Text(
                                addr['type'] as String,
                                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF475569)),
                              ),
                            ),
                            if (isDefault)
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                                child: const Text('DEFAULT', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF16A34A))),
                              ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(addr['title'] as String, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                        const SizedBox(height: 4),
                        Text(addr['address'] as String, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), height: 1.3)),
                        const SizedBox(height: 6),
                        Text(addr['contact'] as String, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF94A3B8))),

                        const SizedBox(height: 14),
                        const Divider(color: Color(0xFFF1F5F9), height: 1),
                        const SizedBox(height: 10),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            TextButton(
                              onPressed: () => setState(() => _defaultAddressIndex = index),
                              child: Text(
                                isDefault ? 'Default Selected' : 'Set as Default',
                                style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: isDefault ? const Color(0xFF16A34A) : const Color(0xFF2563EB)),
                              ),
                            ),
                            Row(
                              children: [
                                IconButton(
                                  icon: const Icon(Icons.edit_outlined, size: 18, color: Color(0xFF64748B)),
                                  onPressed: () {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Editing address "${addr['title']}"...')),
                                    );
                                  },
                                ),
                                IconButton(
                                  icon: const Icon(Icons.delete_outline_rounded, size: 18, color: Color(0xFFEF4444)),
                                  onPressed: () {
                                    setState(() {
                                      _addresses.removeAt(index);
                                      if (_defaultAddressIndex >= _addresses.length) {
                                        _defaultAddressIndex = 0;
                                      }
                                    });
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('Address deleted successfully.')),
                                    );
                                  },
                                ),
                              ],
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                }),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Opening Location Picker to add address...')),
          );
        },
        backgroundColor: const Color(0xFF2563EB),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_location_alt_rounded),
        label: const Text('Add New Address', style: TextStyle(fontWeight: FontWeight.w800)),
      ),
    );
  }
}
