import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';

/// Help screen with search and support options
class HelpScreen extends StatelessWidget {
  const HelpScreen({Key? key}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Help',
        showDrawer: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: () {
              // TODO: Show help menu
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Help Button
            VCButton(
              text: 'Help',
              onPressed: () {
                // TODO: Show help options
              },
              width: double.infinity,
            ),
            const SizedBox(height: 24),
            
            // Search Bar
            VCTextField(
              hint: 'What do you need help verifying',
              prefixIcon: Icons.search,
              suffixIcon: IconButton(
                icon: const Icon(Icons.mic),
                onPressed: () {
                  // TODO: Voice input
                },
              ),
            ),
            const SizedBox(height: 24),
            
            // Quick Filters
            Row(
              children: [
                Expanded(
                  child: _buildFilterChip('Meeting Type'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildFilterChip('Meeting Fr...'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildFilterChip('Meeting Du...'),
                ),
              ],
            ),
          ],
        ),
      ),
      bottomNavigationBar: const VCBottomNavBar(
        currentIndex: 0, // Help is accessible via drawer, use home index
      ),
    );
  }
  
  Widget _buildFilterChip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.divider,
        ),
      ),
      child: Center(
        child: Text(
          label,
          style: AppTextStyles.body2,
        ),
      ),
    );
  }
}

