import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/sessions/providers/session_provider.dart';
import '../../../../frontend/lib/core/models/session.dart';

/// Compliance journey screen showing progress and metrics
class ComplianceJourneyScreen extends StatefulWidget {
  const ComplianceJourneyScreen({Key? key}) : super(key: key);
  
  @override
  State<ComplianceJourneyScreen> createState() => _ComplianceJourneyScreenState();
}

class _ComplianceJourneyScreenState extends State<ComplianceJourneyScreen> {
  Map<String, dynamic>? _statistics;
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
    
    // Load session history
    await sessionProvider.loadSessionHistory(limit: 50, offset: 0);
    
    // Load statistics
    try {
      final stats = await sessionProvider.getStatistics(
        startDate: DateTime.now().subtract(const Duration(days: 30)),
        endDate: DateTime.now(),
      );
      if (mounted) {
        setState(() {
          _statistics = stats;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
  
  int _calculateCompliancePoints(List<Session> sessions) {
    // Calculate points based on completed sessions
    return sessions.where((s) => s.isCheckedOut).length * 150;
  }
  
  int _calculateBadges(List<Session> sessions) {
    // Calculate badges based on milestones
    final completedSessions = sessions.where((s) => s.isCheckedOut).length;
    if (completedSessions >= 10) return 3;
    if (completedSessions >= 5) return 2;
    if (completedSessions >= 1) return 1;
    return 0;
  }
  
  @override
  Widget build(BuildContext context) {
    final sessionProvider = Provider.of<SessionProvider>(context);
    final sessions = sessionProvider.sessionHistory;
    final compliancePoints = _statistics?['total_points'] ?? _calculateCompliancePoints(sessions);
    final badges = _statistics?['badges'] ?? _calculateBadges(sessions);
    
    // Get recent sessions for timeline
    final recentSessions = sessions.take(5).toList();
    
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Compliance Journey',
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Search Bar
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.search,
                          color: AppColors.iconSecondary,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Search meetings (last 30 days)',
                            style: AppTextStyles.body2.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Compliance Journey Section
                  Text(
                    'Your Compliance Journey',
                    style: AppTextStyles.h5,
                  ),
                  const SizedBox(height: 16),
                  VCCard(
                    child: Row(
                      children: [
                        Icon(
                          Icons.emoji_events,
                          color: AppColors.primary,
                          size: 32,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Text(
                            "Keep up the great work! You're making excellent progress on your compliance journey.",
                            style: AppTextStyles.body2,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // Progress Timeline
                  _buildProgressTimeline(recentSessions),
                  const SizedBox(height: 32),
                  
                  // Compliance Metrics
                  Row(
                    children: [
                      Expanded(
                        child: VCCard(
                          child: Column(
                            children: [
                              Icon(
                                Icons.star_outline,
                                color: AppColors.primary,
                                size: 32,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Compliance Points:',
                                style: AppTextStyles.body2.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '$compliancePoints',
                                style: AppTextStyles.h3.copyWith(
                                  color: AppColors.primary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: VCCard(
                          child: Column(
                            children: [
                              Icon(
                                Icons.workspace_premium,
                                color: AppColors.secondary,
                                size: 32,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Badges Earned:',
                                style: AppTextStyles.body2.copyWith(
                                  color: AppColors.textSecondary,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '$badges',
                                style: AppTextStyles.h3.copyWith(
                                  color: AppColors.secondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Payment Reminder Alert Card
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppColors.error,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.white.withOpacity(0.2),
                          ),
                          child: const Icon(
                            Icons.error_outline,
                            color: Colors.white,
                            size: 16,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            "Heads up! A payment for your upcoming session is due soon. Let's keep that streak going!",
                            style: AppTextStyles.body2.copyWith(
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
      bottomNavigationBar: const VCBottomNavBar(
        currentIndex: VCBottomNavBar.getIndexForRoute('/compliance'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          context.push('/subscription');
        },
        label: Text(
          'Pay',
          style: AppTextStyles.button,
        ),
        icon: const Icon(Icons.payment),
      ),
    );
  }
  
  Widget _buildProgressTimeline(List<Session> sessions) {
    if (sessions.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Text(
            'No sessions yet',
            style: AppTextStyles.body2.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ),
      );
    }
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: sessions.asMap().entries.map((entry) {
          final index = entry.key;
          final session = entry.value;
          final isLast = index == sessions.length - 1;
          
          return Expanded(
            child: Column(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: session.isCheckedOut
                        ? AppColors.success
                        : AppColors.primary,
                  ),
                  child: session.isCheckedOut
                      ? const Icon(
                          Icons.check,
                          color: AppColors.onPrimary,
                          size: 20,
                        )
                      : Icon(
                          Icons.calendar_today,
                          color: AppColors.onPrimary,
                          size: 16,
                        ),
                ),
                const SizedBox(height: 8),
                Text(
                  DateFormat('MMM d').format(session.createdAt),
                  style: AppTextStyles.caption,
                ),
                if (session.isCheckedOut)
                  Text(
                    'Completed',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.success,
                    ),
                  ),
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 2,
                      color: session.isCheckedOut
                          ? AppColors.success
                          : AppColors.primary,
                    ),
                  ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
  
}
