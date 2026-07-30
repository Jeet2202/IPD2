import '../models/category_model.dart';
import '../models/service_model.dart';
import '../models/worker_model.dart';
import '../models/booking_model.dart';
import '../models/user_model.dart';

class MockData {
  MockData._();

  // ── User ──────────────────────────────────────────────
  static final UserModel currentUser = UserModel(
    id:         'usr_001',
    name:       'Rahul Sharma',
    email:      'rahul@example.com',
    phone:      '9876543210',
    role:       'customer',
    isVerified: true,
    createdAt:  DateTime(2024, 1, 15),
  );

  // ── Categories ────────────────────────────────────────
  static final List<CategoryModel> categories = [
    const CategoryModel(id: 'cat_01', name: 'Cleaning', icon: 'cleaning', image: '', serviceCount: 12),
    const CategoryModel(id: 'cat_02', name: 'Plumbing', icon: 'plumbing', image: '', serviceCount: 8),
    const CategoryModel(id: 'cat_03', name: 'Electrical', icon: 'electrical', image: '', serviceCount: 15),
    const CategoryModel(id: 'cat_04', name: 'Carpentry', icon: 'carpentry', image: '', serviceCount: 6),
    const CategoryModel(id: 'cat_05', name: 'Painting', icon: 'painting', image: '', serviceCount: 9),
    const CategoryModel(id: 'cat_06', name: 'AC Repair', icon: 'ac', image: '', serviceCount: 5),
    const CategoryModel(id: 'cat_07', name: 'Pest Control', icon: 'pest', image: '', serviceCount: 4),
    const CategoryModel(id: 'cat_08', name: 'Appliance', icon: 'appliance', image: '', serviceCount: 11),
  ];

  // ── Services ──────────────────────────────────────────
  static final List<ServiceModel> services = [
    const ServiceModel(
      id: 'svc_01', categoryId: 'cat_01',
      name: 'Home Deep Cleaning', description: 'Complete deep cleaning of your home.',
      image: '', basePrice: 999, unit: 'per visit', rating: 4.7, reviewCount: 234,
    ),
    const ServiceModel(
      id: 'svc_02', categoryId: 'cat_02',
      name: 'Pipe Leak Repair', description: 'Fix any pipe leaks quickly.',
      image: '', basePrice: 299, unit: 'per visit', rating: 4.5, reviewCount: 128,
    ),
    const ServiceModel(
      id: 'svc_03', categoryId: 'cat_03',
      name: 'Wiring & Switches', description: 'Electrical wiring and switch installation.',
      image: '', basePrice: 399, unit: 'per visit', rating: 4.8, reviewCount: 312,
    ),
    const ServiceModel(
      id: 'svc_04', categoryId: 'cat_06',
      name: 'AC Service & Gas Fill', description: 'Full AC servicing and gas refill.',
      image: '', basePrice: 599, unit: 'per unit', rating: 4.6, reviewCount: 189,
    ),
  ];

  // ── Workers ───────────────────────────────────────────
  static final List<WorkerModel> workers = [
    const WorkerModel(
      id: 'wrk_01', userId: 'usr_w01',
      name: 'Ramesh Kumar', phone: '9000000001',
      skillIds: ['cat_01', 'cat_05'],
      rating: 4.8, completedJobs: 342,
      isAvailable: true, isVerified: true, distanceKm: 1.2,
    ),
    const WorkerModel(
      id: 'wrk_02', userId: 'usr_w02',
      name: 'Suresh Patel', phone: '9000000002',
      skillIds: ['cat_02', 'cat_03'],
      rating: 4.6, completedJobs: 198,
      isAvailable: true, isVerified: true, distanceKm: 2.5,
    ),
  ];

  // ── Address ───────────────────────────────────────────
  static const AddressModel homeAddress = AddressModel(
    label: 'Home', line1: '12, MG Road', line2: 'Near City Mall',
    city: 'Bengaluru', state: 'Karnataka', pincode: '560001',
    lat: 12.9716, lng: 77.5946,
  );
}
