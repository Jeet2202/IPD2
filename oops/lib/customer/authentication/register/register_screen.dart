// File:
// lib/customer/authentication/register/register_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _acceptTerms = false;

  @override
  void dispose() {
    _fullNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
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
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // ── App Logo ──────────────────────────────────────────
                Container(
                  width: 68,
                  height: 68,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2563EB).withOpacity(0.25),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.handyman_rounded,
                    size: 36,
                    color: Colors.white,
                  ),
                ),

                const SizedBox(height: 20),

                // ── Heading & Subtitle ────────────────────────────────
                const Text(
                  'Create Account',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Create your KaamSetu account',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF64748B),
                  ),
                ),

                const SizedBox(height: 32),

                // ── Full Name Field ───────────────────────────────────
                _buildFieldLabel('Full Name'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _fullNameController,
                  keyboardType: TextInputType.name,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                  decoration: _buildInputDecoration(
                    hintText: 'Enter your full name',
                    prefixIcon: Icons.person_outline_rounded,
                  ),
                ),

                const SizedBox(height: 18),

                // ── Phone Number Field ────────────────────────────────
                _buildFieldLabel('Phone Number'),
                const SizedBox(height: 8),
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE2E8F0), width: 1.5),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 15),
                        decoration: const BoxDecoration(
                          border: Border(
                            right: BorderSide(color: Color(0xFFE2E8F0), width: 1.5),
                          ),
                        ),
                        child: const Row(
                          children: [
                            Text(
                              '+91',
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF0F172A),
                              ),
                            ),
                            SizedBox(width: 4),
                            Icon(Icons.keyboard_arrow_down_rounded, size: 16, color: Color(0xFF94A3B8)),
                          ],
                        ),
                      ),
                      Expanded(
                        child: TextFormField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                          decoration: const InputDecoration(
                            hintText: 'Enter phone number',
                            hintStyle: TextStyle(fontSize: 14, color: Color(0xFF94A3B8), fontWeight: FontWeight.w400),
                            border: InputBorder.none,
                            contentPadding: EdgeInsets.symmetric(horizontal: 14),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 18),

                // ── Email Field ───────────────────────────────────────
                _buildFieldLabel('Email Address'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                  decoration: _buildInputDecoration(
                    hintText: 'Enter your email',
                    prefixIcon: Icons.email_outlined,
                  ),
                ),

                const SizedBox(height: 18),

                // ── Password Field ────────────────────────────────────
                _buildFieldLabel('Password'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                  decoration: _buildInputDecoration(
                    hintText: 'Create a password',
                    prefixIcon: Icons.lock_outline_rounded,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                        color: const Color(0xFF94A3B8),
                        size: 20,
                      ),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                ),

                const SizedBox(height: 18),

                // ── Confirm Password Field ────────────────────────────
                _buildFieldLabel('Confirm Password'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _confirmPasswordController,
                  obscureText: _obscureConfirmPassword,
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: Color(0xFF0F172A)),
                  decoration: _buildInputDecoration(
                    hintText: 'Confirm your password',
                    prefixIcon: Icons.lock_reset_rounded,
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                        color: const Color(0xFF94A3B8),
                        size: 20,
                      ),
                      onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // ── Terms & Conditions Checkbox ───────────────────────
                Row(
                  children: [
                    SizedBox(
                      width: 22,
                      height: 22,
                      child: Checkbox(
                        value: _acceptTerms,
                        activeColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(5)),
                        side: const BorderSide(color: Color(0xFFCBD5E1), width: 1.5),
                        onChanged: (val) => setState(() => _acceptTerms = val ?? false),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Wrap(
                        children: [
                          const Text(
                            'I agree to the ',
                            style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                          ),
                          GestureDetector(
                            onTap: () => Navigator.pushNamed(context, AppRoutes.termsConditions),
                            child: const Text(
                              'Terms of Service',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                            ),
                          ),
                          const Text(
                            ' and ',
                            style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                          ),
                          GestureDetector(
                            onTap: () => Navigator.pushNamed(context, AppRoutes.privacyPolicy),
                            child: const Text(
                              'Privacy Policy',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 28),

                // ── Create Account Button ─────────────────────────────
                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.customerOtp);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: const Text(
                      'Create Account',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.2,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                // ── Divider with OR ───────────────────────────────────
                Row(
                  children: [
                    const Expanded(child: Divider(color: Color(0xFFE2E8F0), thickness: 1)),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      child: Text(
                        'OR',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: Colors.grey.shade400,
                          letterSpacing: 1,
                        ),
                      ),
                    ),
                    const Expanded(child: Divider(color: Color(0xFFE2E8F0), thickness: 1)),
                  ],
                ),

                const SizedBox(height: 24),

                // ── Google Button ─────────────────────────────────────
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.pushNamed(context, AppRoutes.customerOtp);
                    },
                    style: OutlinedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: const Color(0xFF1E293B),
                      side: const BorderSide(color: Color(0xFFE2E8F0), width: 1.5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 22,
                          height: 22,
                          decoration: const BoxDecoration(shape: BoxShape.circle),
                          child: const Icon(
                            Icons.g_mobiledata_rounded,
                            size: 26,
                            color: Color(0xFFEA4335),
                          ),
                        ),
                        const SizedBox(width: 10),
                        const Text(
                          'Continue with Google',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF1E293B),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 32),

                // ── Bottom Link: Login ────────────────────────────────
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      'Already have an account? ',
                      style: TextStyle(fontSize: 14, color: Color(0xFF64748B)),
                    ),
                    GestureDetector(
                      onTap: () {
                        if (Navigator.canPop(context)) {
                          Navigator.pop(context);
                        } else {
                          Navigator.pushReplacementNamed(context, AppRoutes.customerLogin);
                        }
                      },
                      child: const Text(
                        'Login',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF2563EB),
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),
              ],
            ),
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
