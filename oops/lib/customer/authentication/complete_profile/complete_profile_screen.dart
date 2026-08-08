// File:
// lib/customer/authentication/complete_profile/complete_profile_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class CompleteProfileScreen extends StatefulWidget {
  const CompleteProfileScreen({super.key});

  @override
  State<CompleteProfileScreen> createState() => _CompleteProfileScreenState();
}

class _CompleteProfileScreenState extends State<CompleteProfileScreen> {
  final _fullNameController = TextEditingController(text: 'Rahul Sharma');
  final _emailController = TextEditingController(text: 'rahul.sharma@example.com');
  final _dobController = TextEditingController();
  final _referralController = TextEditingController();

  String? _selectedGender;
  final List<String> _genders = ['Male', 'Female', 'Other', 'Prefer not to say'];

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _dobController.dispose();
    _referralController.dispose();
    super.dispose();
  }

  Future<void> _selectDateOfBirth(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime(1998, 5, 15),
      firstDate: DateTime(1940),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: Color(0xFF2563EB),
              onPrimary: Colors.white,
              onSurface: Color(0xFF0F172A),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        _dobController.text = "${picked.day.toString().padLeft(2, '0')}/${picked.month.toString().padLeft(2, '0')}/${picked.year}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        title: Text('complete_profile'.tr(context),
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w700,
            color: Color(0xFF0F172A),
          ),
        ),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            }
          },
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 12),

              // ── Circular Profile Picture Upload ───────────────────
              Center(
                child: Stack(
                  children: [
                    Container(
                      width: 110,
                      height: 110,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFFF1F5F9),
                        border: Border.all(color: const Color(0xFF2563EB), width: 2.5),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF2563EB).withOpacity(0.15),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: const CircleAvatar(
                        backgroundColor: Color(0xFFEFF6FF),
                        child: Icon(
                          Icons.person_rounded,
                          size: 60,
                          color: Color(0xFF2563EB),
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF2563EB),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 6,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.camera_alt_rounded,
                          size: 16,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 12),
              Text('upload_profile_photo'.tr(context),
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF64748B),
                ),
              ),

              const SizedBox(height: 32),

              // ── Full Name ─────────────────────────────────────────
              _buildFieldLabel('Full Name'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _fullNameController,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                decoration: _buildInputDecoration(
                  hintText: 'Enter full name',
                  prefixIcon: Icons.person_outline_rounded,
                ),
              ),

              const SizedBox(height: 18),

              // ── Email Address ─────────────────────────────────────
              _buildFieldLabel('Email Address'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                decoration: _buildInputDecoration(
                  hintText: 'Enter email address',
                  prefixIcon: Icons.email_outlined,
                ),
              ),

              const SizedBox(height: 18),

              // ── Gender Dropdown ───────────────────────────────────
              _buildFieldLabel('Gender'),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedGender,
                items: _genders.map((gender) {
                  return DropdownMenuItem(
                    value: gender,
                    child: Text(gender, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A))),
                  );
                }).toList(),
                onChanged: (val) => setState(() => _selectedGender = val),
                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF94A3B8)),
                decoration: _buildInputDecoration(
                  hintText: 'Select gender',
                  prefixIcon: Icons.wc_rounded,
                ),
              ),

              const SizedBox(height: 18),

              // ── Date of Birth Picker ──────────────────────────────
              _buildFieldLabel('Date of Birth'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _dobController,
                readOnly: true,
                onTap: () => _selectDateOfBirth(context),
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                decoration: _buildInputDecoration(
                  hintText: 'DD/MM/YYYY',
                  prefixIcon: Icons.calendar_today_rounded,
                  suffixIcon: const Icon(Icons.arrow_drop_down_rounded, color: Color(0xFF94A3B8)),
                ),
              ),

              const SizedBox(height: 18),

              // ── Referral Code (Optional) ──────────────────────────
              _buildFieldLabel('Referral Code (Optional)'),
              const SizedBox(height: 8),
              TextFormField(
                controller: _referralController,
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                decoration: _buildInputDecoration(
                  hintText: 'Enter referral code',
                  prefixIcon: Icons.card_giftcard_rounded,
                ),
              ),

              const SizedBox(height: 36),

              // ── Continue Button ───────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, AppRoutes.customerLocationPerm);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text('continue'.tr(context),
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.2,
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

  Widget _buildFieldLabel(String label) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: Color(0xFF334155),
        ),
      ),
    );
  }

  InputDecoration _buildInputDecoration({
    required String hintText,
    required IconData prefixIcon,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      hintText: hintText,
      hintStyle: const TextStyle(
        fontSize: 14,
        color: Color(0xFF94A3B8),
        fontWeight: FontWeight.w400,
      ),
      prefixIcon: Icon(prefixIcon, color: const Color(0xFF94A3B8), size: 20),
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: const Color(0xFFF8FAFC),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1.5),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
      ),
    );
  }
}
