// File: lib/worker/earnings/transaction_details/transaction_details_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';

class WorkerTransactionDetailsScreen extends StatelessWidget {
  const WorkerTransactionDetailsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'transaction_details'.tr(context),
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
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Status & Amount Header Card
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFFD1FAE5),
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(
                      color: const Color(0xFF10B981).withOpacity(0.3)),
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0xFF10B981),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.check_rounded,
                          color: Colors.white, size: 28),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'amount_850'.tr(context),
                      style: const TextStyle(
                        fontSize: 34,
                        fontWeight: FontWeight.w900,
                        color: Color(0xFF065F46),
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'credited_to_wallet_mock'.tr(context),
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF047857),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Job & Customer Summary Box
              _buildDetailSection(
                title: 'associated_job_details'.tr(context),
                child: Column(
                  children: [
                    _buildRowItem('booking_id'.tr(context), 'job_id_mock'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('service'.tr(context), 'mcb_short_circuit_repair'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('customer'.tr(context), 'mock_customer_name'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('location'.tr(context), 'dwarka_new_delhi_mock'.tr(context)),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Financial Breakdown Box
              _buildDetailSection(
                title: 'earnings_breakdown'.tr(context),
                child: Column(
                  children: [
                    _buildRowItem('gross_labour_charges'.tr(context), 'amount_850_00'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('customer_tip'.tr(context), 'amount_100_00'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('platform_fee_0'.tr(context), 'amount_0_00'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('tds_tax_deducted_0'.tr(context), 'amount_0_00'.tr(context)),
                    const SizedBox(height: 10),
                    const Divider(color: Color(0xFFE2E8F0)),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'net_earned_amount'.tr(context),
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF0F172A),
                          ),
                        ),
                        Text(
                          'amount_950_00'.tr(context),
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF10B981),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 18),

              // Payment Technical References Box
              _buildDetailSection(
                title: 'payment_references'.tr(context),
                child: Column(
                  children: [
                    _buildRowItem('payment_method'.tr(context), 'online_prepaid_escrow'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('transaction_id'.tr(context), 'mock_txn_id'.tr(context)),
                    const SizedBox(height: 8),
                    _buildRowItem('gateway_reference'.tr(context), 'mock_gateway_ref'.tr(context)),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Action Buttons Row
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('downloading_tax_invoice'.tr(context)),
                            backgroundColor: const Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: const Icon(Icons.download_rounded, size: 18),
                      label: Text('invoice_pdf'.tr(context)),
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
                    child: ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('sharing_transaction_receipt'.tr(context)),
                            backgroundColor: const Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: const Icon(Icons.share_rounded, size: 18),
                      label: Text('share_receipt'.tr(context)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailSection({
    required String title,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFF1F5F9), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 12),
          child,
        ],
      ),
    );
  }

  Widget _buildRowItem(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Color(0xFF64748B),
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Color(0xFF0F172A),
          ),
        ),
      ],
    );
  }
}
