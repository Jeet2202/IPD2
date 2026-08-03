// File: lib/customer/address/select_address_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../models/address_model.dart';
import '../../services/address_service.dart';
import '../../services/api_service.dart';

class SelectAddressScreen extends StatefulWidget {
  const SelectAddressScreen({super.key});

  @override
  State<SelectAddressScreen> createState() => _SelectAddressScreenState();
}

class _SelectAddressScreenState extends State<SelectAddressScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<AddressModel> _savedAddresses = [];
  int _selectedIndex = 0;

  static const _blue = Color(0xFF2563EB);
  static const _darkText = Color(0xFF0F172A);
  static const _mutedText = Color(0xFF64748B);
  static const _border = Color(0xFFE2E8F0);

  @override
  void initState() {
    super.initState();
    _loadAddresses();
  }

  Future<void> _loadAddresses() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final list = await AddressService.instance.listAddresses();
      if (!mounted) return;
      setState(() {
        _savedAddresses = list;
        _isLoading = false;
        // Select default address if available
        if (list.isNotEmpty) {
          final defaultIdx = list.indexWhere((a) => a.isDefault);
          _selectedIndex = defaultIdx >= 0 ? defaultIdx : 0;
        }
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = e.message;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = 'Failed to load saved addresses. Please try again.';
      });
    }
  }

  Future<void> _navigateToAddAddress() async {
    final result = await Navigator.pushNamed(context, AppRoutes.addAddress);
    if (result == true && mounted) {
      _loadAddresses();
    }
  }

  void _confirmSelection() {
    if (_savedAddresses.isEmpty || _selectedIndex >= _savedAddresses.length) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select or add a service address.')),
      );
      return;
    }
    final selected = _savedAddresses[_selectedIndex];
    Navigator.pop(context, selected);
  }

  IconData _getLabelIcon(String label) {
    switch (label.toLowerCase()) {
      case 'home':
        return Icons.home_rounded;
      case 'office':
        return Icons.work_rounded;
      default:
        return Icons.place_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: _darkText),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Select Address',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _darkText),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.add_location_alt_rounded, color: _blue),
            onPressed: _navigateToAddAddress,
          ),
        ],
      ),
      body: Stack(
        children: [
          RefreshIndicator(
            onRefresh: _loadAddresses,
            color: _blue,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Header row
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Saved Addresses',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _darkText, letterSpacing: -0.4),
                            ),
                            GestureDetector(
                              onTap: _navigateToAddAddress,
                              child: const Row(
                                children: [
                                  Icon(Icons.add_rounded, size: 18, color: _blue),
                                  SizedBox(width: 4),
                                  Text(
                                    'Add New',
                                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _blue),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),

                        const SizedBox(height: 16),

                        if (_isLoading)
                          _buildLoadingView()
                        else if (_errorMessage != null)
                          _buildErrorView()
                        else if (_savedAddresses.isEmpty)
                          _buildEmptyView()
                        else
                          _buildAddressList(),

                        const SizedBox(height: 100),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Sticky Confirm Button
          if (!_isLoading && _savedAddresses.isNotEmpty)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 20, offset: const Offset(0, -4)),
                  ],
                ),
                child: SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _confirmSelection,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _blue,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                    child: const Text(
                      'Confirm Address',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildLoadingView() {
    return Column(
      children: List.generate(
        3,
        (_) => Container(
          margin: const EdgeInsets.only(bottom: 14),
          height: 100,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: _border),
          ),
        ),
      ),
    );
  }

  Widget _buildErrorView() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Column(
        children: [
          const Icon(Icons.error_outline_rounded, color: Color(0xFFDC2626), size: 36),
          const SizedBox(height: 10),
          Text(
            _errorMessage ?? 'Unable to load addresses.',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 13, color: _mutedText),
          ),
          const SizedBox(height: 14),
          ElevatedButton.icon(
            onPressed: _loadAddresses,
            icon: const Icon(Icons.refresh_rounded, size: 16),
            label: const Text('Try Again'),
            style: ElevatedButton.styleFrom(
              backgroundColor: _blue,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border),
      ),
      child: Column(
        children: [
          const Icon(Icons.location_off_rounded, size: 48, color: _blue),
          const SizedBox(height: 12),
          const Text(
            'No Saved Addresses Found',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: _darkText),
          ),
          const SizedBox(height: 6),
          const Text(
            'Please add a service address to proceed with booking.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: _mutedText),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _navigateToAddAddress,
            icon: const Icon(Icons.add_location_alt_rounded, size: 18),
            label: const Text('Add New Address', style: TextStyle(fontWeight: FontWeight.w800)),
            style: ElevatedButton.styleFrom(
              backgroundColor: _blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAddressList() {
    return Column(
      children: List.generate(_savedAddresses.length, (index) {
        final addr = _savedAddresses[index];
        final isSelected = index == _selectedIndex;

        return GestureDetector(
          onTap: () => setState(() => _selectedIndex = index),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            margin: const EdgeInsets.only(bottom: 14),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: isSelected ? _blue : _border,
                width: isSelected ? 2 : 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: isSelected ? _blue.withValues(alpha: 0.08) : Colors.black.withValues(alpha: 0.02),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Radio<int>(
                  value: index,
                  groupValue: _selectedIndex,
                  activeColor: _blue,
                  onChanged: (val) => setState(() => _selectedIndex = val!),
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(_getLabelIcon(addr.label), size: 18, color: _blue),
                          const SizedBox(width: 8),
                          Text(
                            addr.label,
                            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: _darkText),
                          ),
                          if (addr.isDefault) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: const Color(0xFFDCFCE7),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'DEFAULT',
                                style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFF16A34A)),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${addr.fullName} • ${addr.phone}',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: _darkText),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        addr.shortAddress,
                        style: const TextStyle(fontSize: 13, color: _mutedText, height: 1.4),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      }),
    );
  }
}
