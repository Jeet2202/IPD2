// File: lib/worker/authentication/register/register_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_service.dart';
import '../../../utils/validators.dart';
import '../../../widgets/phone_input_widget.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

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
        SnackBar(
          content: Text('please_accept_terms'.tr(context)),
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
          content: Text('verification_code_sent'.tr(context).replaceAll('{email}', email)),
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
            content: Text('${'partner_registration_failed'.tr(context)}: $e'),
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
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () {
            if (Navigator.canPop(context)) {
              Navigator.pop(context);
            } else {
              Navigator.pushReplacementNamed(context, AppRoutes.roleSelection);
            }
          },
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF0F172A)),
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0),
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
                        child: Icon(
                          Icons.engineering_rounded,
                          size: 38,
                          color: Colors.white,
                        ),
                      ),
                      SizedBox(height: 16),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            'Ally',
                            style: TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF2563EB),
                            ),
                          ),
                          SizedBox(width: 6),
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0EA5E9).withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              'partner'.tr(context).toUpperCase(),
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF0EA5E9),
                              ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 6),
                      Text(
                        'join_as_service_pro'.tr(context),
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF64748B),
                        ),
                      ),
                    ],
                  ),
                ),

                SizedBox(height: 28),

                _buildFieldLabel('full_name'.tr(context)),
                SizedBox(height: 8),
                TextFormField(
                  controller: _nameController,
                  keyboardType: TextInputType.name,
                  decoration: _buildInputDecoration(
                    hintText: 'enter_full_name'.tr(context),
                    prefixIcon: Icons.person_outline_rounded,
                    errorText: _serverFieldErrors['first_name'] ?? _serverFieldErrors['full_name'],
                  ),
                  validator: Validators.name,
                ),

                SizedBox(height: 16),

                _buildFieldLabel('phone_number'.tr(context)),
                SizedBox(height: 8),
                PhoneInputWidget(
                  controller: _phoneController,
                  errorText: _serverFieldErrors['phone'],
                  onCountryChanged: (c) => setState(() => _selectedCountry = c),
                ),

                SizedBox(height: 16),

                _buildFieldLabel('email_address'.tr(context)),
                SizedBox(height: 8),
                TextFormField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: _buildInputDecoration(
                    hintText: 'email_example'.tr(context),
                    prefixIcon: Icons.email_outlined,
                    errorText: _serverFieldErrors['email'],
                  ),
                  validator: Validators.email,
                ),

                SizedBox(height: 16),

                _buildFieldLabel('password'.tr(context)),
                SizedBox(height: 8),
                TextFormField(
                  controller: _passwordController,
                  obscureText: _obscurePassword,
                  decoration: _buildInputDecoration(
                    hintText: 'password_hint'.tr(context),
                    prefixIcon: Icons.lock_outline_rounded,
                    errorText: _serverFieldErrors['password'],
                    suffixIcon: IconButton(
                      icon: Icon(_obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                      onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                    ),
                  ),
                  validator: Validators.password,
                ),

                SizedBox(height: 16),

                _buildFieldLabel('confirm_password'.tr(context)),
                SizedBox(height: 8),
                TextFormField(
                  controller: _confirmPasswordController,
                  obscureText: _obscureConfirmPassword,
                  decoration: _buildInputDecoration(
                    hintText: 're_enter_password'.tr(context),
                    prefixIcon: Icons.lock_outline_rounded,
                    suffixIcon: IconButton(
                      icon: Icon(_obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                      onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                    ),
                  ),
                  validator: (v) => Validators.confirmPassword(v, _passwordController.text),
                ),

                SizedBox(height: 20),

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
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'agree_terms_policy'.tr(context),
                        style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 24),

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
                        ? SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5),
                          )
                        : Text(
                            'create_account'.tr(context),
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                          ),
                  ),
                ),

                SizedBox(height: 24),

                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('already_registered'.tr(context), style: TextStyle(color: Color(0xFF64748B))),
                    GestureDetector(
                      onTap: _isLoading
                          ? null
                          : () => Navigator.pushReplacementNamed(context, '/worker/auth/login'),
                      child: Text(
                        'sign_in'.tr(context),
                        style: TextStyle(fontWeight: FontWeight.w800, color: Color(0xFF2563EB)),
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 20),
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
      style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
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
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Color(0xFFE2E8F0), width: 1.5),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Color(0xFF2563EB), width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.red, width: 1.5),
      ),
      focusedErrorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.red, width: 1.5),
      ),
    );
  }
}
