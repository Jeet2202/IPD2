import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../app/theme/app_colors.dart';
import '../../../app/theme/app_dimensions.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_service.dart';
import '../../../widgets/app_button.dart';
import '../../../widgets/app_text_field.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtr = TextEditingController();
  bool _loading = false;

  @override
  void dispose() {
    _emailCtr.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final email = _emailCtr.text.trim();

    setState(() => _loading = true);

    try {
      await AuthService.instance.forgotPassword(email);

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('If an account exists with $email, a password reset code has been sent.'),
          backgroundColor: AppColors.primary,
        ),
      );

      Navigator.of(context).pushNamed(
        AppRoutes.customerOtp,
        arguments: {'email': email, 'purpose': 'password_reset'},
      );
    } catch (e) {
      if (!mounted) return;
      final msg = e is ApiException ? e.message : 'Request failed: $e';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Forgot Password'),
        backgroundColor: AppColors.background,
        foregroundColor: AppColors.textPrimary,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppDimensions.lg),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 16),
              const Text('Reset Password', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              const Text(
                'Enter your registered email address to receive a 6-digit OTP code.',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),
              AppTextField(
                label: 'Email Address',
                hint: 'name@example.com',
                controller: _emailCtr,
                keyboardType: TextInputType.emailAddress,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Email address is required';
                  if (!v.contains('@') || !v.contains('.')) return 'Enter a valid email address';
                  return null;
                },
              ),
              const SizedBox(height: 24),
              AppButton(label: 'Send Reset OTP', onPressed: _submit, isLoading: _loading),
            ],
          ),
        ),
      ),
    );
  }
}
