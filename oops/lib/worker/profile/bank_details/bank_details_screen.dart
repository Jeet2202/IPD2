// File: lib/worker/profile/bank_details/bank_details_screen.dart

import 'package:flutter/material.dart';

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
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Bank Details & Payouts',
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
              // Bank Header Illustration Card
              Container(
                padding: const EdgeInsets.all(20),
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
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.account_balance_rounded,
                        color: Colors.white,
                        size: 32,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Direct Bank Settlement',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Secure automated payouts directly to your savings account',
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

              const SizedBox(height: 24),

              // Verification Status Banner
              if (_isVerified)
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFD1FAE5),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                        color: const Color(0xFF10B981).withOpacity(0.3)),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.verified_rounded,
                          color: Color(0xFF10B981), size: 20),
                      SizedBox(width: 10),
                      Text(
                        'Account Status: Verified & Active',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF065F46),
                        ),
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 20),

              // Preferred Payout Method Selector
              _buildFieldLabel('Preferred Payout Method'),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildSelectCard(
                      title: 'Bank Transfer',
                      icon: Icons.account_balance_rounded,
                      isSelected: _preferredMethod == 'Bank Transfer',
                      onTap: () =>
                          setState(() => _preferredMethod = 'Bank Transfer'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildSelectCard(
                      title: 'UPI / VPA',
                      icon: Icons.qr_code_rounded,
                      isSelected: _preferredMethod == 'UPI / VPA',
                      onTap: () =>
                          setState(() => _preferredMethod = 'UPI / VPA'),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Account Holder Name
              _buildFieldLabel('Account Holder Name'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _accountHolderController,
                hintText: 'As per bank records',
                icon: Icons.person_outline_rounded,
              ),

              const SizedBox(height: 18),

              // Bank Name
              _buildFieldLabel('Bank Name'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _bankNameController,
                hintText: 'e.g. State Bank of India, HDFC',
                icon: Icons.account_balance_outlined,
              ),

              const SizedBox(height: 18),

              // Account Number
              _buildFieldLabel('Account Number'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _accountNumberController,
                hintText: 'Enter bank account number',
                icon: Icons.numbers_rounded,
                keyboardType: TextInputType.number,
                obscureText: true,
              ),

              const SizedBox(height: 18),

              // Confirm Account Number
              _buildFieldLabel('Confirm Account Number'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _confirmAccountNumberController,
                hintText: 'Re-enter account number',
                icon: Icons.lock_outline_rounded,
                keyboardType: TextInputType.number,
              ),

              const SizedBox(height: 18),

              // IFSC Code & Verify Button Row
              _buildFieldLabel('IFSC Code'),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _ifscController,
                      hintText: 'e.g. SBIN0001234',
                      icon: Icons.code_rounded,
                    ),
                  ),
                  const SizedBox(width: 10),
                  ElevatedButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('IFSC Verified: SBI Main Branch'),
                          backgroundColor: Color(0xFF10B981),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0EA5E9),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: const Text('Verify'),
                  ),
                ],
              ),

              const SizedBox(height: 18),

              // UPI ID (Optional)
              _buildFieldLabel('UPI ID (Optional)'),
              const SizedBox(height: 8),
              _buildTextField(
                controller: _upiController,
                hintText: 'username@upi or mobile@paytm',
                icon: Icons.phonelink_ring_rounded,
              ),

              const SizedBox(height: 24),

              // Payout Frequency Selector Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Payout Schedule Frequency',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Choose how often your earnings are transferred',
                      style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFF64748B),
                      ),
                    ),
                    const SizedBox(height: 14),
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
                              margin: const EdgeInsets.only(right: 8),
                              padding: const EdgeInsets.symmetric(vertical: 12),
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
                                      ? 'Daily (Instant)'
                                      : 'Weekly (Every Mon)',
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

              const SizedBox(height: 32),

              // Save Details Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Bank details saved securely!'),
                        backgroundColor: Color(0xFF10B981),
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
                  child: const Text(
                    'Save Bank Account',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
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
    bool obscureText = false,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
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

  Widget _buildSelectCard({
    required String title,
    required IconData icon,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
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
            const SizedBox(width: 8),
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
