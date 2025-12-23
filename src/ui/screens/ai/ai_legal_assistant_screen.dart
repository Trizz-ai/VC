import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// AI Legal Assistant chat screen for legal queries
class AILegalAssistantScreen extends StatefulWidget {
  const AILegalAssistantScreen({Key? key}) : super(key: key);
  
  @override
  State<AILegalAssistantScreen> createState() => _AILegalAssistantScreenState();
}

class _AILegalAssistantScreenState extends State<AILegalAssistantScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  final List<ChatMessage> _messages = [
    ChatMessage(
      text: 'Hello! How can I assist you today?',
      isUser: false,
    ),
  ];
  
  bool _isLoading = false;
  
  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
  
  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty || _isLoading) return;
    
    final userMessage = _messageController.text.trim();
    _messageController.clear();
    
    setState(() {
      _messages.add(ChatMessage(
        text: userMessage,
        isUser: true,
      ));
      _isLoading = true;
    });
    
    _scrollToBottom();
    
    try {
      // TODO: Call AI Legal API endpoint
      // final apiService = Provider.of<ApiService>(context, listen: false);
      // final response = await apiService.sendLegalAIMessage(userMessage);
      
      // For now, simulate AI response
      await Future.delayed(const Duration(seconds: 1));
      
      String aiResponse = 'I understand your legal question. Let me help you with that.';
      List<ChatAction>? actions;
      
      // Check if it's a meeting query
      if (userMessage.toLowerCase().contains('meeting') && userMessage.toLowerCase().contains('custody')) {
        aiResponse = 'Here are the meetings about custody in October:\n\n• Oct 15, 2023 | Custody Review\n• Oct 26, 2023 | Co-Parenting';
        actions = [
          ChatAction(
            text: 'Email Report',
            icon: Icons.email,
            onPressed: () {
              // TODO: Email report
            },
          ),
          ChatAction(
            text: 'View Calendar',
            icon: Icons.calendar_today,
            onPressed: () {
              // TODO: View calendar
            },
          ),
        ];
      } else if (userMessage.toLowerCase().contains('balance') || userMessage.toLowerCase().contains('owe')) {
        aiResponse = 'Your outstanding balance for last month\'s sessions is \$350.';
        actions = [
          ChatAction(
            text: 'Pay Now',
            icon: Icons.payment,
            onPressed: () {
              context.push('/subscription');
            },
          ),
          ChatAction(
            text: 'View Invoices',
            icon: Icons.receipt,
            onPressed: () {
              // TODO: View invoices
            },
          ),
        ];
      }
      
      setState(() {
        _messages.add(ChatMessage(
          text: aiResponse,
          isUser: false,
          actions: actions,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add(ChatMessage(
            text: 'Sorry, I encountered an error. Please try again.',
            isUser: false,
          ));
          _isLoading = false;
        });
        _scrollToBottom();
      }
    }
  }
  
  void _scrollToBottom() {
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
          // Chat Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) {
                  return Padding(
                    padding: const EdgeInsets.all(16),
                    child: Center(
                      child: CircularProgressIndicator(),
                    ),
                  );
                }
                return _buildMessageBubble(_messages[index]);
              },
            ),
          ),
          
          // Input Bar
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              boxShadow: [
                BoxShadow(
                  color: AppColors.shadowDark,
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: AppColors.inputBackground,
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Ask your legal assistant...',
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20,
                          vertical: 12,
                        ),
                        hintStyle: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      style: AppTextStyles.body2,
                      maxLines: null,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                      enabled: !_isLoading,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.send),
                  color: AppColors.primary,
                  onPressed: _isLoading ? null : _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMessageBubble(ChatMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment: message.isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: AppColors.surfaceVariant,
              child: Icon(
                Icons.gavel,
                size: 20,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: message.isUser
                    ? AppColors.primary
                    : AppColors.surface,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    message.text,
                    style: AppTextStyles.body2.copyWith(
                      color: message.isUser
                          ? AppColors.onPrimary
                          : AppColors.onSurface,
                    ),
                  ),
                  if (message.actions != null) ...[
                    const SizedBox(height: 12),
                    ...message.actions!.map((action) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: VCButton(
                        text: action.text,
                        icon: action.icon,
                        type: VCButtonType.outlined,
                        onPressed: action.onPressed,
                        width: double.infinity,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                      ),
                    )),
                  ],
                ],
              ),
            ),
          ),
          if (message.isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: AppColors.surfaceVariant,
              child: Icon(
                Icons.person,
                size: 20,
                color: AppColors.iconPrimary,
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final List<ChatAction>? actions;
  
  ChatMessage({
    required this.text,
    required this.isUser,
    this.actions,
  });
}

class ChatAction {
  final String text;
  final IconData? icon;
  final VoidCallback? onPressed;
  
  ChatAction({
    required this.text,
    this.icon,
    this.onPressed,
  });
}
