// File: lib/worker/earnings/payment_accounts/payment_accounts_screen.dart

import 'package:flutter/material.dart';

class WorkerPaymentAccountsScreen extends StatefulWidget {
  const WorkerPaymentAccountsScreen({super.key});

  @override
  State<WorkerPaymentAccountsScreen> createState() =>
      _WorkerPaymentAccountsScreenState();
}

class _WorkerPaymentAccountsScreenState
    extends State<WorkerPaymentAccountsScreen> {
  String _defaultAccountId = 'BANK-1';

  final List<Map<String, String>> _accounts = [
    {
      'id': 'BANK-1',
      'title': 'State Bank of India',
      'subtitle': 'Savings A/C ending ...4321',
      'holder': 'RAMESH KUMAR',
      'ifsc': 'SBIN0001234',
      'type': 'Bank Account',
      'isDefault': 'true',
    },
    {
      'id': 'UPI-1',
      'title': 'Google Pay / PhonePe UPI',
      'subtitle': 'rameshkumar@upi',
      'holder': 'RAMESH KUMAR',
      'ifsc': 'VPA Verified',
      'type': 'UPI ID',
      'isDefault': 'false',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Payout Accounts Management',
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
              const Text(
                'Linked Settlement Accounts',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 6),
              const Text(
                'Select primary account for weekly automated payouts',
                style: TextStyle(
                  fontSize: 13,
                  color: Color(0xFF64748B),
                ),
              ),

              const SizedBox(height: 18),

              ..._accounts.map((acc) {
                final isSelected = _defaultAccountId == acc['id'];
                final isBank = acc['type'] == 'Bank Account';

                return Container(
                  margin: const EdgeInsets.only(bottom: 14),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? const Color(0xFFEFF6FF)
                        : Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF2563EB)
                          : const Color(0xFFE2E8F0),
                      width: isSelected ? 1.5 : 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.03),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Radio<String>(
                            value: acc['id']!,
                            groupValue: _defaultAccountId,
                            activeColor: const Color(0xFF2563EB),
                            onChanged: (val) {
                              if (val != null) {
                                setState(() => _defaultAccountId = val);
                              }
                            },
                          ),
                          Container(
                            padding: const EdgeInsets.all(10),
                            decoration: BoxDecoration(
                              color: isBank
                                  ? const Color(0xFFDBEAFE)
                                  : const Color(0xFFD1FAE5),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              isBank
                                  ? Icons.account_balance_rounded
                                  : Icons.qr_code_rounded,
                              color: isBank
                                  ? const Color(0xFF2563EB)
                                  : const Color(0xFF10B981),
                              size: 20,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  acc['title']!,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  acc['subtitle']!,
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF64748B),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          if (isSelected)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: const Color(0xFF2563EB),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Text(
                                'PRIMARY',
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Divider(color: Color(0xFFE2E8F0)),
                      const SizedBox(height: 6),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Holder: ${acc['holder']}',
                            style: const TextStyle(
                              fontSize: 11,
                              color: Color(0xFF94A3B8),
                            ),
                          ),
                          Row(
                            children: [
                              TextButton(
                                onPressed: () {
                                  Navigator.pushNamed(context, '/worker/profile/bank-details');
                                },
                                child: const Text('Edit',
                                    style: TextStyle(fontSize: 12)),
                              ),
                              TextButton(
                                onPressed: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Account removed.'),
                                    ),
                                  );
                                },
                                child: const Text(
                                  'Remove',
                                  style: TextStyle(
                                      fontSize: 12, color: Color(0xFFEF4444)),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              }).toList(),

              const SizedBox(height: 20),

              // Add New Account Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pushNamed(
                            context, '/worker/profile/bank-details');
                      },
                      icon: const Icon(Icons.add_rounded, size: 18),
                      label: const Text('Add Bank A/C'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF2563EB),
                        side: const BorderSide(color: Color(0xFF2563EB)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pushNamed(
                            context, '/worker/profile/bank-details');
                      },
                      icon: const Icon(Icons.add_rounded, size: 18),
                      label: const Text('Add UPI VPA'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF0EA5E9),
                        side: const BorderSide(color: Color(0xFF0EA5E9)),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
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
    );
  }
}
