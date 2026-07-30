import '../models/service_model.dart';
import '../models/category_model.dart';
import '../constants/api_endpoints.dart';
import 'api_service.dart';

class ServiceProvider {
  ServiceProvider._();
  static final ServiceProvider instance = ServiceProvider._();

  Future<List<CategoryModel>> getCategories() async {
    final res = await ApiService.instance.get(ApiEndpoints.categories);
    final list = res['categories'] as List;
    return list.map((e) => CategoryModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<ServiceModel>> getServices({String? categoryId}) async {
    final params = categoryId != null ? {'categoryId': categoryId} : null;
    final res = await ApiService.instance.get(ApiEndpoints.services, params: params);
    final list = res['services'] as List;
    return list.map((e) => ServiceModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<ServiceModel> getServiceById(String id) async {
    final res = await ApiService.instance.get(
      ApiEndpoints.serviceDetail.replaceFirst(':id', id),
    );
    return ServiceModel.fromJson(res['service'] as Map<String, dynamic>);
  }
}
