import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../l10n/app_translations.dart';

class ServiceFilterData {
  final double? minPrice;
  final double? maxPrice;
  final int? maxDuration;
  final bool isFeatured;
  final String sortBy;
  final String? categoryId;

  const ServiceFilterData({
    this.minPrice,
    this.maxPrice,
    this.maxDuration,
    this.isFeatured = false,
    this.sortBy = 'display_order',
    this.categoryId,
  });

  bool get hasActiveFilters =>
      minPrice != null ||
      maxPrice != null ||
      maxDuration != null ||
      isFeatured ||
      (sortBy != 'display_order' && sortBy != 'relevance') ||
      (categoryId != null && categoryId!.isNotEmpty);

  int get activeFilterCount {
    int count = 0;
    if (minPrice != null || maxPrice != null) count++;
    if (maxDuration != null) count++;
    if (isFeatured) count++;
    if (sortBy != 'display_order' && sortBy != 'relevance') count++;
    if (categoryId != null && categoryId!.isNotEmpty) count++;
    return count;
  }

  ServiceFilterData copyWith({
    double? Function()? minPrice,
    double? Function()? maxPrice,
    int? Function()? maxDuration,
    bool? isFeatured,
    String? sortBy,
    String? Function()? categoryId,
  }) {
    return ServiceFilterData(
      minPrice: minPrice != null ? minPrice() : this.minPrice,
      maxPrice: maxPrice != null ? maxPrice() : this.maxPrice,
      maxDuration: maxDuration != null ? maxDuration() : this.maxDuration,
      isFeatured: isFeatured ?? this.isFeatured,
      sortBy: sortBy ?? this.sortBy,
      categoryId: categoryId != null ? categoryId() : this.categoryId,
    );
  }
}

class ServiceFilterModal extends StatefulWidget {
  final ServiceFilterData initialData;
  final bool showCategoryFilter;
  final Function(ServiceFilterData) onApply;

  const ServiceFilterModal({
    super.key,
    required this.initialData,
    required this.onApply,
    this.showCategoryFilter = false,
  });

  static Future<void> show(
    BuildContext context, {
    required ServiceFilterData initialData,
    required Function(ServiceFilterData) onApply,
    bool showCategoryFilter = false,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => ServiceFilterModal(
        initialData: initialData,
        onApply: onApply,
        showCategoryFilter: showCategoryFilter,
      ),
    );
  }

  @override
  State<ServiceFilterModal> createState() => _ServiceFilterModalState();
}

class _ServiceFilterModalState extends State<ServiceFilterModal> {
  late double? _minPrice;
  late double? _maxPrice;
  late int? _maxDuration;
  late bool _isFeatured;
  late String _sortBy;
  late String? _categoryId;

  final Map<String, String> _sortOptions = {
    'display_order': 'Popularity',
    '-created_at': 'Newest First',
    'price_asc': 'Price: Low to High',
    'price_desc': 'Price: High to Low',
    'title_asc': 'Alphabetical (A-Z)',
    'title_desc': 'Alphabetical (Z-A)',
  };

  @override
  void initState() {
    super.initState();
    _minPrice = widget.initialData.minPrice;
    _maxPrice = widget.initialData.maxPrice;
    _maxDuration = widget.initialData.maxDuration;
    _isFeatured = widget.initialData.isFeatured;
    _sortBy = widget.initialData.sortBy;
    _categoryId = widget.initialData.categoryId;
  }

  void _reset() {
    setState(() {
      _minPrice = null;
      _maxPrice = null;
      _maxDuration = null;
      _isFeatured = false;
      _sortBy = 'display_order';
      _categoryId = null;
    });
  }

