// File: lib/customer/profile/edit_profile/edit_profile_screen.dart

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/auth_service.dart';
import '../../../services/api_service.dart';
import '../../../l10n/app_translations.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _altPhoneController = TextEditingController();
  final _dobController = TextEditingController();

  String? _gender;
  String _preferredLanguage = 'hi';
  bool _pushNotifications = true;
  bool _emailNotifications = true;
  bool _smsNotifications = true;

  bool _isLoading = true;
  bool _isSaving = false;
  bool _isUploadingPhoto = false;
  String? _profilePhotoUrl;
  String? _previousPhotoUrl;

  final ImagePicker _picker = ImagePicker();

  final Map<String, String> _languages = {
    'hi': 'Hindi (हिंदी)',
    'en': 'English',
    'mr': 'Marathi (मराठी)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'bn': 'Bengali (বাংলা)',
    'gu': 'Gujarati (ગુજરાતી)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
  };

  final List<String> _genders = ['male', 'female', 'other', 'prefer_not_to_say'];

  @override
  void initState() {
    super.initState();
    _loadProfileData();
  }

  Future<void> _loadProfileData() async {
    try {
      final res = await AuthService.instance.fetchCustomerProfile();
      if (mounted) {
        setState(() {
          _nameController.text = (res['full_name'] as String?) ?? '';
          _altPhoneController.text = (res['alternate_phone'] as String?) ?? '';
          _dobController.text = (res['date_of_birth'] as String?) ?? '';
          _gender = res['gender'] as String?;
          _preferredLanguage = (res['preferred_language'] as String?) ?? 'hi';
          _profilePhotoUrl = res['profile_photo_url'] as String?;

          final notifs = res['notification_preferences'] as Map<String, dynamic>?;
          if (notifs != null) {
            _pushNotifications = notifs['push'] as bool? ?? true;
            _emailNotifications = notifs['email'] as bool? ?? true;
            _smsNotifications = notifs['sms'] as bool? ?? true;
          }
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load profile: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _selectDateOfBirth() async {
    DateTime initialDate = DateTime.now().subtract(const Duration(days: 365 * 25));
    if (_dobController.text.isNotEmpty) {
      try {
        initialDate = DateTime.parse(_dobController.text);
      } catch (_) {}
    }

    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: DateTime(1940),
      lastDate: DateTime.now().subtract(const Duration(days: 365 * 10)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(primary: Color(0xFF2563EB)),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      final formatted = "${picked.year.toString().padLeft(4, '0')}-${picked.month.toString().padLeft(2, '0')}-${picked.day.toString().padLeft(2, '0')}";
      setState(() {
        _dobController.text = formatted;
      });
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

      final res = await AuthService.instance.uploadCustomerProfilePhoto(file.path);
      final newUrl = res['profile_photo_url'] as String?;

      setState(() {
        _profilePhotoUrl = newUrl;
        _isUploadingPhoto = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('profile_photo_updated_successfully'.tr(context)), backgroundColor: Color(0xFF16A34A)),
        );
      }
    } catch (e) {
      setState(() {
        _profilePhotoUrl = _previousPhotoUrl;
        _isUploadingPhoto = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed: $e'), backgroundColor: Colors.red),
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

      await AuthService.instance.deleteCustomerProfilePhoto();

      setState(() {
        _profilePhotoUrl = null;
        _isUploadingPhoto = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('profile_photo_removed'.tr(context)), backgroundColor: Color(0xFF16A34A)),
        );
      }
    } catch (e) {
      setState(() {
        _profilePhotoUrl = _previousPhotoUrl;
        _isUploadingPhoto = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete photo: $e'), backgroundColor: Colors.red),
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
            padding: EdgeInsets.symmetric(vertical: 16.0, horizontal: 20.0),
            child: Wrap(
              children: [
                Center(
                  child: Text('profile_photo'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                ),
                SizedBox(height: 24),
                ListTile(
                  leading: Icon(Icons.photo_camera_rounded, color: Color(0xFF2563EB)),
                  title: Text('take_photo_camera'.tr(context)),
                  onTap: () {
                    Navigator.pop(context);
                    _pickAndUploadPhoto(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: Icon(Icons.photo_library_rounded, color: Color(0xFF2563EB)),
                  title: Text('choose_from_gallery'.tr(context)),
                  onTap: () {
                    Navigator.pop(context);
                    _pickAndUploadPhoto(ImageSource.gallery);
                  },
                ),
                if (_profilePhotoUrl != null && _profilePhotoUrl!.isNotEmpty)
                  ListTile(
                    leading: Icon(Icons.delete_outline_rounded, color: Colors.red),
                    title: Text('remove_photo'.tr(context), style: TextStyle(color: Colors.red)),
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

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final payload = <String, dynamic>{
      'full_name': _nameController.text.trim(),
      'alternate_phone': _altPhoneController.text.trim().isEmpty ? null : _altPhoneController.text.trim(),
      'date_of_birth': _dobController.text.trim().isEmpty ? null : _dobController.text.trim(),
      'gender': _gender,
      'preferred_language': _preferredLanguage,
      'notification_preferences': {
        'push': _pushNotifications,
        'email': _emailNotifications,
        'sms': _smsNotifications,
      },
    };

    try {
      await AuthService.instance.updateCustomerProfile(payload);
      if (mounted) {
        setState(() => _isSaving = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('profile_updated_successfully'.tr(context)), backgroundColor: Color(0xFF16A34A)),
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
          SnackBar(content: Text('Failed to update profile: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _altPhoneController.dispose();
    _dobController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('edit_profile'.tr(context),
          style: TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.w800, fontSize: 18),
        ),
        centerTitle: true,
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: EdgeInsets.all(20.0),
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
                              CircleAvatar(
                                radius: 50,
                                backgroundColor: const Color(0xFFDBEAFE),
                                backgroundImage: (_profilePhotoUrl != null && _profilePhotoUrl!.isNotEmpty)
                                    ? NetworkImage(_profilePhotoUrl!)
                                    : null,
                                child: _isUploadingPhoto
                                    ? const CircularProgressIndicator(color: Color(0xFF2563EB))
                                    : ((_profilePhotoUrl == null || _profilePhotoUrl!.isEmpty)
                                        ? Icon(Icons.person_rounded, size: 54, color: Color(0xFF2563EB))
                                        : null),
                              ),
                              Positioned(
                                bottom: 0,
                                right: 0,
                                child: Container(
                                  padding: EdgeInsets.all(8),
                                  decoration: BoxDecoration(color: Color(0xFF2563EB), shape: BoxShape.circle),
                                  child: Icon(Icons.camera_alt_rounded, color: Colors.white, size: 18),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      SizedBox(height: 28),

                      // Full Name
                      Text('full_name'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 6),
                      TextFormField(
                        controller: _nameController,
                        decoration: InputDecoration(
                          hintText: 'Enter full name',
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        validator: (v) {
                          if (v == null || v.trim().length < 2) return 'Full name must be at least 2 characters';
                          return null;
                        },
                      ),

                      SizedBox(height: 20),

                      // Alternate Phone
                      Text('alternate_phone_number'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 6),
                      TextFormField(
                        controller: _altPhoneController,
                        keyboardType: TextInputType.phone,
                        decoration: InputDecoration(
                          hintText: '+91 9876543210',
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        validator: (v) {
                          if (v != null && v.trim().isNotEmpty) {
                            if (!RegExp(r'^\+91[6-9]\d{9}$').hasMatch(v.trim())) {
                              return 'Must start with +91 followed by 10 digits';
                            }
                          }
                          return null;
                        },
                      ),

                      SizedBox(height: 20),

                      // Date of Birth
                      Text('date_of_birth'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 6),
                      TextFormField(
                        controller: _dobController,
                        readOnly: true,
                        onTap: _selectDateOfBirth,
                        decoration: InputDecoration(
                          hintText: 'YYYY-MM-DD',
                          suffixIcon: Icon(Icons.calendar_today_rounded, color: Color(0xFF2563EB)),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                      ),

                      SizedBox(height: 20),

                      // Gender Selection
                      Text('gender'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        children: _genders.map((g) {
                          final isSelected = _gender == g;
                          return ChoiceChip(
                            label: Text(g.replaceAll('_', ' ').toUpperCase(), style: TextStyle(color: isSelected ? Colors.white : const Color(0xFF0F172A), fontSize: 12)),
                            selected: isSelected,
                            selectedColor: const Color(0xFF2563EB),
                            backgroundColor: const Color(0xFFF1F5F9),
                            onSelected: (selected) {
                              setState(() => _gender = selected ? g : null);
                            },
                          );
                        }).toList(),
                      ),

                      SizedBox(height: 20),

                      // Preferred Language
                      Text('preferred_app_language'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: _languages.entries.map((entry) {
                          final isSelected = _preferredLanguage == entry.key;
                          return ChoiceChip(
                            label: Text(entry.value, style: TextStyle(color: isSelected ? Colors.white : const Color(0xFF0F172A), fontSize: 12)),
                            selected: isSelected,
                            selectedColor: const Color(0xFF2563EB),
                            backgroundColor: const Color(0xFFF1F5F9),
                            onSelected: (selected) {
                              if (selected) setState(() => _preferredLanguage = entry.key);
                            },
                          );
                        }).toList(),
                      ),

                      SizedBox(height: 24),

                      // Notification Preferences
                      Text('notification_settings'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                      SizedBox(height: 8),
                      SwitchListTile(
                        title: Text('push_notifications'.tr(context), style: TextStyle(fontSize: 13)),
                        value: _pushNotifications,
                        activeThumbColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _pushNotifications = val),
                      ),
                      SwitchListTile(
                        title: Text('email_alerts'.tr(context), style: TextStyle(fontSize: 13)),
                        value: _emailNotifications,
                        activeThumbColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _emailNotifications = val),
                      ),
                      SwitchListTile(
                        title: Text('sms_updates'.tr(context), style: TextStyle(fontSize: 13)),
                        value: _smsNotifications,
                        activeThumbColor: const Color(0xFF2563EB),
                        onChanged: (val) => setState(() => _smsNotifications = val),
                      ),

                      SizedBox(height: 32),

                      // Save Button
                      SizedBox(
                        width: double.infinity,
                        height: 52,
                        child: ElevatedButton(
                          onPressed: _isSaving ? null : _saveProfile,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          child: _isSaving
                              ? const CircularProgressIndicator(color: Colors.white)
                              : Text('save_changes'.tr(context), style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                        ),
                      ),
                      SizedBox(height: 24),
                    ],
                  ),
                ),
              ),
            ),
    );
  }
}
