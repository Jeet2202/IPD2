// File: lib/worker/work/worker_complete_job_dialog.dart
//
// Dialog allowing workers to submit completion notes, work summary,
// and optionally attach photo URLs before marking a job complete.

import 'package:flutter/material.dart';

class WorkerCompleteJobDialog extends StatefulWidget {
  final Future<void> Function(String? notes, String? summary) onConfirm;

  const WorkerCompleteJobDialog({super.key, required this.onConfirm});

  static Future<void> show(
    BuildContext context, {
    required Future<void> Function(String? notes, String? summary) onConfirm,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => WorkerCompleteJobDialog(onConfirm: onConfirm),
    );
  }

  @override
  State<WorkerCompleteJobDialog> createState() => _WorkerCompleteJobDialogState();
}

class _WorkerCompleteJobDialogState extends State<WorkerCompleteJobDialog> {
  final _formKey = GlobalKey<FormState>();
  final _notesController = TextEditingController();
  final _summaryController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _notesController.dispose();
    _summaryController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSubmitting = true);
    try {
      await widget.onConfirm(
        _notesController.text.trim().isEmpty ? null : _notesController.text.trim(),
        _summaryController.text.trim().isEmpty ? null : _summaryController.text.trim(),
      );
      if (mounted) Navigator.pop(context);
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottom = MediaQuery.of(context).viewInsets.bottom;
    return Container(
      margin: EdgeInsets.only(bottom: bottom),
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: const Color(0xFFCBD5E1),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Title
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.teal.shade50,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(Icons.task_alt_rounded, color: Colors.teal.shade700, size: 22),
                ),
                const SizedBox(width: 12),
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Complete Work',
                      style: TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 17,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    Text(
                      'Customer will be asked to confirm.',
                      style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Completion Notes
            TextFormField(
              controller: _notesController,
              maxLines: 3,
              decoration: InputDecoration(
                labelText: 'Completion Notes (optional)',
                hintText: 'Any observations, issues, or notes...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.teal.shade600, width: 1.5),
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Work Summary
            TextFormField(
              controller: _summaryController,
              maxLines: 2,
              decoration: InputDecoration(
                labelText: 'Work Summary (optional)',
                hintText: 'Brief description of work performed...',
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.teal.shade600, width: 1.5),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Submit Button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _submit,
                icon: _isSubmitting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.check_circle_rounded, size: 20),
                label: Text(
                  _isSubmitting ? 'Submitting...' : 'Mark as Completed',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal.shade600,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                  elevation: 0,
                ),
              ),
            ),
            const SizedBox(height: 8),
            // Cancel
            Center(
              child: TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
