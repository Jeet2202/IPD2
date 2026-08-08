import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../modals/service_filter_modal.dart';
import '../../l10n/app_translations.dart';

class ActiveFilterChipsBar extends StatelessWidget {
  final ServiceFilterData filterData;
  final VoidCallback onClearAll;
  final Function(String filterKey) onRemoveFilter;

  const ActiveFilterChipsBar({
    super.key,
    required this.filterData,
    required this.onClearAll,
    required this.onRemoveFilter,
  });

  @override
  Widget build(BuildContext context) {
    if (!filterData.hasActiveFilters) {
      return const SizedBox.shrink();
    }

    final chips = <Widget>[];

    // Sort Chip
    if (filterData.sortBy != 'display_order' && filterData.sortBy != 'relevance') {
      final sortLabel = _getSortLabel(filterData.sortBy);
      chips.add(_buildChip(
        label: 'Sort: $sortLabel',
        onDeleted: () => onRemoveFilter('sort_by'),
      ));
    }

    // Price Range Chip
    if (filterData.minPrice != null || filterData.maxPrice != null) {
      String priceLabel = '';
      if (filterData.minPrice != null && filterData.maxPrice != null) {
        priceLabel = '₹${filterData.minPrice!.toStringAsFixed(0)} – ₹${filterData.maxPrice!.toStringAsFixed(0)}';
      } else if (filterData.maxPrice != null) {
        priceLabel = 'Under ₹${filterData.maxPrice!.toStringAsFixed(0)}';
      } else if (filterData.minPrice != null) {
        priceLabel = '₹${filterData.minPrice!.toStringAsFixed(0)}+';
      }
      chips.add(_buildChip(
        label: priceLabel,
        onDeleted: () => onRemoveFilter('price'),
      ));
    }

    // Duration Chip
    if (filterData.maxDuration != null) {
      chips.add(_buildChip(
        label: 'Max ${filterData.maxDuration}m',
        onDeleted: () => onRemoveFilter('max_duration'),
      ));
    }

    // Featured Chip
    if (filterData.isFeatured) {
      chips.add(_buildChip(
        label: 'Featured Only',
        onDeleted: () => onRemoveFilter('is_featured'),
      ));
    }

    // Category Chip
    if (filterData.categoryId != null && filterData.categoryId!.isNotEmpty) {
      chips.add(_buildChip(
        label: 'Category Selected',
        onDeleted: () => onRemoveFilter('category_id'),
      ));
    }

    return Container(
      width: double.infinity,
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            ...chips.map((chip) => Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: chip,
                )),
            InkWell(
              onTap: onClearAll,
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                child: Text('clear_all'.tr(context),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: AppColors.error,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChip({required String label, required VoidCallback onDeleted}) {
    return Container(
      padding: const EdgeInsets.only(left: 10, right: 4, top: 4, bottom: 4),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 2),
          GestureDetector(
            onTap: onDeleted,
            child: const Icon(
              Icons.cancel_rounded,
              size: 16,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  String _getSortLabel(String sortBy) {
    switch (sortBy) {
      case '-created_at':
        return 'Newest';
      case 'price_asc':
        return 'Low → High';
      case 'price_desc':
        return 'High → Low';
      case 'title_asc':
        return 'A-Z';
      case 'title_desc':
        return 'Z-A';
      default:
        return 'Popularity';
    }
  }
}