  void _apply() {
    widget.onApply(ServiceFilterData(
      minPrice: _minPrice,
      maxPrice: _maxPrice,
      maxDuration: _maxDuration,
      isFeatured: _isFeatured,
      sortBy: _sortBy,
      categoryId: _categoryId,
    ));
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: theme.bottomSheetTheme.backgroundColor ?? colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: EdgeInsets.only(
        top: 20,
        left: 20,
        right: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('filter_sort_services'.tr(context),
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.close_rounded),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
            Divider(height: 1, color: theme.dividerColor),
            const SizedBox(height: 16),

            // Sort By Section
            Text('sort_by'.tr(context),
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _sortOptions.entries.map((entry) {
                final isSelected = _sortBy == entry.key;
                return ChoiceChip(
                  label: Text(entry.value),
                  selected: isSelected,
                  onSelected: (_) => setState(() => _sortBy = entry.key),
                  selectedColor: colorScheme.primary.withValues(alpha: 0.15),
                  backgroundColor: colorScheme.surfaceContainerHighest,
                  labelStyle: TextStyle(
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                    color: isSelected ? colorScheme.primary : colorScheme.onSurfaceVariant,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(20),
                    side: BorderSide(color: isSelected ? colorScheme.primary : Colors.transparent),
                  ),
                  showCheckmark: false,
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Price Range Presets
            Text('price_range'.tr(context),
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildPriceChip(context, 'All Prices', null, null),
                _buildPriceChip(context, 'Under ₹300', null, 300),
                _buildPriceChip(context, '₹300 – ₹800', 300, 800),
                _buildPriceChip(context, '₹800 – ₹1,500', 800, 1500),
                _buildPriceChip(context, '₹1,500+', 1500, null),
              ],
            ),
            const SizedBox(height: 20),

            // Estimated Duration Presets
            Text('max_estimated_duration'.tr(context),
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildDurationChip(context, 'Any Duration', null),
                _buildDurationChip(context, '< 45 Mins', 45),
                _buildDurationChip(context, '< 90 Mins', 90),
                _buildDurationChip(context, '< 3 Hours', 180),
              ],
            ),
            const SizedBox(height: 20),

            // Featured Switch
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('featured_services_only'.tr(context),
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
                    ),
                    SizedBox(height: 2),
                    Text('show_toprated_and_admin_highlighted'.tr(context),
                      style: TextStyle(fontSize: 12),
                    ),
                  ],
                ),
                Switch.adaptive(
                  value: _isFeatured,
                  activeThumbColor: colorScheme.primary,
                  onChanged: (val) => setState(() => _isFeatured = val),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: _reset,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      side: BorderSide(color: theme.dividerColor),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                    ),
                    child: Text('reset_all'.tr(context), style: TextStyle(fontWeight: FontWeight.w600)),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _apply,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: colorScheme.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                    ),
                    child: Text('apply_filters'.tr(context), style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceChip(BuildContext context, String label, double? min, double? max) {
    final isSelected = _minPrice == min && _maxPrice == max;
    final colorScheme = Theme.of(context).colorScheme;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        setState(() {
          _minPrice = min;
          _maxPrice = max;
        });
      },
      selectedColor: colorScheme.primary.withValues(alpha: 0.15),
      backgroundColor: colorScheme.surfaceContainerHighest,
      labelStyle: TextStyle(
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        color: isSelected ? colorScheme.primary : colorScheme.onSurfaceVariant,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: isSelected ? colorScheme.primary : Colors.transparent),
      ),
      showCheckmark: false,
    );
  }

  Widget _buildDurationChip(BuildContext context, String label, int? maxDur) {
    final isSelected = _maxDuration == maxDur;
    final colorScheme = Theme.of(context).colorScheme;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        setState(() {
          _maxDuration = maxDur;
        });
      },
      selectedColor: colorScheme.primary.withValues(alpha: 0.15),
      backgroundColor: colorScheme.surfaceContainerHighest,
      labelStyle: TextStyle(
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
        color: isSelected ? colorScheme.primary : colorScheme.onSurfaceVariant,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(color: isSelected ? colorScheme.primary : Colors.transparent),
      ),
      showCheckmark: false,
    );
  }
}
