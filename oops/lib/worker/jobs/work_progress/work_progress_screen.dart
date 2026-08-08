// File: lib/worker/jobs/work_progress/work_progress_screen.dart

import 'package:flutter/material.dart';
import '../../../l10n/app_translations.dart';

class WorkerWorkProgressScreen extends StatefulWidget {
  const WorkerWorkProgressScreen({super.key});

  @override
  State<WorkerWorkProgressScreen> createState() =>
      _WorkerWorkProgressScreenState();
}

class _WorkerWorkProgressScreenState extends State<WorkerWorkProgressScreen> {
  int _secondsElapsed = 1420; // 23 mins 40 secs
  late Timer _timer;
  double _progressValue = 0.65;
  int _progressPhotos = 3;
  late final TextEditingController _updateNotesController;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _updateNotesController = TextEditingController(
      text: 'mock_work_progress_notes'.tr(context)
    );
  }

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        _secondsElapsed++;
      });
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    _updateNotesController.dispose();
    super.dispose();
  }

  String _formatTimer(int totalSeconds) {
    final minutes = (totalSeconds ~/ 60).toString().padLeft(2, '0');
    final seconds = (totalSeconds % 60).toString().padLeft(2, '0');
    return '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(      appBar: AppBar(        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_rounded, color: Color(0xFF0F172A)),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'work_in_progress'.tr(context),
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w700,
            fontSize: 18,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          physics: const BouncingScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Live Work Timer Card Header
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2563EB), Color(0xFF0EA5E9)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0xFF2563EB).withOpacity(0.25),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'elapsed_work_time'.tr(context),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w800,
                            color: Colors.white,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              CircleAvatar(
                                  radius: 4, backgroundColor: Color(0xFF10B981)),
                              SizedBox(width: 6),
                              Text(
                                'live_timer'.tr(context),
                                style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w800,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 12),
                    Text(
                      _formatTimer(_secondsElapsed),
                      style: TextStyle(
                        fontSize: 44,
                        fontWeight: FontWeight.w900,
                        color: Colors.white,
                        letterSpacing: -1.0,
                      ),
                    ),
                    SizedBox(height: 14),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: _progressValue,
                        minHeight: 8,
                        backgroundColor: Colors.white.withOpacity(0.3),
                        valueColor: const AlwaysStoppedAnimation<Color>(
                            Color(0xFF10B981)),
                      ),
                    ),
                    SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('progress_percentage'.tr(context).replaceAll('{}', '${(_progressValue * 100).round()}'),
                            style: TextStyle(
                                fontSize: 11, color: Colors.white)),
                        Text('est_remaining_mock'.tr(context),
                            style: TextStyle(fontSize: 11, color: Colors.white)),
                      ],
                    ),
                  ],
                ),
              ),

              SizedBox(height: 24),

              // Upload Current Progress Media Card
              Text(
                'work_progress_proof'.tr(context),
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                  letterSpacing: -0.4,
                ),
              ),
              SizedBox(height: 12),

              Row(
                children: [
                  ...List.generate(_progressPhotos, (idx) {
                    return Container(
                      width: 80,
                      height: 80,
                      margin: EdgeInsets.only(right: 10),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFCBD5E1)),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.photo_outlined,
                              color: Color(0xFF2563EB), size: 24),
                          SizedBox(height: 4),
                          Text('photo'.tr(context),
                              style: TextStyle(
                                  fontSize: 10, color: Color(0xFF64748B))),
                        ],
                      ),
                    );
                  }),
                  GestureDetector(
                    onTap: () {
                      setState(() {
                        _progressPhotos++;
                      });
                    },
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                            color: const Color(0xFF2563EB), width: 1.5),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo_rounded,
                              color: Color(0xFF2563EB), size: 22),
                          SizedBox(height: 4),
                          Text('add_media'.tr(context),
                              style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF2563EB))),
                        ],
                      ),
                    ),
                  ),
                ],
              ),

              SizedBox(height: 20),

              // Work Progress Notes Field
              Text(
                'work_notes_parts_replaced'.tr(context),
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF334155),
                ),
              ),
              SizedBox(height: 8),
              TextField(
                controller: _updateNotesController,
                maxLines: 3,
                decoration: InputDecoration(
                  hintText: 'work_notes_hint'.tr(context),
                  hintStyle: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  filled: true,
                  fillColor: const Color(0xFFF8FAFC),
                  contentPadding: EdgeInsets.all(14),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: Color(0xFFE2E8F0)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: Color(0xFF2563EB), width: 1.5),
                  ),
                ),
              ),

              SizedBox(height: 24),

              // Customer Progress Notification Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: OutlinedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('customer_updated_progress'.tr(context)),
                        backgroundColor: const Color(0xFF2563EB),
                      ),
                    );
                  },
                  icon: Icon(Icons.send_rounded, size: 18),
                  label: Text('send_progress_update'.tr(context)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF2563EB),
                    side: BorderSide(color: Color(0xFF2563EB), width: 1.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),

              SizedBox(height: 28),

              // Complete Job Button
              SizedBox(
                width: double.infinity,
                height: 54,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/worker/jobs/complete-work');
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_circle_rounded, size: 22),
                      SizedBox(width: 8),
                      Text(
                        'mark_work_completed'.tr(context),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
