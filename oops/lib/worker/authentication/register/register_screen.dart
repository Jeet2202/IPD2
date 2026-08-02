// File: lib/worker/authentication/register/register_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_service.dart';
import '../../../utils/validators.dart';
import '../../../widgets/phone_input_widget.dart';

class WorkerRegisterScreen extends StatefulWidget {
  const WorkerRegisterScreen({super.key});

  @override
  State<WorkerRegisterScreen> createState() => _WorkerRegisterScreenState();
}

class _WorkerRegisterScreenState extends State<WorkerRegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  CountryInfo _selectedCountry = CountryData.defaultCountry;
  Map<String, String> _serverFieldErrors = {};

  bool _acceptTerms = false;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String get _fullPhoneNumber {
    final rawNumber = _phoneController.text.trim();
    if (rawNumber.isEmpty) return '';
    return '${_selectedCountry.dialCode}$rawNumber';
  }

  Future<void> _submitRegister() async {
    setState(() => _serverFieldErrors.clear());

    if (!_formKey.currentState!.validate()) return;

    if (!_acceptTerms) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please accept the Terms of Service and Partner Policy.'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final fullName = _nameController.text.trim();
    final phoneFormatted = _fullPhoneNumber;
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    final parts = fullName.split(' ');
    final firstName = parts.isNotEmpty ? parts.first : fullName;
    final lastName = parts.length > 1 ? parts.sublist(1).join(' ') : 'Worker';

    setState(() => _isLoading = true);

    try {
      await AuthService.instance.register(
        email: email,
        phone: phoneFormatted,
        password: password,
        firstName: firstName,
        lastName: lastName,
        role: 'worker',
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("We've sent a verification code to $email."),
          backgroundColor: const Color(0xFF2563EB),
          behavior: SnackBarBehavior.floating,
        ),
      );

      Navigator.pushNamed(
        context,
        '/worker/auth/otp',
        arguments: {'email': email, 'purpose': 'registration'},
      );
    } catch (e) {
      if (!mounted) return;

      if (e is ApiException) {
        setState(() {
          _serverFieldErrors = e.fieldErrors;
        });

        if (_serverFieldErrors.isNotEmpty) {
          _formKey.currentState!.validate();
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Partner registration failed: $e'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
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
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.roleSelection);
            }
          },
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
          physics: const BouncingScrollPhysics(),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Column(
                    children: [
                      Container(
                        width: 72,
                        height: 72,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(22),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF2563EB).withValues(alpha: 0.25),
                              blurRadius: 20,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.engineering_rounded,
                          size: 38,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'KaamSetu',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0EA5E9).withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'PARTNER',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0EA5E9),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      const Text(
                        'Join as a Service Professional',
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 28),

                _buildFieldLabel('Full Name'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _nameController,
                  keyboardType: TextInputType.name,
                  decoration: _buildInputDecoration(
                    hintText: 'Enter your full name',
                    prefixIcon: Icons.person_outline_rounded,
                    errorText: _serverFieldErrors['first_name'] ?? _serverFieldErrors['full_name'],
                  ),
                  validator: Validators.name,
                ),

                const SizedBox(height: 16),

                _buildFieldLabel('Phone Number'),
                const SizedBox(height: 8),
                PhoneInputWidget(
                  controller: _phoneController,
                  errorText: _serverFieldErrors['phone'],
                  onCountryChanged: (c) => setState(() => _selectedCountry = c),
                ),

                const SizedBox(height: 16),

                _buildFieldLabel('Email Address'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: _buildInputDecoration(
                    hintText: 'name@example.com',
                    prefixIcon: Icons.email_outlined,
                    errorText: _serverFieldErrors['email'],
                  ),
                  validator: Validators.email,
                ),

                const SizedBox(height: 16),

                _buildFieldLabel('Password'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  decoration: _buildInputDecoration(
                    hintText: 'Min 8 chars (A-Z, a-z, 0-9, @#\$)',
                    prefixIcon: Icons.lock_outline_rounded,
                    errorText: _serverFieldErrors['password'],
                    suffixIcon: IconButton(
                      icon: Icon(_obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                  validator: Validators.password,
                ),

                const SizedBox(height: 16),

                _buildFieldLabel('Confirm Password'),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _confirmPasswordController,
                  obscureText: _obscureConfirmPassword,
                  decoration: _buildInputDecoration(
                    hintText: 'Re-enter password',
                    prefixIcon: Icons.lock_outline_rounded,
                    suffixIcon: IconButton(
                      icon: Icon(_obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                      onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                    ),
                  ),
                  validator: (v) => Validators.confirmPassword(v, _passwordController.text),
                ),

                const SizedBox(height: 20),

                Row(
                  children: [
                    SizedBox(
                      width: 24,
                      height: 24,
                      child: Checkbox(
                        value: _acceptTerms,
                        onChanged: _isLoading ? null : (val) => setState(() => _acceptTerms = val ?? false),
                        activeColor: const Color(0xFF2563EB),
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'I agree to the Terms of Service & Partner Policy',
                        style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                SizedBox(
                  width: double.infinity,
                  height: 54,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _submitRegister,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                          )
                        : const Text(
                            'Create Account',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                          ),
                  ),
                ),

                const SizedBox(height: 24),

                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Already registered? ', style: TextStyle(color: Color(0xFF64748B))),
                    GestureDetector(
                      onTap: _isLoading
                          ? null
                          : () => Navigator.pushReplacementNamed(context, '/worker/auth/login'),
                      child: const Text(
                        'Sign In',
                        style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFieldLabel(String label) {
    return Text(
      label,
      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
    );
  }

  InputDecoration _buildInputDecoration({
    required String hintText,
    required IconData prefixIcon,
    Widget? suffixIcon,
    String? errorText,
  }) {
    return InputDecoration(
      hintText: hintText,
      prefixIcon: Icon(prefixIcon, color: const Color(0xFF94A3B8), size: 20),
      suffixIcon: suffixIcon,
      errorText: errorText,
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
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Colors.red, width: 1.5),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: const BorderSide(color: Colors.red, width: 1.5),
      ),
    );
  }
}
