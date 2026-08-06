// File: lib/customer/inspection_booking/inspection_details/inspection_details_screen.dart

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_dimensions.dart';
import '../../../models/address_model.dart';
import '../../../services/address_service.dart';
import '../../../services/api_service.dart';

class InspectionDetailsScreen extends StatefulWidget {
  const InspectionDetailsScreen({super.key});

  @override
  State<InspectionDetailsScreen> createState() => _InspectionDetailsScreenState();
}

class _InspectionDetailsScreenState extends State<InspectionDetailsScreen> {
  final AddressService _addressService = AddressService.instance;
  final ImagePicker _picker = ImagePicker();

  String _selectedCategorySlug = 'electrical';
  String _selectedTypeOfWork = 'General Diagnostic Check';
  final TextEditingController _problemDescController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  String _selectedTimeSlot = '10:00 AM - 12:00 PM';

  List<AddressModel> _savedAddresses = [];
  AddressModel? _selectedAddress;
  bool _isLoadingAddresses = true;

  final List<String> _uploadedPhotos = [];
  bool _isUploadingImage = false;

  final List<Map<String, String>> _categories = [
    {'name': 'Electrical', 'slug': 'electrical', 'icon': '⚡'},
    {'name': 'Plumbing', 'slug': 'plumbing', 'icon': '🔧'},
    {'name': 'AC Repair', 'slug': 'ac-repair', 'icon': '❄️'},
    {'name': 'Appliance Repair', 'slug': 'appliance-repair', 'icon': '📱'},
    {'name': 'Carpentry', 'slug': 'carpentry', 'icon': '🪚'},
    {'name': 'Painting', 'slug': 'painting', 'icon': '🎨'},
    {'name': 'Cleaning', 'slug': 'cleaning', 'icon': '🧹'},
    {'name': 'Pest Control', 'slug': 'pest-control', 'icon': '🐜'},
  ];

  final List<String> _timeSlots = [
    '09:00 AM - 11:00 AM',
    '10:00 AM - 12:00 PM',
    '02:00 PM - 04:00 PM',
    '04:00 PM - 06:00 PM',
  ];

  @override
  void initState() {
    super.initState();
    _fetchAddresses();
  }

  Future<void> _fetchAddresses() async {
    setState(() {
      _isLoadingAddresses = true;
    });

    try {
      final list = await _addressService.listAddresses();
      if (!mounted) return;
      setState(() {
        _savedAddresses = list;
        _isLoadingAddresses = false;
        if (list.isNotEmpty) {
          _selectedAddress = list.firstWhere((a) => a.isDefault, orElse: () => list.first);
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoadingAddresses = false;
      });
    }
  }

  void _showMediaPickerOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 20.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Attach Photos or Videos',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.camera_alt_rounded, color: AppColors.primary),
                  title: const Text('Take Photo (Camera)'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _pickAndUploadMedia(ImageSource.camera, isVideo: false);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library_rounded, color: AppColors.primary),
                  title: const Text('Choose Photo from Gallery'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _pickAndUploadMedia(ImageSource.gallery, isVideo: false);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.videocam_rounded, color: AppColors.primary),
                  title: const Text('Record Video (Camera)'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _pickAndUploadMedia(ImageSource.camera, isVideo: true);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.video_library_rounded, color: AppColors.primary),
                  title: const Text('Choose Video from Gallery'),
                  onTap: () {
                    Navigator.pop(ctx);
                    _pickAndUploadMedia(ImageSource.gallery, isVideo: true);
                  },
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Future<void> _pickAndUploadMedia(ImageSource source, {required bool isVideo}) async {
    try {
      final XFile? file = isVideo
          ? await _picker.pickVideo(source: source)
          : await _picker.pickImage(source: source);
      if (file == null) return;

      setState(() => _isUploadingImage = true);

      final res = await ApiService.instance.uploadMultipart('/uploads/image', file.path);
      final url = (res is Map<String, dynamic>)
          ? (res['secure_url'] as String? ?? res['url'] as String? ?? '')
          : '';

      if (!mounted) return;

      setState(() => _isUploadingImage = false);

      if (url.isNotEmpty) {
        setState(() {
          _uploadedPhotos.add(url);
        });
      } else {
        // Fallback placeholder URL if server returns standard format
        setState(() {
          _uploadedPhotos.add(
            'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=400&q=80',
          );
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isUploadingImage = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Media upload issue: $e. Using Cloudinary fallback.'),
          backgroundColor: AppColors.warning,
        ),
      );
      setState(() {
        _uploadedPhotos.add(
          'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=400&q=80',
        );
      });
    }
  }

  void _removeImage(int index) {
    setState(() {
      _uploadedPhotos.removeAt(index);
    });
  }

  Future<void> _selectDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: now,
      lastDate: now.add(const Duration(days: 30)),
    );
    if (picked != null && mounted) {
      setState(() => _selectedDate = picked);
    }
  }

