// File:
// lib/customer/inspection_booking/negotiation_chat/negotiation_chat_screen.dart

import 'package:flutter/material.dart';
import '../../../app/routes/app_routes.dart';

class NegotiationChatScreen extends StatefulWidget {
  const NegotiationChatScreen({super.key});

  @override
  State<NegotiationChatScreen> createState() => _NegotiationChatScreenState();
}

class _NegotiationChatScreenState extends State<NegotiationChatScreen> {
  final TextEditingController _msgController = TextEditingController();

  final List<Map<String, dynamic>> _messages = [
    {
      'isMe': false,
      'text': 'Hello Sir! I have submitted the diagnostic quotation of ₹5,200 for replacing the main DB box & rewiring.',
      'time': '10:42 AM',
    },
    {
      'isMe': true,
      'text': 'Hi Sunil, ₹5,200 feels slightly high. Is it possible to adjust the labor charges?',
      'time': '10:44 AM',
    },
    {
      'isOffer': true,
      'customerOffer': '₹4,500',
      'workerOffer': '₹5,200',
      'platformEstimate': '₹4,850',
      'time': '10:45 AM',
    },
    {
      'isMe': false,
      'text': 'I can offer a revised rate of ₹4,850 by using direct wholesale Havells parts!',
      'time': '10:46 AM',
    },
  ];

  @override
  void dispose() {
    _msgController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: Color(0xFFDBEAFE),
              child: Icon(Icons.engineering_rounded, color: Color(0xFF2563EB), size: 22),
            ),
            SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Sunil Verma', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w800, color: Color(0xFF0F172A))),
                Text('Online • Price Negotiation', style: TextStyle(fontSize: 11, color: Color(0xFF16A34A), fontWeight: FontWeight.w600)),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // ── Chat List ────────────────────────────────────────────────
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              physics: const BouncingScrollPhysics(),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];

                if (msg['isOffer'] == true) {
                  return _buildOfferComparisonCard(msg);
                }

                final isMe = msg['isMe'] == true;
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isMe ? const Color(0xFF2563EB) : Colors.white,
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(18),
                        topRight: const Radius.circular(18),
                        bottomLeft: Radius.circular(isMe ? 18 : 4),
                        bottomRight: Radius.circular(isMe ? 4 : 18),
                      ),
                      border: isMe ? null : Border.all(color: const Color(0xFFE2E8F0)),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 8, offset: const Offset(0, 2)),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: isMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                      children: [
                        Text(
                          msg['text'] as String,
                          style: TextStyle(fontSize: 13, color: isMe ? Colors.white : const Color(0xFF0F172A), height: 1.4),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          msg['time'] as String,
                          style: TextStyle(fontSize: 10, color: isMe ? const Color(0xFFDBEAFE) : const Color(0xFF94A3B8)),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),

          // ── Negotiation Action Bar ─────────────────────────────────
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            color: Colors.white,
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {},
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Color(0xFF2563EB)),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    child: const Text('Counter ₹4,700', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF2563EB))),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF16A34A),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                    ),
                    child: const Text('Accept ₹4,850', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700)),
                  ),
                ),
              ],
            ),
          ),

          // ── Text Input Field ─────────────────────────────────────────
          Container(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            color: Colors.white,
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.attach_file_rounded, color: Color(0xFF64748B)),
                  onPressed: () {},
                ),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF1F5F9),
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: TextField(
                      controller: _msgController,
                      decoration: const InputDecoration(
                        hintText: 'Type your message or offer...',
                        hintStyle: TextStyle(fontSize: 13, color: Color(0xFF94A3B8)),
                        border: InputBorder.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  backgroundColor: const Color(0xFF2563EB),
                  child: IconButton(
                    icon: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
                    onPressed: () {
                      final text = _msgController.text.trim();
                      if (text.isNotEmpty) {
                        setState(() {
                          _messages.add({
                            'sender': 'customer',
                            'text': text,
                            'time': 'Just now',
                            'isCounterOffer': false,
                          });
                          _msgController.clear();
                        });
                      }
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOfferComparisonCard(Map<String, dynamic> msg) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFFBFDBFE)),
        boxShadow: [
          BoxShadow(color: const Color(0xFF2563EB).withOpacity(0.06), blurRadius: 12),
        ],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('NEGOTIATION STATUS', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w800, color: Color(0xFF2563EB))),
              Text(msg['time'] as String, style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8))),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildPriceColumn('Your Offer', msg['customerOffer'] as String, const Color(0xFF0F172A)),
              _buildPriceColumn('Sunil\'s Offer', msg['workerOffer'] as String, const Color(0xFFEF4444)),
              _buildPriceColumn('Fair Estimate', msg['platformEstimate'] as String, const Color(0xFF16A34A)),
            ],
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            height: 44,
            child: ElevatedButton.icon(
              onPressed: () => Navigator.pushNamed(context, AppRoutes.repairConfirmation),
              icon: const Icon(Icons.check_circle_rounded, size: 18),
              label: const Text('Accept Offer & Start Repair', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w800)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF16A34A),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPriceColumn(String label, String val, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
        const SizedBox(height: 4),
        Text(val, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: color)),
      ],
    );
  }
}
