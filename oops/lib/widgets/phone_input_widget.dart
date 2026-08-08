import 'package:flutter/material.dart';
import '../l10n/app_translations.dart';

class CountryInfo {
  final String name;
  final String code;
  final String dialCode;
  final String flag;
  final int minLength;
  final int maxLength;
  final RegExp? regex;

  const CountryInfo({
    required this.name,
    required this.code,
    required this.dialCode,
    required this.flag,
    required this.minLength,
    required this.maxLength,
    this.regex,
  });
}

class CountryData {
  static final List<CountryInfo> countries = [
    const CountryInfo(
      name: 'India',
      code: 'IN',
      dialCode: '+91',
      flag: '🇮🇳',
      minLength: 10,
      maxLength: 10,
      regex: null, // Custom validation handled in widget
    ),
    const CountryInfo(
      name: 'United States',
      code: 'US',
      dialCode: '+1',
      flag: '🇺🇸',
      minLength: 10,
      maxLength: 10,
      regex: null,
    ),
    const CountryInfo(
      name: 'United Kingdom',
      code: 'GB',
      dialCode: '+44',
      flag: '🇬🇧',
      minLength: 10,
      maxLength: 10,
      regex: null,
    ),
    const CountryInfo(
      name: 'United Arab Emirates',
      code: 'AE',
      dialCode: '+971',
      flag: '🇦🇪',
      minLength: 9,
      maxLength: 9,
      regex: null,
    ),
    const CountryInfo(
      name: 'Saudi Arabia',
      code: 'SA',
      dialCode: '+966',
      flag: '🇸🇦',
      minLength: 9,
      maxLength: 9,
      regex: null,
    ),
    const CountryInfo(
      name: 'Canada',
      code: 'CA',
      dialCode: '+1',
      flag: '🇨🇦',
      minLength: 10,
      maxLength: 10,
      regex: null,
    ),
    const CountryInfo(
      name: 'Australia',
      code: 'AU',
      dialCode: '+61',
      flag: '🇦🇺',
      minLength: 9,
      maxLength: 9,
      regex: null,
    ),
  ];

  static CountryInfo get defaultCountry => countries.first; // India (+91)
}

class PhoneInputWidget extends StatefulWidget {
  final TextEditingController controller;
  final String? errorText;
  final ValueChanged<String>? onChanged;
  final ValueChanged<CountryInfo>? onCountryChanged;
  final String? Function(String?)? validator;
  final CountryInfo? initialCountry;

  const PhoneInputWidget({
    super.key,
    required this.controller,
    this.errorText,
    this.onChanged,
    this.onCountryChanged,
    this.validator,
    this.initialCountry,
  });

  @override
  State<PhoneInputWidget> createState() => _PhoneInputWidgetState();
}

class _PhoneInputWidgetState extends State<PhoneInputWidget> {
  late CountryInfo _selectedCountry;

  @override
  void initState() {
    super.initState();
    _selectedCountry = widget.initialCountry ?? CountryData.defaultCountry;
  }

  String get fullPhoneNumber {
    var rawNumber = widget.controller.text.trim();
    if (rawNumber.isEmpty) return '';
    if (rawNumber.startsWith('0')) {
      rawNumber = rawNumber.replaceFirst(RegExp(r'^0+'), '');
    }
    if (rawNumber.startsWith('+')) {
      return rawNumber;
    }
    return '${_selectedCountry.dialCode}$rawNumber';
  }