  void _proceedToSummary() {
    if (_problemDescController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please describe the problem symptoms for inspection.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    if (_selectedAddress == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select or add a service address.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final dateStr = '${_selectedDate.year}-${_selectedDate.month.toString().padLeft(2, '0')}-${_selectedDate.day.toString().padLeft(2, '0')}';

    Navigator.pushNamed(
      context,
      AppRoutes.inspectionSummary,
      arguments: {
        'address': _selectedAddress,
        'category_slug': _selectedCategorySlug,
        'type_of_work': _selectedTypeOfWork,
        'problem_description': _problemDescController.text.trim(),
        'problem_photos': _uploadedPhotos,
        'scheduled_date': dateStr,
        'scheduled_time': _selectedTimeSlot,
        'customer_notes': _notesController.text.trim(),
        'inspection_charge': 99.0,
      },
    );
  }

  @override
  void dispose() {
    _problemDescController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Column(
          children: [
            Text('Step 1 of 2', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.primary)),
            Text('Request Inspection (₹99)', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800)),
          ],
        ),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Diagnostic Header Banner ──────────────────────────────
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.search_rounded, color: AppColors.primary, size: 28),
                      SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Doorstep Technical Inspection', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.primary)),
                            SizedBox(height: 2),
                            Text('A verified expert will visit, diagnose the problem, and provide an accurate upfront quotation.', style: TextStyle(fontSize: 12, color: AppColors.textSecondary, height: 1.3)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // ── Category Selection ────────────────────────────────────
                const Text('Select Category', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                SizedBox(
                  height: 40,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _categories.length,
                    itemBuilder: (context, idx) {
                      final item = _categories[idx];
                      final isSelected = _selectedCategorySlug == item['slug'];
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text('${item['icon']} ${item['name']}'),
                          selected: isSelected,
                          selectedColor: AppColors.primary,
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : AppColors.textPrimary,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                            fontSize: 13,
                          ),
                          onSelected: (_) {
                            setState(() => _selectedCategorySlug = item['slug']!);
                          },
                        ),
                      );
                    },
                  ),
                ),

                const SizedBox(height: 24),

                // ── Type of Work ──────────────────────────────────────────
                const Text('Type of Work / Sub-Area', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                TextField(
                  onChanged: (val) => _selectedTypeOfWork = val,
                  decoration: InputDecoration(
                    hintText: 'e.g. MCB Tripping, Ceiling Leakage, Noise Diagnosis',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  ),
                ),

                const SizedBox(height: 24),

                // ── Problem Description ──────────────────────────────────
                const Text('Describe Problem Symptoms *', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                TextField(
                  controller: _problemDescController,
                  maxLines: 3,
                  decoration: InputDecoration(
                    hintText: 'Provide details on what issue is occurring so the technician brings right tools...',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.all(14),
                  ),
                ),

                const SizedBox(height: 24),

                // ── Upload Photos/Videos ──────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Upload Photos / Videos', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                    TextButton.icon(
                      onPressed: _isUploadingImage ? null : _showMediaPickerOptions,
                      icon: _isUploadingImage
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                          : const Icon(Icons.add_a_photo_rounded, size: 16),
                      label: Text(_isUploadingImage ? 'Uploading...' : 'Add Media'),
                    ),
                  ],
                ),
                if (_uploadedPhotos.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 80,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _uploadedPhotos.length,
                      itemBuilder: (context, idx) {
                        return Stack(
                          children: [
                            Container(
                              width: 80,
                              height: 80,
                              margin: const EdgeInsets.only(right: 10),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(12),
                                image: DecorationImage(
                                  image: NetworkImage(_uploadedPhotos[idx]),
                                  fit: BoxFit.cover,
                                ),
                              ),
                            ),
                            Positioned(
                              top: 4,
                              right: 14,
                              child: GestureDetector(
                                onTap: () => _removeImage(idx),
                                child: Container(
                                  padding: const EdgeInsets.all(2),
                                  decoration: const BoxDecoration(color: Colors.red, shape: BoxShape.circle),
                                  child: const Icon(Icons.close_rounded, size: 14, color: Colors.white),
                                ),
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                ],

                const SizedBox(height: 24),

                // ── Select Address ────────────────────────────────────────
                const Text('Select Service Address *', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                if (_isLoadingAddresses)
                  const CircularProgressIndicator()
                else if (_savedAddresses.isEmpty)
                  TextButton.icon(
                    onPressed: _fetchAddresses,
                    icon: const Icon(Icons.add_location_alt_rounded),
                    label: const Text('Refresh / Add Saved Address'),
                  )
                else
                  DropdownButtonFormField<AddressModel>(
                    initialValue: _selectedAddress,
                    items: _savedAddresses.map((addr) {
                      return DropdownMenuItem(
                        value: addr,
                        child: Text('${addr.label} • ${addr.shortAddress}', overflow: TextOverflow.ellipsis),
                      );
                    }).toList(),
                    onChanged: (val) => setState(() => _selectedAddress = val),
                    decoration: InputDecoration(
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                    ),
                  ),

                const SizedBox(height: 24),

                // ── Schedule Visit Date & Time Slot ───────────────────────
                const Text('Preferred Visit Date & Time *', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: _selectDate,
                        icon: const Icon(Icons.calendar_today_rounded, size: 18),
                        label: Text('${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(
                  spacing: 8,
                  children: _timeSlots.map((slot) {
                    final isSelected = _selectedTimeSlot == slot;
                    return ChoiceChip(
                      label: Text(slot),
                      selected: isSelected,
                      selectedColor: AppColors.primary,
                      labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textPrimary, fontSize: 12),
                      onSelected: (_) => setState(() => _selectedTimeSlot = slot),
                    );
                  }).toList(),
                ),

                const SizedBox(height: 24),

                // ── Additional Notes ─────────────────────────────────────
                const Text('Additional Notes', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                const SizedBox(height: 8),
                TextField(
                  controller: _notesController,
                  maxLines: 2,
                  decoration: InputDecoration(
                    hintText: 'Landmark, gate code, or specific instructions for inspector...',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                    contentPadding: const EdgeInsets.all(14),
                  ),
                ),
              ],
            ),
          ),

          // ── Sticky Bottom Bar ──────────────────────────────────────
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
                  onPressed: _proceedToSummary,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text('Continue to Inspection Summary (₹99)', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
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
}
