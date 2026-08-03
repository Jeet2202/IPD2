// File: lib/worker/quotations/quotation_form_screen.dart

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/quotation_model.dart';
import '../../services/quotation_service.dart';

class QuotationFormScreen extends StatefulWidget {
  final String bookingId;
  final String applicationId;
  final String bookingNumber;
  final String serviceName;

  const QuotationFormScreen({
    super.key,
    required this.bookingId,
    required this.applicationId,
    required this.bookingNumber,
    required this.serviceName,
  });

  @override
  State<QuotationFormScreen> createState() => _QuotationFormScreenState();
}

class _QuotationFormScreenState extends State<QuotationFormScreen> {
  final _formKey = GlobalKey<FormState>();

  // Cost Controllers
  final _labourCostController = TextEditingController(text: '0');
  final _materialCostController = TextEditingController(text: '0');
  final _inspectionChargeController = TextEditingController(text: '0');
  final _additionalChargesController = TextEditingController(text: '0');
  final _taxAmountController = TextEditingController(text: '0');
  final _discountAmountController = TextEditingController(text: '0');

  // Schedule & Scope Controllers
  final _estimatedDurationController = TextEditingController(text: '2 days');
  final _workDescriptionController = TextEditingController();
  final _termsController = TextEditingController();
  final _notesController = TextEditingController();

  DateTime _validityDate = DateTime.now().add(const Duration(days: 14));
  DateTime? _workStartDate = DateTime.now().add(const Duration(days: 1));

  bool _isLoading = true;
  bool _isSaving = false;
  String? _errorMessage;
  QuotationItem? _existingQuotation;

  @override
  void initState() {
    super.initState();
    _loadExistingQuotation();
  }

  @override
  void dispose() {
    _labourCostController.dispose();
    _materialCostController.dispose();
    _inspectionChargeController.dispose();
    _additionalChargesController.dispose();
    _taxAmountController.dispose();
    _discountAmountController.dispose();
    _estimatedDurationController.dispose();
    _workDescriptionController.dispose();
    _termsController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadExistingQuotation() async {
    try {
      final q = await QuotationService.instance
          .fetchQuotationByApplication(widget.applicationId);
      if (mounted && q != null) {
        setState(() {
          _existingQuotation = q;
          _labourCostController.text = q.labourCost.toStringAsFixed(0);
          _materialCostController.text = q.materialCost.toStringAsFixed(0);
          _inspectionChargeController.text = q.inspectionCharge.toStringAsFixed(0);
          _additionalChargesController.text = q.additionalCharges.toStringAsFixed(0);
          _taxAmountController.text = q.taxAmount.toStringAsFixed(0);
          _discountAmountController.text = q.discountAmount.toStringAsFixed(0);
          _estimatedDurationController.text = q.estimatedDuration;
          if (q.workDescription != null) {
            _workDescriptionController.text = q.workDescription!;
          }
          if (q.termsAndConditions != null) {
            _termsController.text = q.termsAndConditions!;
          }
          if (q.notes != null) {
            _notesController.text = q.notes!;
          }
          try {
            _validityDate = DateTime.parse(q.validityDate);
          } catch (_) {}
          if (q.workStartDate != null) {
            try {
              _workStartDate = DateTime.parse(q.workStartDate!);
            } catch (_) {}
          }
        });
      }
    } catch (e) {
      // Ignore load error for new quotations
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  double get _labour => double.tryParse(_labourCostController.text.trim()) ?? 0.0;
  double get _material => double.tryParse(_materialCostController.text.trim()) ?? 0.0;
  double get _inspection => double.tryParse(_inspectionChargeController.text.trim()) ?? 0.0;
  double get _additional => double.tryParse(_additionalChargesController.text.trim()) ?? 0.0;
  double get _tax => double.tryParse(_taxAmountController.text.trim()) ?? 0.0;
  double get _discount => double.tryParse(_discountAmountController.text.trim()) ?? 0.0;

  double get _subtotal => _labour + _material + _inspection + _additional;
  double get _calculatedTotal => (_subtotal + _tax - _discount).clamp(0.0, double.infinity);

  bool get _isReadOnly => _existingQuotation != null && !_existingQuotation!.isDraft;

  Future<void> _submitOrSave({required bool isDraft}) async {
    if (!_formKey.currentState!.validate()) return;

    if (_discount > (_subtotal + _tax)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Discount cannot exceed total charges'),
          backgroundColor: Color(0xFFDC2626),
        ),
      );
      return;
    }

    setState(() {
      _isSaving = true;
      _errorMessage = null;
    });

    final dateFormat = DateFormat('yyyy-MM-dd');
    final valDateStr = dateFormat.format(_validityDate);
    final startDateStr = _workStartDate != null ? dateFormat.format(_workStartDate!) : null;

    try {
      if (_existingQuotation == null) {
        // Create new
        final res = await QuotationService.instance.createQuotation(
          bookingId: widget.bookingId,
          applicationId: widget.applicationId,
          labourCost: _labour,
          materialCost: _material,
          inspectionCharge: _inspection,
          additionalCharges: _additional,
          taxAmount: _tax,
          discountAmount: _discount,
          estimatedDuration: _estimatedDurationController.text.trim(),
          validityDate: valDateStr,
          workStartDate: startDateStr,
          workDescription: _workDescriptionController.text.trim(),
          termsAndConditions: _termsController.text.trim(),
          notes: _notesController.text.trim(),
          isDraft: isDraft,
        );
        _existingQuotation = res;
      } else {
        // Update existing draft
        final res = await QuotationService.instance.updateQuotation(
          quotationId: _existingQuotation!.id,
          labourCost: _labour,
          materialCost: _material,
          inspectionCharge: _inspection,
          additionalCharges: _additional,
          taxAmount: _tax,
          discountAmount: _discount,
          estimatedDuration: _estimatedDurationController.text.trim(),
          validityDate: valDateStr,
          workStartDate: startDateStr,
          workDescription: _workDescriptionController.text.trim(),
          termsAndConditions: _termsController.text.trim(),
          notes: _notesController.text.trim(),
          submitNow: !isDraft,
        );
        _existingQuotation = res;
      }

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            isDraft
                ? 'Quotation saved as DRAFT successfully'
                : 'Quotation SUBMITTED successfully!',
          ),
          backgroundColor: isDraft ? const Color(0xFF2563EB) : const Color(0xFF059669),
        ),
      );

