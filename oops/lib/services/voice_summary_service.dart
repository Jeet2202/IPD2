// File: lib/services/voice_summary_service.dart
//
// Worker-only Voice Summary Service.
// Calls the AI service to generate a spoken summary of the current screen
// using Groq LLM + ElevenLabs TTS, then plays the MP3 audio.
//
// Language rules:
//   'en' → English voice
//   'hi' → Hindi voice
//   'mr' → mapped to 'hi' here before sending to AI service

import 'dart:async';
import 'dart:convert';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../config/environment.dart';
import '../utils/token_storage.dart';

// ── State Enum ────────────────────────────────────────────────────────────────

enum VoiceSummaryState { idle, loading, speaking, error }

// ── Service ───────────────────────────────────────────────────────────────────

class VoiceSummaryService {
  VoiceSummaryService._() {
    // Listen for playback completion to reset state to idle
    _audioPlayer.onPlayerStateChanged.listen((playerState) {
      if (playerState == PlayerState.completed ||
          playerState == PlayerState.stopped) {
        if (state.value == VoiceSummaryState.speaking) {
          state.value = VoiceSummaryState.idle;
        }
      }
    });
  }

  static final VoiceSummaryService instance = VoiceSummaryService._();

  final AudioPlayer _audioPlayer = AudioPlayer();
  final ValueNotifier<VoiceSummaryState> state =
      ValueNotifier(VoiceSummaryState.idle);

  String? _lastError;
  String? get lastError => _lastError;

  // ── Language Mapping ──────────────────────────────────────────────────────

  /// Maps app language code to TTS language code.
  /// 'mr' (Marathi) → 'hi' (Hindi), anything else → 'en'.
  static String _mapLanguage(String langCode) {
    if (langCode == 'hi' || langCode == 'mr') return 'hi';
    return 'en';
  }

  // ── Main speak() API ──────────────────────────────────────────────────────

  /// Call this to generate and play a voice summary.
  ///
  /// [screenName] — identifier like 'dashboard', 'wallet', 'marketplace'
  /// [screenData] — key-value map of data currently visible on screen
  /// [appLanguageCode] — current app language ('en', 'hi', 'mr')
  Future<void> speak({
    required String screenName,
    required Map<String, dynamic> screenData,
    required String appLanguageCode,
  }) async {
    if (state.value == VoiceSummaryState.loading) return;

    // If already speaking, stop first
    if (state.value == VoiceSummaryState.speaking) {
      await stop();
      return;
    }

    _lastError = null;
    state.value = VoiceSummaryState.loading;

    try {
      final ttsLanguage = _mapLanguage(appLanguageCode);
      final audioBase64 = await _fetchVoiceSummary(
        screenName: screenName,
        screenData: screenData,
        language: ttsLanguage,
      );

      final mp3Bytes = base64Decode(audioBase64);
      await _audioPlayer.play(BytesSource(mp3Bytes));
      state.value = VoiceSummaryState.speaking;
    } on VoiceSummaryException catch (e) {
      _lastError = e.message;
      state.value = VoiceSummaryState.error;
      // Auto-reset to idle after a short delay so UI recovers
      Future.delayed(const Duration(seconds: 3), () {
        if (state.value == VoiceSummaryState.error) {
          state.value = VoiceSummaryState.idle;
        }
      });
      debugPrint('[VoiceSummary] Error: ${e.message}');
    } catch (e) {
      _lastError = 'Unexpected error: $e';
      state.value = VoiceSummaryState.error;
      Future.delayed(const Duration(seconds: 3), () {
        if (state.value == VoiceSummaryState.error) {
          state.value = VoiceSummaryState.idle;
        }
      });
      debugPrint('[VoiceSummary] Unexpected error: $e');
    }
  }

  /// Stop currently playing audio immediately.
  Future<void> stop() async {
    await _audioPlayer.stop();
    state.value = VoiceSummaryState.idle;
  }

  // ── HTTP call to AI service ────────────────────────────────────────────────

  Future<String> _fetchVoiceSummary({
    required String screenName,
    required Map<String, dynamic> screenData,
    required String language,
  }) async {
    final token = TokenStorage.accessToken;
    if (token.isEmpty || token == 'null') {
      throw const VoiceSummaryException('Not authenticated. Please log in again.');
    }

    final url = Uri.parse(
      '${EnvironmentConfig.aiServiceUrl}$_endpoint',
    );

    final body = jsonEncode({
      'screen_name': screenName,
      'screen_data': screenData,
      'language': language,
    });

    late http.Response response;
    try {
      response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: body,
      ).timeout(const Duration(seconds: 20));
    } on TimeoutException {
      throw const VoiceSummaryException('Request timed out. Check your connection.');
    } catch (e) {
      throw VoiceSummaryException('Could not reach AI service: $e');
    }

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      final audioBase64 = json['audio_base64'] as String?;
      if (audioBase64 == null || audioBase64.isEmpty) {
        throw const VoiceSummaryException('AI service returned empty audio.');
      }
      return audioBase64;
    } else if (response.statusCode == 401) {
      throw const VoiceSummaryException('Session expired. Please log in again.');
    } else if (response.statusCode == 403) {
      throw const VoiceSummaryException('Voice summary is only available for workers.');
    } else if (response.statusCode == 502) {
      throw const VoiceSummaryException('Voice synthesis failed. Please try again.');
    } else {
      throw VoiceSummaryException(
        'AI service error (${response.statusCode}). Please try again.',
      );
    }
  }

  static const String _endpoint = '/ai/worker/voice-summary';
}

// ── Exception ─────────────────────────────────────────────────────────────────

class VoiceSummaryException implements Exception {
  final String message;
  const VoiceSummaryException(this.message);

  @override
  String toString() => 'VoiceSummaryException: $message';
}
