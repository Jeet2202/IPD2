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
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';
import '../../../utils/booking_slot_utils.dart';

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

  final List<Map<String, String>> _categories = [
    {'name': 'Plumbing', 'slug': 'plumbing'},
    {'name': 'Electrical', 'slug': 'electrical'},
    {'name': 'Cleaning', 'slug': 'cleaning'},
    {'name': 'AC & Appliance Repair', 'slug': 'appliance-repair'},
    {'name': 'Painting', 'slug': 'painting'},
    {'name': 'Carpentry', 'slug': 'carpentry'},
  ];

  ServiceModel? _service;
  List<AddressModel> _savedAddresses = [];
  AddressModel? _selectedAddress;

  bool _isLoadingAddresses = true;
  String? _addressError;
  final List<String> _uploadedPhotos = [];

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

        final avail = res.slots.where((s) => s.isAvailable && BookingSlotUtils.isSlotAvailable(s.slotId, dt)).toList();
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

  void _showAddressPickerModal() {
    showModalBottomSheet(
      context: context,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('selectserviceaddress'.tr(context).tr(context),
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      _addNewAddress();
                    },
                    icon: Icon(Icons.add_rounded, size: 18, color: AppColors.primary),
                    label: Text('addnew'.tr(context).tr(context), style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                  ),
                ],
              ),
              SizedBox(height: 12),
              Flexible(
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: _savedAddresses.length,
                  separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.divider),
                  itemBuilder: (context, idx) {
                    final addr = _savedAddresses[idx];
                    final isSelected = _selectedAddress?.id == addr.id;

                    return ListTile(
                      contentPadding: EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                      leading: Container(
                        padding: EdgeInsets.all(8),
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
                          Text(addr.label, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          if (addr.isDefault) ...[
                            SizedBox(width: 8),
                            Container(
                              padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(4)),
                              child: Text('default'.tr(context), style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
                            ),
                          ],
                        ],
                      ),
                      subtitle: Text(
                        '${addr.fullName} • ${addr.shortAddress}',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(fontSize: 12),
                      ),
                      trailing: isSelected
                          ? Icon(Icons.check_circle_rounded, color: AppColors.primary)
                          : Icon(Icons.radio_button_unchecked_rounded, color: AppColors.textHint),
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
        SnackBar(content: Text('please_select_or_add_a'.tr(context))),
      );
      return;
    }

    if (_bookingType == 'normal_service' && _service == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('please_select_a_valid_service'.tr(context))),
      );
      return;
    }

    if (_bookingType == 'custom_service' && _customTitleController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('please_enter_a_service_title'.tr(context)),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    if (_bookingType == 'inspection_request' && _problemDescController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('please_provide_a_problem_description'.tr(context)),
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
        'problem_photos': _uploadedPhotos,
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
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          children: [
            Text('bookingdetailsstep1'.tr(context).tr(context),
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.primary),
            ),
            Text('bookingdetails'.tr(context).tr(context),
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800),
            ),
          ],
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: AppColors.primary),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Selected Service Summary ─────────────────────────
                if (service != null) ...[
                  Container(
                    padding: EdgeInsets.all(16),
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
                              errorBuilder: (_, __, ___) => Icon(Icons.build_rounded, color: AppColors.primary, size: 28),
                            ),
                          ),
                        ),
                        SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                service.name,
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                              ),
                              SizedBox(height: 4),
                              Text(
                                '${service.categorySlug.replaceAll('-', ' ').toUpperCase()} • ${service.durationDisplay}',
                                style: TextStyle(fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.primary),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 20),
                ],

                // ── Address Selection Section ──────────────────────────
                _buildSectionHeader(
                  title: 'service_address'.tr(context),
                  icon: Icons.location_on_rounded,
                ),
                SizedBox(height: 10),
                _buildAddressCard(),

                SizedBox(height: 24),

                // ── Category Selector for Custom / Standalone Inspection ─────
                if (_bookingType != 'normal_service' || _service == null) ...[
                  _buildSectionHeader(
                    title: 'select_service_category'.tr(context),
                    icon: Icons.grid_view_rounded,
                  ),
                  SizedBox(height: 10),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.divider),
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedCategorySlug,
                        isExpanded: true,
                        icon: Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.primary),
                        items: _categories.map((c) {
                          return DropdownMenuItem<String>(
                            value: c['slug'],
                            child: Text(
                              AppTranslations.getLocalizedName(context, c['name']!),
                              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
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
                  SizedBox(height: 24),
                ],

                // ── Custom Service Requirements Form ──────────────────────
                if (_bookingType == 'custom_service') ...[
                  _buildSectionHeader(
                    title: 'custom_service_details'.tr(context),
                    icon: Icons.edit_document,
                  ),
                  SizedBox(height: 10),
                  Container(
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('servicetitlerequired'.tr(context).tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        SizedBox(height: 6),
                        TextField(
                          controller: _customTitleController,
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            hintText: 'search_placeholder'.tr(context),
                            hintStyle: TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.divider)),
                          ),
                        ),
                        SizedBox(height: 14),
                        Text('detailedrequirementsoptional'.tr(context).tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        SizedBox(height: 6),
                        TextField(
                          controller: _customDescController,
                          maxLines: 3,
                          style: TextStyle(fontSize: 14),
                          decoration: InputDecoration(
                            hintText: 'write_review'.tr(context),
                            hintStyle: TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.divider)),
                          ),
                        ),
                        SizedBox(height: 14),
                        Text('estimatedbudgetoptional'.tr(context).tr(context),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textSecondary),
                        ),
                        SizedBox(height: 6),
                        TextField(
                          controller: _customBudgetController,
                          keyboardType: TextInputType.number,
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            prefixText: '₹ ',
                            hintText: '500',
                            hintStyle: TextStyle(fontSize: 13, color: AppColors.textHint),
                            isDense: true,
                            contentPadding: EdgeInsets.all(12),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: BorderSide(color: AppColors.divider)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 24),
                ],

                // ── Date Selector ──────────────────────────────────────
                _buildSectionHeader(
                  title: 'preferred_date'.tr(context),
                  icon: Icons.calendar_month_rounded,
                ),
                SizedBox(height: 10),
                GestureDetector(
                  onTap: _selectDate,
                  child: Container(
                    padding: EdgeInsets.all(16),
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
                            Icon(Icons.today_rounded, color: AppColors.primary, size: 22),
                            SizedBox(width: 12),
                            Text(
                              '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            Text('changedate'.tr(context).tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                            SizedBox(width: 4),
                            Icon(Icons.chevron_right_rounded, color: AppColors.primary, size: 18),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),

                SizedBox(height: 24),

                // ── Time Slot Selector ─────────────────────────────────
                _buildSectionHeader(
                  title: 'preferred_time_slot'.tr(context),
                  icon: Icons.access_time_rounded,
                ),
                _buildTimeSlotsWidget(),

                SizedBox(height: 24),

                // ── Inspection Problem Description (Required if inspection_request) ──
                if (_bookingType == 'inspection_request') ...[
                  _buildSectionHeader(
                    title: 'problem_desc_required'.tr(context),
                    icon: Icons.assignment_late_rounded,
                  ),
                  SizedBox(height: 10),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFD97706), width: 1.5),
                    ),
                    child: TextField(
                      controller: _problemDescController,
                      maxLines: 3,
                      style: TextStyle(fontSize: 14),
                      decoration: InputDecoration(
                        hintText: 'problem_description'.tr(context),
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.all(14),
                      ),
                    ),
                  ),
                  SizedBox(height: 24),
                ],

                // ── Customer Notes ─────────────────────────────────────
                _buildSectionHeader(
                  title: 'customer_notes_optional'.tr(context),
                  icon: Icons.edit_note_rounded,
                ),
                SizedBox(height: 10),
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.divider),
                  ),
                  child: TextField(
                    controller: _notesController,
                    maxLines: 3,
                    style: TextStyle(fontSize: 14),
                    decoration: InputDecoration(
                      hintText: 'customer_notes_optional'.tr(context),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.all(14),
                    ),
                  ),
                ),

                SizedBox(height: 110), // Bottom padding for sticky button
              ],
            ),
          ),

          // ── Sticky Bottom CTA Bar ────────────────────────────────────
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
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
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('continuetosummary'.tr(context).tr(context),
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
        SizedBox(width: 8),
        Text(
          title,
          style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
      ],
    );
  }

  Widget _buildAddressCard() {
    if (_isLoadingAddresses) {
      return Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: Row(
          children: [
            SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            SizedBox(width: 12),
            Text('loading_saved_addresses'.tr(context), style: TextStyle(fontSize: 13)),
          ],
        ),
      );
    }

    if (_addressError != null) {
      return Container(
        padding: EdgeInsets.all(14),
        decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(16), border: Border.all(color: const Color(0xFFFCA5A5))),
        child: Row(
          children: [
            Icon(Icons.error_outline_rounded, color: AppColors.error, size: 20),
            SizedBox(width: 10),
            Expanded(child: Text(_addressError!, style: TextStyle(fontSize: 12, color: AppColors.error))),
            TextButton(onPressed: _fetchSavedAddresses, child: Text('retry'.tr(context))),
          ],
        ),
      );
    }

    if (_savedAddresses.isEmpty) {
      return Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.location_off_rounded, color: AppColors.warning, size: 24),
                SizedBox(width: 12),
                Expanded(
                  child: Text('no_saved_addresses_found_please'.tr(context),
                    style: TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _addNewAddress,
                icon: Icon(Icons.add_location_alt_rounded, size: 18),
                label: Text('add_address_now'.tr(context), style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      );
    }

    final addr = _selectedAddress;
    if (addr == null) return SizedBox.shrink();

    return GestureDetector(
      onTap: _showAddressPickerModal,
      child: Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.primary, width: 1.5),
        ),
        child: Row(
          children: [
            Container(
              padding: EdgeInsets.all(10),
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
            SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(addr.label, style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                      if (addr.isDefault) ...[
                        SizedBox(width: 8),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(4)),
                          child: Text('default'.tr(context), style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
                        ),
                      ],
                    ],
                  ),
                  SizedBox(height: 4),
                  Text(
                    addr.shortAddress,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 13, height: 1.3),
                  ),
                ],
              ),
            ),
            Column(
              children: [
                Text('change'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.primary)),
                Icon(Icons.keyboard_arrow_down_rounded, color: AppColors.primary, size: 20),
              ],
            ),
          ],
        ),
      ),
    );
  }



  Widget _buildTimeSlotsWidget() {
    if (_isLoadingSlots) {
      return Container(
        padding: EdgeInsets.all(16),
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16), border: Border.all(color: AppColors.divider)),
        child: Row(
          children: [
            SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
            SizedBox(width: 12),
            Text('loading_available_time_slots'.tr(context), style: TextStyle(fontSize: 13)),
          ],
        ),
      );
    }

    final slots = _availableSlots.isNotEmpty
        ? _availableSlots
        : [
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
        final isAvail = slot.isAvailable && BookingSlotUtils.isSlotAvailable(slot.slotId, _selectedDate);

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
          selectedColor: AppColors.primary,
          shape: RoundedRectangleBorder(
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
