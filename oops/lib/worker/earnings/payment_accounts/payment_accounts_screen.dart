// File: lib/worker/earnings/payment_accounts/payment_accounts_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';

class WorkerPaymentAccountsScreen extends StatefulWidget {
  const WorkerPaymentAccountsScreen({super.key});

  @override
  State<WorkerPaymentAccountsScreen> createState() =>
      _WorkerPaymentAccountsScreenState();
}

class _WorkerPaymentAccountsScreenState
    extends State<WorkerPaymentAccountsScreen> {
  String _defaultAccountId = 'BANK-1';

  List<Map<String, String>> get _accounts => [
    {
      'id': 'BANK-1',
      'title': 'mock_bank_name_sbi'.tr(context),
      'subtitle': 'mock_bank_account_ending'.tr(context),
      'holder': 'mock_bank_holder_name'.tr(context),
      'ifsc': 'SBIN0001234',
      'type': 'bank_account'.tr(context),
      'isDefault': 'true',
    },
    {
      'id': 'UPI-1',
      'title': 'mock_upi_name'.tr(context),
      'subtitle': 'mock_upi_id'.tr(context),
      'holder': 'mock_bank_holder_name'.tr(context),
      'ifsc': 'vpa_verified'.tr(context),
      'type': 'upi_id'.tr(context),
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
        title: Text(
          'payout_accounts_management'.tr(context),
          style: const TextStyle(
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
              Text(
                'linked_settlement_accounts'.tr(context),
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                'select_primary_account_desc'.tr(context),
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF64748B),
                ),
              ),

              const SizedBox(height: 18),

              ..._accounts.map((acc) {
                final isSelected = _defaultAccountId == acc['id'];
                final isBank = acc['type'] == 'bank_account'.tr(context);

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
                              child: Text(
                                'primary_caps'.tr(context),
                                style: const TextStyle(
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
                            'holder_prefix'.tr(context).replaceAll('{}', acc['holder'] ?? ''),
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
                                child: Text('edit'.tr(context),
                                    style: const TextStyle(fontSize: 12)),
                              ),
                              TextButton(
                                onPressed: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                      content: Text('account_removed_success'.tr(context)),
                                    ),
                                  );
                                },
                                child: Text(
                                  'remove'.tr(context),
                                  style: const TextStyle(
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
                      label: Text('add_bank_ac'.tr(context)),
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
                      label: Text('add_upi_vpa'.tr(context)),
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
