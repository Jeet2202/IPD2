// File: lib/customer/support/raise_complaint/raise_complaint_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../models/booking_model.dart';
import '../../../services/booking_service.dart';
import '../../../services/support_service.dart';
import '../../../l10n/app_translations.dart';

class RaiseComplaintScreen extends StatefulWidget {
  const RaiseComplaintScreen({super.key});

  @override
  State<RaiseComplaintScreen> createState() => _RaiseComplaintScreenState();
}

class _RaiseComplaintScreenState extends State<RaiseComplaintScreen> {
  final SupportService _supportService = SupportService.instance;
  final BookingService _bookingService = BookingService.instance;

  final TextEditingController _subjectController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  bool _isLoading = true;
  bool _isSubmitting = false;

  List<BookingModel> _userBookings = [];
  BookingModel? _selectedBooking;
  bool _noBookingSelected = false;

  List<String> _categories = [
    'Technician Behavior',
    'Overcharging / Price Mismatch',
    'Unsatisfactory Work Quality',
    'Damage Caused During Repair',
    'Delay in Arrival',
    'General Query',
  ];
  String _selectedCategory = 'General Query';

  String _priority = 'medium';

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  @override
  void dispose() {
    _subjectController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        _bookingService.fetchBookings(),
        _supportService.fetchSupportCategories(),
      ]);

      final bookings = results[0] as List<BookingModel>;
      final catMap = results[1] as Map<String, List<String>>;

      final ticketCats = catMap['ticket_categories'] ?? [];
      if (ticketCats.isNotEmpty) {
        _categories = ticketCats;
        _selectedCategory = ticketCats.first;
      }

      setState(() {
        _userBookings = bookings;
        if (bookings.isNotEmpty) {
          _selectedBooking = bookings.first;
        } else {
          _noBookingSelected = true;
        }
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _submitTicket() async {
    final subject = _subjectController.text.trim();
    final description = _descriptionController.text.trim();

    if (subject.isEmpty) {
      _showSnackBar('Please enter a brief subject for your ticket.');
      return;
    }
    if (description.isEmpty) {
      _showSnackBar('Please explain your issue in detail.');
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final ticket = await _supportService.createTicket(
        subject: subject,
        description: description,
        category: _selectedCategory,
        priority: _priority,
        bookingId: _noBookingSelected ? null : _selectedBooking?.id,
      );

      if (!mounted) return;
      _showSnackBar('Support Ticket #${ticket.ticketId} created successfully!');

      // Navigate straight to Live Chat thread with Admin
      Navigator.pushReplacementNamed(
        context,
        AppRoutes.liveChat,
        arguments: {'ticketId': ticket.ticketId},
      );
    } catch (e) {
      setState(() => _isSubmitting = false);
      _showSnackBar('Failed to submit ticket. Please check backend connection.');
    }
  }

  void _showSnackBar(String text) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(text), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text('raise_a_complaint_ticket'.tr(context),
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: _isLoading
            ? Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
            : SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                padding: EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Select Related Booking ─────────────────────────────
                    Text('related_booking_optional'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    SizedBox(height: 6),

                    if (_userBookings.isEmpty)
                      Container(
                        padding: EdgeInsets.all(14),
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFCBD5E1)),
                        ),
                        child: Text('no_recent_bookings_found_raising'.tr(context),
                          style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                        ),
                      )
                    else
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFCBD5E1)),
                        ),
                        child: DropdownButtonHideUnderline(
                          child: DropdownButton<BookingModel?>(
                            value: _noBookingSelected ? null : _selectedBooking,
                            isExpanded: true,
                            hint: Text('none_general_query'.tr(context), style: TextStyle(fontSize: 13)),
                            items: [
                              const DropdownMenuItem<BookingModel?>(
                                value: null,
                                child: Text('none_general_query'.tr(context), style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                              ),
                              ..._userBookings.map((b) => DropdownMenuItem<BookingModel?>(
                                    value: b,
                                    child: Text(
                                      '#${b.bookingNumber.isNotEmpty ? b.bookingNumber : b.id.substring(0, 8)} • ${b.serviceSnapshot.name.isNotEmpty ? b.serviceSnapshot.name : "Service"}',
                                      style: TextStyle(fontSize: 13),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  )),
                            ],
                            onChanged: (val) {
                              setState(() {
                                if (val == null) {
                                  _noBookingSelected = true;
                                  _selectedBooking = null;
                                } else {
                                  _noBookingSelected = false;
                                  _selectedBooking = val;
                                }
                              });
                            },
                          ),
                        ),
                      ),

                    SizedBox(height: 16),

                    // ── Complaint Category ──────────────────────────────────
                    Text('ticket_category'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    SizedBox(height: 6),
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFCBD5E1)),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _selectedCategory,
                          isExpanded: true,
                          items: _categories
                              .map((c) => DropdownMenuItem(value: c, child: Text(c, style: TextStyle(fontSize: 13))))
                              .toList(),
                          onChanged: (val) => setState(() => _selectedCategory = val!),
                        ),
                      ),
                    ),

                    SizedBox(height: 16),

                    // ── Priority Chips ──────────────────────────────────────
                    Text('priority_level'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    SizedBox(height: 8),

                    Row(
                      children: [
                        _buildPriorityChip('Low', 'low'),
                        _buildPriorityChip('Medium', 'medium'),
                        _buildPriorityChip('High / Urgent', 'high'),
                      ],
                    ),

                    SizedBox(height: 16),

                    // ── Subject ─────────────────────────────────────────────
                    Text('ticket_subject'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    SizedBox(height: 6),
                    TextField(
                      controller: _subjectController,
                      decoration: InputDecoration(
                        hintText: 'Brief summary of your issue...',
                        fillColor: Colors.white,
                        filled: true,
                        contentPadding: EdgeInsets.all(14),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
                        ),
                      ),
                    ),

                    SizedBox(height: 16),

                    // ── Description ─────────────────────────────────────────
                    Text('detailed_description'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF0F172A))),
                    SizedBox(height: 6),
                    TextField(
                      controller: _descriptionController,
                      maxLines: 5,
                      decoration: InputDecoration(
                        hintText: 'Explain what happened in detail so support admin can assist you...',
                        fillColor: Colors.white,
                        filled: true,
                        contentPadding: EdgeInsets.all(14),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(16),
                          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
                        ),
                      ),
                    ),

                    SizedBox(height: 28),

                    // ── Submit Button ───────────────────────────────────────
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: ElevatedButton(
                        onPressed: _isSubmitting ? null : _submitTicket,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        ),
                        child: _isSubmitting
                            ? SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                              )
                            : Text('submit_ticket_start_admin_chat'.tr(context), style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                      ),
                    ),

                    SizedBox(height: 24),
                  ],
                ),
              ),
      ),
    );
  }

  Widget _buildPriorityChip(String label, String value) {
    final isSelected = _priority == value;
    return Padding(
      padding: EdgeInsets.only(right: 8.0),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        selectedColor: const Color(0xFF2563EB),
        labelStyle: TextStyle(
          fontSize: 12,
          fontWeight: isSelected ? FontWeight.w800 : FontWeight.w500,
          color: isSelected ? Colors.white : const Color(0xFF475569),
        ),
        onSelected: (_) => setState(() => _priority = value),
      ),
    );
  }
}
