import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../app/theme/app_colors.dart';
import '../../services/booking_chat_service.dart';
import '../l10n/app_translations.dart';

class BookingChatBottomSheet extends StatefulWidget {
  final BookingChatService chatService;
  final bool isActive;

  const BookingChatBottomSheet({super.key, required this.chatService, this.isActive = true});

  static void show(BuildContext context, {required BookingChatService chatService, bool isActive = true}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => BookingChatBottomSheet(chatService: chatService, isActive: isActive),
    );
  }

  @override
  State<BookingChatBottomSheet> createState() => _BookingChatBottomSheetState();
}

class _BookingChatBottomSheetState extends State<BookingChatBottomSheet> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isUploading = false;

  @override
  void initState() {
    super.initState();
    widget.chatService.addListener(_onChatUpdate);
  }

  @override
  void dispose() {
    widget.chatService.removeListener(_onChatUpdate);
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onChatUpdate() {
    if (!mounted) return;
    setState(() {});
    _scrollToBottom();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void _sendMessage() {
    final text = _controller.text;
    if (text.trim().isNotEmpty) {
      widget.chatService.sendMessage(text);
      _controller.clear();
      widget.chatService.setTyping(false);
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    Navigator.pop(context); // Close bottom sheet
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source, imageQuality: 80);
    if (pickedFile != null) {
      _uploadMedia(File(pickedFile.path), 'image');
    }
  }

  Future<void> _pickDocument() async {
    Navigator.pop(context); // Close bottom sheet
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (result != null && result.files.single.path != null) {
      _uploadMedia(File(result.files.single.path!), 'document');
    }
  }

  Future<void> _uploadMedia(File file, String type) async {
    setState(() => _isUploading = true);
    try {
      await widget.chatService.sendMediaMessage(file, type);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to upload $type. Please try again.')),
        );
      }
    } finally {
      if (mounted) setState(() => _isUploading = false);
    }
  }

  void _showAttachmentOptions() {
    showModalBottomSheet(
      context: context,      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: Icon(Icons.camera_alt, color: AppColors.primary),
                title: Text('camera'.tr(context)),
                onTap: () => _pickImage(ImageSource.camera),
              ),
              ListTile(
                leading: Icon(Icons.photo_library, color: AppColors.primary),
                title: Text('gallery'.tr(context)),
                onTap: () => _pickImage(ImageSource.gallery),
              ),
              ListTile(
                leading: Icon(Icons.insert_drive_file, color: AppColors.primary),
                title: Text('document_pdf'.tr(context)),
                onTap: _pickDocument,
              ),
            ],
          ),
        );
      },
    );
  }

  void _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  void _showImageFullScreen(String url) {
    Navigator.push(context, MaterialPageRoute(builder: (_) {
      return Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          backgroundColor: Colors.black,
          iconTheme: const IconThemeData(color: Colors.white),
        ),
        body: Center(
          child: InteractiveViewer(
            child: Image.network(url, fit: BoxFit.contain),
          ),
        ),
      );
    }));
  }

  @override
  Widget build(BuildContext context) {
    final messages = widget.chatService.messages;
    final isTyping = widget.chatService.isOtherPartyTyping;

    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(
              border: Border(bottom: BorderSide(color: Color(0xFFE2E8F0))),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('live_chat'.tr(context),
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.close_rounded),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),
          ),

          // Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: EdgeInsets.all(20),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                final isMe = msg.senderId == widget.chatService.currentUserId;
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.only(bottom: 12),
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.75,
                    ),
                    decoration: BoxDecoration(
                      color: isMe ? AppColors.primary : const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(16),
                        topRight: const Radius.circular(16),
                        bottomLeft: Radius.circular(isMe ? 16 : 4),
                        bottomRight: Radius.circular(isMe ? 4 : 16),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        if (msg.mediaUrl != null && msg.mediaType == 'image')
                          GestureDetector(
                            onTap: () => _showImageFullScreen(msg.mediaUrl!),
                            child: Padding(
                              padding: EdgeInsets.only(bottom: 8.0),
                              child: ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.network(
                                  msg.mediaUrl!,
                                  width: 200,
                                  height: 200,
                                  fit: BoxFit.cover,
                                  loadingBuilder: (context, child, progress) {
                                    if (progress == null) return child;
                                    return Container(
                                      width: 200, height: 200,
                                      color: Colors.black12,
                                      child: Center(child: CircularProgressIndicator()),
                                    );
                                  },
                                ),
                              ),
                            ),
                          )
                        else if (msg.mediaUrl != null && msg.mediaType == 'document')
                          GestureDetector(
                            onTap: () => _openUrl(msg.mediaUrl!),
                            child: Container(
                              padding: EdgeInsets.all(12),
                              margin: EdgeInsets.only(bottom: 8),
                              decoration: BoxDecoration(
                                color: isMe ? Colors.white.withOpacity(0.2) : Colors.white,
                                borderRadius: BorderRadius.circular(12),
                                border: isMe ? null : Border.all(color: Colors.grey.shade300),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.picture_as_pdf, color: isMe ? Colors.white : Colors.red, size: 28),
                                  SizedBox(width: 8),
                                  Flexible(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          msg.mediaName ?? 'Document.pdf',
                                          style: TextStyle(
                                            color: isMe ? Colors.white : AppColors.textPrimary,
                                            fontWeight: FontWeight.w600,
                                            fontSize: 14,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        if (msg.mediaSize != null)
                                          Text(
                                            '${(msg.mediaSize! / 1024).toStringAsFixed(1)} KB',
                                            style: TextStyle(
                                              color: isMe ? Colors.white70 : AppColors.textSecondary,
                                              fontSize: 12,
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          )
                        else
                          Text(
                            msg.content,
                            style: TextStyle(
                              color: isMe ? Colors.white : AppColors.textPrimary,
                              fontSize: 15,
                            ),
                          ),
                        if (isMe) ...[
                          SizedBox(height: 4),
                          Icon(
                            msg.isRead ? Icons.done_all : Icons.check,
                            size: 14,
                            color: msg.isRead ? Colors.blue[200] : Colors.white70,
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          if (_isUploading)
            Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Text('uploading_media'.tr(context), style: TextStyle(fontSize: 12)),
            ),

          // Typing Indicator
          if (isTyping)
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('typing'.tr(context),
                  style: TextStyle(
                    fontSize: 12,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ),

          // Input Area
          if (widget.isActive)
            Container(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 16,
                left: 16,
                right: 16,
                top: 12,
              ),
              decoration: BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: Color(0xFFE2E8F0))),
              ),
              child: Row(
                children: [
                  IconButton(
                    icon: Icon(Icons.attach_file, color: AppColors.primary),
                    onPressed: _showAttachmentOptions,
                  ),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onChanged: (val) {
                        widget.chatService.setTyping(val.isNotEmpty);
                      },
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                        filled: true,
                        fillColor: const Color(0xFFF1F5F9),
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 14,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                  InkWell(
                    onTap: _sendMessage,
                    borderRadius: BorderRadius.circular(24),
                    child: Container(
                      width: 48,
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.send_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            Container(
              width: double.infinity,
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 24,
                top: 24,
              ),
              decoration: BoxDecoration(
                color: Color(0xFFF8FAFC),
                border: Border(top: BorderSide(color: Color(0xFFE2E8F0))),
              ),
              child: Text('this_booking_session_has_endednmedia'.tr(context),
                textAlign: TextAlign.center,
                style: TextStyle(
                                    fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
