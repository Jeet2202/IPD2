import 'dart:async';
import 'package:flutter/material.dart';
import '../../models/job_application_model.dart';
import '../../services/job_application_service.dart';
import '../quotations/quotation_form_screen.dart';
import '../../l10n/app_translations.dart';

class WorkerApplicationsScreen extends StatefulWidget {
  const WorkerApplicationsScreen({super.key});

  @override
  State<WorkerApplicationsScreen> createState() => _WorkerApplicationsScreenState();
}

class _WorkerApplicationsScreenState extends State<WorkerApplicationsScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<JobApplicationItem> _applications = [];
  int _totalApplications = 0;
  Timer? _autoRefreshTimer;

  @override
  void initState() {
    super.initState();
    _loadApplications();
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _loadApplications(isSilent: true);
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadApplications({bool isSilent = false}) async {
    if (!mounted) return;

    if (!isSilent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final result = await JobApplicationService.instance.fetchWorkerApplications(
        page: 1,
        pageSize: 50,
      );

      if (!mounted) return;

      setState(() {
        _applications = result.items;
        _totalApplications = result.total;
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
    return Scaffold(      appBar: AppBar(        elevation: 0,
        title: Text(
          'my_applications'.tr(context),
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0F172A),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF64748B)),
            onPressed: _loadApplications,
            tooltip: 'Refresh Applications',
          ),
        ],
      ),
      body: SafeArea(
        child: RefreshIndicator(
          color: const Color(0xFF2563EB),
          onRefresh: _loadApplications,
          child: _buildBodyContent(),
        ),
      ),
    );
  }

  Widget _buildBodyContent() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(color: Color(0xFF2563EB)),
      );
    }

    if (_errorMessage != null) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.2),
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline_rounded, size: 52, color: Color(0xFFEF4444)),
                  const SizedBox(height: 16),
                  Text(
                    'failed_to_load_applications'.tr(context),
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _errorMessage!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: _loadApplications,
                    icon: const Icon(Icons.refresh_rounded, size: 18),
                    label: Text('try_again'.tr(context)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    if (_applications.isEmpty) {
      return ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        children: [
          SizedBox(height: MediaQuery.of(context).size.height * 0.2),
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: const BoxDecoration(
                      color: Color(0xFFF1F5F9),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.assignment_outlined,
                      size: 44,
                      color: Color(0xFF64748B),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'no_job_applications_yet'.tr(context),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'no_job_applications_desc'.tr(context),
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 13,
                      color: Color(0xFF64748B),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(20.0),
      physics: const AlwaysScrollableScrollPhysics(),
      itemCount: _applications.length,
      itemBuilder: (context, index) {
        final item = _applications[index];
        return _buildApplicationCard(item);
      },
    );
  }

  Widget _buildApplicationCard(JobApplicationItem item) {
    Color statusBg = const Color(0xFFFEF3C7);
    Color statusFg = const Color(0xFFD97706);
    String statusText = 'pending_review'.tr(context);

    if (item.isAccepted) {
      statusBg = const Color(0xFFD1FAE5);
      statusFg = const Color(0xFF059669);
      statusText = 'selected'.tr(context);
    } else if (item.isRejected) {
      statusBg = const Color(0xFFFEE2E2);
      statusFg = const Color(0xFFDC2626);
      statusText = 'rejected'.tr(context);
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Row: Service Name & Status Badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  item.serviceName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusBg,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  statusText,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: statusFg,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          // Booking Ref Number
          Text(
            '${'ref_prefix'.tr(context)}${item.bookingNumber}',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Color(0xFF64748B),
            ),
          ),

          const SizedBox(height: 12),
          const Divider(height: 1, color: Color(0xFFF1F5F9)),
          const SizedBox(height: 12),

          if (item.isAccepted) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFECFDF5),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFA7F3D0)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.emoji_events_rounded, color: Color(0xFF059669), size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'congrats_selected'.tr(context),
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF047857),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
          ],

          // Info Grid: Applied Date & Scheduled Date
          Row(
            children: [
              Expanded(
                child: Row(
                  children: [
                    const Icon(Icons.send_rounded, size: 14, color: Color(0xFF64748B)),
                    const SizedBox(width: 6),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'applied_on'.tr(context),
                          style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                        ),
                        Text(
                          '${item.appliedAt.day}/${item.appliedAt.month}/${item.appliedAt.year}',
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF334155),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today_rounded, size: 14, color: Color(0xFF64748B)),
                    const SizedBox(width: 6),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'scheduled_date'.tr(context),
                          style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                        ),
                        Text(
                          item.scheduledDate ?? 'on_demand'.tr(context),
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF334155),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),

          // Optional Cover Letter
          if (item.coverLetter != null && item.coverLetter!.isNotEmpty) ...[
            const SizedBox(height: 10),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                '"${item.coverLetter}"',
                style: const TextStyle(
                  fontSize: 11,
                  fontStyle: FontStyle.italic,
                  color: Color(0xFF475569),
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],

          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () async {
                final refresh = await Navigator.push<bool>(
                  context,
                  MaterialPageRoute(
                    builder: (context) => QuotationFormScreen(
                      bookingId: item.bookingId,
                      applicationId: item.id,
                      bookingNumber: item.bookingNumber,
                      serviceName: item.serviceName,
                    ),
                  ),
                );
                if (refresh == true) {
                  _loadApplications();
                }
              },
              icon: const Icon(Icons.request_quote_rounded, size: 18),
              label: Text('manage_quotation'.tr(context)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0F172A),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 10),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
