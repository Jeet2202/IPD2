import 'package:flutter/material.dart';

/// Category & Service Visual Identity System Helper.
/// Maps category & service slugs/names to distinct Material Icons, colors,
/// and high-resolution Unsplash images.
class CategoryHelper {
  static const Map<String, _CategoryMeta> _categoryMap = {
    'electrical': _CategoryMeta(
      name: 'Electrical',
      icon: Icons.bolt_rounded,
      color: Color(0xFFFF5722),
      bgLight: Color(0xFFFFF7ED),
      imageUrl: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=500&auto=format&fit=crop&q=80',
    ),
    'plumbing': _CategoryMeta(
      name: 'Plumbing',
      icon: Icons.plumbing_rounded,
      color: Color(0xFF2196F3),
      bgLight: Color(0xFFEFF6FF),
      imageUrl: 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=500&auto=format&fit=crop&q=80',
    ),
    'cleaning': _CategoryMeta(
      name: 'Cleaning',
      icon: Icons.cleaning_services_rounded,
      color: Color(0xFF10B981),
      bgLight: Color(0xFFECFDF5),
      imageUrl: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format&fit=crop&q=80',
    ),
    'painting': _CategoryMeta(
      name: 'Painting',
      icon: Icons.format_paint_rounded,
      color: Color(0xFF8B5CF6),
      bgLight: Color(0xFFF5F3FF),
      imageUrl: 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=500&auto=format&fit=crop&q=80',
    ),
    'carpentry': _CategoryMeta(
      name: 'Carpentry',
      icon: Icons.carpenter_rounded,
      color: Color(0xFFB45309),
      bgLight: Color(0xFFFEF3C7),
      imageUrl: 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=500&auto=format&fit=crop&q=80',
    ),
    'ac-repair': _CategoryMeta(
      name: 'AC Repair',
      icon: Icons.ac_unit_rounded,
      color: Color(0xFF06B6D4),
      bgLight: Color(0xFFCFFAFE),
      imageUrl: 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=500&auto=format&fit=crop&q=80',
    ),
    'appliance-repair': _CategoryMeta(
      name: 'Appliance Repair',
      icon: Icons.home_repair_service_rounded,
      color: Color(0xFFF97316),
      bgLight: Color(0xFFFFEDD5),
      imageUrl: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&auto=format&fit=crop&q=80',
    ),
    'pest-control': _CategoryMeta(
      name: 'Pest Control',
      icon: Icons.bug_report_rounded,
      color: Color(0xFFE11D48),
      bgLight: Color(0xFFFFE4E6),
      imageUrl: 'https://images.unsplash.com/photo-1611284446314-60a55ac0d49d?w=500&auto=format&fit=crop&q=80',
    ),
  };

  static const Map<String, String> _serviceImageMap = {
    'ceiling-fan-installation': 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=500&auto=format&fit=crop&q=80',
    'ceiling-fan-repair': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=500&auto=format&fit=crop&q=80',
    'tap-installation': 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=500&auto=format&fit=crop&q=80',
    'tap-repair': 'https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=500&auto=format&fit=crop&q=80',
    'drain-cleaning': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&auto=format&fit=crop&q=80',
    'deep-home-cleaning': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format&fit=crop&q=80',
    'kitchen-cleaning': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&auto=format&fit=crop&q=80',
    'bathroom-cleaning': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=500&auto=format&fit=crop&q=80',
    'interior-painting': 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=500&auto=format&fit=crop&q=80',
    'texture-painting': 'https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=500&auto=format&fit=crop&q=80',
    'furniture-repair': 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?w=500&auto=format&fit=crop&q=80',
    'door-installation': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500&auto=format&fit=crop&q=80',
    'ac-installation': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=500&auto=format&fit=crop&q=80',
    'ac-gas-refill': 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=500&auto=format&fit=crop&q=80',
    'ac-deep-cleaning': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=500&auto=format&fit=crop&q=80',
    'washing-machine-repair': 'https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=500&auto=format&fit=crop&q=80',
    'refrigerator-repair': 'https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=500&auto=format&fit=crop&q=80',
    'cockroach-control': 'https://images.unsplash.com/photo-1611284446314-60a55ac0d49d?w=500&auto=format&fit=crop&q=80',
    'termite-treatment': 'https://images.unsplash.com/photo-1611284446314-60a55ac0d49d?w=500&auto=format&fit=crop&q=80',
  };

