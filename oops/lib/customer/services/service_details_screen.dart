// File: lib/customer/services/service_details_screen.dart

import 'package:flutter/material.dart';
import '../../app/routes/app_routes.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_dimensions.dart';
import '../../models/service_model.dart';
import '../../services/api_service.dart';
import '../../shared/cards/service_card.dart';
import '../../shared/utils/category_helper.dart';
import '../../l10n/app_translations.dart';

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
      context: context,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return Padding(
          padding: EdgeInsets.all(24.0),
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
              SizedBox(height: 16),
              Text(
                isInspection ? 'Request Inspection (Phase 5)' : 'Book Service (Phase 5)',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                isInspection
                    ? 'In Phase 5, an expert will visit your doorstep for an on-site inspection and provide an exact job quote.'
                    : 'In Phase 5, you will be able to select your preferred date, time slot, address, and place a direct booking.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, height: 1.5),
              ),
              SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                  ),
                  child: Text('got_it'.tr(context), style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
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

    return Scaffold(      body: Stack(
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
                              SizedBox(width: 10),
                              _buildCircleIconButton(
                                icon: Icons.share_outlined,
                                onTap: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('service_link_copied_to_clipboard'.tr(context))),
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
                  padding: EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Category & Featured Badges
                      Row(
                        children: [
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFEFF6FF),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              service.categorySlug.replaceAll('-', ' ').toUpperCase(),
                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: AppColors.primary),
                            ),
                          ),
                          if (service.isFeatured) ...[
                            SizedBox(width: 8),
                            Container(
                              padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFEF3C7),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.star_rounded, size: 12, color: Color(0xFFD97706)),
                                  SizedBox(width: 3),
                                  Text('featured'.tr(context),
                                    style: TextStyle(fontSize: 10, fontWeight: FontWeight.w800, color: Color(0xFFD97706)),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                      SizedBox(height: 10),

                      // Service Title
                      Text(
                        service.name,
                        style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
                      ),
                      if (service.shortDescription.isNotEmpty) ...[
                        SizedBox(height: 6),
                        Text(
                          service.shortDescription,
                          style: TextStyle(fontSize: 14, height: 1.4),
                        ),
                      ],
                      SizedBox(height: 12),

                      // Rating & Reviews Stats Row
                      Row(
                        children: [
                          Icon(Icons.star_rounded, size: 18, color: Color(0xFFFBBF24)),
                          SizedBox(width: 4),
                          Text('${service.rating}', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
                          Text(' (${service.reviewCount} reviews)', style: TextStyle(fontSize: 12)),
                          SizedBox(width: 16),
                          Container(width: 4, height: 4, decoration: BoxDecoration(color: Color(0xFFCBD5E1), shape: BoxShape.circle)),
                          SizedBox(width: 16),
                          Text('verified_pros'.tr(context), style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF10B981))),
                        ],
                      ),

                      SizedBox(height: 16),

                      // Price & Duration Banner Card
                      Container(
                        padding: EdgeInsets.all(16),
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
                                    Text('base_market_price'.tr(context), style: TextStyle(fontSize: 12)),
                                    SizedBox(height: 2),
                                    Text(
                                      priceDisplay,
                                      style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppColors.primary),
                                    ),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    Text('est_duration'.tr(context), style: TextStyle(fontSize: 12)),
                                    SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Icon(Icons.schedule_rounded, size: 16),
                                        SizedBox(width: 4),
                                        Text(durationDisplay, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            SizedBox(height: 10),
                            Divider(height: 1, color: AppColors.divider),
                            SizedBox(height: 8),
                            Row(
                              children: [
                                Icon(Icons.info_outline_rounded, size: 14, color: AppColors.textHint),
                                SizedBox(width: 6),
                                Expanded(
                                  child: Text('final_price_may_vary_depending_2'.tr(context),
                                    style: TextStyle(fontSize: 11, fontStyle: FontStyle.italic),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      SizedBox(height: 28),

                      // About Service Section
                      if (service.description.isNotEmpty) ...[
                        _buildSectionTitle('About Service'),
                        SizedBox(height: 8),
                        Text(
                          service.description,
                          style: TextStyle(fontSize: 14, color: Color(0xFF475569), height: 1.6),
                        ),
                        SizedBox(height: 28),
                      ],

                      // What's Included
                      _buildSectionTitle('What\'s Included'),
                      SizedBox(height: 12),
                      Column(
                        children: service.whatsIncluded.map((item) {
                          return Padding(
                            padding: EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  margin: EdgeInsets.only(top: 2),
                                  padding: EdgeInsets.all(4),
                                  decoration: BoxDecoration(color: Color(0xFFDCFCE7), shape: BoxShape.circle),
                                  child: Icon(Icons.check_rounded, size: 14, color: Color(0xFF16A34A)),
                                ),
                                SizedBox(width: 12),
                                Expanded(child: Text(item, style: TextStyle(fontSize: 14, color: Color(0xFF334155), height: 1.4))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      SizedBox(height: 24),

                      // What's Not Included
                      _buildSectionTitle('What\'s Not Included'),
                      SizedBox(height: 12),
                      Column(
                        children: service.whatsNotIncluded.map((item) {
                          return Padding(
                            padding: EdgeInsets.only(bottom: 10.0),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  margin: EdgeInsets.only(top: 2),
                                  padding: EdgeInsets.all(4),
                                  decoration: BoxDecoration(color: Color(0xFFFEE2E2), shape: BoxShape.circle),
                                  child: Icon(Icons.close_rounded, size: 14, color: Color(0xFFDC2626)),
                                ),
                                SizedBox(width: 12),
                                Expanded(child: Text(item, style: TextStyle(fontSize: 14, color: Color(0xFF64748B), height: 1.4))),
                              ],
                            ),
                          );
                        }).toList(),
                      ),

                      SizedBox(height: 28),

                      // Trust & Assurance Section
                      _buildSectionTitle('Why Choose Ally?'),
                      SizedBox(height: 14),
                      _buildTrustCard(Icons.shield_rounded, '30-Day Service Guarantee', 'Free re-service if any issue recurs within 30 days.'),
                      _buildTrustCard(Icons.verified_user_rounded, 'Background Verified Pros', 'Every professional is ID verified and skill-certified.'),
                      _buildTrustCard(Icons.receipt_long_rounded, 'Transparent Rate Card', 'No hidden charges. Standardized rate card upfront.'),

                      // Related Services
                      if (_relatedServices.isNotEmpty) ...[
                        SizedBox(height: 28),
                        _buildSectionTitle('Related Services'),
                        SizedBox(height: 12),
                        Column(
                          children: _relatedServices.map((relSrv) {
                            return Padding(
                              padding: EdgeInsets.only(bottom: 12),
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

                      SizedBox(height: 140), // Spacing for sticky bottom CTA
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
              padding: EdgeInsets.fromLTRB(20, 14, 20, 24),
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
                  SizedBox(
                    width: double.infinity,
                    height: 50,
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
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppDimensions.radiusMd)),
                      ),
                      child: Text('book_service'.tr(context),
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                      ),
                    ),
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
          padding: EdgeInsets.all(28),
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
      margin: EdgeInsets.only(bottom: 12),
      padding: EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.divider),
      ),
      child: Row(
        children: [
          Container(
            padding: EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: AppColors.primary, size: 22),
          ),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700)),
                SizedBox(height: 2),
                Text(subtitle, style: TextStyle(fontSize: 12)),
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
      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, letterSpacing: -0.4),
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
        padding: EdgeInsets.all(10),
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
    return Scaffold(      appBar: AppBar(backgroundColor: Colors.white, elevation: 0.5),
      body: Padding(
        padding: EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(height: 200, decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(16))),
            SizedBox(height: 20),
            Container(height: 24, width: 180, color: Colors.grey.shade200),
            SizedBox(height: 12),
            Container(height: 16, width: 280, color: Colors.grey.shade200),
            SizedBox(height: 20),
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
          padding: EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.cloud_off_rounded, size: 64, color: AppColors.error),
              SizedBox(height: 16),
              Text('failed_to_load_service'.tr(context), style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              SizedBox(height: 8),
              Text(_errorMessage ?? 'Unexpected error', textAlign: TextAlign.center, style: TextStyle()),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  if (_resolvedServiceId != null) {
                    _fetchServiceDetails(_resolvedServiceId!);
                  }
                },
                child: Text('try_again'.tr(context)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
