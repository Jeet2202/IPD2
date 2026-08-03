// File: lib/services/quotation_service.dart

import '../models/quotation_model.dart';
import 'api_service.dart';

class QuotationService {
  QuotationService._privateConstructor();
  static final QuotationService instance = QuotationService._privateConstructor();

  /// Create a new draft or submitted quotation
  Future<QuotationItem> createQuotation({
    required String bookingId,
    required String applicationId,
    required double labourCost,
    double materialCost = 0.0,
    double inspectionCharge = 0.0,
    double additionalCharges = 0.0,
    double taxAmount = 0.0,
    double discountAmount = 0.0,
    required String estimatedDuration,
    required String validityDate,
    String? workStartDate,
    String? workDescription,
    String? termsAndConditions,
    String? notes,
    bool isDraft = false,
  }) async {
    final body = <String, dynamic>{
      'booking_id': bookingId,
      'application_id': applicationId,
      'labour_cost': labourCost,
      'material_cost': materialCost,
      'inspection_charge': inspectionCharge,
      'additional_charges': additionalCharges,
      'tax_amount': taxAmount,
      'discount_amount': discountAmount,
      'estimated_duration': estimatedDuration,
      'validity_date': validityDate,
      'is_draft': isDraft,
    };

    if (workStartDate != null && workStartDate.isNotEmpty) {
      body['work_start_date'] = workStartDate;
    }
    if (workDescription != null && workDescription.isNotEmpty) {
      body['work_description'] = workDescription;
    }
    if (termsAndConditions != null && termsAndConditions.isNotEmpty) {
      body['terms_and_conditions'] = termsAndConditions;
    }
    if (notes != null && notes.isNotEmpty) {
      body['notes'] = notes;
    }

    final res = await ApiService.instance.post(
      '/quotations',
      body,
    );

    return QuotationItem.fromJson(res);
  }

  /// Update an existing draft quotation or submit it
  Future<QuotationItem> updateQuotation({
    required String quotationId,
    double? labourCost,
    double? materialCost,
    double? inspectionCharge,
    double? additionalCharges,
    double? taxAmount,
    double? discountAmount,
    String? estimatedDuration,
    String? validityDate,
    String? workStartDate,
    String? workDescription,
    String? termsAndConditions,
    String? notes,
    bool submitNow = false,
  }) async {
    final body = <String, dynamic>{
      'submit_now': submitNow,
    };

    if (labourCost != null) body['labour_cost'] = labourCost;
    if (materialCost != null) body['material_cost'] = materialCost;
    if (inspectionCharge != null) body['inspection_charge'] = inspectionCharge;
    if (additionalCharges != null) body['additional_charges'] = additionalCharges;
    if (taxAmount != null) body['tax_amount'] = taxAmount;
    if (discountAmount != null) body['discount_amount'] = discountAmount;
    if (estimatedDuration != null) body['estimated_duration'] = estimatedDuration;
    if (validityDate != null) body['validity_date'] = validityDate;
    if (workStartDate != null) body['work_start_date'] = workStartDate;
    if (workDescription != null) body['work_description'] = workDescription;
    if (termsAndConditions != null) body['terms_and_conditions'] = termsAndConditions;
    if (notes != null) body['notes'] = notes;

    final res = await ApiService.instance.put(
      '/quotations/$quotationId',
      body,
    );

    return QuotationItem.fromJson(res);
  }

  /// Fetch existing quotation for a job application
  Future<QuotationItem?> fetchQuotationByApplication(String applicationId) async {
    try {
      final res = await ApiService.instance.get(
        '/quotations/application/$applicationId',
      );
      if (res.isEmpty) return null;
      return QuotationItem.fromJson(res);
    } catch (_) {
      return null;
    }
  }

  /// Fetch quotation details by quotation ID
  Future<QuotationItem> fetchQuotationDetail(String quotationId) async {
    final res = await ApiService.instance.get(
      '/quotations/$quotationId',
    );
    return QuotationItem.fromJson(res);
  }

  /// Fetch all submitted worker quotations for a customer booking
  Future<List<CustomerQuotationItem>> fetchCustomerBookingQuotations(String bookingId) async {
    final dynamic res = await ApiService.instance.get(
      '/customer/bookings/$bookingId/quotations',
    );
    final List<dynamic> rawList = (res is List)
        ? res
        : (res is Map && res['items'] is List)
            ? res['items'] as List
            : [];
    return rawList
        .map((e) => CustomerQuotationItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Fetch customer quotation details including worker profile
  Future<CustomerQuotationItem> fetchCustomerQuotationDetail(String quotationId) async {
    final dynamic res = await ApiService.instance.get(
      '/customer/quotations/$quotationId',
    );
    return CustomerQuotationItem.fromJson(res as Map<String, dynamic>);
  }

  /// Accept worker quotation and assign booking
  Future<Map<String, dynamic>> acceptQuotation(String quotationId) async {
    final dynamic res = await ApiService.instance.post(
      '/customer/quotations/$quotationId/accept',
      {},
    );
    return res as Map<String, dynamic>;
  }

  /// Reject worker quotation
  Future<CustomerQuotationItem> rejectQuotation(String quotationId) async {
    final dynamic res = await ApiService.instance.post(
      '/customer/quotations/$quotationId/reject',
      {},
    );
    return CustomerQuotationItem.fromJson(res as Map<String, dynamic>);
  }

  /// Fetch assigned worker details for a customer booking
  Future<Map<String, dynamic>?> fetchAssignedWorker(String bookingId) async {
    try {
      final dynamic res = await ApiService.instance.get(
        '/customer/bookings/$bookingId/assigned-worker',
      );
      return res as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  /// Fetch read-only audit trail history for a quotation
  Future<List<QuotationHistoryLogItem>> fetchQuotationHistory(
    String quotationId, {
    bool isCustomer = true,
  }) async {
    final endpoint = isCustomer
        ? '/customer/quotations/$quotationId/history'
        : '/worker/quotations/$quotationId/history';
    final dynamic res = await ApiService.instance.get(endpoint);

    final List<dynamic> rawList = (res is List)
        ? res
        : (res is Map && res['items'] is List)
            ? res['items'] as List
            : [];

    return rawList
        .map((e) => QuotationHistoryLogItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
