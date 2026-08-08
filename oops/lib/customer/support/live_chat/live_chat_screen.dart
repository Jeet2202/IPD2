// File: lib/customer/support/live_chat/live_chat_screen.dart

import 'dart:async';
import 'package:flutter/material.dart';
import '../../../models/support_model.dart';
import '../../../services/support_service.dart';
import '../../../l10n/app_translations.dart';

class LiveChatScreen extends StatefulWidget {
  const LiveChatScreen({super.key});

  @override
  State<LiveChatScreen> createState() => _LiveChatScreenState();
}

class _LiveChatScreenState extends State<LiveChatScreen> {
  final SupportService _supportService = SupportService.instance;
  final TextEditingController _msgController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool _isLoading = true;
  bool _isSending = false;

  SupportTicketModel? _ticket;
  Timer? _pollTimer;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_ticket == null) {
      _initTicket();
    }
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _msgController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _initTicket() async {
    final args = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
    final ticketId = args?['ticketId'] as String?;

    if (ticketId != null && ticketId.isNotEmpty) {
      await _fetchTicketDetails(ticketId);
    } else {
      // Find latest ticket from user
      try {
        final tickets = await _supportService.fetchUserTickets();
        if (tickets.isNotEmpty) {
          final open = tickets.firstWhere((t) => t.isOpen, orElse: () => tickets.first);
          await _fetchTicketDetails(open.ticketId);
        } else {
          setState(() {
            _isLoading = false;
          });
        }
      } catch (_) {
        setState(() => _isLoading = false);
      }
    }

    // Poll for admin replies every 4 seconds
    _pollTimer = Timer.periodic(const Duration(seconds: 4), (_) {
      if (_ticket != null) {
        _silentRefreshTicket(_ticket!.ticketId);
      }
    });
  }

  Future<void> _fetchTicketDetails(String ticketId) async {
    try {
      final t = await _supportService.fetchTicketById(ticketId);
      setState(() {
        _ticket = t;
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _silentRefreshTicket(String ticketId) async {
    try {
      final t = await _supportService.fetchTicketById(ticketId);
      if (t.responses.length != _ticket?.responses.length) {
        setState(() {
          _ticket = t;
        });
        _scrollToBottom();
      }
    } catch (_) {}
  }

  Future<void> _sendMessage() async {
    final text = _msgController.text.trim();
    if (text.isEmpty || _ticket == null || _isSending) return;

    setState(() => _isSending = true);
    _msgController.clear();

    try {
      final updatedTicket = await _supportService.replyToTicket(
        ticketId: _ticket!.ticketId,
        message: text,
      );

      setState(() {
        _ticket = updatedTicket;
        _isSending = false;
      });
      _scrollToBottom();
    } catch (e) {
      setState(() => _isSending = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('failed_to_send_message_please'.tr(context))),
      );
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final ticket = _ticket;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: Color(0xFFDCFCE7),
              child: Icon(Icons.support_agent_rounded, color: Color(0xFF16A34A), size: 22),
            ),
            SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    ticket != null ? 'Support (#${ticket.ticketId})' : 'Ally Support Agent',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    ticket != null ? 'Status: ${ticket.status.toUpperCase()}' : 'Connecting...',
                    style: TextStyle(fontSize: 10, color: Color(0xFF16A34A), fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : ticket == null
              ? Center(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.mark_email_read_outlined, size: 54, color: Color(0xFF94A3B8)),
                        SizedBox(height: 16),
                        Text('no_active_ticket_found'.tr(context),
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
                        ),
                        SizedBox(height: 6),
                        Text('submit_a_ticket_to_start'.tr(context),
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                        SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () => Navigator.pushReplacementNamed(context, '/customer/support/raise-complaint'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: Text('raise_a_complaint_ticket'.tr(context)),
                        ),
                      ],
                    ),
                  ),
                )
              : Column(
                  children: [
                    // Ticket Subject Banner
                    Container(
                      width: double.infinity,
                      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                      color: ticket.isOpen ? const Color(0xFFEFF6FF) : const Color(0xFFDCFCE7),
                      child: Row(
                        children: [
                          Icon(
                            ticket.isOpen ? Icons.info_outline_rounded : Icons.check_circle_rounded,
                            color: ticket.isOpen ? const Color(0xFF2563EB) : const Color(0xFF16A34A),
                            size: 18,
                          ),
                          SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              ticket.isOpen
                                  ? '${ticket.category}: ${ticket.subject}'
                                  : 'Ticket Resolved: ${ticket.subject}',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: ticket.isOpen ? const Color(0xFF1E40AF) : const Color(0xFF15803D),
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Messages List
                    Expanded(
                      child: ListView(
                        controller: _scrollController,
                        padding: EdgeInsets.all(16),
                        physics: const BouncingScrollPhysics(),
                        children: [
                          // First message: Ticket Description
                          _buildChatBubble(
                            text: ticket.description,
                            time: ticket.createdAt.length >= 16 ? ticket.createdAt.substring(0, 16) : ticket.createdAt,
                            isAgent: false,
                            senderLabel: 'You (Original Issue)',
                          ),

                          // Subsequent responses
                          ...ticket.responses.map((resp) {
                            final isAgent = resp.isAdminMessage;
                            final senderName = isAgent ? 'Priya (Ally Admin Support)' : 'You';
                            return _buildChatBubble(
                              text: resp.message,
                              time: resp.createdAt.length >= 16 ? resp.createdAt.substring(0, 16) : resp.createdAt,
                              isAgent: isAgent,
                              senderLabel: senderName,
                            );
                          }),
                        ],
                      ),
                    ),

                    // Input Box
                    Container(
                      padding: EdgeInsets.fromLTRB(16, 8, 16, 16),
                      color: Colors.white,
                      child: Row(
                        children: [
                          Expanded(
                            child: Container(
                              padding: EdgeInsets.symmetric(horizontal: 16),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF1F5F9),
                                borderRadius: BorderRadius.circular(24),
                              ),
                              child: TextField(
                                controller: _msgController,
                                onSubmitted: (_) => _sendMessage(),
                                decoration: const InputDecoration(
                                  hintText: 'Type your message to admin...',
                                  hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                                  border: InputBorder.none,
                                ),
                              ),
                            ),
                          ),
                          SizedBox(width: 8),
                          CircleAvatar(
                            backgroundColor: const Color(0xFF2563EB),
                            child: IconButton(
                              icon: _isSending
                                  ? SizedBox(
                                      height: 16,
                                      width: 16,
                                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                    )
                                  : Icon(Icons.send_rounded, color: Colors.white, size: 18),
                              onPressed: _sendMessage,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }

  Widget _buildChatBubble({
    required String text,
    required String time,
    required bool isAgent,
    required String senderLabel,
  }) {
    return Align(
      alignment: isAgent ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        margin: EdgeInsets.only(bottom: 12),
        padding: EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isAgent ? Colors.white : const Color(0xFF2563EB),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(18),
            topRight: const Radius.circular(18),
            bottomLeft: Radius.circular(isAgent ? 4 : 18),
            bottomRight: Radius.circular(isAgent ? 18 : 4),
          ),
          border: isAgent ? Border.all(color: const Color(0xFFE2E8F0)) : null,
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 8, offset: const Offset(0, 2)),
          ],
        ),
        child: Column(
          crossAxisAlignment: isAgent ? CrossAxisAlignment.start : CrossAxisAlignment.end,
          children: [
            Text(
              senderLabel,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w800,
                color: isAgent ? const Color(0xFF2563EB) : const Color(0xFFDBEAFE),
              ),
            ),
            SizedBox(height: 4),
            Text(
              text,
              style: TextStyle(fontSize: 13, color: isAgent ? const Color(0xFF0F172A) : Colors.white, height: 1.4),
            ),
            SizedBox(height: 4),
            Text(
              time,
              style: TextStyle(fontSize: 9, color: isAgent ? const Color(0xFF94A3B8) : const Color(0xFFBFDBFE)),
            ),
          ],
        ),
      ),
    );
  }
}
