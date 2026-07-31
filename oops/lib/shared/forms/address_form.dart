import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../widgets/app_button.dart';
import '../../widgets/app_text_field.dart';

class AddressForm extends StatefulWidget {
  final VoidCallback? onSave;

  const AddressForm({super.key, this.onSave});

  @override
  State<AddressForm> createState() => _AddressFormState();
}

class _AddressFormState extends State<AddressForm> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _houseController = TextEditingController();
  final _streetController = TextEditingController();
  final _pincodeController = TextEditingController();
  String _addressType = 'Home';

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _houseController.dispose();
    _streetController.dispose();
    _pincodeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          AppTextField(
            label: 'Full Name',
            hint: 'e.g. Rahul Sharma',
            controller: _nameController,
            validator: (v) => v == null || v.isEmpty ? 'Please enter name' : null,
          ),
          const SizedBox(height: AppDimensions.md),
          AppTextField(
            label: 'Phone Number',
            hint: '+91 98765 43210',
            keyboardType: TextInputType.phone,
            controller: _phoneController,
            validator: (v) => v == null || v.isEmpty ? 'Please enter phone' : null,
          ),
          const SizedBox(height: AppDimensions.md),
          AppTextField(
            label: 'House / Flat / Building No.',
            hint: 'e.g. Flat 302, B-Block',
            controller: _houseController,
            validator: (v) => v == null || v.isEmpty ? 'Please enter house details' : null,
          ),
          const SizedBox(height: AppDimensions.md),
          AppTextField(
            label: 'Street / Area / Locality',
            hint: 'e.g. 7th Cross, HSR Layout Sector 6',
            controller: _streetController,
            validator: (v) => v == null || v.isEmpty ? 'Please enter street address' : null,
          ),
          const SizedBox(height: AppDimensions.md),
          AppTextField(
            label: 'Pincode',
            hint: '560102',
            keyboardType: TextInputType.number,
            controller: _pincodeController,
            validator: (v) => v == null || v.length < 6 ? 'Enter valid 6-digit pincode' : null,
          ),
          const SizedBox(height: AppDimensions.md),
          const Text(
            'Save Address As',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: ['Home', 'Office', 'Other'].map((type) {
              final isSelected = _addressType == type;
              return Padding(
                padding: const EdgeInsets.only(right: 10),
                child: ChoiceChip(
                  label: Text(type),
                  selected: isSelected,
                  onSelected: (val) {
                    if (val) setState(() => _addressType = type);
                  },
                  selectedColor: AppColors.primary,
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : AppColors.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                  backgroundColor: AppColors.surfaceVariant,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: AppDimensions.lg),
          AppButton(
            label: 'Save Address',
            onPressed: () {
              if (_formKey.currentState?.validate() ?? false) {
                if (widget.onSave != null) widget.onSave!();
              }
            },
          ),
        ],
      ),
    );
  }
}
