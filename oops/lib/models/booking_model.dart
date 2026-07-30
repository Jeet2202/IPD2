class BookingModel {
  final String id;
  final String customerId;
  final String workerId;
  final String serviceId;
  final String serviceName;
  final String status;
  final AddressModel address;
  final DateTime scheduledAt;
  final double totalAmount;
  final String paymentMethod;
  final String paymentStatus;
  final DateTime createdAt;

  const BookingModel({
    required this.id,
    required this.customerId,
    required this.workerId,
    required this.serviceId,
    required this.serviceName,
    required this.status,
    required this.address,
    required this.scheduledAt,
    required this.totalAmount,
    required this.paymentMethod,
    required this.paymentStatus,
    required this.createdAt,
  });

  factory BookingModel.fromJson(Map<String, dynamic> json) => BookingModel(
        id:            json['_id'] as String,
        customerId:    json['customerId'] as String,
        workerId:      json['workerId'] as String,
        serviceId:     json['serviceId'] as String,
        serviceName:   json['serviceName'] as String,
        status:        json['status'] as String,
        address:       AddressModel.fromJson(json['address'] as Map<String, dynamic>),
        scheduledAt:   DateTime.parse(json['scheduledAt'] as String),
        totalAmount:   (json['totalAmount'] as num).toDouble(),
        paymentMethod: json['paymentMethod'] as String,
        paymentStatus: json['paymentStatus'] as String,
        createdAt:     DateTime.parse(json['createdAt'] as String),
      );

  Map<String, dynamic> toJson() => {
        '_id':           id,
        'customerId':    customerId,
        'workerId':      workerId,
        'serviceId':     serviceId,
        'serviceName':   serviceName,
        'status':        status,
        'address':       address.toJson(),
        'scheduledAt':   scheduledAt.toIso8601String(),
        'totalAmount':   totalAmount,
        'paymentMethod': paymentMethod,
        'paymentStatus': paymentStatus,
        'createdAt':     createdAt.toIso8601String(),
      };
}

class AddressModel {
  final String label;
  final String line1;
  final String? line2;
  final String city;
  final String state;
  final String pincode;
  final double lat;
  final double lng;

  const AddressModel({
    required this.label,
    required this.line1,
    this.line2,
    required this.city,
    required this.state,
    required this.pincode,
    required this.lat,
    required this.lng,
  });

  factory AddressModel.fromJson(Map<String, dynamic> json) => AddressModel(
        label:   json['label'] as String,
        line1:   json['line1'] as String,
        line2:   json['line2'] as String?,
        city:    json['city'] as String,
        state:   json['state'] as String,
        pincode: json['pincode'] as String,
        lat:     (json['lat'] as num).toDouble(),
        lng:     (json['lng'] as num).toDouble(),
      );

  Map<String, dynamic> toJson() => {
        'label':   label,
        'line1':   line1,
        'line2':   line2,
        'city':    city,
        'state':   state,
        'pincode': pincode,
        'lat':     lat,
        'lng':     lng,
      };
}
