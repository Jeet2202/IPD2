// File: lib/customer/quotations/quotation_history_timeline_screen.dart

import 'package:flutter/material.dart';
import '../../models/quotation_model.dart';
import '../../services/quotation_service.dart';

class QuotationHistoryTimelineScreen extends StatefulWidget {
  final String quotationId;
  final String bookingNumber;
  final bool isCustomer;

  const QuotationHistoryTimelineScreen({
    super.key,
    required this.quotationId,
    required this.bookingNumber,
    this.isCustomer = true,
  });

  @override
  State<QuotationHistoryTimelineScreen> createState() =>
      _QuotationHistoryTimelineScreenState();
}

class _QuotationHistoryTimelineScreenState
    extends State<QuotationHistoryTimelineScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<QuotationHistoryLogItem> _logs = [];

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final list = await QuotationService.instance.fetchQuotationHistory(
        widget.quotationId,
        isCustomer: widget.isCustomer,
      );
      if (!mounted) return;
      setState(() {
        _logs = list;
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
            const Text(
              'Audit Trail & History',
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
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadHistory,
          color: const Color(0xFF2563EB),
          child: _isLoading
              ? const Center(
                  child: CircularProgressIndicator(color: Color(0xFF2563EB)),
                )
              : _errorMessage != null
                  ? _buildErrorView()
                  : _logs.isEmpty
                      ? _buildEmptyView()
                      : ListView.builder(
                          physics: const AlwaysScrollableScrollPhysics(
                            parent: BouncingScrollPhysics(),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20.0,
                            vertical: 24.0,
                          ),
                          itemCount: _logs.length,
                          itemBuilder: (context, index) {
                            final log = _logs[index];
                            final isFirst = index == 0;
                            final isLast = index == _logs.length - 1;
                            return _buildTimelineTile(log, isFirst, isLast);
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
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded,
                size: 56, color: Color(0xFFDC2626)),
            const SizedBox(height: 16),
            Text(
              _errorMessage!,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 14, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loadHistory,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
              ),
              child: const Text('Retry'),
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
        padding: const EdgeInsets.all(32.0),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history_rounded, size: 64, color: Color(0xFF94A3B8)),
            SizedBox(height: 16),
            Text(
              'No History Events Found',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: Color(0xFF0F172A),
              ),
            ),
            SizedBox(height: 8),
            Text(
              'Audit log entries for this quotation will appear here as status updates occur.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: Color(0xFF64748B)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineTile(
      QuotationHistoryLogItem log, bool isFirst, bool isLast) {
    final eventStyle = _getEventStyle(log.eventType);

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline Node & Line Column
          Column(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: eventStyle.bgColor,
                  shape: BoxShape.circle,
                  border: Border.all(color: eventStyle.fgColor, width: 2),
                ),
                child: Icon(
                  eventStyle.icon,
                  size: 18,
                  color: eventStyle.fgColor,
                ),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    color: const Color(0xFFCBD5E1),
                  ),
                ),
            ],
          ),

          const SizedBox(width: 14),

          // Event Card Box
          Expanded(
            child: Container(
              margin: const EdgeInsets.only(bottom: 20),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFE2E8F0)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.02),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title & Actor Badge Row
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        eventStyle.title,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      _buildActorBadge(log.actorRole),
                    ],
                  ),

                  const SizedBox(height: 6),

                  // Timestamp text
                  Text(
                    _formatTimestamp(log.createdAt),
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF64748B),
                    ),
                  ),

                  if (log.previousStatus != null ||
                      log.newStatus.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        if (log.previousStatus != null) ...[
                          _buildStatusPill(log.previousStatus!, isOld: true),
                          const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 6),
                            child: Icon(Icons.arrow_forward_rounded,
                                size: 14, color: Color(0xFF94A3B8)),
                          ),
                        ],
                        _buildStatusPill(log.newStatus, isOld: false),
                      ],
                    ),
                  ],

                  if (log.notes != null && log.notes!.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        log.notes!,
                        style: const TextStyle(
                          fontSize: 12,
                          color: Color(0xFF334155),
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActorBadge(String role) {
    final isCustomer = role == 'customer';
    final isWorker = role == 'worker';

    final label = isCustomer
        ? 'Customer'
        : isWorker
            ? 'Worker'
            : 'Admin';

    final bg = isCustomer
        ? const Color(0xFFEFF6FF)
        : isWorker
            ? const Color(0xFFF0FDF4)
            : const Color(0xFFF5F3FF);

    final fg = isCustomer
        ? const Color(0xFF2563EB)
        : isWorker
            ? const Color(0xFF166534)
            : const Color(0xFF7C3AED);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: fg),
      ),
    );
  }

  Widget _buildStatusPill(String status, {required bool isOld}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: isOld ? const Color(0xFFE2E8F0) : const Color(0xFFE0F2FE),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        status.toUpperCase(),
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w800,
          color: isOld ? const Color(0xFF64748B) : const Color(0xFF0369A1),
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime dt) {
    final local = dt.toLocal();
    final dateStr =
        '${local.day.toString().padLeft(2, '0')}/${local.month.toString().padLeft(2, '0')}/${local.year}';
    final timeStr =
        '${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
    return '$dateStr at $timeStr';
  }

  _EventStyle _getEventStyle(String eventType) {
    switch (eventType.toLowerCase()) {
      case 'created':
        return _EventStyle(
          title: 'Quotation Created',
          icon: Icons.note_add_rounded,
          bgColor: const Color(0xFFEFF6FF),
          fgColor: const Color(0xFF2563EB),
        );
      case 'updated':
        return _EventStyle(
          title: 'Quotation Updated',
          icon: Icons.edit_note_rounded,
          bgColor: const Color(0xFFF5F3FF),
          fgColor: const Color(0xFF7C3AED),
        );
      case 'submitted':
        return _EventStyle(
          title: 'Quotation Submitted',
          icon: Icons.send_rounded,
          bgColor: const Color(0xFFFEF3C7),
          fgColor: const Color(0xFFD97706),
        );
      case 'accepted':
        return _EventStyle(
          title: 'Quotation Accepted',
          icon: Icons.check_circle_rounded,
          bgColor: const Color(0xFFD1FAE5),
          fgColor: const Color(0xFF059669),
        );
      case 'worker_assigned':
        return _EventStyle(
          title: 'Worker Assigned',
          icon: Icons.person_add_alt_1_rounded,
          bgColor: const Color(0xFFECFDF5),
          fgColor: const Color(0xFF047857),
        );
      case 'rejected':
        return _EventStyle(
          title: 'Quotation Rejected',
          icon: Icons.cancel_rounded,
          bgColor: const Color(0xFFFEE2E2),
          fgColor: const Color(0xFFDC2626),
        );
      case 'expired':
        return _EventStyle(
          title: 'Quotation Expired',
          icon: Icons.timer_off_rounded,
          bgColor: const Color(0xFFF1F5F9),
          fgColor: const Color(0xFF64748B),
        );
      default:
        return _EventStyle(
          title: 'Event Logged',
          icon: Icons.info_outline_rounded,
          bgColor: const Color(0xFFF1F5F9),
          fgColor: const Color(0xFF475569),
        );
    }
  }
}

class _EventStyle {
  final String title;
  final IconData icon;
  final Color bgColor;
  final Color fgColor;

  _EventStyle({
    required this.title,
    required this.icon,
    required this.bgColor,
    required this.fgColor,
  });
}
