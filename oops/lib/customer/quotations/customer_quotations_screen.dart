import 'dart:async';
import 'package:flutter/material.dart';
import '../../models/quotation_model.dart';
import '../../services/quotation_service.dart';
import '../../l10n/app_translations.dart';
import '../../widgets/language_selector_widget.dart';
import 'customer_quotation_detail_screen.dart';
import 'quotation_comparison_screen.dart';

class CustomerQuotationsScreen extends StatefulWidget {
  final String bookingId;
  final String bookingNumber;

  const CustomerQuotationsScreen({
    super.key,
    required this.bookingId,
    required this.bookingNumber,
  });

  @override
  State<CustomerQuotationsScreen> createState() => _CustomerQuotationsScreenState();
}

class _CustomerQuotationsScreenState extends State<CustomerQuotationsScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<CustomerQuotationItem> _quotations = [];
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _loadQuotations();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _loadQuotations(isSilent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadQuotations({bool isSilent = false}) async {
    if (!isSilent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final list = await QuotationService.instance
          .fetchCustomerBookingQuotations(widget.bookingId);
      if (!mounted) return;
      setState(() {
        _quotations = list;
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
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('receivedquotations'.tr(context).tr(context),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            Text(
              'Booking Ref: ${widget.bookingNumber}',
              style: TextStyle(fontSize: 11, color: Color(0xFF64748B)),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
          if (_quotations.length >= 2)
            Padding(
              padding: EdgeInsets.only(right: 12),
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => QuotationComparisonScreen(
                        bookingNumber: widget.bookingNumber,
                        quotations: _quotations,
                      ),
                    ),
                  );
                },
                icon: Icon(Icons.compare_arrows_rounded, size: 16),
                label: Text('compare'.tr(context).tr(context)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadQuotations,
          color: const Color(0xFF2563EB),
          child: _isLoading
              ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
              : _errorMessage != null
                  ? _buildErrorView()
                  : _quotations.isEmpty
                      ? _buildEmptyView()
                      : ListView.builder(
                          physics: const AlwaysScrollableScrollPhysics(
                            parent: BouncingScrollPhysics(),
                          ),
                          padding: EdgeInsets.all(20.0),
                          itemCount: _quotations.length,
                          itemBuilder: (context, index) {
                            return _buildQuotationCard(_quotations[index]);
                          },
                        ),
        ),
      ),
    );
  }

  Widget _buildErrorView() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: Container(
        height: MediaQuery.of(context).size.height * 0.7,
        alignment: Alignment.center,
        padding: EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline_rounded, size: 56, color: Color(0xFFDC2626)),
            SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 14, color: Color(0xFF64748B)),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loadQuotations,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
              ),
              child: Text('retry'.tr(context)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyView() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: Container(
        height: MediaQuery.of(context).size.height * 0.7,
        alignment: Alignment.center,
        padding: EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.request_quote_outlined, size: 64, color: Color(0xFF94A3B8)),
            SizedBox(height: 16),
            Text('no_quotations_received_yet'.tr(context),
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Color(0xFF0F172A)),
            ),
            SizedBox(height: 8),
            Text('workers_who_applied_for_your'.tr(context),
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuotationCard(CustomerQuotationItem item) {
    final q = item.quotation;
    final w = item.worker;

    return Container(
      margin: EdgeInsets.only(bottom: 16),
      padding: EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Worker Profile Header Row
          Row(
            children: [
              CircleAvatar(
                radius: 22,
                backgroundColor: const Color(0xFFEFF6FF),
                backgroundImage: w.profilePhotoUrl != null ? NetworkImage(w.profilePhotoUrl!) : null,
                child: w.profilePhotoUrl == null
                    ? Text(
                        w.fullName.isNotEmpty ? w.fullName[0].toUpperCase() : 'W',
                        style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF2563EB)),
                      )
                    : null,
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      w.fullName,
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    SizedBox(height: 2),
                    Row(
                      children: [
                        Icon(Icons.star_rounded, size: 14, color: Color(0xFFEAB308)),
                        SizedBox(width: 4),
                        Text(
                          w.rating.toStringAsFixed(1),
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                        ),
                        SizedBox(width: 8),
                        Text(
                          '•  ${w.experienceYears.toStringAsFixed(0)} yrs exp',
                          style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  q.quotationNumber,
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: Color(0xFF475569)),
                ),
              ),
            ],
          ),

          SizedBox(height: 14),

          // Total Price Callout Box
          Container(
            padding: EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF0FDF4),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFBBF7D0)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('total_price'.tr(context),
                      style: TextStyle(fontSize: 11, color: Color(0xFF166534)),
                    ),
                    Text(
                      '₹${q.totalAmount.toStringAsFixed(0)}',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        color: Color(0xFF15803D),
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      'Est. Duration: ${q.estimatedDuration}',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF166534)),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Valid: ${q.validityDate}',
                      style: TextStyle(fontSize: 11, color: Color(0xFF15803D)),
                    ),
                  ],
                ),
              ],
            ),
          ),

          if (q.workDescription != null && q.workDescription!.isNotEmpty) ...[
            SizedBox(height: 12),
            Text(
              q.workDescription!,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(fontSize: 12, color: Color(0xFF475569), height: 1.4),
            ),
          ],

          SizedBox(height: 14),

          // Details Action Button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () async {
                final accepted = await Navigator.push<bool>(
                  context,
                  MaterialPageRoute(
                    builder: (context) => CustomerQuotationDetailScreen(
                      quotationId: q.id,
                      bookingNumber: widget.bookingNumber,
                      initialItem: item,
                    ),
                  ),
                );
                if (accepted == true && mounted) {
                  Navigator.pop(context, true);
                } else {
                  _loadQuotations();
                }
              },
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Color(0xFF2563EB)),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
                padding: EdgeInsets.symmetric(vertical: 10),
              ),
              child: Text('view_detailed_quotation'.tr(context),
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF2563EB)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
