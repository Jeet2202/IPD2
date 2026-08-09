// File: lib/worker/profile/edit_profile/edit_profile_screen.dart

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/auth_service.dart';
import '../../../services/api_service.dart';
import '../../../l10n/app_translations.dart';

class WorkerEditProfileScreen extends StatefulWidget {
  const WorkerEditProfileScreen({super.key});

  @override
  State<WorkerEditProfileScreen> createState() => _WorkerEditProfileScreenState();
}

class _WorkerEditProfileScreenState extends State<WorkerEditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _bioController = TextEditingController();
  final _experienceController = TextEditingController();
  final _hourlyRateController = TextEditingController();

  double _workingRadiusKm = 10.0;
  String _availability = 'available';
  List<String> _selectedSkills = [];
  List<String> _selectedLanguages = [];

  bool _isLoading = true;
  bool _isSaving = false;
  bool _isUploadingPhoto = false;
  String? _profilePhotoUrl;
  String? _previousPhotoUrl;

  final ImagePicker _picker = ImagePicker();

  final List<Map<String, dynamic>> _skillOptions = const [
    {'id': 'plumbing', 'label': 'Plumbing', 'dbSlugs': ['plumbing']},
    {'id': 'electrical', 'label': 'Electrical', 'dbSlugs': ['electrical']},
    {'id': 'cleaning', 'label': 'Cleaning', 'dbSlugs': ['cleaning']},
    {'id': 'ac_appliance', 'label': 'AC & Appliance Repair', 'dbSlugs': ['ac-repair', 'appliance-repair']},
    {'id': 'painting', 'label': 'Painting', 'dbSlugs': ['painting']},
    {'id': 'carpentry', 'label': 'Carpentry', 'dbSlugs': ['carpentry']},
  ];

  final Map<String, String> _availableLanguages = {
    'hi': 'Hindi',
    'en': 'English',
    'mr': 'Marathi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'bn': 'Bengali',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
  };

  final List<String> _availabilities = ['available', 'on_job', 'unavailable'];

  @override
  void initState() {
    super.initState();
    _loadWorkerProfile();
  }

  Future<void> _loadWorkerProfile() async {
    try {
      final res = await AuthService.instance.fetchWorkerProfile();
      if (mounted) {
        setState(() {
          _nameController.text = (res['full_name'] as String?) ?? '';
          _bioController.text = (res['bio'] as String?) ?? '';
          final exp = (res['experience_years'] as num?)?.toDouble() ?? 0.0;
          _experienceController.text = exp > 0 ? exp.toString() : '';
          final rate = (res['hourly_rate'] as num?)?.toDouble();
          _hourlyRateController.text = rate != null && rate > 0 ? rate.toStringAsFixed(0) : '';
          _workingRadiusKm = (res['working_radius_km'] as num?)?.toDouble() ?? 10.0;
          _availability = (res['availability'] as String?) ?? 'available';
          _profilePhotoUrl = res['profile_photo_url'] as String?;

          final rawSkills = res['skills'] as List?;
          _selectedSkills = rawSkills?.map((s) => s.toString()).toList() ?? [];

          final rawLangs = res['languages'] as List?;
          _selectedLanguages = rawLangs?.map((l) => l.toString()).toList() ?? [];

          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${'failed_load_worker_profile'.tr(context)}$e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _pickAndUploadPhoto(ImageSource source) async {
    try {
      final XFile? file = await _picker.pickImage(
        source: source,
        maxWidth: 1000,
        maxHeight: 1000,
        imageQuality: 85,
      );

      if (file == null) return;

      setState(() {
        _previousPhotoUrl = _profilePhotoUrl;
        _isUploadingPhoto = true;
      });

      final res = await AuthService.instance.uploadWorkerProfilePhoto(file.path);
      final newUrl = res['profile_photo_url'] as String?;

      setState(() {
        _profilePhotoUrl = newUrl;
        _isUploadingPhoto = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('worker_profile_photo_updated'.tr(context)), backgroundColor: const Color(0xFF16A34A)),
        );
      }
    } catch (e) {
      setState(() {
        _profilePhotoUrl = _previousPhotoUrl;
        _isUploadingPhoto = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${'photo_upload_failed'.tr(context)}$e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _deletePhoto() async {
    try {
      setState(() {
        _previousPhotoUrl = _profilePhotoUrl;
        _isUploadingPhoto = true;
      });

      await AuthService.instance.deleteWorkerProfilePhoto();

      setState(() {
        _profilePhotoUrl = null;
        _isUploadingPhoto = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('worker_profile_photo_removed'.tr(context)), backgroundColor: const Color(0xFF16A34A)),
        );
      }
    } catch (e) {
      setState(() {
        _profilePhotoUrl = _previousPhotoUrl;
        _isUploadingPhoto = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${'failed_delete_photo'.tr(context)}$e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _showPhotoOptionsModal() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 20.0),
            child: Wrap(
              children: [
                Center(
                  child: Text('partner_profile_photo'.tr(context), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                ),
                const SizedBox(height: 24),
                ListTile(
                  leading: const Icon(Icons.photo_camera_rounded, color: Color(0xFF2563EB)),
                  title: Text('take_photo_camera'.tr(context)),
                  onTap: () {
                    Navigator.pop(context);
                    _pickAndUploadPhoto(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library_rounded, color: Color(0xFF2563EB)),
                  title: Text('choose_from_gallery'.tr(context)),
                  onTap: () {
                    Navigator.pop(context);
                    _pickAndUploadPhoto(ImageSource.gallery);
                  },
                ),
                if (_profilePhotoUrl != null && _profilePhotoUrl!.isNotEmpty)
                  ListTile(
                    leading: const Icon(Icons.delete_outline_rounded, color: Colors.red),
                    title: Text('remove_photo'.tr(context), style: const TextStyle(color: Colors.red)),
                    onTap: () {
                      Navigator.pop(context);
                      _deletePhoto();
                    },
                  ),
              ],
            ),
          ),
        );
      },
    );
  }



  Future<void> _saveWorkerProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final expYears = double.tryParse(_experienceController.text.trim());
    final hourlyRate = double.tryParse(_hourlyRateController.text.trim());

    final payload = <String, dynamic>{
      'full_name': _nameController.text.trim(),
      'bio': _bioController.text.trim().isEmpty ? null : _bioController.text.trim(),
      'experience_years': expYears,
      'skills': _selectedSkills,
      'languages': _selectedLanguages,
      'working_radius_km': _workingRadiusKm,
      'availability': _availability,
      'hourly_rate': hourlyRate,
    };

    try {
      await AuthService.instance.updateWorkerProfile(payload);
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('partner_profile_updated_success'.tr(context)), backgroundColor: const Color(0xFF16A34A)),
        );
        Navigator.pop(context);
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.message), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${'failed_update_partner_profile'.tr(context)}$e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _bioController.dispose();
    _experienceController.dispose();
    _hourlyRateController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'edit_partner_profile'.tr(context),
          style: const TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.w800, fontSize: 18),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Avatar Edit Stack
                      Center(
                        child: GestureDetector(
                          onTap: _isUploadingPhoto ? null : _showPhotoOptionsModal,
                          child: Stack(
                            children: [
                              Container(
                                width: 100,
                                height: 100,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: const Color(0xFFEFF6FF),
                                  border: Border.all(color: const Color(0xFF2563EB), width: 2),
                                  image: (_profilePhotoUrl != null && _profilePhotoUrl!.isNotEmpty)
                                      ? DecorationImage(image: NetworkImage(_profilePhotoUrl!), fit: BoxFit.cover)
                                      : null,
                                ),
                                child: _isUploadingPhoto
                                    ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
                                    : ((_profilePhotoUrl == null || _profilePhotoUrl!.isEmpty)
                                        ? const Center(child: Icon(Icons.person_rounded, size: 56, color: Color(0xFF2563EB)))
                                        : null),
                              ),
                              Positioned(
                                bottom: 0,
                                right: 0,
                                child: Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: const BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                                  child: const Icon(Icons.camera_alt_rounded, color: Colors.white, size: 16),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 28),

                      // Full Name
                      Text('full_name_star'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      const SizedBox(height: 6),
                      TextFormField(
                        controller: _nameController,
                        decoration: InputDecoration(
                          hintText: 'enter_full_name'.tr(context),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        validator: (v) {
                          if (v == null || v.trim().length < 2) return 'name_min_chars'.tr(context);
                          return null;
                        },
                      ),

                      const SizedBox(height: 20),

                      // Availability Dropdown
                      Text('availability_status'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      const SizedBox(height: 6),
                      DropdownButtonFormField<String>(
                        value: _availability,
                        decoration: InputDecoration(
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        items: _availabilities.map((a) {
                          return DropdownMenuItem(
                            value: a,
                            child: Text(a.replaceAll('_', ' ').toUpperCase(), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _availability = val);
                        },
                      ),

                      const SizedBox(height: 20),

                      // Experience & Hourly Rate (2 Column Row)
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('experience_years'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                                const SizedBox(height: 6),
                                TextFormField(
                                  controller: _experienceController,
                                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                  decoration: InputDecoration(
                                    hintText: 'eg_5_5'.tr(context),
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                                  ),
                                  validator: (v) {
                                    if (v != null && v.trim().isNotEmpty) {
                                      final numVal = double.tryParse(v.trim());
                                      if (numVal == null || numVal < 0 || numVal > 50) {
                                        return 'zero_to_fifty_yrs'.tr(context);
                                      }
                                    }
                                    return null;
                                  },
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('hourly_rate_per_hr'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                                const SizedBox(height: 6),
                                TextFormField(
                                  controller: _hourlyRateController,
                                  keyboardType: TextInputType.number,
                                  decoration: InputDecoration(
                                    hintText: 'eg_350'.tr(context),
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                                  ),
                                  validator: (v) {
                                    if (v != null && v.trim().isNotEmpty) {
                                      final numVal = double.tryParse(v.trim());
                                      if (numVal == null || numVal < 0) {
                                        return 'invalid_rate'.tr(context);
                                      }
                                    }
                                    return null;
                                  },
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 20),

                      // Service Radius Slider
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('service_radius_km'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                          Text('${_workingRadiusKm.toInt()} ${'km_radius'.tr(context)}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                        ],
                      ),
                      Slider(
                        value: _workingRadiusKm,
                        min: 1.0,
                        max: 50.0,
                        divisions: 49,
                        activeColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _workingRadiusKm = val),
                      ),

                      const SizedBox(height: 16),

                      // Offered Skills & Services (Multi-select Chips)
                      Text('offered_services_skills'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _skillOptions.map((opt) {
                          final label = opt['label'] as String;
                          final dbSlugs = opt['dbSlugs'] as List<String>;
                          final isSelected = dbSlugs.any((slug) => _selectedSkills.contains(slug));

                          return FilterChip(
                            label: Text(
                              label,
                              style: TextStyle(color: isSelected ? Colors.white : const Color(0xFF0F172A), fontSize: 12),
                            ),
                            selected: isSelected,
                            selectedColor: const Color(0xFF2563EB),
                            backgroundColor: const Color(0xFFF1F5F9),
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  for (final slug in dbSlugs) {
                                    if (!_selectedSkills.contains(slug)) {
                                      _selectedSkills.add(slug);
                                    }
                                  }
                                } else {
                                  for (final slug in dbSlugs) {
                                    _selectedSkills.remove(slug);
                                  }
                                }
                              });
                            },
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 20),

                      // Spoken Languages
                      Text('spoken_languages'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _availableLanguages.entries.map((entry) {
                          final isSelected = _selectedLanguages.contains(entry.key);
                          return FilterChip(
                            label: Text(entry.value, style: TextStyle(color: isSelected ? Colors.white : const Color(0xFF0F172A), fontSize: 12)),
                            selected: isSelected,
                            selectedColor: const Color(0xFF2563EB),
                            backgroundColor: const Color(0xFFF1F5F9),
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  _selectedLanguages.add(entry.key);
                                } else {
                                  _selectedLanguages.remove(entry.key);
                                }
                              });
                            },
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 20),

                      // Bio
                      Text('professional_bio'.tr(context), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      const SizedBox(height: 6),
                      TextFormField(
                        controller: _bioController,
                        maxLines: 4,
                        maxLength: 1000,
                        decoration: InputDecoration(
                          hintText: 'describe_expertise_hint'.tr(context),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: const EdgeInsets.all(14),
                        ),
                      ),

                      const SizedBox(height: 28),

                      // Save Button
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _isSaving ? null : _saveWorkerProfile,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          child: _isSaving
                              ? const CircularProgressIndicator(color: Colors.white)
                              : Text('save_partner_profile'.tr(context), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        ),
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ),
    );
  }
}
