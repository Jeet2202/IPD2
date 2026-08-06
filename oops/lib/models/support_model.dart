// File: lib/models/support_model.dart

class FAQModel {
  final String faqId;
  final String question;
  final String answer;
  final String category;
  final bool isPopular;
  final int viewCount;
  final List<String> tags;

  FAQModel({
    required this.faqId,
    required this.question,
    required this.answer,
    required this.category,
    this.isPopular = false,
    this.viewCount = 0,
    this.tags = const [],
  });

  factory FAQModel.fromJson(Map<String, dynamic> json) {
    return FAQModel(
      faqId: json['faq_id'] as String? ?? json['id'] as String? ?? '',
      question: json['question'] as String? ?? '',
      answer: json['answer'] as String? ?? '',
      category: json['category'] as String? ?? 'General',
      isPopular: json['is_popular'] as bool? ?? false,
      viewCount: json['view_count'] as int? ?? 0,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() => {
        'faq_id': faqId,
        'question': question,
        'answer': answer,
        'category': category,
        'is_popular': isPopular,
        'view_count': viewCount,
        'tags': tags,
      };
}

class HelpArticleModel {
  final String articleId;
  final String title;
  final String content;
  final String category;
  final String targetRole;
  final int viewCount;
  final String? videoUrl;
  final List<String> tags;

  HelpArticleModel({
    required this.articleId,
    required this.title,
    required this.content,
    required this.category,
    this.targetRole = 'all',
    this.viewCount = 0,
    this.videoUrl,
    this.tags = const [],
  });

  factory HelpArticleModel.fromJson(Map<String, dynamic> json) {
    return HelpArticleModel(
      articleId: json['article_id'] as String? ?? json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      content: json['content'] as String? ?? '',
      category: json['category'] as String? ?? 'General',
      targetRole: json['target_role'] as String? ?? 'all',
      viewCount: json['view_count'] as int? ?? 0,
      videoUrl: json['video_url'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
    );
  }
}

class TicketMessageModel {
  final String senderId;
  final String senderRole;
  final String message;
  final List<String> attachments;
  final String createdAt;

  TicketMessageModel({
    required this.senderId,
    required this.senderRole,
    required this.message,
    this.attachments = const [],
    required this.createdAt,
  });

  factory TicketMessageModel.fromJson(Map<String, dynamic> json) {
    return TicketMessageModel(
      senderId: json['sender_id'] as String? ?? json['user_id'] as String? ?? '',
      senderRole: json['sender_role'] as String? ?? json['user_role'] as String? ?? 'customer',
      message: json['message'] as String? ?? '',
      attachments: (json['attachments'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: json['created_at'] as String? ?? '',
    );
  }

  bool get isUserMessage => senderRole.toLowerCase() == 'customer' || senderRole.toLowerCase() == 'user';
  bool get isAdminMessage => senderRole.toLowerCase() == 'admin' || senderRole.toLowerCase() == 'agent' || senderRole.toLowerCase() == 'support';
}

class SupportTicketModel {
  final String ticketId;
  final String userId;
  final String userRole;
  final String subject;
  final String description;
  final String category;
  final String priority;
  final String status;
  final String? bookingId;
  final String? assignedAdminId;
  final List<TicketMessageModel> responses;
  final List<String> attachments;
  final String createdAt;
  final String updatedAt;

  SupportTicketModel({
    required this.ticketId,
    required this.userId,
    required this.userRole,
    required this.subject,
    required this.description,
    required this.category,
    required this.priority,
    required this.status,
    this.bookingId,
    this.assignedAdminId,
    this.responses = const [],
    this.attachments = const [],
    required this.createdAt,
    required this.updatedAt,
  });

  factory SupportTicketModel.fromJson(Map<String, dynamic> json) {
    var rawResponses = json['responses'] as List<dynamic>? ?? [];
    List<TicketMessageModel> parsedResponses = rawResponses
        .map((r) => TicketMessageModel.fromJson(r as Map<String, dynamic>))
        .toList();

    return SupportTicketModel(
      ticketId: json['ticket_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      userRole: json['user_role'] as String? ?? 'customer',
      subject: json['subject'] as String? ?? '',
      description: json['description'] as String? ?? '',
      category: json['category'] as String? ?? 'General',
      priority: json['priority'] as String? ?? 'medium',
      status: json['status'] as String? ?? 'open',
      bookingId: json['booking_id'] as String?,
      assignedAdminId: json['assigned_admin_id'] as String?,
      responses: parsedResponses,
      attachments: (json['attachments'] as List<dynamic>?)
              ?.map((e) => e is Map ? (e['url'] ?? '').toString() : e.toString())
              .toList() ??
          [],
      createdAt: json['created_at'] as String? ?? '',
      updatedAt: json['updated_at'] as String? ?? '',
    );
  }

  bool get isOpen => status.toLowerCase() == 'open' || status.toLowerCase() == 'in_progress';
}

class ContactInfoModel {
  final String email;
  final String helplinePhone;
  final String? whatsappNumber;
  final String operatingHours;
  final String? address;

  ContactInfoModel({
    required this.email,
    required this.helplinePhone,
    this.whatsappNumber,
    required this.operatingHours,
    this.address,
  });

  factory ContactInfoModel.fromJson(Map<String, dynamic> json) {
    return ContactInfoModel(
      email: json['email'] as String? ?? 'support@kaamsetu.com',
      helplinePhone: json['phone'] as String? ?? json['helpline_phone'] as String? ?? '+919579601589',
      whatsappNumber: json['whatsapp'] as String? ?? json['whatsapp_number'] as String? ?? '+919579601589',
      operatingHours: json['business_hours'] as String? ?? json['operating_hours'] as String? ?? '24/7 Available',
      address: json['address'] as String?,
    );
  }
}

class SOSConfigModel {
  final String policeHelpline;
  final String womenHelpline;
  final String ambulanceHelpline;
  final String kaamsetuEmergencyPhone;
  final List<Map<String, String>> safetyGuidelines;
  final List<String> emergencyInstructions;

  SOSConfigModel({
    required this.policeHelpline,
    required this.womenHelpline,
    required this.ambulanceHelpline,
    required this.kaamsetuEmergencyPhone,
    required this.safetyGuidelines,
    required this.emergencyInstructions,
  });

  factory SOSConfigModel.fromJson(Map<String, dynamic> json) {
    var guidelinesRaw = json['safety_guidelines'] as List<dynamic>? ?? [];
    List<Map<String, String>> parsedGuidelines = guidelinesRaw.map((g) {
      if (g is Map) {
        return {
          'title': (g['title'] ?? '').toString(),
          'description': (g['description'] ?? '').toString(),
        };
      }
      return {'title': 'Safety Tip', 'description': g.toString()};
    }).toList();

    var instructionsRaw = json['emergency_instructions'] as List<dynamic>? ?? [];
    List<String> parsedInstructions = instructionsRaw.map((i) => i.toString()).toList();

    return SOSConfigModel(
      policeHelpline: json['police_helpline'] as String? ?? '112',
      womenHelpline: json['women_helpline'] as String? ?? '1091',
      ambulanceHelpline: json['ambulance_helpline'] as String? ?? '108',
      kaamsetuEmergencyPhone: json['kaamsetu_emergency_phone'] as String? ?? '1800-999-767',
      safetyGuidelines: parsedGuidelines,
      emergencyInstructions: parsedInstructions,
    );
  }
}