      if (!isDraft) {
        Navigator.pop(context, true);
      } else {
        setState(() => _isSaving = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = e.toString();
        _isSaving = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final titleText = _isReadOnly ? 'Quotation Details' : 'Create Quotation';

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titleText,
              style: const TextStyle(
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
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: Form(
                key: _formKey,
                child: ListView(
                  padding: const EdgeInsets.all(20.0),
                  children: [
                    // Banner header
                    _buildHeaderBanner(),

                    const SizedBox(height: 18),

                    if (_errorMessage != null) _buildErrorCard(),

                    // Section 1: Scope & Description
                    _buildSectionCard(
                      title: '1. Work Scope & Description',
                      icon: Icons.description_outlined,
                      child: Column(
                        children: [
                          _buildTextField(
                            controller: _workDescriptionController,
                            label: 'Work Description / Scope',
                            hint: 'Detail the tasks, materials, and procedures to be executed...',
                            maxLines: 3,
                            readOnly: _isReadOnly,
                            validator: (v) =>
                                (v == null || v.trim().isEmpty) ? 'Please describe the work' : null,
                          ),
                          const SizedBox(height: 12),
                          _buildTextField(
                            controller: _estimatedDurationController,
                            label: 'Estimated Duration',
                            hint: 'e.g. 2 days, 4 hours',
                            readOnly: _isReadOnly,
                            validator: (v) =>
                                (v == null || v.trim().isEmpty) ? 'Required' : null,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 18),

                    // Section 2: Pricing Breakdown
                    _buildSectionCard(
                      title: '2. Professional Cost Breakdown (₹)',
                      icon: Icons.payments_outlined,
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField(
                                  controller: _labourCostController,
                                  label: 'Labour Cost (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField(
                                  controller: _materialCostController,
                                  label: 'Material Cost (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField(
                                  controller: _inspectionChargeController,
                                  label: 'Inspection Visit (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField(
                                  controller: _additionalChargesController,
                                  label: 'Additional (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField(
                                  controller: _taxAmountController,
                                  label: 'Tax Amount (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField(
                                  controller: _discountAmountController,
                                  label: 'Discount (₹)',
                                  readOnly: _isReadOnly,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 18),

                    // Section 3: Schedule & Validity
                    _buildSectionCard(
                      title: '3. Schedule & Validity',
                      icon: Icons.date_range_rounded,
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: _buildDatePickerField(
                                  label: 'Earliest Start Date',
                                  selectedDate: _workStartDate,
                                  onSelect: (d) => setState(() => _workStartDate = d),
                                  readOnly: _isReadOnly,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: _buildDatePickerField(
                                  label: 'Valid Until',
                                  selectedDate: _validityDate,
                                  onSelect: (d) => setState(() => _validityDate = d),
                                  readOnly: _isReadOnly,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          _buildTextField(
                            controller: _termsController,
                            label: 'Terms & Conditions (Optional)',
                            hint: 'Payment milestones, warranty, customer responsibilities...',
                            maxLines: 2,
                            readOnly: _isReadOnly,
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 18),

                    // Section 4: Live Cost Summary Card
                    _buildCostSummaryCard(),

                    const SizedBox(height: 24),

                    // Action buttons
                    if (!_isReadOnly) _buildActionButtons(),

                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildHeaderBanner() {
    String statusLabel = 'NEW DRAFT';
    Color statusBg = const Color(0xFFEFF6FF);
    Color statusFg = const Color(0xFF2563EB);

    if (_existingQuotation != null) {
      if (_existingQuotation!.isSubmitted) {
        statusLabel = 'SUBMITTED (READ-ONLY)';
        statusBg = const Color(0xFFECFDF5);
        statusFg = const Color(0xFF059669);
      } else if (_existingQuotation!.isDraft) {
        statusLabel = 'SAVED DRAFT';
        statusBg = const Color(0xFFFEF3C7);
        statusFg = const Color(0xFFD97706);
      }
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.serviceName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Booking Ref: ${widget.bookingNumber}',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: statusBg,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              statusLabel,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w800,
                color: statusFg,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFFEE2E2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFFCA5A5)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: Color(0xFFDC2626), size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _errorMessage!,
              style: const TextStyle(fontSize: 12, color: Color(0xFF991B1B)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
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
              Icon(icon, size: 18, color: const Color(0xFF2563EB)),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0F172A),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          child,
        ],
      ),
    );
  }

  Widget _buildCostSummaryCard() {
    return Container(
      padding: const EdgeInsets.all(18),
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
      child: Column(
        children: [
          _buildSummaryRow('Subtotal Costs', '₹${_subtotal.toStringAsFixed(0)}', Colors.white70),
          const SizedBox(height: 6),
          _buildSummaryRow('Taxes & Levies', '+ ₹${_tax.toStringAsFixed(0)}', Colors.white70),
          const SizedBox(height: 6),
          _buildSummaryRow('Discount Offered', '- ₹${_discount.toStringAsFixed(0)}', const Color(0xFF34D399)),
          const Divider(height: 20, color: Colors.white24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Total Quotation',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              Text(
                '₹${_calculatedTotal.toStringAsFixed(0)}',
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF38BDF8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, Color valueColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 13, color: Colors.white70),
        ),
        Text(
          value,
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: valueColor),
        ),
      ],
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    int maxLines = 1,
    bool readOnly = false,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          maxLines: maxLines,
          readOnly: readOnly,
          validator: validator,
          style: const TextStyle(fontSize: 14, color: Color(0xFF0F172A)),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
            filled: true,
            fillColor: readOnly ? const Color(0xFFF1F5F9) : Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildNumberField({
    required TextEditingController controller,
    required String label,
    bool readOnly = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          keyboardType: TextInputType.number,
          readOnly: readOnly,
          onChanged: (_) => setState(() {}),
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF0F172A)),
          decoration: InputDecoration(
            filled: true,
            fillColor: readOnly ? const Color(0xFFF1F5F9) : Colors.white,
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(10),
              borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDatePickerField({
    required String label,
    required DateTime? selectedDate,
    required ValueChanged<DateTime> onSelect,
    bool readOnly = false,
  }) {
    final text = selectedDate != null
        ? DateFormat('dd/MM/yyyy').format(selectedDate)
        : 'Select Date';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569)),
        ),
        const SizedBox(height: 6),
        InkWell(
          onTap: readOnly
              ? null
              : () async {
                  final picked = await showDatePicker(
                    context: context,
                    initialDate: selectedDate ?? DateTime.now(),
                    firstDate: DateTime.now(),
                    lastDate: DateTime.now().add(const Duration(days: 90)),
                  );
                  if (picked != null) onSelect(picked);
                },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            decoration: BoxDecoration(
              color: readOnly ? const Color(0xFFF1F5F9) : Colors.white,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFCBD5E1)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  text,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF0F172A)),
                ),
                const Icon(Icons.calendar_today_rounded, size: 16, color: Color(0xFF64748B)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton(
            onPressed: _isSaving ? null : () => _submitOrSave(isDraft: true),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              side: const BorderSide(color: Color(0xFF64748B)),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: _isSaving
                ? const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF64748B)),
                  )
                : const Text(
                    'Save Draft',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF475569)),
                  ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton(
            onPressed: _isSaving ? null : () => _submitOrSave(isDraft: false),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF059669),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            child: _isSaving
                ? const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Text(
                    'Submit Quotation',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
                  ),
          ),
        ),
      ],
    );
  }
}
