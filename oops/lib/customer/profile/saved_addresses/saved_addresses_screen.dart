// File: lib/customer/profile/saved_addresses/saved_addresses_screen.dart
//
// Phase 4.3.2 — Full backend-integrated Address Management screen.
//
// Features:
//   • Pull-to-refresh
//   • Loading skeleton / empty state / error state
//   • Address cards: label, full_name, phone, address, default badge
//   • Edit → navigates to AddEditAddressScreen (pre-populated)
//   • Delete → confirmation dialog → backend soft-delete → list refresh
//   • Set Default → PATCH /default → optimistic UI update
//   • Add New → navigates to AddEditAddressScreen (blank)

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';
import '../../../models/address_model.dart';
import '../../../services/address_service.dart';
import '../../../services/api_service.dart';

class SavedAddressesScreen extends StatefulWidget {
  const SavedAddressesScreen({super.key});

  @override
  State<SavedAddressesScreen> createState() => _SavedAddressesScreenState();
}

class _SavedAddressesScreenState extends State<SavedAddressesScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<AddressModel> _addresses = [];

  // ── Colour constants (match existing app palette) ──────────────────────
  static const _blue = Color(0xFF2563EB);
  static const _darkText = Color(0xFF0F172A);
  static const _mutedText = Color(0xFF64748B);
  static const _border = Color(0xFFE2E8F0);
  static const _bgPage = Color(0xFFF8FAFC);

  // ─────────────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    _loadAddresses();
  }

  // ── Data Fetching ─────────────────────────────────────────────────────

  Future<void> _loadAddresses() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final list = await AddressService.instance.listAddresses();
      if (mounted) {
        setState(() {
          _addresses = list;
          _isLoading = false;
        });
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = _friendlyError(e);
          _isLoading = false;
        });
      }
    } catch (e, stack) {
      debugPrint('SavedAddressesScreen _loadAddresses error: $e\n$stack');
      if (mounted) {
        setState(() {
          _errorMessage = 'Failed to load addresses: ${e.toString()}';
          _isLoading = false;
        });
      }
    }
  }

  // ── Set Default ───────────────────────────────────────────────────────

  Future<void> _setDefault(AddressModel addr) async {
    if (addr.isDefault) return; // Already default — idempotent guard

    // Optimistic UI update
    setState(() {
      _addresses = _addresses.map((a) {
        return a.copyWith(isDefault: a.id == addr.id);
      }).toList();
    });

    try {
      await AddressService.instance.setDefaultAddress(addr.id);
      _showSnack('Default address updated.', isSuccess: true);
    } on ApiException catch (e) {
      // Revert optimistic update
      await _loadAddresses();
      _showSnack(_friendlyError(e));
    } catch (_) {
      await _loadAddresses();
      _showSnack('Failed to update default address. Please try again.');
    }
  }

  // ── Delete ────────────────────────────────────────────────────────────

  Future<void> _confirmDelete(AddressModel addr) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => _DeleteConfirmDialog(addressLabel: addr.label, fullName: addr.fullName),
    );
    if (confirmed != true) return;

    // Optimistic removal
    setState(() {
      _addresses = _addresses.where((a) => a.id != addr.id).toList();
    });

    try {
      await AddressService.instance.deleteAddress(addr.id);
      _showSnack('Address deleted successfully.', isSuccess: true);
      // Reload to get updated default promotion from backend
      _loadAddresses();
    } on ApiException catch (e) {
      await _loadAddresses(); // Revert
      _showSnack(_friendlyError(e));
    } catch (_) {
      await _loadAddresses();
      _showSnack('Failed to delete address. Please try again.');
    }
  }

  // ── Navigation ────────────────────────────────────────────────────────

  Future<void> _navigateToAdd() async {
    final refreshNeeded = await Navigator.pushNamed(
      context,
      AppRoutes.addAddress,
    );
    if (refreshNeeded == true) _loadAddresses();
  }

  Future<void> _navigateToEdit(AddressModel addr) async {
    final refreshNeeded = await Navigator.pushNamed(
      context,
      AppRoutes.editAddress,
      arguments: addr,
    );
    if (refreshNeeded == true) _loadAddresses();
  }

  // ── Helpers ───────────────────────────────────────────────────────────

  String _friendlyError(ApiException e) {
    if (e.statusCode == 408) return 'Request timed out. Check your internet connection.';
    if (e.statusCode == 503) return 'Server unavailable. Please try again later.';
    if (e.statusCode == 401) return 'Session expired. Please log in again.';
    if (e.statusCode == 403) return 'You do not have permission to perform this action.';
    if (e.statusCode == 404) return 'Address not found.';
    return e.message;
  }

  void _showSnack(String message, {bool isSuccess = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isSuccess ? Icons.check_circle_rounded : Icons.error_outline_rounded,
              color: Colors.white,
              size: 18,
            ),
            const SizedBox(width: 10),
            Expanded(child: Text(message, style: const TextStyle(fontSize: 13))),
          ],
        ),
        backgroundColor: isSuccess ? const Color(0xFF16A34A) : const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgPage,
      appBar: AppBar(        elevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: _darkText),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Saved Addresses',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _darkText),
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: _border),
        ),
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadAddresses,
          color: _blue,
          child: _isLoading
              ? _buildSkeleton()
              : _errorMessage != null
                  ? _buildError()
                  : _addresses.isEmpty
                      ? _buildEmpty()
                      : _buildList(),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToAdd,
        backgroundColor: _blue,
        foregroundColor: Colors.white,
        elevation: 4,
        icon: const Icon(Icons.add_location_alt_rounded),
        label: const Text('Add Address', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 14)),
      ),
    );
  }

  // ── List View ─────────────────────────────────────────────────────────

  Widget _buildList() {
    return ListView.separated(
      physics: const AlwaysScrollableScrollPhysics(parent: BouncingScrollPhysics()),
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
      itemCount: _addresses.length,
      separatorBuilder: (_, __) => const SizedBox(height: 14),
      itemBuilder: (_, index) => _AddressCard(
        address: _addresses[index],
        onSetDefault: () => _setDefault(_addresses[index]),
        onEdit: () => _navigateToEdit(_addresses[index]),
        onDelete: () => _confirmDelete(_addresses[index]),
      ),
    );
  }

  // ── Skeleton Loader ───────────────────────────────────────────────────

  Widget _buildSkeleton() {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 100),
      itemCount: 3,
      separatorBuilder: (_, __) => const SizedBox(height: 14),
      itemBuilder: (_, __) => const _SkeletonCard(),
    );
  }

  // ── Empty State ───────────────────────────────────────────────────────

  Widget _buildEmpty() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.7,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEFF6FF),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFFBFDBFE), width: 2),
                  ),
                  child: const Icon(Icons.location_off_rounded, size: 44, color: _blue),
                ),
                const SizedBox(height: 24),
                const Text(
                  'No Saved Addresses',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: _darkText),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Add your home, office, or any other\ndelivery address to get started.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: _mutedText, height: 1.5),
                ),
                const SizedBox(height: 32),
                ElevatedButton.icon(
                  onPressed: _navigateToAdd,
                  icon: const Icon(Icons.add_location_alt_rounded),
                  label: const Text('Add First Address', style: TextStyle(fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    elevation: 0,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ── Error State ───────────────────────────────────────────────────────

  Widget _buildError() {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.7,
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFFFECACA), width: 2),
                  ),
                  child: const Icon(Icons.cloud_off_rounded, size: 44, color: Color(0xFFDC2626)),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Something went wrong',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: _darkText),
                ),
                const SizedBox(height: 10),
                Text(
                  _errorMessage ?? 'Unable to load addresses.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 14, color: _mutedText, height: 1.5),
                ),
                const SizedBox(height: 32),
                ElevatedButton.icon(
                  onPressed: _loadAddresses,
                  icon: const Icon(Icons.refresh_rounded),
                  label: const Text('Try Again', style: TextStyle(fontWeight: FontWeight.w800)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    elevation: 0,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Address Card Widget
// ══════════════════════════════════════════════════════════════════════════════

class _AddressCard extends StatelessWidget {
  final AddressModel address;
  final VoidCallback onSetDefault;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _AddressCard({
    required this.address,
    required this.onSetDefault,
    required this.onEdit,
    required this.onDelete,
  });

  IconData _labelIcon(String label) {
    switch (label.toLowerCase()) {
      case 'home':
        return Icons.home_rounded;
      case 'office':
        return Icons.work_rounded;
      default:
        return Icons.place_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    const blue = Color(0xFF2563EB);
    const darkText = Color(0xFF0F172A);
    const mutedText = Color(0xFF64748B);
    const border = Color(0xFFE2E8F0);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(
          color: address.isDefault ? blue : border,
          width: address.isDefault ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: address.isDefault
                ? blue.withValues(alpha: 0.08)
                : Colors.black.withValues(alpha: 0.03),
            blurRadius: 14,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header Row: label chip + default badge ──────────────────
          Row(
            children: [
              // Label chip with icon
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: address.isDefault
                      ? const Color(0xFFEFF6FF)
                      : const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _labelIcon(address.label),
                      size: 14,
                      color: address.isDefault ? blue : mutedText,
                    ),
                    const SizedBox(width: 5),
                    Text(
                      address.label.toUpperCase(),
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w800,
                        color: address.isDefault ? blue : mutedText,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              // Default badge
              if (address.isDefault)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: const Color(0xFFDCFCE7),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.star_rounded, size: 12, color: Color(0xFF16A34A)),
                      SizedBox(width: 4),
                      Text(
                        'DEFAULT',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF16A34A),
                          letterSpacing: 0.5,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),

          const SizedBox(height: 12),

          // ── Full Name ─────────────────────────────────────────────
          Text(
            address.fullName,
            style: const TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w800,
              color: darkText,
            ),
          ),

          const SizedBox(height: 6),

          // ── Address ──────────────────────────────────────────────
          Text(
            address.shortAddress,
            style: const TextStyle(fontSize: 13, color: mutedText, height: 1.4),
          ),

          // ── Landmark ─────────────────────────────────────────────
          if (address.landmark != null && address.landmark!.isNotEmpty) ...[
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.push_pin_rounded, size: 12, color: Color(0xFF94A3B8)),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    address.landmark!,
                    style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                  ),
                ),
              ],
            ),
          ],

          const SizedBox(height: 6),

          // ── Phone ─────────────────────────────────────────────────
          Row(
            children: [
              const Icon(Icons.phone_rounded, size: 13, color: Color(0xFF94A3B8)),
              const SizedBox(width: 5),
              Text(
                address.phone,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF94A3B8),
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),
          const Divider(color: Color(0xFFF1F5F9), height: 1),
          const SizedBox(height: 10),

          // ── Action Row ────────────────────────────────────────────
          Row(
            children: [
              // Set Default
              if (!address.isDefault)
                GestureDetector(
                  onTap: onSetDefault,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFEFF6FF),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: const Color(0xFFBFDBFE)),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.star_border_rounded, size: 13, color: blue),
                        SizedBox(width: 5),
                        Text(
                          'Set Default',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: blue,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              if (address.isDefault)
                const Row(
                  children: [
                    Icon(Icons.check_circle_rounded, size: 14, color: Color(0xFF16A34A)),
                    SizedBox(width: 5),
                    Text(
                      'Default Selected',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF16A34A),
                      ),
                    ),
                  ],
                ),

              const Spacer(),

              // Edit Button
              _ActionIconBtn(
                icon: Icons.edit_outlined,
                color: const Color(0xFF475569),
                tooltip: 'Edit',
                onTap: onEdit,
              ),
              const SizedBox(width: 4),

              // Delete Button
              _ActionIconBtn(
                icon: Icons.delete_outline_rounded,
                color: const Color(0xFFEF4444),
                tooltip: 'Delete',
                onTap: onDelete,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Small icon action button ───────────────────────────────────────────────

class _ActionIconBtn extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String tooltip;
  final VoidCallback onTap;

  const _ActionIconBtn({
    required this.icon,
    required this.color,
    required this.tooltip,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 18, color: color),
        ),
      ),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Delete Confirmation Dialog
