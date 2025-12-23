import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/ai_service.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// AI Legal Assistant Screen - Connected to Backend
class AILegalAssistantScreenConnected extends StatefulWidget {
  const AILegalAssistantScreenConnected({Key? key}) : super(key: key);
  
  @override
  State<AILegalAssistantScreenConnected> createState() => _AILegalAssistantScreenConnectedState();
}

class _AILegalAssistantScreenConnectedState extends State<AILegalAssistantScreenConnected> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  String? _conversationId;
  
  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }
  
  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;
    
    setState(() {
      _messages.add({
        'role': 'user',
        'content': message,
        'timestamp': DateTime.now(),
      });
      _isLoading = true;
    });
    
    _messageController.clear();
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final aiService = AIService(apiService);
      
      final result = await aiService.chat(
        message,
        conversationId: _conversationId,
        context: {
          'screen': 'legal_assistant',
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      
      if (mounted) {
        setState(() {
          _isLoading = false;
          
          if (result['success'] == true) {
            _conversationId = result['conversation_id'];
            _messages.add({
              'role': 'assistant',
              'content': result['message'],
              'timestamp': DateTime.now(),
            });
          } else {
            _messages.add({
              'role': 'error',
              'content': result['message'] ?? 'Failed to get response',
              'timestamp': DateTime.now(),
            });
          }
        });
        
        // Scroll to bottom
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeOut,
            );
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _messages.add({
            'role': 'error',
            'content': 'Error: ${e.toString()}',
            'timestamp': DateTime.now(),
          });
        });
      }
    }
  }
  
  Future<void> _generateReport() async {
    setState(() => _isLoading = true);
    
    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final aiService = AIService(apiService);
      
      final result = await aiService.generateLegalBrief(
        briefType: 'compliance_summary',
      );
      
      if (mounted) {
        setState(() => _isLoading = false);
        
        if (result['success'] == true) {
          _showSuccess('Report generated successfully!');
          // Add the brief to chat
          setState(() {
            _messages.add({
              'role': 'assistant',
              'content': result['brief'],
              'timestamp': DateTime.now(),
              'type': 'brief',
            });
          });
        } else {
          _showError(result['message'] ?? 'Failed to generate report');
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        _showError('Error: ${e.toString()}');
      }
    }
  }
  
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
      ),
    );
  }
  
  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.success,
      ),
    );
  }
  
  final ScrollController _scrollController = ScrollController();
  
  @override
  void initState() {
    super.initState();
    // Add welcome message
    _messages.add({
      'role': 'assistant',
      'content': 'Hello! How can I assist you today?',
      'timestamp': DateTime.now(),
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'AI Legal Assistant',
      ),
      body: Column(
        children: [
          // Chat messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length && _isLoading) {
                  return _buildLoadingMessage();
                }
                
                final message = _messages[index];
                return _buildMessage(message);
              },
            ),
          ),
          
          // Quick action buttons
          if (_messages.length <= 1)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _buildQuickAction(
                    'Generate Q3 Report',
                    Icons.description,
                    () => _sendMessage(),
                  ),
                  _buildQuickAction(
                    'Financial Summary',
                    Icons.attach_money,
                    () => _sendMessage(),
                  ),
                  _buildQuickAction(
                    'View Calendar',
                    Icons.calendar_today,
                    () => context.push('/calendar'),
                  ),
                ],
              ),
            ),
          
          // Input field
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: 'Ask your legal assistant...',
                      hintStyle: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide(color: AppColors.border),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                    enabled: !_isLoading,
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.send),
                    color: AppColors.onPrimary,
                    onPressed: _isLoading ? null : _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMessage(Map<String, dynamic> message) {
    final isUser = message['role'] == 'user';
    final isError = message['role'] == 'error';
    
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser)
            Container(
              width: 32,
              height: 32,
              margin: const EdgeInsets.only(right: 12),
              decoration: BoxDecoration(
                color: isError ? AppColors.error : AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: Icon(
                isError ? Icons.error_outline : Icons.smart_toy,
                color: AppColors.onPrimary,
                size: 20,
              ),
            ),
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isUser ? AppColors.primary : AppColors.surface,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                message['content'],
                style: AppTextStyles.body1.copyWith(
                  color: isUser ? AppColors.onPrimary : AppColors.textPrimary,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildLoadingMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 32,
            height: 32,
            margin: const EdgeInsets.only(right: 12),
            decoration: BoxDecoration(
              color: AppColors.primary,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.smart_toy,
              color: AppColors.onPrimary,
              size: 20,
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Thinking...',
                  style: AppTextStyles.body1.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildQuickAction(String label, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: AppColors.primary),
            const SizedBox(width: 8),
            Text(
              label,
              style: AppTextStyles.caption.copyWith(
                color: AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}