  void _showCountryPicker() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => _CountryPickerBottomSheet(
        selected: _selectedCountry,
        onSelect: (country) {
          setState(() {
            _selectedCountry = country;
          });
          if (widget.onCountryChanged != null) {
            widget.onCountryChanged!(country);
          }
          if (widget.onChanged != null) {
            widget.onChanged!(fullPhoneNumber);
          }
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      keyboardType: TextInputType.phone,
      onChanged: (_) {
        if (widget.onChanged != null) {
          widget.onChanged!(fullPhoneNumber);
        }
      },
      decoration: InputDecoration(
        hintText: '9876543210',
        hintStyle: const TextStyle(
          fontSize: 14,
          color: Color(0xFF94A3B8),
          fontWeight: FontWeight.w400,
        ),
        errorText: widget.errorText,
        prefixIconConstraints: const BoxConstraints(minWidth: 0, minHeight: 0),
        prefixIcon: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: _showCountryPicker,
          child: Container(
            padding: const EdgeInsets.only(left: 14, right: 10, top: 12, bottom: 12),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _selectedCountry.flag,
                  style: const TextStyle(fontSize: 20),
                ),
                const SizedBox(width: 6),
                Text(
                  _selectedCountry.dialCode,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  color: Color(0xFF64748B),
                  size: 20,
                ),
                const SizedBox(width: 8),
                Container(
                  height: 20,
                  width: 1,
                  color: const Color(0xFFCBD5E1),
                ),
              ],
            ),
          ),
        ),
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE2E8F0), width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF2563EB), width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Colors.red, width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Colors.red, width: 1.5),
        ),
      ),
      validator: (val) {
        if (widget.validator != null) {
          final customError = widget.validator!(val);
          if (customError != null) return customError;
        }

        final trimmed = val?.trim() ?? '';
        if (trimmed.isEmpty) {
          return 'Phone number is required';
        }
        if (_selectedCountry.code == 'IN') {
          if (!RegExp(r'^[6-9]\d{9}$').hasMatch(trimmed)) {
            return 'Enter a valid 10-digit Indian mobile number';
          }
        } else {
          if (trimmed.length < _selectedCountry.minLength ||
              trimmed.length > _selectedCountry.maxLength) {
            return 'Enter a valid ${_selectedCountry.minLength}-digit mobile number';
          }
        }
        return null;
      },
    );
  }
}

class _CountryPickerBottomSheet extends StatefulWidget {
  final CountryInfo selected;
  final ValueChanged<CountryInfo> onSelect;

  const _CountryPickerBottomSheet({
    required this.selected,
    required this.onSelect,
  });

  @override
  State<_CountryPickerBottomSheet> createState() => _CountryPickerBottomSheetState();
}

class _CountryPickerBottomSheetState extends State<_CountryPickerBottomSheet> {
  final _searchController = TextEditingController();
  List<CountryInfo> _filtered = CountryData.countries;

  void _filter(String query) {
    setState(() {
      if (query.trim().isEmpty) {
        _filtered = CountryData.countries;
      } else {
        final q = query.toLowerCase().trim();
        _filtered = CountryData.countries
            .where((c) =>
                c.name.toLowerCase().contains(q) ||
                c.dialCode.contains(q) ||
                c.code.toLowerCase().contains(q))
            .toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Container(
        height: MediaQuery.of(context).size.height * 0.60,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFFCBD5E1),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            Text('select_country_country_code'.tr(context),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _searchController,
              onChanged: _filter,
              decoration: InputDecoration(
                hintText: 'Search country or dial code (e.g. India, +91)',
                prefixIcon: const Icon(Icons.search_rounded, color: Color(0xFF94A3B8)),
                filled: true,
                fillColor: const Color(0xFFF8FAFC),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                  borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
                ),
              ),
            ),
            const SizedBox(height: 14),
            Expanded(
              child: ListView.separated(
                itemCount: _filtered.length,
                separatorBuilder: (ctx, i) => const Divider(height: 1, color: Color(0xFFF1F5F9)),
                itemBuilder: (ctx, idx) {
                  final country = _filtered[idx];
                  final isSelected = country.code == widget.selected.code;
                  return ListTile(
                    leading: Text(country.flag, style: const TextStyle(fontSize: 26)),
                    title: Text(
                      country.name,
                      style: TextStyle(
                        fontWeight: isSelected ? FontWeight.w800 : FontWeight.w600,
                        color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF0F172A),
                      ),
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          country.dialCode,
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: isSelected ? const Color(0xFF2563EB) : const Color(0xFF64748B),
                          ),
                        ),
                        if (isSelected) ...[
                          const SizedBox(width: 8),
                          const Icon(Icons.check_circle_rounded, color: Color(0xFF2563EB), size: 20),
                        ],
                      ],
                    ),
                    onTap: () {
                      widget.onSelect(country);
                      Navigator.pop(context);
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
