// File: lib/widgets/worker_voice_summary_button.dart
//
// Reusable AppBar speaker button for worker screens.
// Shows: Idle → speaker icon | Loading → spinner | Speaking → stop icon (pulsing)
//
// Usage:
//   WorkerVoiceSummaryButton(
//     screenName: 'dashboard',
//     getScreenData: () => {'available_jobs': 5, ...},
//   )

import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../services/language_service.dart';
import '../services/voice_summary_service.dart';

class WorkerVoiceSummaryButton extends StatefulWidget {
  /// The screen identifier sent to the AI service (e.g. 'dashboard', 'wallet').
  final String screenName;

  /// Callback that returns the current screen's data at the moment of the tap.
  final Map<String, dynamic> Function() getScreenData;

  const WorkerVoiceSummaryButton({
    super.key,
    required this.screenName,
    required this.getScreenData,
  });

  @override
  State<WorkerVoiceSummaryButton> createState() =>
      _WorkerVoiceSummaryButtonState();
}

class _WorkerVoiceSummaryButtonState extends State<WorkerVoiceSummaryButton>
    with SingleTickerProviderStateMixin {
  final _service = VoiceSummaryService.instance;
  late final AnimationController _pulseController;
  late final Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    // Pulse animation used when speaking (stop icon pulses amber)
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.85, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    _service.state.addListener(_onStateChange);
  }

  @override
  void dispose() {
    _service.state.removeListener(_onStateChange);
    _pulseController.dispose();
    super.dispose();
  }

  void _onStateChange() {
    if (!mounted) return;
    setState(() {});

    if (_service.state.value == VoiceSummaryState.error) {
      final error = _service.lastError ?? 'Voice summary unavailable.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error),
          backgroundColor: const Color(0xFFEF4444),
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  Future<void> _handleTap() async {
    final currentState = _service.state.value;

    // If speaking → stop
    if (currentState == VoiceSummaryState.speaking) {
      await _service.stop();
      return;
    }

    // If loading → ignore double-tap
    if (currentState == VoiceSummaryState.loading) return;

    // Collect screen data at tap time
    final screenData = widget.getScreenData();
    final lang = LanguageService.instance.currentLanguageCode;

    await _service.speak(
      screenName: widget.screenName,
      screenData: screenData,
      appLanguageCode: lang,
    );
  }

  @override
  Widget build(BuildContext context) {
    final stateVal = _service.state.value;

    switch (stateVal) {
      // ── Loading: small circular progress ring over speaker icon ─────────
      case VoiceSummaryState.loading:
        return Padding(
          padding: const EdgeInsets.all(8.0),
          child: SizedBox(
            width: 32,
            height: 32,
            child: Stack(
              alignment: Alignment.center,
              children: [
                const SizedBox(
                  width: 32,
                  height: 32,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    valueColor:
                        AlwaysStoppedAnimation<Color>(Color(0xFF2563EB)),
                  ),
                ),
                const Icon(
                  Icons.record_voice_over_rounded,
                  color: Color(0xFF2563EB),
                  size: 16,
                ),
              ],
            ),
          ),
        );

      // ── Speaking: pulsing amber stop icon ────────────────────────────────
      case VoiceSummaryState.speaking:
        return AnimatedBuilder(
          animation: _pulseAnimation,
          builder: (context, child) {
            return Transform.scale(
              scale: _pulseAnimation.value,
              child: IconButton(
                icon: const Icon(
                  Icons.stop_circle_rounded,
                  color: Color(0xFFF59E0B),
                  size: 28,
                ),
                tooltip: 'Stop',
                onPressed: _handleTap,
              ),
            );
          },
        );

      // ── Error or Idle: standard speaker icon ─────────────────────────────
      case VoiceSummaryState.error:
      case VoiceSummaryState.idle:
        final isError = stateVal == VoiceSummaryState.error;
        return IconButton(
          icon: Icon(
            Icons.record_voice_over_rounded,
            color: isError
                ? const Color(0xFFEF4444)
                : const Color(0xFF2563EB),
            size: 24,
          ),
          tooltip: _tooltip(context),
          onPressed: _handleTap,
        );
    }
  }

  String _tooltip(BuildContext context) {
    final lang = LanguageService.instance.currentLanguageCode;
    if (lang == 'hi' || lang == 'mr') return 'सारांश सुनें';
    return 'Listen to summary';
  }
}

// ── Animated Wave Bars ────────────────────────────────────────────────────────
// Optional: draws 3 animated bars like an equalizer while speaking.
// Used as child in speaking state above if needed in future.

class _WaveBars extends StatefulWidget {
  final Color color;
  const _WaveBars({required this.color});

  @override
  State<_WaveBars> createState() => _WaveBarsState();
}

class _WaveBarsState extends State<_WaveBars> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(vsync: this, duration: const Duration(milliseconds: 600))
      ..repeat(reverse: true);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (_, __) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [0.0, 0.33, 0.66].map((offset) {
            final progress = (_ctrl.value + offset) % 1.0;
            final height = 6 + 10 * math.sin(progress * math.pi);
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 1.0),
              child: Container(
                width: 3,
                height: height,
                decoration: BoxDecoration(
                  color: widget.color,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            );
          }).toList(),
        );
      },
    );
  }
}
