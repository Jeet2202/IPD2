// File:
// lib/customer/payment/invoice_screen.dart

import 'package:flutter/material.dart';
import '../../l10n/app_translations.dart';

class InvoiceScreen extends StatelessWidget {
  const InvoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.close_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('tax_invoice'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: Icon(Icons.share_outlined, color: Color(0xFF2563EB)),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('sharing_tax_invoice_ksinv9812'.tr(context))),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            children: [
              // ── Invoice Card ─────────────────────────────────────────
              Container(
                padding: EdgeInsets.all(22),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 16, offset: const Offset(0, 4)),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Brand Header & Invoice Badge
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.handyman_rounded, color: Color(0xFF2563EB), size: 26),
                            SizedBox(width: 8),
                            Text('ally'.tr(context), style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                          ],
                        ),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(8)),
                          child: Text('paid'.tr(context), style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: Color(0xFF16A34A))),
                        ),
                      ],
                    ),

                    SizedBox(height: 20),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 16),

                    // Meta Row 1: Invoice & Booking ID
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _MetaText(label: 'Invoice No.', val: '#KS-INV-9812'),
                        _MetaText(label: 'Booking ID', val: '#KS-94821'),
                      ],
                    ),

                    SizedBox(height: 14),

                    // Meta Row 2: Date & Customer
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _MetaText(label: 'Date', val: '31 July 2026, 11:30 AM'),
                        _MetaText(label: 'Customer', val: 'Rahul Sharma'),
                      ],
                    ),

                    SizedBox(height: 20),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 16),

                    // Professional & Service Info
                    Text('service_details'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                    SizedBox(height: 8),
                    Text('switchboard_wiring_repair'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                    SizedBox(height: 4),
                    Text('assigned_professional_ramesh_kumar_electrician'.tr(context), style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),

                    SizedBox(height: 20),
                    Divider(color: Color(0xFFF1F5F9), height: 1),
                    SizedBox(height: 16),

                    // Line Items
                    Text('amount_breakdown'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                    SizedBox(height: 12),

                    _buildLineItem('Service Charge', '₹349.00'),
                    SizedBox(height: 8),
                    _buildLineItem('Inspection Fee', '₹99.00'),
                    SizedBox(height: 8),
                    _buildLineItem('Safety & Platform Fee', '₹29.00'),
                    SizedBox(height: 8),
                    _buildLineItem('Taxes & GST (18%)', '₹47.00'),
                    SizedBox(height: 8),
                    _buildLineItem('Discount (ALLY50)', '-₹100.00', isDiscount: true),

                    SizedBox(height: 16),
                    Divider(color: Color(0xFFE2E8F0), height: 1),
                    SizedBox(height: 14),

                    // Grand Total
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('total_amount_paid'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w900, color: Color(0xFF0F172A))),
                        Text('37700'.tr(context), style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF2563EB))),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 28),

              // ── Action Buttons ────────────────────────────────────────
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('invoice_pdf_downloaded_to_device'.tr(context)),
                            backgroundColor: Color(0xFF2563EB),
                          ),
                        );
                      },
                      icon: Icon(Icons.download_rounded, size: 18),
                      label: Text('download_pdf'.tr(context)),
                      style: OutlinedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 14),
                        side: BorderSide(color: Color(0xFF2563EB)),
                        foregroundColor: const Color(0xFF2563EB),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                  SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => Navigator.pop(context),
                      icon: Icon(Icons.home_rounded, size: 18),
                      label: Text('back_to_home'.tr(context)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLineItem(String label, String val, {bool isDiscount = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(fontSize: 13, color: isDiscount ? const Color(0xFF16A34A) : const Color(0xFF64748B))),
        Text(
          val,
          style: TextStyle(
            fontSize: 13,
            fontWeight: isDiscount ? FontWeight.w800 : FontWeight.w600,
            color: isDiscount ? const Color(0xFF16A34A) : const Color(0xFF0F172A),
          ),
        ),
      ],
    );
  }
}

class _MetaText extends StatelessWidget {
  final String label;
  final String val;
  const _MetaText({required this.label, required this.val});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
        SizedBox(height: 2),
        Text(val, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
      ],
    );
  }
}