// ══════════════════════════════════════════════════════════════════════════════

class _DeleteConfirmDialog extends StatelessWidget {
  final String addressLabel;
  final String fullName;

  const _DeleteConfirmDialog({
    required this.addressLabel,
    required this.fullName,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      icon: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFFFEF2F2),
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0xFFFECACA)),
        ),
        child: const Icon(Icons.delete_outline_rounded, color: Color(0xFFDC2626), size: 28),
      ),
      title: const Text(
        'Delete Address?',
        textAlign: TextAlign.center,
        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
      ),
      content: Text(
        'Are you sure you want to delete the $addressLabel address for $fullName? This cannot be undone.',
        textAlign: TextAlign.center,
        style: const TextStyle(fontSize: 14, color: Color(0xFF64748B), height: 1.5),
      ),
      actionsPadding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
      actions: [
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () => Navigator.pop(context, false),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  side: const BorderSide(color: Color(0xFFE2E8F0)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text(
                  'Cancel',
                  style: TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF64748B)),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                  elevation: 0,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Delete', style: TextStyle(fontWeight: FontWeight.w800)),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// Skeleton Loader Card
// ══════════════════════════════════════════════════════════════════════════════

class _SkeletonCard extends StatefulWidget {
  const _SkeletonCard();

  @override
  State<_SkeletonCard> createState() => _SkeletonCardState();
}

class _SkeletonCardState extends State<_SkeletonCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _animation = Tween<double>(begin: 0.3, end: 0.7).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (_, __) {
        return Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(22),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _bar(80, 16, _animation.value),
              const SizedBox(height: 12),
              _bar(140, 14, _animation.value),
              const SizedBox(height: 8),
              _bar(double.infinity, 12, _animation.value),
              const SizedBox(height: 4),
              _bar(200, 12, _animation.value),
              const SizedBox(height: 4),
              _bar(120, 12, _animation.value),
              const SizedBox(height: 16),
              _bar(100, 32, _animation.value, radius: 10),
            ],
          ),
        );
      },
    );
  }

  Widget _bar(double width, double height, double opacity, {double radius = 6}) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.grey.withValues(alpha: opacity),
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}
