import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/api_service.dart';

/// AI Assistant chat screen
class AIAssistantScreen extends StatefulWidget {
  const AIAssistantScreen({Key? key}) : super(key: key);
  
  @override
  State<AIAssistantScreen> createState() => _AIAssistantScreenState();
}

class _AIAssistantScreenState extends State<AIAssistantScreen> {
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
      // TODO: Call AI API endpoint
      // final apiService = Provider.of<ApiService>(context, listen: false);
      // final response = await apiService.sendAIMessage(userMessage);
      
      // For now, simulate AI response
      await Future.delayed(const Duration(seconds: 1));
      
      String aiResponse = 'I understand you\'re asking about: $userMessage. How can I help you with that?';
      
      // Check if it's a meeting query
      if (userMessage.toLowerCase().contains('meeting')) {
        aiResponse = 'Here are some AA meetings nearby:\n\n• Serenity Group - Today, 7:00 PM - 123 Main St\n• Steps to Sobriety - Tomorrow, 10:00 AM - 456 Oak Ave\n• One Day at a Time - Tomorrow, 8:00 PM - 789 Pine Ln';
        
        setState(() {
          _messages.add(ChatMessage(
            text: aiResponse,
            isUser: false,
            actions: [
              ChatAction(
                text: 'View on Map',
                icon: Icons.map,
                onPressed: () {
                  context.push('/meetings/finder');
                },
              ),
            ],
          ));
          _isLoading = false;
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            text: aiResponse,
            isUser: false,
          ));
          _isLoading = false;
        });
      }
      
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
        title: 'Aya AI Assistant',
        actions: [
          Container(
            width: 32,
            height: 32,
            margin: const EdgeInsets.only(right: 8),
            decoration: BoxDecoration(
              color: AppColors.success,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check,
              color: AppColors.onPrimary,
              size: 20,
            ),
          ),
        ],
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
                        hintText: 'Type your message',
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
                  icon: const Icon(Icons.attach_file),
                  onPressed: () {
                    // TODO: Attach file
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.mic),
                  onPressed: () {
                    // TODO: Voice input
                  },
                ),
                VCButton(
                  text: 'Send',
                  onPressed: _isLoading ? null : _sendMessage,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: const VCBottomNavBar(),
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
                Icons.smart_toy,
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
                  if (!message.isUser)
                    Text(
                      'Aya AI Assistant',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  if (!message.isUser) const SizedBox(height: 4),
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