  static String _normalizeSlug(String input) {
    return input.trim().toLowerCase().replaceAll(' ', '-').replaceAll('&', 'and');
  }

  static IconData getCategoryIcon(String categorySlugOrName) {
    final slug = _normalizeSlug(categorySlugOrName);
    for (final entry in _categoryMap.entries) {
      if (slug.contains(entry.key) || entry.key.contains(slug) || slug.contains(entry.value.name.toLowerCase())) {
        return entry.value.icon;
      }
    }
    if (slug.contains('electric') || slug.contains('fan') || slug.contains('wiring')) return Icons.bolt_rounded;
    if (slug.contains('plumb') || slug.contains('tap') || slug.contains('drain') || slug.contains('pipe')) return Icons.plumbing_rounded;
    if (slug.contains('clean') || slug.contains('wash') || slug.contains('sofa')) return Icons.cleaning_services_rounded;
    if (slug.contains('paint') || slug.contains('wall') || slug.contains('texture')) return Icons.format_paint_rounded;
    if (slug.contains('carpent') || slug.contains('wood') || slug.contains('door') || slug.contains('lock')) return Icons.carpenter_rounded;
    if (slug.contains('ac') || slug.contains('cool') || slug.contains('air')) return Icons.ac_unit_rounded;
    if (slug.contains('appliance') || slug.contains('fridge') || slug.contains('tv') || slug.contains('ro')) return Icons.home_repair_service_rounded;
    if (slug.contains('pest') || slug.contains('bug') || slug.contains('rat') || slug.contains('termite')) return Icons.bug_report_rounded;
    return Icons.grid_view_rounded;
  }

  static Color getCategoryColor(String categorySlugOrName) {
    final slug = _normalizeSlug(categorySlugOrName);
    for (final entry in _categoryMap.entries) {
      if (slug.contains(entry.key) || entry.key.contains(slug)) {
        return entry.value.color;
      }
    }
    return const Color(0xFF2563EB);
  }

  static Color getCategoryBgLight(String categorySlugOrName) {
    final slug = _normalizeSlug(categorySlugOrName);
    for (final entry in _categoryMap.entries) {
      if (slug.contains(entry.key) || entry.key.contains(slug)) {
        return entry.value.bgLight;
      }
    }
    return const Color(0xFFEFF6FF);
  }

  static String getCategoryImageUrl(String categorySlugOrName) {
    final slug = _normalizeSlug(categorySlugOrName);
    for (final entry in _categoryMap.entries) {
      if (slug.contains(entry.key) || entry.key.contains(slug)) {
        return entry.value.imageUrl;
      }
    }
    return 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=500&auto=format&fit=crop&q=80';
  }

  static String getServiceImageUrl(String serviceSlug, String categorySlug, String name) {
    final sSlug = _normalizeSlug(serviceSlug.isNotEmpty ? serviceSlug : name);
    if (_serviceImageMap.containsKey(sSlug)) {
      return _serviceImageMap[sSlug]!;
    }
    return getCategoryImageUrl(categorySlug.isNotEmpty ? categorySlug : name);
  }
}

class _CategoryMeta {
  final String name;
  final IconData icon;
  final Color color;
  final Color bgLight;
  final String imageUrl;

  const _CategoryMeta({
    required this.name,
    required this.icon,
    required this.color,
    required this.bgLight,
    required this.imageUrl,
  });
}
