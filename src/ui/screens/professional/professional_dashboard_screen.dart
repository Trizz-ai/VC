import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/core/services/api_service.dart';
import '../../../../frontend/lib/core/models/contact.dart';

/// Professional dashboard for attorneys and court officials
class ProfessionalDashboardScreen extends StatefulWidget {
  const ProfessionalDashboardScreen({Key? key}) : super(key: key);
  
  @override
  State<ProfessionalDashboardScreen> createState() => _ProfessionalDashboardScreenState();
}

class _ProfessionalDashboardScreenState extends State<ProfessionalDashboardScreen> {
  Map<String, dynamic>? _dashboardData;
  List<Map<String, dynamic>> _clients = [];
  bool _isLoading = true;
  
  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    final apiService = Provider.of<ApiService>(context, listen: false);
    
    try {
      // Load admin dashboard data
      final dashboard = await apiService.getAdminDashboard();
      
      // Load admin users (clients)
      final users = await apiService.getAdminUsers(limit: 10, activeOnly: true);
      
      if (mounted) {
        setState(() {
          _dashboardData = dashboard;
          _clients = users;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading dashboard: ${e.toString()}'),
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
          title: 'Professional Dashboard',
        ),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Professional Dashboard',
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Active Cases Section
            Text(
              'Active Cases',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: _dashboardData?['active_cases'] != null
                  ? ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: (_dashboardData!['active_cases'] as List).length,
                      itemBuilder: (context, index) {
                        final caseData = _dashboardData!['active_cases'][index];
                        return _buildCaseCard(
                          caseNumber: 'Case ${index + 1}',
                          title: caseData['title'] ?? 'Case',
                          status: caseData['status'] ?? 'In Progress',
                        );
                      },
                    )
                  : ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        _buildCaseCard(
                          caseNumber: 'Case 1',
                          title: 'No cases available',
                          status: 'No data',
                        ),
                      ],
                    ),
            ),
            
            const SizedBox(height: 32),
            
            // Recent Client Activity Section
            Text(
              'Recent Client Activity',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 16),
            _clients.isEmpty
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Text(
                        'No clients found',
                        style: AppTextStyles.body2.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ),
                  )
                : Column(
                    children: _clients.take(3).map((client) {
                      return _buildClientActivityItem(
                        name: '${client['first_name'] ?? ''} ${client['last_name'] ?? ''}'.trim(),
                        activity: client['last_activity'] ?? 'No recent activity',
                      );
                    }).toList(),
                  ),
            
            const SizedBox(height: 32),
            
            // Quick Access Section
            Text(
              'Quick Access',
              style: AppTextStyles.h5,
            ),
            const SizedBox(height: 16),
            VCCard(
              onTap: () {
                context.push('/admin/users');
              },
              child: Column(
                children: [
                  Icon(
                    Icons.description,
                    size: 64,
                    color: AppColors.primary,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Client Reports',
                    style: AppTextStyles.h6,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
  
  Widget _buildCaseCard({
    required String caseNumber,
    required String title,
    required String status,
  }) {
    return Container(
      width: 280,
      margin: const EdgeInsets.only(right: 16),
      child: VCCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Placeholder for case image
            Container(
              height: 120,
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Icon(
                  Icons.gavel,
                  size: 48,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              '$caseNumber: $title',
              style: AppTextStyles.h6,
            ),
            const SizedBox(height: 4),
            Text(
              'Status: $status',
              style: AppTextStyles.body2.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildClientActivityItem({
    required String name,
    required String activity,
  }) {
    return VCCard(
      margin: const EdgeInsets.only(bottom: 12),
      onTap: () {
        // TODO: Navigate to client details
      },
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: AppColors.surfaceVariant,
            child: Icon(
              Icons.person,
              color: AppColors.iconPrimary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Client: $name',
                  style: AppTextStyles.body1,
                ),
                const SizedBox(height: 4),
                Text(
                  activity,
                  style: AppTextStyles.body2.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Icon(
            Icons.arrow_forward_ios,
            size: 16,
            color: AppColors.iconSecondary,
          ),
        ],
      ),
    );
  }
}
