// File: lib/customer/normal_booking/booking_details/booking_details_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_dimensions.dart';
import '../../../models/address_model.dart';
import '../../../models/booking_model.dart';
import '../../../models/service_model.dart';
import '../../../services/address_service.dart';
import '../../../services/booking_service.dart';

class BookingDetailsScreen extends StatefulWidget {
  final ServiceModel? service;
  final String? initialBookingType;

  const BookingDetailsScreen({
    super.key,
    this.service,
    this.initialBookingType,
  });

  @override
  State<BookingDetailsScreen> createState() => _BookingDetailsScreenState();
}

class _BookingDetailsScreenState extends State<BookingDetailsScreen> {
  final AddressService _addressService = AddressService.instance;
  final TextEditingController _notesController = TextEditingController();
  final TextEditingController _problemDescController = TextEditingController();
  final TextEditingController _customTitleController = TextEditingController();
  final TextEditingController _customDescController = TextEditingController();
  final TextEditingController _customBudgetController = TextEditingController();

  String _selectedCategorySlug = 'plumbing';

  final List<Map<String, String>> _categories = const [
    {'name': 'Plumbing', 'slug': 'plumbing'},
    {'name': 'Electrical', 'slug': 'electrical'},
    {'name': 'Cleaning', 'slug': 'cleaning'},
    {'name': 'AC & Appliance Repair', 'slug': 'appliance-repair'},
    {'name': 'Painting', 'slug': 'painting'},
    {'name': 'Carpentry', 'slug': 'carpentry'},
    {'name': 'General Maintenance', 'slug': 'general'},
  ];

  ServiceModel? _service;
  List<AddressModel> _savedAddresses = [];
  AddressModel? _selectedAddress;

  bool _isLoadingAddresses = true;
  String? _addressError;

  late String _bookingType; // 'normal_service', 'custom_service', or 'inspection_request'
  late DateTime _selectedDate;
  String _selectedTimeSlot = '';
  bool _isLoadingSlots = false;
  List<TimeSlotModel> _availableSlots = [];

