import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/app_colors.dart';

class CopyButton extends StatefulWidget {
  final String text;
  final IconData icon;
  final double size;

  const CopyButton({
    super.key,
    required this.text,
    this.icon = Icons.copy,
    this.size = 18,
  });

  @override
  State<CopyButton> createState() => _CopyButtonState();
}

class _CopyButtonState extends State<CopyButton> {
  bool _copied = false;

  Future<void> _copyToClipboard() async {
    await Clipboard.setData(ClipboardData(text: widget.text));
    setState(() => _copied = true);
    await Future.delayed(const Duration(seconds: 2));
    if (mounted) setState(() => _copied = false);
  }

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Icon(
        _copied ? Icons.check : widget.icon,
        size: widget.size,
        color: _copied ? AppColors.success : AppColors.primary,
      ),
      onPressed: _copyToClipboard,
      tooltip: _copied ? 'Copied!' : 'Copy to clipboard',
    );
  }
}
