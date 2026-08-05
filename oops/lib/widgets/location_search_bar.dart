import 'dart:async';
import 'package:flutter/material.dart';
import '../services/location_service.dart';

class LocationSearchBar extends StatefulWidget {
  final Function(SearchResultLocation) onLocationSelected;
  final String hintText;

  const LocationSearchBar({
    super.key,
    required this.onLocationSelected,
    this.hintText = 'Search for area, street, or landmark...',
  });

  @override
  State<LocationSearchBar> createState() => _LocationSearchBarState();
}

class _LocationSearchBarState extends State<LocationSearchBar> {
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();
  
  Timer? _debounceTimer;
  bool _isLoading = false;
  List<SearchResultLocation> _results = [];
  bool _showResults = false;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      if (!_focusNode.hasFocus) {
        // Delay hiding slightly so tap on list item registers
        Future.delayed(const Duration(milliseconds: 200), () {
          if (mounted) setState(() => _showResults = false);
        });
      } else {
        if (_controller.text.isNotEmpty && _results.isNotEmpty) {
          setState(() => _showResults = true);
        }
      }
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    if (_debounceTimer?.isActive ?? false) _debounceTimer!.cancel();

    if (query.trim().isEmpty) {
      setState(() {
        _results = [];
        _showResults = false;
        _isLoading = false;
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _showResults = true;
    });

    _debounceTimer = Timer(const Duration(milliseconds: 400), () async {
      final results = await LocationService.instance.searchLocations(query);
      if (mounted) {
        setState(() {
          _results = results;
          _isLoading = false;
          _showResults = results.isNotEmpty;
        });
      }
    });
  }

  void _clearSearch() {
    _controller.clear();
    _focusNode.unfocus();
    setState(() {
      _results = [];
      _showResults = false;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        // ── Search Field ──
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFE2E8F0)),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0A000000),
                blurRadius: 4,
                offset: Offset(0, 2),
              ),
            ],
          ),
          child: TextField(
            controller: _controller,
            focusNode: _focusNode,
            onChanged: _onSearchChanged,
            decoration: InputDecoration(
              hintText: widget.hintText,
              hintStyle: const TextStyle(color: Color(0xFF94A3B8)),
              prefixIcon: const Icon(Icons.search, color: Color(0xFF64748B)),
              suffixIcon: _controller.text.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear, color: Color(0xFF64748B)),
                      onPressed: _clearSearch,
                    )
                  : null,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
          ),
        ),

        // ── Results Dropdown ──
        if (_showResults)
          Container(
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFE2E8F0)),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x0F000000),
                  blurRadius: 8,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            child: _isLoading && _results.isEmpty
                ? const Padding(
                    padding: EdgeInsets.all(16.0),
                    child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
                  )
                : ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _results.length,
                    separatorBuilder: (ctx, i) => const Divider(height: 1),
                    itemBuilder: (context, index) {
                      final result = _results[index];
                      return ListTile(
                        leading: const Icon(Icons.location_on_outlined, color: Color(0xFF64748B)),
                        title: Text(
                          result.displayName,
                          style: const TextStyle(fontSize: 14, color: Color(0xFF0F172A)),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        onTap: () {
                          _controller.text = result.displayName;
                          _focusNode.unfocus();
                          setState(() => _showResults = false);
                          widget.onLocationSelected(result);
                        },
                      );
                    },
                  ),
          ),
      ],
    );
  }
}
