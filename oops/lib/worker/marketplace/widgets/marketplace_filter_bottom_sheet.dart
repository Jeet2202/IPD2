// File: lib/worker/marketplace/widgets/marketplace_filter_bottom_sheet.dart

import 'package:flutter/material.dart';

class MarketplaceFilterData {
  final String? bookingType;
  final String? scheduledDate;
  final double? minPrice;
  final double? maxPrice;

  MarketplaceFilterData({
    this.bookingType,
    this.scheduledDate,
    this.minPrice,
    this.maxPrice,
  });

  bool get hasActiveFilters =>
      (bookingType != null && bookingType!.isNotEmpty) ||
      (scheduledDate != null && scheduledDate!.isNotEmpty) ||
      minPrice != null ||
      maxPrice != null;

  MarketplaceFilterData copyWith({
    String? bookingType,
    String? scheduledDate,
    double? minPrice,
    double? maxPrice,
    bool clearType = false,
    bool clearDate = false,
    bool clearPrice = false,
  }) {
    return MarketplaceFilterData(
      bookingType: clearType ? null : (bookingType ?? this.bookingType),
      scheduledDate: clearDate ? null : (scheduledDate ?? this.scheduledDate),
      minPrice: clearPrice ? null : (minPrice ?? this.minPrice),
      maxPrice: clearPrice ? null : (maxPrice ?? this.maxPrice),
    );
  }
}

class MarketplaceFilterBottomSheet extends StatefulWidget {
  final MarketplaceFilterData initialFilter;

  const MarketplaceFilterBottomSheet({
    super.key,
    required this.initialFilter,
  });

  static Future<MarketplaceFilterData?> show(
    BuildContext context,
    MarketplaceFilterData initialFilter,
  ) {
    return showModalBottomSheet<MarketplaceFilterData>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => MarketplaceFilterBottomSheet(initialFilter: initialFilter),
    );
  }

  @override
  State<MarketplaceFilterBottomSheet> createState() =>
      _MarketplaceFilterBottomSheetState();
}

class _MarketplaceFilterBottomSheetState
    extends State<MarketplaceFilterBottomSheet> {
  String? _selectedBookingType;
  String? _selectedDate;
  RangeValues _priceRange = const RangeValues(0, 5000);
  bool _enablePriceFilter = false;

  @override
  void initState() {
    super.initState();
    _selectedBookingType = widget.initialFilter.bookingType;
    _selectedDate = widget.initialFilter.scheduledDate;

    if (widget.initialFilter.minPrice != null || widget.initialFilter.maxPrice != null) {
      _enablePriceFilter = true;
      _priceRange = RangeValues(
        widget.initialFilter.minPrice ?? 0,
        widget.initialFilter.maxPrice ?? 5000,
      );
    }
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: now,
      lastDate: now.add(const Duration(days: 60)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: Color(0xFF2563EB),
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      final formatted =
          '${picked.year}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}';
      setState(() {
        _selectedDate = formatted;
      });
    }
  }

  void _clearAll() {
    setState(() {
      _selectedBookingType = null;
      _selectedDate = null;
      _enablePriceFilter = false;
      _priceRange = const RangeValues(0, 5000);
    });
  }

  void _apply() {
    final filter = MarketplaceFilterData(
      bookingType: _selectedBookingType,
      scheduledDate: _selectedDate,
      minPrice: _enablePriceFilter ? _priceRange.start : null,
      maxPrice: _enablePriceFilter ? _priceRange.end : null,
    );
    Navigator.pop(context, filter);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.8,
      ),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle
          const SizedBox(height: 12),
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: const Color(0xFFCBD5E1),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 12),

          // Title Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Filter Bookings',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                TextButton(
                  onPressed: _clearAll,
                  child: const Text(
                    'Clear All',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFFEF4444),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const Divider(height: 1, color: Color(0xFFF1F5F9)),

          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 1. Booking Type Section
                  const Text(
                    'Booking Type',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      _buildTypeChip(null, 'All Types'),
                      const SizedBox(width: 8),
                      _buildTypeChip('normal_service', 'Standard Service'),
                      const SizedBox(width: 8),
                      _buildTypeChip('inspection_request', 'Inspection'),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // 2. Scheduled Date Section
                  const Text(
                    'Scheduled Date',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 10),
                  GestureDetector(
                    onTap: _pickDate,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFE2E8F0)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.calendar_month_rounded,
                                  size: 18, color: Color(0xFF2563EB)),
                              const SizedBox(width: 10),
                              Text(
                                _selectedDate ?? 'Select preferred date',
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: _selectedDate != null
                                      ? FontWeight.w700
                                      : FontWeight.w500,
                                  color: _selectedDate != null
                                      ? const Color(0xFF0F172A)
                                      : const Color(0xFF94A3B8),
                                ),
                              ),
                            ],
                          ),
                          if (_selectedDate != null)
                            GestureDetector(
                              onTap: () {
                                setState(() {
                                  _selectedDate = null;
                                });
                              },
                              child: const Icon(Icons.close_rounded,
                                  size: 18, color: Color(0xFF64748B)),
                            )
                          else
                            const Icon(Icons.arrow_drop_down_rounded,
                                color: Color(0xFF64748B)),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // 3. Price Range Section
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Estimated Price Range',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      Switch(
                        value: _enablePriceFilter,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) {
                          setState(() {
                            _enablePriceFilter = val;
                          });
                        },
                      ),
                    ],
                  ),

                  if (_enablePriceFilter) ...[
                    const SizedBox(height: 6),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '₹ ${_priceRange.start.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                        Text(
                          '₹ ${_priceRange.end.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF2563EB),
                          ),
                        ),
                      ],
                    ),
                    RangeSlider(
                      values: _priceRange,
                      min: 0,
                      max: 5000,
                      divisions: 50,
                      activeColor: const Color(0xFF2563EB),
                      inactiveColor: const Color(0xFFE2E8F0),
                      labels: RangeLabels(
                        '₹ ${_priceRange.start.toStringAsFixed(0)}',
                        '₹ ${_priceRange.end.toStringAsFixed(0)}',
                      ),
                      onChanged: (values) {
                        setState(() {
                          _priceRange = values;
                        });
                      },
                    ),
                  ],

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),

          // Apply Button
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _apply,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 0,
                ),
                child: const Text(
                  'Apply Filters',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypeChip(String? typeValue, String label) {
    final isSelected = _selectedBookingType == typeValue;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedBookingType = typeValue;
        });
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
            color: isSelected ? Colors.white : const Color(0xFF475569),
          ),
        ),
      ),
    );
  }
}
