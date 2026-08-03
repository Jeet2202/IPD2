// File: lib/services/marketplace_service.dart

import '../models/marketplace_booking_model.dart';
import 'api_service.dart';

class MarketplaceService {
  MarketplaceService._();
  static final MarketplaceService instance = MarketplaceService._();

  Future<MarketplacePaginatedResult> fetchMarketplaceBookings({
    String? query,
    String? categorySlug,
    String? bookingType,
    String? scheduledDate,
    double? minPrice,
    double? maxPrice,
    String? city,
    String sortBy = 'newest',
    int page = 1,
    int pageSize = 20,
  }) async {
    final queryParams = <String, String>{
      'page': page.toString(),
      'page_size': pageSize.toString(),
      'sort_by': sortBy,
    };

    if (query != null && query.trim().isNotEmpty) {
      queryParams['query'] = query.trim();
    }
    if (categorySlug != null && categorySlug.isNotEmpty) {
      queryParams['category_slug'] = categorySlug;
    }
    if (bookingType != null && bookingType.isNotEmpty) {
      queryParams['booking_type'] = bookingType;
    }
    if (scheduledDate != null && scheduledDate.isNotEmpty) {
      queryParams['scheduled_date'] = scheduledDate;
    }
    if (minPrice != null) {
      queryParams['min_price'] = minPrice.toString();
    }
    if (maxPrice != null) {
      queryParams['max_price'] = maxPrice.toString();
    }
    if (city != null && city.isNotEmpty) {
      queryParams['city'] = city;
    }

    final res = await ApiService.instance.get(
      '/worker/marketplace',
      params: queryParams,
    );

    return MarketplacePaginatedResult.fromJson(res);
  }

  Future<MarketplaceBookingDetail> fetchMarketplaceBookingDetail(String bookingId) async {
    final res = await ApiService.instance.get('/worker/marketplace/$bookingId');
    return MarketplaceBookingDetail.fromJson(res);
  }
}
