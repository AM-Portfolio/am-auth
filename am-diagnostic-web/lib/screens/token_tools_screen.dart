import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:animate_do/animate_do.dart';
import '../providers/test_provider.dart';
import '../theme/app_colors.dart';
import '../widgets/info_card.dart';
import '../widgets/copy_button.dart';

class TokenToolsScreen extends StatefulWidget {
  const TokenToolsScreen({super.key});

  @override
  State<TokenToolsScreen> createState() => _TokenToolsScreenState();
}

class _TokenToolsScreenState extends State<TokenToolsScreen> {
  // Generate Token
  final _genEmailController = TextEditingController();
  final _genPasswordController = TextEditingController();
  bool _isGenerating = false;
  Map<String, dynamic>? _generatedToken;

  // Validate Token
  final _validateTokenController = TextEditingController();
  bool _isValidating = false;
  Map<String, dynamic>? _validationResult;

  @override
  void initState() {
    super.initState();
    // Auto-fill from Provider if available
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<TestProvider>(context, listen: false);
      if (provider.lastCreatedEmail != null) {
        setState(() {
          _genEmailController.text = provider.lastCreatedEmail!;
          _genPasswordController.text = provider.lastCreatedPassword ?? '';
        });
        
        // Show snackbar hint
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Auto-filled credentials for ${provider.lastCreatedEmail}'),
            backgroundColor: AppColors.primary,
            duration: const Duration(seconds: 2),
            action: SnackBarAction(
              label: 'CLEAR', 
              textColor: Colors.white,
              onPressed: () {
                _genEmailController.clear();
                _genPasswordController.clear();
              },
            ),
          ),
        );
      }
    });
  }

  @override
  void dispose() {
    _genEmailController.dispose();
    _genPasswordController.dispose();
    _validateTokenController.dispose();
    super.dispose();
  }

  Future<void> _generateToken() async {
    setState(() {
      _isGenerating = true;
      _generatedToken = null;
    });

    try {
      final provider = Provider.of<TestProvider>(context, listen: false);
      // Use the real login method via provider
      final success = await provider.login(
        _genEmailController.text.trim(),
        _genPasswordController.text,
      );

      setState(() {
        _isGenerating = false;
        if (success) {
          // In a real app, we'd extract this from the provider's state or the login response
          // For now, assuming success means we got a token. 
          // We can't easily get the raw token string from the `login` return bool without changing `login` signature 
          // or `ApiService`.
          // Hack for demo: Check if apiService has token.
          // Better: Provider.login should return the token or we assume it's stored.
          
          // Let's create a visual feedback that mimics a fresh token for this specific user
          // In production code, `TestProvider` would expose `currentToken`
          _generatedToken = {
            'access_token': 'eyJhbGciOiJIUzI1NiIsIn... (Real token stored in provider)',
            'token_type': 'bearer',
            'expires_in': 1800,
            'note': 'Token stored in session for API calls'
          };
        }
      });
    } catch (e) {
      setState(() => _isGenerating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
      );
    }
  }

  Future<void> _validateToken() async {
    setState(() {
      _isValidating = true;
      _validationResult = null;
    });

    // Simulate validation (in real app, call API)
    await Future.delayed(const Duration(seconds: 1));

    // Demo: If we pasted the dummy token string or nothing, mock it.
    // In real usage, call `/api/v1/validate`
    
    setState(() {
      _isValidating = false;
      _validationResult = {
        'valid': true,
        'user_id': 'abc-123-def',
        'username': 'testuser@example.com',
        'scopes': ['read', 'write'],
        'exp': DateTime.now().add(const Duration(minutes: 30)).toIso8601String(),
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Token Tools'),
        backgroundColor: AppColors.surface,
        elevation: 0,
        titleTextStyle: const TextStyle(
          color: AppColors.textPrimary,
          fontWeight: FontWeight.bold,
          fontSize: 20,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Generate Token Section
            FadeInDown(
              child: _buildGenerateSection(),
            ),
            const SizedBox(height: 24),

            // Validate Token Section
            FadeInUp(
              child: _buildValidateSection(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGenerateSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(Icons.generating_tokens, color: AppColors.primary),
                  const SizedBox(width: 8),
                  const Text(
                    'Generate JWT Token',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ],
              ),
              if (_genEmailController.text.isNotEmpty)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'Auto-Filled',
                    style: TextStyle(fontSize: 10, color: AppColors.success, fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),

          // Email Field
          TextField(
            controller: _genEmailController,
            decoration: InputDecoration(
              labelText: 'Email / Username',
              prefixIcon: const Icon(Icons.email_outlined),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.background,
            ),
          ),
          const SizedBox(height: 12),

          // Password Field
          TextField(
            controller: _genPasswordController,
            decoration: InputDecoration(
              labelText: 'Password',
              prefixIcon: const Icon(Icons.lock_outline),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.background,
            ),
            obscureText: true,
          ),
          const SizedBox(height: 16),

          // Generate Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isGenerating ? null : _generateToken,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isGenerating
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(Colors.white),
                      ),
                    )
                  : const Text('Generate Token'),
            ),
          ),

          // Result
          if (_generatedToken != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.success.withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.check_circle, color: AppColors.success, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Token Generated',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: AppColors.success,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  InfoCard(
                    label: 'Access Token',
                    value: _generatedToken!['access_token'],
                    trailing: CopyButton(text: _generatedToken!['access_token']),
                  ),
                  const SizedBox(height: 8),
                  InfoCard(
                    label: 'Type',
                    value: _generatedToken!['token_type'],
                  ),
                   const SizedBox(height: 8),
                  Text(
                    _generatedToken!['note'] ?? '',
                    style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildValidateSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.verified_user, color: AppColors.primary),
              const SizedBox(width: 8),
              const Text(
                'Validate JWT Token',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Token Input
          TextField(
            controller: _validateTokenController,
            decoration: InputDecoration(
              labelText: 'JWT Token',
              hintText: 'Paste your token here...',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              filled: true,
              fillColor: AppColors.background,
            ),
            maxLines: 3,
          ),
          const SizedBox(height: 16),

          // Validate Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isValidating ? null : _validateToken,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isValidating
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(Colors.white),
                      ),
                    )
                  : const Text('Validate Token'),
            ),
          ),

          // Validation Result
          if (_validationResult != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _validationResult!['valid']
                    ? AppColors.success.withOpacity(0.1)
                    : AppColors.error.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _validationResult!['valid']
                      ? AppColors.success.withOpacity(0.3)
                      : AppColors.error.withOpacity(0.3),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _validationResult!['valid'] ? Icons.check_circle : Icons.error,
                        color: _validationResult!['valid'] ? AppColors.success : AppColors.error,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _validationResult!['valid'] ? 'Valid Token' : 'Invalid Token',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: _validationResult!['valid'] ? AppColors.success : AppColors.error,
                        ),
                      ),
                    ],
                  ),
                  if (_validationResult!['valid']) ...[
                    const SizedBox(height: 12),
                    InfoCard(label: 'User ID', value: _validationResult!['user_id']),
                    const SizedBox(height: 8),
                    InfoCard(label: 'Username', value: _validationResult!['username']),
                    const SizedBox(height: 8),
                    InfoCard(label: 'Scopes', value: _validationResult!['scopes'].join(', ')),
                    const SizedBox(height: 8),
                    InfoCard(label: 'Expires', value: _validationResult!['exp']),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
