// File: lib/worker/verification/kyc_verification/kyc_verification_screen.dart

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_service.dart';

class WorkerKycVerificationScreen extends StatefulWidget {
  const WorkerKycVerificationScreen({super.key});

  @override
  State<WorkerKycVerificationScreen> createState() =>
      _WorkerKycVerificationScreenState();
}

class _WorkerKycVerificationScreenState
    extends State<WorkerKycVerificationScreen> {
  final _formKey = GlobalKey<FormState>();

  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _idNumberController = TextEditingController();

  String _selectedIdType = 'Aadhaar Card';
  final List<String> _idTypeOptions = [
    'Aadhaar Card',
    'PAN Card',
    'Driving License',
    'Passport',
  ];

  bool _isLoadingStatus = true;
  bool _isUploadingDocument = false;
  bool _isSubmitting = false;

  String? _status; // 'draft', 'submitted', 'under_review', 'approved', 'rejected'
  String? _rejectionReason;
  String? _uploadedDocId;
  String? _uploadedDocName;
  File? _selectedImageFile;

  @override
  void initState() {
    super.initState();
    _fetchExistingVerificationStatus();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _idNumberController.dispose();
    super.dispose();
  }

  Future<void> _fetchExistingVerificationStatus() async {
    setState(() => _isLoadingStatus = true);
    try {
      final profile = await AuthService.instance.fetchWorkerProfile();
      final data = profile['data'] as Map<String, dynamic>? ?? profile;
      if (data['full_name'] != null && _nameController.text.isEmpty) {
        _nameController.text = data['full_name'] as String;
      }
      final isVerified = data['is_verified'] == true;
      if (isVerified) {
        setState(() {
          _status = 'approved';
          _isLoadingStatus = false;
        });
        return;
      }

      final res = await ApiService.instance.get('/verification/status');
      if (res is Map<String, dynamic>) {
        final overall = res['overall_status'] as String? ?? 'draft';
        setState(() {
          _status = overall;
        });
      }

      // Check history if rejected to get reason
      if (_status == 'rejected' || _status == 'resubmission_required') {
        try {
          final history = await ApiService.instance.get('/verification/history');
          if (history is List && history.isNotEmpty) {
            final latest = history.first as Map<String, dynamic>;
            _rejectionReason = latest['review_notes'] as String?;
          }
        } catch (_) {}
      }
    } catch (_) {
      // Ignore — fallback to draft state
    } finally {
      if (mounted) setState(() => _isLoadingStatus = false);
    }
  }

  String _maskIdNumber(String input) {
    final clean = input.replaceAll(' ', '');
    if (clean.length <= 4) return clean;
    final visible = clean.substring(clean.length - 4);
    final maskedPrefix = 'X' * (clean.length - 4);
    return '$maskedPrefix$visible';
  }

  Future<void> _pickAndUploadDocument() async {
    try {
      final picker = ImagePicker();
      final XFile? pickedFile = await picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1600,
      );

      if (pickedFile == null) return;

      setState(() {
        _isUploadingDocument = true;
        _selectedImageFile = File(pickedFile.path);
        _uploadedDocName = pickedFile.name;
      });

      final String docTypeKey = _selectedIdType.toLowerCase().replaceAll(' ', '_');
      final String maskedNum = _maskIdNumber(_idNumberController.text.trim());

      final res = await ApiService.instance.uploadMultipart(
        '/verification/upload',
        pickedFile.path,
        fileField: 'file',
        fields: {
          'document_type': docTypeKey,
          if (maskedNum.isNotEmpty) 'document_number': maskedNum,
        },
      );

      if (res is Map<String, dynamic>) {
        final docId = res['document_id'] as String? ?? (res['id'] as String?);
        setState(() {
          _uploadedDocId = docId;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Identity document uploaded successfully!'),
              backgroundColor: Color(0xFF10B981),
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to upload image: $e'),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isUploadingDocument = false);
    }
  }

  Future<void> _submitVerificationRequest() async {
    if (!_formKey.currentState!.validate()) return;

    if (_uploadedDocId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please upload your identity document before submitting.'),
          backgroundColor: Color(0xFFEF4444),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);
    try {
      final legalName = _nameController.text.trim();
      final maskedNum = _maskIdNumber(_idNumberController.text.trim());

      await ApiService.instance.post('/verification/submit', {
        'verification_type': 'identity',
        'document_ids': [_uploadedDocId!],
        'notes': 'Verification submission for $legalName',
        'metadata': {
          'legal_name': legalName,
          'id_type': _selectedIdType,
          'id_number_masked': maskedNum,
        },
      });

      setState(() {
        _status = 'submitted';
      });

      if (mounted) {
        _showSubmissionDialog(context);
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.message),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to submit verification: $e'),
            backgroundColor: const Color(0xFFEF4444),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Verify Worker Account',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: _isLoadingStatus
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Status Banners if already Submitted, Approved, or Rejected
                    if (_status == 'approved') ...[
                      _buildApprovedStatusBanner(),
                      const SizedBox(height: 24),
                    ] else if (_status == 'submitted' || _status == 'under_review') ...[
                      _buildPendingStatusBanner(),
                      const SizedBox(height: 24),
                    ] else ...[
                      if (_status == 'rejected' || _status == 'resubmission_required') ...[
                        _buildRejectedStatusBanner(),
                        const SizedBox(height: 20),
                      ],
                      _buildVerificationFormCard(),
                    ],
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildApprovedStatusBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFFECFDF5),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFA7F3D0)),
      ),
      child: Column(
        children: [
          const Icon(Icons.verified_rounded, size: 56, color: Color(0xFF10B981)),
          const SizedBox(height: 12),
          const Text(
            'Your Account is Verified!',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF065F46)),
          ),
          const SizedBox(height: 8),
          const Text(
            'You are fully eligible to receive job dispatches and apply for bookings on the marketplace.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Color(0xFF047857), height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildPendingStatusBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFBEB),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFFDE68A)),
      ),
      child: Column(
        children: [
          const Icon(Icons.hourglass_top_rounded, size: 56, color: Color(0xFFD97706)),
          const SizedBox(height: 12),
          const Text(
            'Verification Under Review',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF92400E)),
          ),
          const SizedBox(height: 8),
          const Text(
            'Your identity verification request has been submitted and is currently being reviewed by our admin team. Check back soon!',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 13, color: Color(0xFFB45309), height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _buildRejectedStatusBanner() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, size: 28, color: Color(0xFFEF4444)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Verification Rejected',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF991B1B)),
                ),
                const SizedBox(height: 4),
                Text(
                  _rejectionReason != null && _rejectionReason!.isNotEmpty
                      ? 'Reason: $_rejectionReason. Please resubmit clear document photo.'
                      : 'Your previous verification attempt was rejected. Please upload valid document details.',
                  style: const TextStyle(fontSize: 12, color: Color(0xFFB91C1C)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVerificationFormCard() {
    return Form(
      key: _formKey,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.03),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Identity Verification Details',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 6),
            const Text(
              'Provide your government identity details for verification.',
              style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
            ),
            const SizedBox(height: 20),

            // Legal Full Name
            const Text('Full Legal Name', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            const SizedBox(height: 6),
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                hintText: 'Enter name as shown on ID card',
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
              ),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter your full legal name' : null,
            ),
            const SizedBox(height: 16),

            // Government ID Type Dropdown
            const Text('Government ID Type', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              initialValue: _selectedIdType,
              items: _idTypeOptions.map((opt) => DropdownMenuItem(value: opt, child: Text(opt))).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedIdType = val);
              },
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
              ),
            ),
            const SizedBox(height: 16),

            // Government ID Number
            const Text('Government ID Number', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            const SizedBox(height: 6),
            TextFormField(
              controller: _idNumberController,
              decoration: InputDecoration(
                hintText: 'e.g. 1234 5678 9012',
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: const BorderSide(color: Color(0xFFE2E8F0))),
              ),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter your ID number' : null,
            ),
            const SizedBox(height: 20),

            // Upload Document Card
            const Text('Identity Document Photo', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF334155))),
            const SizedBox(height: 8),
            InkWell(
              onTap: _isUploadingDocument ? null : _pickAndUploadDocument,
              borderRadius: BorderRadius.circular(16),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: _uploadedDocId != null ? const Color(0xFFECFDF5) : const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _uploadedDocId != null ? const Color(0xFF10B981) : const Color(0xFFCBD5E1),
                    width: 1.5,
                  ),
                ),
                child: Row(
                  children: [
                    if (_isUploadingDocument) ...[
                      const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2.5, color: Color(0xFF2563EB))),
                    ] else if (_selectedImageFile != null) ...[
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(_selectedImageFile!, width: 36, height: 36, fit: BoxFit.cover),
                      ),
                    ] else if (_uploadedDocId != null) ...[
                      const Icon(Icons.check_circle_rounded, color: Color(0xFF10B981), size: 28),
                    ] else ...[
                      const Icon(Icons.cloud_upload_outlined, color: Color(0xFF2563EB), size: 28),
                    ],
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _uploadedDocId != null ? 'Document Uploaded' : 'Upload ID Photo / Document',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _uploadedDocId != null ? const Color(0xFF065F46) : const Color(0xFF0F172A),
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _uploadedDocName ?? 'PNG, JPG or WebP image under 5MB',
                            style: TextStyle(
                              fontSize: 11,
                              color: _uploadedDocId != null ? const Color(0xFF047857) : const Color(0xFF64748B),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submitVerificationRequest,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                child: _isSubmitting
                    ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                    : const Text('Submit Verification Request', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSubmissionDialog(BuildContext context) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 72,
              height: 72,
              decoration: const BoxDecoration(
                color: Color(0xFFD1FAE5),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.verified_rounded,
                size: 40,
                color: Color(0xFF10B981),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Application Submitted!',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Your verification documents have been submitted securely. Our admin team will review your identity details.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 13,
                color: Color(0xFF64748B),
                height: 1.5,
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pop(context);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: const Text(
                  'Back to Profile',
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