  @override
  void initState() {
    super.initState();
    _selectedDate = DateTime.now();
    _bookingType = widget.initialBookingType ?? 'normal_service';

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractArgsAndFetch();
      _fetchSlotsForDate(_selectedDate);
    });
  }

  void _extractArgsAndFetch() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map<String, dynamic>) {
      if (args['service'] is ServiceModel) {
        _service = args['service'] as ServiceModel;
      }
      if (args['booking_type'] is String) {
        _bookingType = args['booking_type'] as String;
      }
    } else if (widget.service != null) {
      _service = widget.service;
    }

    _fetchSavedAddresses();
  }

  Future<void> _fetchSavedAddresses() async {
    setState(() {
      _isLoadingAddresses = true;
      _addressError = null;
    });

    try {
      final list = await _addressService.listAddresses();
      if (!mounted) return;

      setState(() {
        _savedAddresses = list;
        _isLoadingAddresses = false;
        // Pre-select default address or first address
        if (list.isNotEmpty) {
          _selectedAddress = list.firstWhere(
            (a) => a.isDefault,
            orElse: () => list.first,
          );
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoadingAddresses = false;
        _addressError = 'Failed to load saved addresses. Please try again.';
      });
    }
  }

  Future<void> _selectDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate.isBefore(now) ? now : _selectedDate,
      firstDate: DateTime(now.year, now.month, now.day),
      lastDate: DateTime.now().add(const Duration(days: 90)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppColors.primary,
              onPrimary: Colors.white,
              onSurface: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null && mounted) {
      setState(() {
        _selectedDate = picked;
      });
      _fetchSlotsForDate(picked);
    }
  }

  Future<void> _fetchSlotsForDate(DateTime dt) async {
    setState(() {
      _isLoadingSlots = true;
    });

    final dateStr = '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';

    try {
      final res = await BookingService.instance.fetchAvailableSlots(dateStr);
      if (!mounted) return;

      setState(() {
        _availableSlots = res.slots;
        _isLoadingSlots = false;

        final avail = res.slots.where((s) => s.isAvailable).toList();
        if (avail.isNotEmpty) {
          _selectedTimeSlot = avail.first.slotId;
        } else {
          _selectedTimeSlot = '';
        }
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoadingSlots = false;
      });
    }
  }

  Future<void> _addNewAddress() async {
    final result = await Navigator.pushNamed(context, AppRoutes.addAddress);
    if (result == true && mounted) {
      _fetchSavedAddresses();
    }
  }

  Future<void> _changeAddress() async {
    final selected = await Navigator.pushNamed(context, AppRoutes.selectAddress);
    if (selected is AddressModel && mounted) {
      setState(() {
        _selectedAddress = selected;
      });
    } else if (mounted) {
      _fetchSavedAddresses();
    }
  }

  void _showAddressPickerModal() {
    showModalBottomSheet(
      context: context,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Select Service Address',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      _addNewAddress();
                    },
                    icon: const Icon(Icons.add_rounded, size: 18, color: AppColors.primary),
                    label: const Text('Add New', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Flexible(
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: _savedAddresses.length,
                  separatorBuilder: (_, __) => const Divider(height: 1, color: AppColors.divider),
                  itemBuilder: (context, idx) {
                    final addr = _savedAddresses[idx];
                    final isSelected = _selectedAddress?.id == addr.id;

                    return ListTile(
                      contentPadding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                      leading: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: isSelected ? AppColors.primary.withValues(alpha: 0.1) : const Color(0xFFF1F5F9),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          addr.label == 'Home'
                              ? Icons.home_rounded
                              : addr.label == 'Office'
                                  ? Icons.work_rounded
                                  : Icons.location_on_rounded,
                          color: isSelected ? AppColors.primary : AppColors.textSecondary,
                          size: 20,
                        ),
                      ),
                      title: Row(
                        children: [
                          Text(addr.label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          if (addr.isDefault) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(4)),
                              child: const Text('DEFAULT', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
                            ),
                          ],
                        ],
                      ),
                      subtitle: Text(
                        '${addr.fullName} • ${addr.shortAddress}',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontSize: 12),
                      ),
                      trailing: isSelected
                          ? const Icon(Icons.check_circle_rounded, color: AppColors.primary)
                          : const Icon(Icons.radio_button_unchecked_rounded, color: AppColors.textHint),
                      onTap: () {
                        setState(() => _selectedAddress = addr);
                        Navigator.pop(ctx);
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _proceedToSummary() {
    if (_selectedAddress == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select or add a service address.')),
      );
      return;
    }

    if (_bookingType == 'normal_service' && _service == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a valid service.')),
      );
      return;
    }

    if (_bookingType == 'custom_service' && _customTitleController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a service title for your custom booking.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    if (_bookingType == 'inspection_request' && _problemDescController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please provide a problem description for the inspection request.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final dateStr = '${_selectedDate.year}-${_selectedDate.month.toString().padLeft(2, '0')}-${_selectedDate.day.toString().padLeft(2, '0')}';

    Navigator.pushNamed(
      context,
      AppRoutes.bookingSummary,
      arguments: {
        'service': _service,
        'address': _selectedAddress,
        'booking_type': _bookingType,
        'scheduled_date': dateStr,
        'scheduled_time': _selectedTimeSlot,
        'customer_notes': _notesController.text.trim(),
        'problem_description': _problemDescController.text.trim(),
        'custom_title': _customTitleController.text.trim(),
        'custom_description': _customDescController.text.trim(),
        'custom_budget': double.tryParse(_customBudgetController.text.trim()),
        'category_slug': _selectedCategorySlug,
      },
    );
  }

  @override
  void dispose() {
    _notesController.dispose();
    _problemDescController.dispose();
    _customTitleController.dispose();
    _customDescController.dispose();
    _customBudgetController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final service = _service;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Column(
          children: [
            Text(
              'Step 1 of 2',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.primary),
            ),
            Text(
              'Booking Details',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Selected Service Summary ─────────────────────────
                if (service != null) ...[
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppColors.divider),
                    ),
                    child: Row(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Container(
                            width: 60,
                            height: 60,
                            color: const Color(0xFFF1F5F9),
                            child: Image.network(
                              service.resolvedImage,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => const Icon(Icons.build_rounded, color: AppColors.primary, size: 28),
                            ),
                          ),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                service.name,
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${service.categorySlug.replaceAll('-', ' ').toUpperCase()} • ${service.durationDisplay}',
                                style: const TextStyle(fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.primary),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                ],

                // ── Address Selection Section ──────────────────────────
                _buildSectionHeader(
                  title: 'Service Address',
                  icon: Icons.location_on_rounded,
                ),
                const SizedBox(height: 10),
                _buildAddressCard(),

                const SizedBox(height: 24),

                // ── Booking Type Selector ──────────────────────────────
                _buildSectionHeader(
                  title: 'Choose Booking Type',
                  icon: Icons.category_rounded,
                ),
                const SizedBox(height: 10),
                Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: _buildBookingTypeTile(
                            typeKey: 'normal_service',
                            title: 'Predefined Service',
                            subtitle: 'Fixed catalog booking',
                            icon: Icons.flash_on_rounded,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: _buildBookingTypeTile(
                            typeKey: 'custom_service',
                            title: 'Custom Service',
                            subtitle: 'Your custom requirements',
                            icon: Icons.edit_attributes_rounded,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    _buildBookingTypeTile(
                      typeKey: 'inspection_request',
                      title: 'Request Inspection Visit',
                      subtitle: 'On-site diagnostic before quotation',
                      icon: Icons.search_rounded,
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // ── Category Selector for Custom / Standalone Inspection ─────
                if (_bookingType != 'normal_service' || _service == null) ...[
                  _buildSectionHeader(
                    title: 'Select Service Category',
                    icon: Icons.grid_view_rounded,
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.divider),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedCategorySlug,
                        isExpanded: true,
                        icon: const Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.primary),
                        items: _categories.map((c) {
                          return DropdownMenuItem<String>(
                            value: c['slug'],
                            child: Text(
                              c['name']!,
                              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                            ),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) {
                            setState(() => _selectedCategorySlug = val);
                          }
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // ── Custom Service Requirements Form ──────────────────────
                if (_bookingType == 'custom_service') ...[
                  _buildSectionHeader(
                    title: 'Custom Service Details',
                    icon: Icons.edit_document,
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.primary.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Service Title *',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _customTitleController,
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            hintText: 'e.g., Fix leaking underground pipe & replace tap',
                            hintStyle: const TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: const EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppColors.divider)),
                          ),
                        ),
                        const SizedBox(height: 14),
                        const Text(
                          'Detailed Requirements (Optional)',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _customDescController,
                          maxLines: 3,
                          style: const TextStyle(fontSize: 14),
                          decoration: InputDecoration(
                            hintText: 'Provide details on what needs to be repaired or installed...',
                            hintStyle: const TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: const EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppColors.divider)),
                          ),
                        ),
                        const SizedBox(height: 14),
                        const Text(
                          'Estimated Budget (Optional - INR)',
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        const SizedBox(height: 6),
                        TextField(
                          controller: _customBudgetController,
                          keyboardType: TextInputType.number,
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            prefixText: '₹ ',
                            hintText: '500',
                            hintStyle: const TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: const EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: AppColors.divider)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // ── Date Selector ──────────────────────────────────────
                _buildSectionHeader(
                  title: 'Preferred Date',
                  icon: Icons.calendar_month_rounded,
                ),
                const SizedBox(height: 10),
                GestureDetector(
                  onTap: _selectDate,
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.divider),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.today_rounded, color: AppColors.primary, size: 22),
                            const SizedBox(width: 12),
                            Text(
                              '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}',
                              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                        const Row(
                          children: [
                            Text('Change Date', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                            SizedBox(width: 4),
                            Icon(Icons.chevron_right_rounded, color: AppColors.primary, size: 18),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // ── Time Slot Selector ─────────────────────────────────
                _buildSectionHeader(
                  title: 'Preferred Time Slot',
                  icon: Icons.access_time_rounded,
                ),
                _buildTimeSlotsWidget(),

                const SizedBox(height: 24),

                // ── Inspection Problem Description (Required if inspection_request) ──
                if (_bookingType == 'inspection_request') ...[
                  _buildSectionHeader(
                    title: 'Problem Description (Required)',
                    icon: Icons.assignment_late_rounded,
                  ),
                  const SizedBox(height: 10),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFD97706), width: 1.5),
                    ),
                    child: TextField(
                      controller: _problemDescController,
                      maxLines: 3,
                      style: const TextStyle(fontSize: 14),
                      decoration: const InputDecoration(
                        hintText: 'Describe the issue in detail (e.g. AC unit leaking, switchboard sparking)...',                        border: InputBorder.none,
                        contentPadding: EdgeInsets.all(14),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],

                // ── Customer Notes ─────────────────────────────────────
                _buildSectionHeader(
                  title: 'Customer Notes (Optional)',
                  icon: Icons.edit_note_rounded,
                ),
                const SizedBox(height: 10),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.divider),
                  ),
                  child: TextField(
                    controller: _notesController,
                    maxLines: 3,
                    style: const TextStyle(fontSize: 14),
                    decoration: const InputDecoration(
                      hintText: 'Add instructions like landmark, gate code, or specific preferences...',                      border: InputBorder.none,
                      contentPadding: EdgeInsets.all(14),
                    ),
                  ),
                ),

                const SizedBox(height: 110), // Bottom padding for sticky button
              ],
            ),
          ),

          // ── Sticky Bottom CTA Bar ────────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.08),
                    blurRadius: 20,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _proceedToSummary,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                    ),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Continue to Summary',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader({required String title, required IconData icon}) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppColors.primary),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
      ],
    );
  }

  Widget _buildAddressCard() {
    if (_isLoadingAddresses) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: const Row(
          children: [
            SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            SizedBox(width: 12),
            Text('Loading saved addresses...', style: TextStyle(fontSize: 13)),
          ],
        ),
      );
    }

    if (_addressError != null) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFFCA5A5))),
        child: Row(
          children: [
            const Icon(Icons.error_outline_rounded, color: AppColors.error, size: 20),
            const SizedBox(width: 10),
            Expanded(child: Text(_addressError!, style: const TextStyle(fontSize: 12, color: AppColors.error))),
            TextButton(onPressed: _fetchSavedAddresses, child: const Text('Retry')),
          ],
        ),
      );
    }

    if (_savedAddresses.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: Column(
          children: [
            const Row(
              children: [
                Icon(Icons.location_off_rounded, color: AppColors.warning, size: 24),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'No saved addresses found. Please add a service location.',
                    style: TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _addNewAddress,
                icon: const Icon(Icons.add_location_alt_rounded, size: 18),
                label: const Text('Add Address Now', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      );
    }

    final addr = _selectedAddress;
    if (addr == null) return const SizedBox.shrink();

    return GestureDetector(
      onTap: _changeAddress,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.primary, width: 1.5),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                addr.label == 'Home'
                    ? Icons.home_rounded
                    : addr.label == 'Office'
                        ? Icons.work_rounded
                        : Icons.location_on_rounded,
                color: AppColors.primary,
                size: 20,
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(addr.label, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                      if (addr.isDefault) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(4)),
                          child: const Text('DEFAULT', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    addr.shortAddress,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 13, height: 1.3),
                  ),
                ],
              ),
            ),
            const Column(
              children: [
                Text('Change', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.primary, size: 20),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBookingTypeTile({
    required String typeKey,
    required String title,
    required String subtitle,
    required IconData icon,
  }) {
    final isSelected = _bookingType == typeKey;

    return GestureDetector(
      onTap: () => setState(() => _bookingType = typeKey),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary.withValues(alpha: 0.05) : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.divider,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: isSelected ? AppColors.primary : AppColors.textSecondary, size: 22),
                if (isSelected) const Icon(Icons.check_circle_rounded, color: AppColors.primary, size: 18),
              ],
            ),
            const SizedBox(height: 10),
            Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: isSelected ? AppColors.primary : AppColors.textPrimary)),
            const SizedBox(height: 2),
            Text(subtitle, style: const TextStyle(fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeSlotsWidget() {
    if (_isLoadingSlots) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: const Row(
          children: [
            SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
            SizedBox(width: 12),
            Text('Loading available time slots...', style: TextStyle(fontSize: 13)),
          ],
        ),
      );
    }

    final slots = _availableSlots.isNotEmpty
        ? _availableSlots
        : const [
            TimeSlotModel(slotId: '09:00 - 11:00', startTime: '09:00', endTime: '11:00', isAvailable: true),
            TimeSlotModel(slotId: '11:00 - 13:00', startTime: '11:00', endTime: '13:00', isAvailable: true),
            TimeSlotModel(slotId: '14:00 - 16:00', startTime: '14:00', endTime: '16:00', isAvailable: true),
            TimeSlotModel(slotId: '16:00 - 18:00', startTime: '16:00', endTime: '18:00', isAvailable: true),
          ];

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: slots.map((slot) {
        final isSelected = _selectedTimeSlot == slot.slotId;
        final isAvail = slot.isAvailable;

        return ChoiceChip(
          label: Text(
            isAvail ? slot.slotId : '${slot.slotId} (Passed)',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: isSelected
                  ? Colors.white
                  : (isAvail ? AppColors.textPrimary : AppColors.textHint),
              decoration: isAvail ? TextDecoration.none : TextDecoration.lineThrough,
            ),
          ),
          selected: isSelected && isAvail,
          disabledColor: const Color(0xFFF1F5F9),
          selectedColor: AppColors.primary,          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: isSelected
                  ? AppColors.primary
                  : (isAvail ? AppColors.divider : const Color(0xFFE2E8F0)),
            ),
          ),
          onSelected: isAvail
              ? (val) {
                  if (val) setState(() => _selectedTimeSlot = slot.slotId);
                }
              : null,
        );
      }).toList(),
    );
  }
}
