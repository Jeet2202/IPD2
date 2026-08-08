// File: lib/widgets/language_selector_widget.dart

import 'package:flutter/material.dart';
import '../l10n/app_translations.dart';
import '../services/language_service.dart';

class LanguageSelectorWidget {
  static void show(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        final currentCode = LanguageService.instance.currentLanguageCode;

        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('selectlanguage'.tr(context).tr(context),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: Color(0xFF64748B)),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildOptionTile(
                ctx,
                code: 'en',
                title: 'English',
                subtitle: 'Default',
                flag: '🇬🇧',
                isSelected: currentCode == 'en',
              ),
              const SizedBox(height: 10),
              _buildOptionTile(
                ctx,
                code: 'hi',
                title: 'हिंदी (Hindi)',
                subtitle: 'हिन्दी',
                flag: '🇮🇳',
                isSelected: currentCode == 'hi',
              ),
              const SizedBox(height: 10),
              _buildOptionTile(
                ctx,
                code: 'mr',
                title: 'मराठी (Marathi)',
                subtitle: 'मराठी',
                flag: '🇮🇳',
                isSelected: currentCode == 'mr',
              ),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  static Widget _buildOptionTile(
    BuildContext context, {
    required String code,
    required String title,
    required String subtitle,
    required String flag,
    required bool isSelected,
  }) {
    return InkWell(
      onTap: () async {
        await LanguageService.instance.changeLanguage(code);
        if (context.mounted) {
          Navigator.pop(context);
        }
      },
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFEFF6FF) : const Color(0xFFF8FAFC),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? const Color(0xFF2563EB) : const Color(0xFFE2E8F0),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Text(flag, style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                      color: isSelected ? const Color(0xFF1E40AF) : const Color(0xFF0F172A),
                    ),
                  ),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                  ),
                ],
              ),
            ),
            if (isSelected)
              const Icon(Icons.check_circle_rounded, color: Color(0xFF2563EB), size: 22),
          ],
        ),
      ),
    );
  }
}
