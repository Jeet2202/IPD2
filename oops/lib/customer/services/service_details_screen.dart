// File: lib/customer/services/service_details_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';
import '../../shared/cards/service_card.dart';
import '../../shared/utils/category_helper.dart';

class ServiceDetailsScreen extends StatefulWidget {
  final String? serviceId;
  final String serviceTitle;

  const ServiceDetailsScreen({
    super.key,
    this.serviceId,
    this.serviceTitle = 'Service Details',
  });

  @override
  State<ServiceDetailsScreen> createState() => _ServiceDetailsScreenState();
}

class _ServiceDetailsScreenState extends State<ServiceDetailsScreen> {
  final ApiService _apiService = ApiService.instance;

  ServiceModel? _service;
  List<ServiceModel> _relatedServices = [];

  bool _isLoading = true;
  bool _isBookmarked = false;
  String? _errorMessage;
  String? _resolvedServiceId;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractArgsAndFetch();
    });
  }

  void _extractArgsAndFetch() {
    final routeArgs = ModalRoute.of(context)?.settings.arguments;
    String? sId = widget.serviceId;

    if (routeArgs is Map) {
      sId = routeArgs['service_id'] as String? ?? sId;
    }

    _resolvedServiceId = sId;

    if (sId != null && sId.isNotEmpty) {
      _fetchServiceDetails(sId);
    } else {
      setState(() {
        _isLoading = false;
        _errorMessage = 'No service ID provided.';
      });
    }
  }

  Future<void> _fetchServiceDetails(String sId) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await _apiService.getServiceById(sId);
      final model = ServiceModel.fromJson(res);

      if (!mounted) return;

      setState(() {
        _service = model;
        _isLoading = false;
      });

      // Fetch related services from same category
      if (model.categoryId.isNotEmpty) {
        _fetchRelatedServices(model.categoryId, model.id);
      }
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = e.message;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _errorMessage = 'Unable to connect to server. Please try again.';
      });
    }
  }

  Future<void> _fetchRelatedServices(String categoryId, String currentServiceId) async {
    try {
      final res = await _apiService.fetchServices(
        categoryId: categoryId,
        limit: 6,
      );
      final List rawItems = res['items'] as List? ?? [];
      final list = rawItems
          .map((e) => ServiceModel.fromJson(e as Map<String, dynamic>))
          .where((s) => s.id != currentServiceId)
          .take(4)
          .toList();

      if (mounted) {
        setState(() {
          _relatedServices = list;
        });
      }
    } catch (_) {}
  }

  void _showPhase5Modal({required bool isInspection}) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: isInspection ? const Color(0xFFFEF3C7) : const Color(0xFFDBEAFE),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  isInspection ? Icons.search_rounded : Icons.calendar_today_rounded,
                  color: isInspection ? const Color(0xFFD97706) : AppColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                isInspection ? 'Request Inspection (Phase 5)' : 'Book Service (Phase 5)',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              Text(
                isInspection
                    ? 'In Phase 5, an expert will visit your doorstep for an on-site inspection and provide an exact job quote.'
                    : 'In Phase 5, you will be able to select your preferred date, time slot, address, and place a direct booking.',
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 13, color: AppColors.textSecondary, height: 1.5),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                  ),
                  child: const Text('Got It', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return _buildSkeletonLoader();
    }

    if (_errorMessage != null) {
      return _buildErrorState();
    }

    final service = _service!;
    final priceDisplay = service.priceRangeDisplay.isNotEmpty ? service.priceRangeDisplay : '₹${service.basePrice.toStringAsFixed(0)}';
    final durationDisplay = service.durationDisplay.isNotEmpty ? service.durationDisplay : '${service.estimatedDurationMinutes} min';

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Scrollable Body Content
          SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Service Hero Image Banner
                Stack(
                  children: [
                    Container(
                      height: 260,
                      width: double.infinity,
                      color: const Color(0xFF0F172A),
                      child: Image.network(
                        service.resolvedImage,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) => _buildFallbackHeroBanner(service),
                      ),
                    ),

                    // App Bar Overlay
                    Positioned(
                      top: 44,
                      left: 16,
                      right: 16,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildCircleIconButton(
                            icon: Icons.arrow_back_rounded,
                            onTap: () => Navigator.pop(context),
                          ),
                          Row(
                            children: [
                              _buildCircleIconButton(
                                icon: _isBookmarked ? Icons.bookmark_rounded : Icons.bookmark_border_rounded,
                                iconColor: _isBookmarked ? AppColors.primary : AppColors.textPrimary,
                                onTap: () => setState(() => _isBookmarked = !_isBookmarked),
                              ),
                              const SizedBox(width: 10),
                              _buildCircleIconButton(
                                icon: Icons.share_outlined,
                                onTap: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Service link copied to clipboard')),
                                  );
                                },
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                // Main Details Container
                Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Category & Featured Badges
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEFF6FF),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              service.categorySlug.replaceAll('-', ' ').toUpperCase(),
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppColors.primary),
                            ),
                          ),
                          if (service.isFeatured) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFEF3C7),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Row(
                                children: [
                                  Icon(Icons.star_rounded, size: 12, color: Color(0xFFD97706)),
                                  SizedBox(width: 3),
                                  Text(
                                    'FEATURED',
                                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFFD97706)),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 10),

                      // Service Title
                      Text(
                        service.name,
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
                      ),
                      if (service.shortDescription.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Text(
                          service.shortDescription,
                          style: const TextStyle(fontSize: 14, color: AppColors.textSecondary, height: 1.4),
                        ),
                      ],
                      const SizedBox(height: 12),

                      // Rating & Reviews Stats Row
                      Row(
                        children: [
                          const Icon(Icons.star_rounded, size: 18, color: Color(0xFFFBBF24)),
                          const SizedBox(width: 4),
                          Text('${service.rating}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
                          Text(' (${service.reviewCount} reviews)', style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                          const SizedBox(width: 16),
                          Container(width: 4, height: 4, decoration: const BoxDecoration(color: Color(0xFFCBD5E1), shape: BoxShape.circle)),
                          const SizedBox(width: 16),
                          const Text('Verified Pros', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF10B981))),
                        ],
                      ),

                      const SizedBox(height: 16),

                      // Price & Duration Banner Card
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF8FAFC),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.divider),
                        ),
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Base Market Price', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                                    const SizedBox(height: 2),
                                    Text(
                                      priceDisplay,
                                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppColors.primary),
                                    ),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    const Text('Est. Duration', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        const Icon(Icons.schedule_rounded, size: 16, color: AppColors.textPrimary),
                                        const SizedBox(width: 4),
                                        Text(durationDisplay, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            const Divider(height: 1, color: AppColors.divider),
                            const SizedBox(height: 8),
                            const Row(
                              children: [
                                Icon(Icons.info_outline_rounded, size: 14, color: AppColors.textHint),
                                SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    'Final price may vary depending on actual work required.',
                                    style: TextStyle(fontSize: 11, color: AppColors.textSecondary, fontStyle: FontStyle.italic),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 28),

                      // About Service Section
                      if (service.description.isNotEmpty) ...[
                        _buildSectionTitle('About Service'),
                        const SizedBox(height: 8),
                        Text(
                          service.description,
                          style: const TextStyle(fontSize: 14, color: Color(0xFF475569), height: 1.6),
                        ),
                        const SizedBox(height: 28),
                      ],

                      // What's Included
                      _buildSectionTitle('What\'s Included'),
                      const SizedBox(height: 12),
                      Column(
                        children: service.whatsIncluded.map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  margin: const EdgeInsets.only(top: 2),
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(color: Color(0xFFDCFCE7), shape: BoxShape.circle),
                                  child: const Icon(Icons.check_rounded, size: 14, color: Color(0xFF16A34A)),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Text(item, style: const TextStyle(fontSize: 14, color: Color(0xFF334155), height: 1.4))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 24),

                      // What's Not Included
                      _buildSectionTitle('What\'s Not Included'),
                      const SizedBox(height: 12),
                      Column(
                        children: service.whatsNotIncluded.map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  margin: const EdgeInsets.only(top: 2),
                                  padding: const EdgeInsets.all(4),
                                  decoration: const BoxDecoration(color: Color(0xFFFEE2E2), shape: BoxShape.circle),
                                  child: const Icon(Icons.close_rounded, size: 14, color: Color(0xFFDC2626)),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Text(item, style: const TextStyle(fontSize: 14, color: Color(0xFF64748B), height: 1.4))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      const SizedBox(height: 28),

                      // Trust & Assurance Section
                      _buildSectionTitle('Why Choose KaamSetu?'),
                      const SizedBox(height: 14),
                      _buildTrustCard(Icons.shield_rounded, '30-Day Service Guarantee', 'Free re-service if any issue recurs within 30 days.'),
                      _buildTrustCard(Icons.verified_user_rounded, 'Background Verified Pros', 'Every professional is ID verified and skill-certified.'),
                      _buildTrustCard(Icons.receipt_long_rounded, 'Transparent Rate Card', 'No hidden charges. Standardized rate card upfront.'),

                      // Related Services
                      if (_relatedServices.isNotEmpty) ...[
                        const SizedBox(height: 28),
                        _buildSectionTitle('Related Services'),
                        const SizedBox(height: 12),
                        Column(
                          children: _relatedServices.map((relSrv) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: ServiceCard(
                                title: relSrv.name,
                                category: relSrv.categorySlug.replaceAll('-', ' '),
                                price: relSrv.priceRangeDisplay,
                                imageUrl: relSrv.resolvedImage,
                                duration: relSrv.durationDisplay,
                                shortDescription: relSrv.shortDescription,
                                isFeatured: relSrv.isFeatured,
                                onTap: () {
                                  Navigator.pushReplacementNamed(
                                    context,
                                    AppRoutes.customerServiceDetail,
                                    arguments: {
                                      'service_title': relSrv.name,
                                      'service_id': relSrv.id,
                                    },
                                  );
                                },
                              ),
                            );
                          }).toList(),
                        ),
                      ],

                      const SizedBox(height: 140), // Spacing for sticky bottom CTA
                    ],
                  ),
                ),
              ],
            ),
          ),

          // Two Workflow Entry Sticky Bottom Bar
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.08),
                    blurRadius: 20,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Do you know what work needs to be done?',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            Navigator.pushNamed(
                              context,
                              AppRoutes.createBookingDetails,
                              arguments: {
                                'service': service,
                                'booking_type': 'inspection_request',
                              },
                            );
                          },
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: const BorderSide(color: AppColors.primary, width: 1.5),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                          ),
                          child: const Text(
                            'Request Inspection',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.primary),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            Navigator.pushNamed(
                              context,
                              AppRoutes.createBookingDetails,
                              arguments: {
                                'service': service,
                                'booking_type': 'normal_service',
                              },
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            elevation: 0,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                          ),
                          child: const Text(
                            'Book Service',
                            style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFallbackHeroBanner(ServiceModel service) {
    final catIcon = CategoryHelper.getCategoryIcon(service.categorySlug);
    final catColor = CategoryHelper.getCategoryColor(service.categorySlug);

    return Stack(
      alignment: Alignment.center,
      children: [
        Positioned.fill(
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [catColor, const Color(0xFF0F172A)],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.15),
            shape: BoxShape.circle,
          ),
          child: Icon(
            catIcon,
            size: 64,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _buildTrustCard(IconData icon, String title, String subtitle) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: AppColors.primary, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                const SizedBox(height: 2),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: AppColors.textPrimary, letterSpacing: -0.4),
    );
  }

  Widget _buildCircleIconButton({
    required IconData icon,
    Color iconColor = AppColors.textPrimary,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(color: Colors.black.withValues(alpha: 0.12), blurRadius: 10),
          ],
        ),
        child: Icon(icon, size: 20, color: iconColor),
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(backgroundColor: Colors.white, elevation: 0.5),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(height: 200, decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(16))),
            const SizedBox(height: 20),
            Container(height: 24, width: 180, color: Colors.grey.shade200),
            const SizedBox(height: 12),
            Container(height: 16, width: 280, color: Colors.grey.shade200),
            const SizedBox(height: 20),
            Container(height: 80, decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(16))),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Scaffold(
      appBar: AppBar(title: Text(widget.serviceTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off_rounded, size: 64, color: AppColors.error),
              const SizedBox(height: 16),
              const Text('Failed to load service', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(_errorMessage ?? 'Unexpected error', textAlign: TextAlign.center, style: const TextStyle(color: AppColors.textSecondary)),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  if (_resolvedServiceId != null) {
                    _fetchServiceDetails(_resolvedServiceId!);
                  }
                },
                child: const Text('Try Again'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
