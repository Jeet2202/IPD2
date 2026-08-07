import 'package:flutter/material.dart';
import '../l10n/app_translations.dart';

class ReviewDialog extends StatefulWidget {
  final String bookingId;
  final Function(
    double overall,
    double punctuality,
    double quality,
    double professionalism,
    double communication,
    String? title,
    String? comment,
    bool recommend,
  ) onSubmit;

  const ReviewDialog({
    super.key,
    required this.bookingId,
    required this.onSubmit,
  });

  static Future<void> show(
    BuildContext context, {
    required String bookingId,
    required Function(
      double overall,
      double punctuality,
      double quality,
      double professionalism,
      double communication,
      String? title,
      String? comment,
      bool recommend,
    ) onSubmit,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom,
        ),
        child: ReviewDialog(bookingId: bookingId, onSubmit: onSubmit),
      ),
    );
  }

  @override
  State<ReviewDialog> createState() => _ReviewDialogState();
}

class _ReviewDialogState extends State<ReviewDialog> {
  double _overall = 5.0;
  double _punctuality = 5.0;
  double _quality = 5.0;
  double _professionalism = 5.0;
  double _communication = 5.0;
  bool _wouldRecommend = true;

  final _titleController = TextEditingController();
  final _commentController = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _titleController.dispose();
    _commentController.dispose();
    super.dispose();
  }

  Widget _buildStarRating(String label, double rating, Function(double) onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
          Row(
            children: List.generate(5, (index) {
              final starVal = (index + 1).toDouble();
              return IconButton(
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                icon: Icon(
                  starVal <= rating ? Icons.star_rounded : Icons.star_outline_rounded,
                  color: Colors.amber,
                  size: 24,
                ),
                onPressed: () => onChanged(starVal),
              );
            }),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'rate_review_worker'.tr(context),
            style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            'Your feedback helps maintain quality standards.',
            style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey.shade600),
          ),
          const SizedBox(height: 16),
          _buildStarRating('Overall Rating', _overall, (val) => setState(() => _overall = val)),
          const Divider(),
          _buildStarRating('Punctuality', _punctuality, (val) => setState(() => _punctuality = val)),
          _buildStarRating('Quality of Work', _quality, (val) => setState(() => _quality = val)),
          _buildStarRating('Professionalism', _professionalism, (val) => setState(() => _professionalism = val)),
          _buildStarRating('Communication', _communication, (val) => setState(() => _communication = val)),
          const SizedBox(height: 12),
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(
              labelText: 'Review Title (Optional)',
              border: OutlineInputBorder(),
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _commentController,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'Feedback Comment (Optional)',
              border: OutlineInputBorder(),
              contentPadding: EdgeInsets.all(12),
            ),
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Would recommend this worker to others'),
            value: _wouldRecommend,
            onChanged: (val) => setState(() => _wouldRecommend = val),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _submitting
                  ? null
                  : () async {
                      setState(() => _submitting = true);
                      await widget.onSubmit(
                        _overall,
                        _punctuality,
                        _quality,
                        _professionalism,
                        _communication,
                        _titleController.text,
                        _commentController.text,
                        _wouldRecommend,
                      );
                      if (mounted) {
                        Navigator.of(context).pop();
                      }
                    },
              style: ElevatedButton.styleFrom(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: _submitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : Text('submit_review'.tr(context), style: const TextStyle(fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }
}
