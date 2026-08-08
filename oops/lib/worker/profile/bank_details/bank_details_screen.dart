// File: lib/worker/profile/bank_details/bank_details_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';
import '../../../widgets/language_selector_widget.dart';

class WorkerBankDetailsScreen extends StatefulWidget {
  const WorkerBankDetailsScreen({super.key});

  @override
  State<WorkerBankDetailsScreen> createState() =>
      _WorkerBankDetailsScreenState();
}

class _WorkerBankDetailsScreenState extends State<WorkerBankDetailsScreen> {
  final _accountHolderController =
      TextEditingController(text: 'RAMESH KUMAR');
  final _bankNameController =
      TextEditingController(text: 'State Bank of India');
  final _accountNumberController =
      TextEditingController(text: '30987654321');
  final _confirmAccountNumberController =
      TextEditingController(text: '30987654321');
  final _ifscController = TextEditingController(text: 'SBIN0001234');
  final _upiController = TextEditingController(text: 'rameshkumar@upi');

  String _payoutFrequency = 'Weekly';
  String _preferredMethod = 'Bank Transfer';
  bool _isVerified = true;

  @override
  void dispose() {
    _accountHolderController.dispose();
    _bankNameController.dispose();
    _accountNumberController.dispose();
    _confirmAccountNumberController.dispose();
    _ifscController.dispose();
    _upiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'bank_details_payouts'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF0F172A)),
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Bank Header Illustration Card
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF2563EB).withOpacity(0.25),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.account_balance_rounded,
                        color: Colors.white,
                        size: 32,
                      ),
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'direct_bank_settlement'.tr(context),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'secure_automated_payouts'.tr(context),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.white.withOpacity(0.85),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // Verification Status Banner
              if (_isVerified)
                Container(
                  padding: EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFD1FAE5),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                        color: const Color(0xFF10B981).withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.verified_rounded,
                          color: Color(0xFF10B981), size: 20),
                      SizedBox(width: 10),
                      Text(
                        'account_status_verified'.tr(context),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF065F46),
                        ),
                      ),
                    ],
                  ),
                ),

              SizedBox(height: 20),

              // Preferred Payout Method Selector
              _buildFieldLabel('preferred_payout_method'.tr(context)),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildSelectCard(
                      title: 'bank_transfer'.tr(context),
                      icon: Icons.account_balance_rounded,
                      isSelected: _preferredMethod == 'Bank Transfer',
                      onTap: () =>
                          setState(() => _preferredMethod = 'Bank Transfer'),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: _buildSelectCard(
                      title: 'upi_vpa'.tr(context),
                      icon: Icons.qr_code_rounded,
                      isSelected: _preferredMethod == 'UPI / VPA',
                      onTap: () =>
                          setState(() => _preferredMethod = 'UPI / VPA'),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 20),

              // Account Holder Name
              _buildFieldLabel('account_holder_name'.tr(context)),
              SizedBox(height: 8),
              _buildTextField(
                controller: _accountHolderController,
                hintText: 'as_per_bank_records'.tr(context),
                icon: Icons.person_outline_rounded,
              ),

              SizedBox(height: 18),

              // Bank Name
              _buildFieldLabel('bank_name'.tr(context)),
              SizedBox(height: 8),
              _buildTextField(
                controller: _bankNameController,
                hintText: 'eg_sbi_hdfc'.tr(context),
                icon: Icons.account_balance_outlined,
              ),

              SizedBox(height: 18),

              // Account Number
              _buildFieldLabel('account_number'.tr(context)),
              SizedBox(height: 8),
              _buildTextField(
                controller: _accountNumberController,
                hintText: 'enter_account_number'.tr(context),
                icon: Icons.numbers_rounded,
                keyboardType: TextInputType.number,
                obscureText: true,
              ),

              SizedBox(height: 18),

              // Confirm Account Number
              _buildFieldLabel('confirm_account_number'.tr(context)),
              SizedBox(height: 8),
              _buildTextField(
                controller: _confirmAccountNumberController,
                hintText: 're_enter_account_number'.tr(context),
                icon: Icons.lock_outline_rounded,
                keyboardType: TextInputType.number,
              ),

              SizedBox(height: 18),

              // IFSC Code & Verify Button Row
              _buildFieldLabel('ifsc_code'.tr(context)),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _ifscController,
                      hintText: 'eg_sbin'.tr(context),
                      icon: Icons.code_rounded,
                    ),
                  ),
                  SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('ifsc_verified_success'.tr(context)),
                          backgroundColor: const Color(0xFF10B981),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0EA5E9),
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(
                          horizontal: 16, vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Text('verify'.tr(context)),
                  ),
                ],
              ),

              SizedBox(height: 18),

              // UPI ID (Optional)
              _buildFieldLabel('upi_id_optional'.tr(context)),
              SizedBox(height: 8),
              _buildTextField(
                controller: _upiController,
                hintText: 'upi_hint'.tr(context),
                icon: Icons.phonelink_ring_rounded,
              ),

              SizedBox(height: 24),

              // Payout Frequency Selector Card
              Container(
                padding: EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'payout_schedule_frequency'.tr(context),
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'choose_how_often_transferred'.tr(context),
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF64748B),
                      ),
                    ),
                    SizedBox(height: 14),
                    Row(
                      children: ['Daily', 'Weekly'].map((freq) {
                        final selected = _payoutFrequency == freq;
                        return Expanded(
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _payoutFrequency = freq;
                              });
                            },
                            child: Container(
                              margin: EdgeInsets.only(right: 8),
                              padding: EdgeInsets.symmetric(vertical: 12),
                              decoration: BoxDecoration(
                                color: selected
                                    ? const Color(0xFF2563EB)
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(
                                  color: selected
                                      ? const Color(0xFF2563EB)
                                      : const Color(0xFFCBD5E1),
                                ),
                              ),
                              child: Center(
                                child: Text(
                                  freq == 'Daily'
                                      ? 'daily_instant'.tr(context)
                                      : 'weekly_mon'.tr(context),
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: selected
                                        ? FontWeight.w700
                                        : FontWeight.w500,
                                    color: selected
                                        ? Colors.white
                                        : const Color(0xFF475569),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 32),

              // Save Details Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('bank_details_saved'.tr(context)),
                        backgroundColor: const Color(0xFF10B981),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Text(
                    'save_bank_account'.tr(context),
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFieldLabel(String label) {
    return Text(
      label,
      style: TextStyle(
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
    bool obscureText = false,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        hintText: hintText,
        hintStyle: TextStyle(color: Color(0xFF94A3B8)),
        prefixIcon: Icon(icon, color: const Color(0xFF64748B)),
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        contentPadding:
            EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Color(0xFFE2E8F0)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Color(0xFF2563EB), width: 1.5),
        ),
      ),
    );
  }

  Widget _buildSelectCard({
    required String title,
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 14, horizontal: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFEFF6FF) : const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
            width: isSelected ? 1.5 : 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon,
                size: 20,
                color: isSelected
                    ? const Color(0xFF2563EB)
                    : const Color(0xFF64748B)),
            SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                fontSize: 13,
                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                color: isSelected
                    ? const Color(0xFF2563EB)
                    : const Color(0xFF475569),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
