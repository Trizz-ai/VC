import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/services/api_service.dart';
import '../../../../frontend/lib/core/models/contact.dart';

/// Personal log detail screen showing individual log entry
class PersonalLogDetailScreen extends StatefulWidget {
  final String? sessionId;
  
  const PersonalLogDetailScreen({Key? key, this.sessionId}) : super(key: key);
  
  @override
  State<PersonalLogDetailScreen> createState() => _PersonalLogDetailScreenState();
}

class _PersonalLogDetailScreenState extends State<PersonalLogDetailScreen> {
  Map<String, dynamic>? _sessionDetails;
  Contact? _currentUser;
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }
  
  Future<void> _loadData() async {
    final sessionProvider = Provider.of<SessionProvider>(context, listen: false);
    final apiService = Provider.of<ApiService>(context, listen: false);
    
    try {
      String? sessionId = widget.sessionId;
      
      // If no session ID, try to get from session history
      if (sessionId == null) {
        await sessionProvider.loadSessionHistory(limit: 1, offset: 0);
        if (sessionProvider.sessionHistory.isNotEmpty) {
          sessionId = sessionProvider.sessionHistory.first.id;
        }
      }
      
      if (sessionId == null) {
        throw Exception('No session found');
      }
      
      // Load session details
      final details = await sessionProvider.getSessionDetailsFull(sessionId);
      
      // Load current user
      final user = await apiService.getCurrentUser();
      
      if (mounted) {
        setState(() {
          _sessionDetails = details;
          _currentUser = user;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load log: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        backgroundColor: AppColors.background,
        drawer: const VCNavigationDrawer(),
        appBar: VCAppBar(
          title: 'Personal Log',
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Personal Log',
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // TODO: Show options menu
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // User Information Card
            VCCard(
              child: Row(
                children: [
                  // Profile Picture
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppColors.surfaceVariant,
                    ),
                    child: Icon(
                      Icons.person,
                      color: AppColors.textSecondary,
                      size: 32,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _currentUser != null
                              ? '${_currentUser!.firstName} ${_currentUser!.lastName}'
                              : 'User',
                          style: AppTextStyles.h5,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _sessionDetails != null && _sessionDetails!['check_in_latitude'] != null
                              ? 'GPS: ${_sessionDetails!['check_in_latitude'].toStringAsFixed(4)}° N, ${_sessionDetails!['check_in_longitude'].toStringAsFixed(4)}° W'
                              : 'GPS: Location unavailable',
                          style: AppTextStyles.body2.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Map Section
            Container(
              height: 300,
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.map,
                      size: 64,
                      color: AppColors.textSecondary,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Map View',
                      style: AppTextStyles.body1.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Log Details Card
            VCCard(
              child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Timestamp',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          Text(
                            _sessionDetails != null && _sessionDetails!['check_in_time'] != null
                                ? DateFormat('h:mm a, d MMM yyyy').format(DateTime.parse(_sessionDetails!['check_in_time']))
                                : 'N/A',
                            style: AppTextStyles.body1.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                      const Divider(height: 32),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Status',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          Row(
                            children: [
                              Icon(
                                Icons.verified,
                                color: AppColors.success,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              VCStatusBadge(
                                label: _sessionDetails != null && _sessionDetails!['check_out_time'] != null
                                    ? 'Verified by AI'
                                    : 'In Progress',
                                type: _sessionDetails != null && _sessionDetails!['check_out_time'] != null
                                    ? VCStatusType.verified
                                    : VCStatusType.pending,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Action Buttons
            VCButton(
              text: 'Log Dashboard',
              onPressed: () {
                context.go('/logs/personal');
              },
              width: double.infinity,
            ),
            const SizedBox(height: 12),
            VCButton(
              text: 'Download Log',
              type: VCButtonType.text,
              onPressed: () {
                // TODO: Download PDF log
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Download coming soon'),
                    backgroundColor: AppColors.info,
                  ),
                );
              },
              width: double.infinity,
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
}

