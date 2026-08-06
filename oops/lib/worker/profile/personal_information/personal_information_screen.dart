// File: lib/worker/profile/personal_information/personal_information_screen.dart

import 'package:flutter/material.dart';

class WorkerPersonalInformationScreen extends StatefulWidget {
  const WorkerPersonalInformationScreen({super.key});

  @override
  State<WorkerPersonalInformationScreen> createState() =>
      _WorkerPersonalInformationScreenState();
}

class _WorkerPersonalInformationScreenState
    extends State<WorkerPersonalInformationScreen> {
  final _fullNameController = TextEditingController(text: 'Ramesh Kumar');
  final _emailController = TextEditingController(text: 'ramesh.kumar@example.com');
  final _dobController = TextEditingController(text: '15/08/1992');
  final _addressController =
      TextEditingController(text: 'Flat 402, Shanti Vihar Apartments');
  final _cityController = TextEditingController(text: 'New Delhi');
  final _stateController = TextEditingController(text: 'Delhi');
  final _pinController = TextEditingController(text: '110001');
  final _emergencyContactController = TextEditingController(text: '+91 98112 34567');

  String _selectedGender = 'Male';

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _dobController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pinController.dispose();
    _emergencyContactController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Personal Details',
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
              // Onboarding Progress Header
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFF2563EB),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E8F0),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Container(
                      height: 6,
                      decoration: BoxDecoration(
                        color: const Color(0xFFE2E8F0),
                        borderRadius: BorderRadius.circular(3),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Text(
                'Step 1 of 3: Personal Information',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF2563EB),
                ),
              ),

              const SizedBox(height: 24),

              // Profile Photo Upload Avatar
              Center(
                child: Stack(
                  children: [
                    Container(
                      width: 104,
                      height: 104,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFFEFF6FF),
                        border: Border.all(
                            color: const Color(0xFF2563EB).withOpacity(0.3),
                            width: 2.5),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF2563EB).withOpacity(0.12),
                            blurRadius: 16,
                            offset: const Offset(0, 6),
                          ),
                        ],
                      ),
                      child: const Center(
                        child: Icon(
                          Icons.person_rounded,
                          size: 56,
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

              const SizedBox(height: 28),

              // Full Name
              _buildFieldLabel('Full Name'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _fullNameController,
                hintText: 'Enter your full name',
                icon: Icons.person_outline_rounded,
              ),

              const SizedBox(height: 18),

              // Email Address
              _buildFieldLabel('Email Address'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _emailController,
                hintText: 'Enter your email address',
                icon: Icons.email_outlined,
                keyboardType: TextInputType.emailAddress,
              ),

              const SizedBox(height: 18),

              // Gender Selector
              _buildFieldLabel('Gender'),
              const SizedBox(height: 8),
              Row(
                children: ['Male', 'Female', 'Other'].map((gender) {
                  final selected = _selectedGender == gender;
                  return Expanded(
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedGender = gender;
                        });
                      },
                      child: Container(
                        margin: const EdgeInsets.only(right: 8),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        decoration: BoxDecoration(
                          color: selected
                              ? const Color(0xFFEFF6FF)
                              : const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: selected
                                ? const Color(0xFF2563EB)
                                : const Color(0xFFE2E8F0),
                            width: selected ? 1.5 : 1,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            gender,
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: selected
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              color: selected
                                  ? const Color(0xFF2563EB)
                                  : const Color(0xFF475569),
                            ),
                          ),
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 18),

              // Date of Birth
              _buildFieldLabel('Date of Birth'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _dobController,
                hintText: 'DD/MM/YYYY',
                icon: Icons.calendar_today_rounded,
                keyboardType: TextInputType.datetime,
              ),

              const SizedBox(height: 18),

              // Address Line
              _buildFieldLabel('Street Address'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _addressController,
                hintText: 'House/Flat No, Street, Landmark',
                icon: Icons.location_on_outlined,
              ),

              const SizedBox(height: 18),

              // City & State Row
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildFieldLabel('City'),
                        const SizedBox(height: 8),
                        _buildTextField(
                          controller: _cityController,
                          hintText: 'City',
                          icon: Icons.location_city_rounded,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildFieldLabel('State'),
                        const SizedBox(height: 8),
                        _buildTextField(
                          controller: _stateController,
                          hintText: 'State',
                          icon: Icons.map_outlined,
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 18),

              // PIN Code
              _buildFieldLabel('PIN Code'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _pinController,
                hintText: 'Enter 6-digit PIN code',
                icon: Icons.pin_drop_outlined,
                keyboardType: TextInputType.number,
              ),

              const SizedBox(height: 18),

              // Emergency Contact
              _buildFieldLabel('Emergency Contact'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _emergencyContactController,
                hintText: "Family or friend's mobile number",
                icon: Icons.contact_phone_outlined,
                keyboardType: TextInputType.phone,
              ),

              const SizedBox(height: 32),

              // Continue Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                        context, '/worker/profile/professional-info');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Flexible(
                        child: Text(
                          'Continue to Professional Details',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      SizedBox(width: 8),
                      Icon(Icons.arrow_forward_rounded, size: 20),
                    ],
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
    return Text(
      label,
      style: const TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: Color(0xFF334155),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String hintText,
    required IconData icon,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        hintText: hintText,
        hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
        prefixIcon: Icon(icon, color: const Color(0xFF64748B)),
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
        ),
      ),
    );
  }
}
