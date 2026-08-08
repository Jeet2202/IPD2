// File: lib/worker/inspection/negotiation_chat/negotiation_chat_screen.dart

import 'package:flutter/material.dart';
import '../../../../l10n/app_translations.dart';
import '../../../../widgets/language_selector_widget.dart';

class WorkerNegotiationChatScreen extends StatefulWidget {
  const WorkerNegotiationChatScreen({super.key});

  @override
  State<WorkerNegotiationChatScreen> createState() =>
      _WorkerNegotiationChatScreenState();
}

class _WorkerNegotiationChatScreenState
    extends State<WorkerNegotiationChatScreen> {
  final _messageController = TextEditingController();

  final List<Map<String, dynamic>> _messages = [
    {
      'isSystem': true,
      'text': 'Quotation #Q-4902 for ₹ 1,298 submitted to Pooja Sharma',
      'time': '3:45 PM',
    },
    {
      'isSender': false,
      'text':
          'Hi Ramesh, I checked the quotation. Is it possible to give a small discount on the labour charges?',
      'time': '3:50 PM',
    },
    {
      'isSender': true,
      'text':
          'Hello ma\'am! I have already included a ₹ 50 discount. I can offer an additional ₹ 100 off on labour as a gesture.',
      'time': '3:52 PM',
    },
    {
      'isSender': false,
      'text':
          'That sounds fair! Please send the revised quotation for ₹ 1,198. I will approve immediately.',
      'time': '3:55 PM',
    },
  ];

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  void _sendMessage(String text) {
    if (text.trim().isEmpty) return;
    setState(() {
      _messages.add({
        'isSender': true,
        'text': text,
        'time': 'Just now',
      });
      _messageController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(        elevation: 0.5,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: const BoxDecoration(
                color: Color(0xFFDBEAFE),
                shape: BoxShape.circle,
              ),
              child: const Center(
                child: Text(
                  'PS',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF2563EB),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Pooja Sharma',
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'online_quote'.tr(context),
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF10B981),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.description_outlined,
                color: Color(0xFF2563EB)),
            onPressed: () {
              Navigator.pushNamed(
                  context, '/worker/inspection/revised-quotation');
            },
          ),
          IconButton(
            icon: const Icon(Icons.language_rounded, color: Color(0xFF2563EB)),
            tooltip: 'Select Language',
            onPressed: () => LanguageSelectorWidget.show(context),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Quotation Floating Top Banner Card
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              color: Colors.white,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'original_quote_amount'.tr(context),
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF475569),
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'negotiation_in_progress'.tr(context),
                        style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFF2563EB),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.pushNamed(
                          context, '/worker/inspection/revised-quotation');
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                    child: Text(
                      'revise_quote'.tr(context),
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ),
            ),

            const Divider(height: 1, color: Color(0xFFE2E8F0)),

            // Chat Messages List
            Expanded(
              child: ListView.builder(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                itemCount: _messages.length,
                itemBuilder: (ctx, idx) {
                  final msg = _messages[idx];

                  if (msg['isSystem'] == true) {
                    return Center(
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 10),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE2E8F0),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          msg['text']!,
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF475569),
                          ),
                        ),
                      ),
                    );
                  }

                  final isSender = msg['isSender'] == true;

                  return Align(
                    alignment:
                        isSender ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(14),
                      constraints: BoxConstraints(
                        maxWidth: MediaQuery.of(context).size.width * 0.75,
                      ),
                      decoration: BoxDecoration(
                        color: isSender
                            ? const Color(0xFF2563EB)
                            : Colors.white,
                        borderRadius: BorderRadius.only(
                          topLeft: const Radius.circular(16),
                          topRight: const Radius.circular(16),
                          bottomLeft: Radius.circular(isSender ? 16 : 4),
                          bottomRight: Radius.circular(isSender ? 4 : 16),
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: isSender
                            ? CrossAxisAlignment.end
                            : CrossAxisAlignment.start,
                        children: [
                          Text(
                            msg['text']!,
                            style: TextStyle(
                              fontSize: 14,
                              color: isSender
                                  ? Colors.white
                                  : const Color(0xFF0F172A),
                              height: 1.4,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            msg['time']!,
                            style: TextStyle(
                              fontSize: 10,
                              color: isSender
                                  ? Colors.white.withOpacity(0.7)
                                  : const Color(0xFF94A3B8),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),

            // Quick Reply Chips Bar
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
              child: Row(
                children: [
                  _buildQuickReplyChip('quick_reply_offer_100'.tr(context)),
                  _buildQuickReplyChip('quick_reply_parts_non_neg'.tr(context)),
                  _buildQuickReplyChip('quick_reply_sending_revised'.tr(context)),
                ],
              ),
            ),

            // Message Input Bar
            Container(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
              color: Colors.white,
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'type_your_message'.tr(context),
                        hintStyle: const TextStyle(
                            color: Color(0xFF94A3B8), fontSize: 14),
                        filled: true,
                        fillColor: const Color(0xFFF8FAFC),
                        contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide:
                              const BorderSide(color: Color(0xFFE2E8F0)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: const BorderSide(
                              color: Color(0xFF2563EB), width: 1.5),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  GestureDetector(
                    onTap: () => _sendMessage(_messageController.text),
                    child: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: const BoxDecoration(
                        color: Color(0xFF2563EB),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.send_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickReplyChip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 8.0),
      child: ActionChip(
        label: Text(text),
        backgroundColor: const Color(0xFFEFF6FF),
        labelStyle: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: Color(0xFF2563EB),
        ),
        side: const BorderSide(color: Color(0xFFDBEAFE)),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
        onPressed: () => _sendMessage(text),
      ),
    );
  }
}
