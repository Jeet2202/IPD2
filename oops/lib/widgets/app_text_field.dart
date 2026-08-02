import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../app/theme/app_colors.dart';
import '../app/theme/app_dimensions.dart';

class AppTextField extends StatelessWidget {
  final String label;
  final String? hint;
  final String? helperText;
  final TextEditingController? controller;
  final String? Function(String?)? validator;
  final TextInputType keyboardType;
  final bool obscureText;
  final int? maxLength;
  final int maxLines;
  final Widget? suffix;
  final Widget? prefix;
  final List<TextInputFormatter>? formatters;
  final void Function(String)? onChanged;
  final VoidCallback? onTap;
  final bool readOnly;
  final bool autofocus;
  final TextInputAction? textInputAction;

  const AppTextField({
    super.key,
    required this.label,
    this.hint,
    this.helperText,
    this.controller,
    this.validator,
    this.keyboardType = TextInputType.text,
    this.obscureText = false,
    this.maxLength,
    this.maxLines = 1,
    this.suffix,
    this.prefix,
    this.formatters,
    this.onChanged,
    this.onTap,
    this.readOnly = false,
    this.autofocus = false,
    this.textInputAction,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label.isNotEmpty) ...[
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
        ],
        TextFormField(
          controller:          controller,
          validator:           validator,
          keyboardType:        keyboardType,
          obscureText:         obscureText,
          maxLength:           maxLength,
          maxLines:            obscureText ? 1 : maxLines,
          inputFormatters:     formatters,
          onChanged:           onChanged,
          onTap:               onTap,
          readOnly:            readOnly,
          autofocus:           autofocus,
          textInputAction:     textInputAction,
          decoration: InputDecoration(
            hintText:        hint,
            helperText:      helperText,
            hintStyle:       const TextStyle(color: AppColors.textHint, fontSize: 14),
            suffixIcon:      suffix,
            prefixIcon:      prefix,
            counterText:     '',
            filled:          true,
            fillColor:       AppColors.surface,
            contentPadding:  const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide:   const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide:   const BorderSide(color: AppColors.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide:   const BorderSide(color: AppColors.primary, width: 2),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide:   const BorderSide(color: AppColors.error),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide:   const BorderSide(color: AppColors.error, width: 2),
            ),
          ),
        ),
      ],
    );
  }
}

