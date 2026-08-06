// File: lib/customer/quotations/customer_quotation_detail_screen.dart

import 'package:flutter/material.dart';
import '../../models/quotation_model.dart';
import '../../services/quotation_service.dart';

import 'quotation_history_timeline_screen.dart';

class CustomerQuotationDetailScreen extends StatefulWidget {
  final String quotationId;
  final String bookingNumber;
  final CustomerQuotationItem? initialItem;

  const CustomerQuotationDetailScreen({
    super.key,
    required this.quotationId,
    required this.bookingNumber,
    this.initialItem,
  });

  @override
  State<CustomerQuotationDetailScreen> createState() => _CustomerQuotationDetailScreenState();
}

class _CustomerQuotationDetailScreenState extends State<CustomerQuotationDetailScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  CustomerQuotationItem? _item;

  @override
  void initState() {
    super.initState();
    _item = widget.initialItem;
    if (_item != null) {
      _isLoading = false;
    } else {
      _loadDetail();
    }
  }

  Future<void> _loadDetail() async {
    try {
      final res = await QuotationService.instance
          .fetchCustomerQuotationDetail(widget.quotationId);
      if (!mounted) return;
      setState(() {
        _item = res;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quotation Details',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            Text(
              'Ref: ${widget.bookingNumber}',
              style: const TextStyle(fontSize: 11, color: Color(0xFF64748B)),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history_rounded, color: Color(0xFF2563EB)),
            tooltip: 'View Audit Trail',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => QuotationHistoryTimelineScreen(
                    quotationId: widget.quotationId,
                    bookingNumber: widget.bookingNumber,
                    isCustomer: true,
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : _errorMessage != null
              ? _buildErrorView()
              : _item == null
                  ? const Center(child: Text('Quotation not found.'))
                  : SafeArea(
                      child: ListView(
                        padding: const EdgeInsets.all(20.0),
                        children: [
                          // Worker Profile Card
                          _buildWorkerCard(_item!.worker),

                          const SizedBox(height: 18),

                          // Total Cost Summary Card
                          _buildCostSummaryCard(_item!.quotation),

                          const SizedBox(height: 18),

                          // Detailed Cost Breakdown Table
                          _buildCostBreakdownCard(_item!.quotation),

                          const SizedBox(height: 18),

                          // Schedule & Validity Card
                          _buildScheduleCard(_item!.quotation),

                          const SizedBox(height: 18),

                          // Scope of Work Card
                          _buildScopeCard(_item!.quotation),

                          const SizedBox(height: 24),

                          // Acceptance Action or Status Badge
                          if (_item!.quotation.isSubmitted)
                            _buildAcceptButton()
                          else
                            _buildStatusBadge(_item!.quotation),

                          const SizedBox(height: 20),
                        ],
                      ),
                    ),
    );
  }

  bool _isAccepting = false;

  Future<void> _showAcceptConfirmationDialog() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.check_circle_outline_rounded, color: Color(0xFF059669)),
            SizedBox(width: 8),
            Text('Accept Quotation?', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Text(
          'Are you sure you want to accept this quotation from ${_item!.worker.fullName} for ₹${_item!.quotation.totalAmount.toStringAsFixed(0)}?\n\nThis will assign ${_item!.worker.fullName} to your booking.',
          style: const TextStyle(fontSize: 13, color: Color(0xFF475569), height: 1.4),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF059669),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Confirm & Accept'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      _acceptQuotation();
    }
  }

  Future<void> _acceptQuotation() async {
    setState(() => _isAccepting = true);
    try {
      await QuotationService.instance.acceptQuotation(widget.quotationId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Quotation Accepted! ${_item!.worker.fullName} assigned successfully.'),
          backgroundColor: const Color(0xFF059669),
        ),
      );
      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;
      setState(() => _isAccepting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to accept quotation: ${e.toString()}'),
          backgroundColor: const Color(0xFFDC2626),
        ),
      );
    }
  }

  Widget _buildAcceptButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: _isAccepting ? null : _showAcceptConfirmationDialog,
        icon: _isAccepting
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              )
            : const Icon(Icons.check_circle_rounded, size: 20),
        label: Text(
          _isAccepting ? 'Processing...' : 'Accept Quotation & Assign Worker',
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF059669),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(QuotationItem q) {
    final isAccepted = q.isAccepted;
    final isRejected = q.isRejected;

    final bgColor = isAccepted
        ? const Color(0xFFECFDF5)
        : isRejected
            ? const Color(0xFFFEE2E2)
            : const Color(0xFFF1F5F9);

    final fgColor = isAccepted
        ? const Color(0xFF059669)
        : isRejected
            ? const Color(0xFFDC2626)
            : const Color(0xFF475569);

    final text = isAccepted
        ? 'ACCEPTED QUOTATION — WORKER ASSIGNED'
        : isRejected
            ? 'REJECTED QUOTATION'
            : q.quotationStatus.toUpperCase();

    return Container(
      padding: const EdgeInsets.all(14),
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: fgColor.withOpacity(0.3)),
      ),
      child: Text(
        text,
        style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800, color: fgColor),
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded, size: 56, color: Color(0xFFDC2626)),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loadDetail,
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2563EB), foregroundColor: Colors.white),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWorkerCard(WorkerSummary w) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 26,
                backgroundColor: const Color(0xFFEFF6FF),
                backgroundImage: w.profilePhotoUrl != null ? NetworkImage(w.profilePhotoUrl!) : null,
                child: w.profilePhotoUrl == null
                    ? Text(
                        w.fullName.isNotEmpty ? w.fullName[0].toUpperCase() : 'W',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF2563EB)),
                      )
                    : null,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      w.fullName,
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.star_rounded, size: 16, color: Color(0xFFEAB308)),
                        const SizedBox(width: 4),
                        Text(
                          w.rating.toStringAsFixed(1),
                          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '•  ${w.experienceYears.toStringAsFixed(0)} Years Experience',
                          style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (w.skills.isNotEmpty) ...[
            const SizedBox(height: 14),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: w.skills.map((skill) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    skill,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCostSummaryCard(QuotationItem q) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Total Quotation Amount', style: TextStyle(fontSize: 13, color: Colors.white70)),
              SizedBox(height: 4),
              Text(
                'Includes taxes & discount',
                style: TextStyle(fontSize: 11, color: Colors.white38),
              ),
            ],
          ),
          Text(
            '₹${q.totalAmount.toStringAsFixed(0)}',
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Color(0xFF38BDF8)),
          ),
        ],
      ),
    );
  }

  Widget _buildCostBreakdownCard(QuotationItem q) {
    final subtotal = q.labourCost + q.materialCost + q.inspectionCharge + q.additionalCharges;

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.receipt_long_rounded, size: 18, color: Color(0xFF2563EB)),
              SizedBox(width: 8),
              Text(
                'Itemized Pricing Breakdown',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildBreakdownRow('Labour Cost', '₹${q.labourCost.toStringAsFixed(0)}'),
          _buildBreakdownRow('Material Cost', '₹${q.materialCost.toStringAsFixed(0)}'),
          _buildBreakdownRow('Inspection Charge', '₹${q.inspectionCharge.toStringAsFixed(0)}'),
          _buildBreakdownRow('Additional Charges', '₹${q.additionalCharges.toStringAsFixed(0)}'),
          const Divider(height: 18, color: Color(0xFFE2E8F0)),
          _buildBreakdownRow('Subtotal', '₹${subtotal.toStringAsFixed(0)}', isBold: true),
          _buildBreakdownRow('Taxes & Levies', '+ ₹${q.taxAmount.toStringAsFixed(0)}'),
          _buildBreakdownRow('Discount Offered', '- ₹${q.discountAmount.toStringAsFixed(0)}', isHighlight: true),
        ],
      ),
    );
  }

  Widget _buildBreakdownRow(String label, String value, {bool isBold = false, bool isHighlight = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 13,
              fontWeight: isBold ? FontWeight.w700 : FontWeight.w500,
              color: isBold ? const Color(0xFF0F172A) : const Color(0xFF64748B),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 13,
              fontWeight: isBold || isHighlight ? FontWeight.w800 : FontWeight.w600,
              color: isHighlight
                  ? const Color(0xFF059669)
                  : isBold
                      ? const Color(0xFF0F172A)
                      : const Color(0xFF334155),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScheduleCard(QuotationItem q) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.date_range_rounded, size: 18, color: Color(0xFF2563EB)),
              SizedBox(width: 8),
              Text(
                'Schedule & Validity',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildBreakdownRow('Estimated Duration', q.estimatedDuration),
          _buildBreakdownRow('Earliest Work Start', q.workStartDate ?? 'Immediate / Flexible'),
          _buildBreakdownRow('Quotation Valid Until', q.validityDate),
        ],
      ),
    );
  }

  Widget _buildScopeCard(QuotationItem q) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.description_outlined, size: 18, color: Color(0xFF2563EB)),
              SizedBox(width: 8),
              Text(
                'Scope of Work & Terms',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Text('Work Description:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
          const SizedBox(height: 4),
          Text(
            q.workDescription ?? 'No specific scope description provided.',
            style: const TextStyle(fontSize: 13, color: Color(0xFF334155), height: 1.4),
          ),
          if (q.termsAndConditions != null && q.termsAndConditions!.isNotEmpty) ...[
            const SizedBox(height: 14),
            const Text('Terms & Conditions:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF475569))),
            const SizedBox(height: 4),
            Text(
              q.termsAndConditions!,
              style: const TextStyle(fontSize: 13, color: Color(0xFF334155), height: 1.4),
            ),
          ],
        ],
      ),
    );
  }
}
