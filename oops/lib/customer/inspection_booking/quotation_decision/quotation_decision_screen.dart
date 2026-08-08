// File:
// lib/customer/inspection_booking/quotation_decision/quotation_decision_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../l10n/app_translations.dart';

class QuotationDecisionScreen extends StatefulWidget {
  const QuotationDecisionScreen({super.key});

  @override
  State<QuotationDecisionScreen> createState() => _QuotationDecisionScreenState();
}

class _QuotationDecisionScreenState extends State<QuotationDecisionScreen> {
  bool _isNegotiating = false;
  final TextEditingController _counterAmountController = TextEditingController(text: '1100');
  String _selectedReason = 'Budget Constraints';

  final List<String> _reasons = [
    'Budget Constraints',
    'Spare Parts Seem Expensive',
    'Labor Charge High',
    'Found Alternative Option',
  ];

  @override
  void dispose() {
    _counterAmountController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('quotation_decision'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Quote Summary Highlight Card ────────────────────────
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
                    BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.28), blurRadius: 16, offset: const Offset(0, 6)),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('final_quotation'.tr(context), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFFDBEAFE))),
                        SizedBox(height: 4),
                        Text('125000'.tr(context), style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Colors.white)),
                        SizedBox(height: 2),
                        Text('includes_havells_mcb_30day_warranty'.tr(context), style: TextStyle(fontSize: 11, color: Color(0xFFE0F2FE))),
                      ],
                    ),
                    Icon(Icons.gavel_rounded, color: Colors.white, size: 36),
                  ],
                ),
              ),

              SizedBox(height: 28),

              Text('select_action'.tr(context), style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
              SizedBox(height: 14),

              // ── 1. Accept Button ────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: () => Navigator.pushNamed(context, AppRoutes.repairConfirmation),
                  icon: Icon(Icons.check_circle_rounded, size: 22),
                  label: Text('accept_quote_start_repair'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF16A34A),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  ),
                ),
              ),

              SizedBox(height: 14),

              // ── 2. Negotiate Accordion ──────────────────────────────
              OutlinedButton.icon(
                onPressed: () => setState(() => _isNegotiating = !_isNegotiating),
                icon: Icon(Icons.handshake_outlined, size: 20),
                label: Text(_isNegotiating ? 'Hide Negotiation Panel' : 'Negotiate / Counter Offer'),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 52),
                  foregroundColor: const Color(0xFF2563EB),
                  side: BorderSide(color: Color(0xFF2563EB)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                ),
              ),

              if (_isNegotiating) ...[
                SizedBox(height: 14),
                Container(
                  padding: EdgeInsets.all(18),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: const Color(0xFFBFDBFE)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('your_counter_offer'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      SizedBox(height: 6),
                      TextField(
                        controller: _counterAmountController,
                        keyboardType: TextInputType.number,
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        decoration: InputDecoration(
                          prefixIcon: Icon(Icons.currency_rupee_rounded, color: Color(0xFF2563EB), size: 18),
                          contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      ),
                      SizedBox(height: 14),
                      Text('reason_for_counter_offer'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                      SizedBox(height: 6),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFCBD5E1)),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<String>(
                            value: _selectedReason,
                            isExpanded: true,
                            items: _reasons.map((r) => DropdownMenuItem(value: r, child: Text(r, style: TextStyle(fontSize: 13)))).toList(),
                            onChanged: (val) => setState(() => _selectedReason = val!),
                          ),
                        ),
                      ),
                      SizedBox(height: 14),
                      SizedBox(
                        width: double.infinity,
                        height: 46,
                        child: ElevatedButton(
                          onPressed: () => Navigator.pushNamed(context, AppRoutes.negotiationChat),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: Text('send_counter_offer'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              SizedBox(height: 14),

              // ── 3. Reject Button ────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: OutlinedButton.icon(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: Text('reject_quotation'.tr(context)),
                        content: Text('are_you_sure_you_want_2'.tr(context)),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx), child: Text('cancel'.tr(context))),
                          ElevatedButton(
                            onPressed: () {
                              Navigator.pop(ctx);
                              Navigator.pop(context);
                            },
                            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFEF4444)),
                            child: Text('reject'.tr(context)),
                          ),
                        ],
                      ),
                    );
                  },
                  icon: Icon(Icons.cancel_outlined, size: 20),
                  label: Text('reject_quotation_2'.tr(context), style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFFEF4444),
                    side: BorderSide(color: Color(0xFFEF4444)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  ),
                ),
              ),

              SizedBox(height: 28),

              // ── Info Cards ──────────────────────────────────────────
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline_rounded, color: Color(0xFF2563EB), size: 20),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text('upon_accepting_sunil_will_immediately'.tr(context),
                        style: TextStyle(fontSize: 12, color: Color(0xFF1E40AF), height: 1.3),
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
