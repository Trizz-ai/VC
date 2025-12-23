import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/widgets.dart';
import '../../../../frontend/lib/features/meetings/providers/meeting_provider.dart';
import '../../../../frontend/lib/core/models/meeting.dart';
import '../../../../frontend/lib/core/services/location_service.dart';
import 'package:geolocator/geolocator.dart';

/// Meeting finder screen with map and nearby meetings list
class MeetingFinderScreen extends StatefulWidget {
  const MeetingFinderScreen({Key? key}) : super(key: key);
  
  @override
  State<MeetingFinderScreen> createState() => _MeetingFinderScreenState();
}

class _MeetingFinderScreenState extends State<MeetingFinderScreen> {
  String? _currentAddress;
  Position? _currentPosition;
  
  @override
  void initState() {
    super.initState();
    // Use WidgetsBinding to ensure context is available
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadMeetings();
      _getCurrentLocation();
    });
  }
  
  Future<void> _loadMeetings() async {
    if (!mounted) return;
    
    try {
      final meetingProvider = Provider.of<MeetingProvider>(context, listen: false);
      // loadNearbyMeetings gets location internally, no need to pass lat/lng
      await meetingProvider.loadNearbyMeetings();
    } catch (e) {
      if (mounted) {
        debugPrint('Error loading meetings: $e');
      }
    }
  }
  
  Future<void> _getCurrentLocation() async {
    if (!mounted) return;
    
    try {
      final locationService = Provider.of<LocationService>(context, listen: false);
      final position = await locationService.getCurrentPosition();
      if (position != null && mounted) {
        setState(() {
          _currentPosition = position;
          _currentAddress = '123 Legal St, Justice City'; // Would use geocoding in real app
        });
      }
    } catch (e) {
      if (mounted) {
        debugPrint('Error getting location: $e');
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      drawer: const VCNavigationDrawer(),
      appBar: VCAppBar(
        title: 'Find Meetings',
      ),
      body: Stack(
        children: [
          // Map Section (would use Google Maps widget in real implementation)
          Container(
            color: AppColors.surface,
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
          
          // Search Bar Overlay
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
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
                      'Search meetings',
                      style: AppTextStyles.body2.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Bottom Sheet with Meetings List
          DraggableScrollableSheet(
            initialChildSize: 0.5,
            minChildSize: 0.3,
            maxChildSize: 0.9,
            builder: (context, scrollController) {
              return Consumer<MeetingProvider>(
                builder: (context, meetingProvider, _) {
                  final meetings = meetingProvider.nearbyMeetings;
                  
                  return Container(
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                    ),
                    child: Column(
                      children: [
                        // Handle
                        Container(
                          margin: const EdgeInsets.only(top: 12),
                          width: 40,
                          height: 4,
                          decoration: BoxDecoration(
                            color: AppColors.divider,
                            borderRadius: BorderRadius.circular(2),
                          ),
                        ),
                        
                        // Header
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Row(
                            children: [
                              Text(
                                'Nearby AA Meetings',
                                style: AppTextStyles.h5,
                              ),
                              const Spacer(),
                              IconButton(
                                icon: const Icon(Icons.send),
                                onPressed: () {
                                  // TODO: Share meetings
                                },
                              ),
                            ],
                          ),
                        ),
                        
                        // Meetings List
                        meetingProvider.isLoadingNearby
                            ? Expanded(
                                child: Center(
                                  child: CircularProgressIndicator(
                                    color: AppColors.primary,
                                  ),
                                ),
                              )
                            : meetings.isEmpty
                                ? Expanded(
                                    child: Center(
                                      child: Column(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.location_off,
                                            size: 48,
                                            color: AppColors.textSecondary,
                                          ),
                                          const SizedBox(height: 16),
                                          Text(
                                            'No meetings found nearby',
                                            style: AppTextStyles.body2.copyWith(
                                              color: AppColors.textSecondary,
                                            ),
                                          ),
                                          if (meetingProvider.errorMessage != null) ...[
                                            const SizedBox(height: 8),
                                            Text(
                                              meetingProvider.errorMessage!,
                                              style: AppTextStyles.caption.copyWith(
                                                color: AppColors.error,
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                          ],
                                        ],
                                      ),
                                    ),
                                  )
                                : Expanded(
                                    child: ListView.builder(
                                      controller: scrollController,
                                      padding: const EdgeInsets.symmetric(horizontal: 16),
                                      itemCount: meetings.length,
                                      itemBuilder: (context, index) {
                                        final meeting = meetings[index];
                                        return _buildMeetingCard(meeting);
                                      },
                                    ),
                                  ),
                        
                        // Footer with Current Location
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceVariant,
                            borderRadius: const BorderRadius.vertical(bottom: Radius.circular(20)),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.location_on,
                                color: AppColors.primary,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _currentAddress ?? 'Getting location...',
                                      style: AppTextStyles.body2,
                                    ),
                                    const SizedBox(height: 4),
                                    Row(
                                      children: [
                                        Icon(
                                          Icons.check_circle,
                                          color: AppColors.success,
                                          size: 16,
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          'Last Verified: Today, ${DateTime.now().hour}:${DateTime.now().minute.toString().padLeft(2, '0')} ${DateTime.now().hour >= 12 ? 'PM' : 'AM'}',
                                          style: AppTextStyles.caption.copyWith(
                                            color: AppColors.success,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                },
              );
            },
          ),
        ],
      ),
      bottomNavigationBar: const VCBottomNavBar(),
    );
  }
  
  Widget _buildMeetingCard(Meeting meeting) {
    return VCCard(
      margin: const EdgeInsets.only(bottom: 12),
      onTap: () {
        context.push('/meetings/${meeting.id}');
      },
      child: Row(
        children: [
          Icon(
            Icons.location_on,
            color: AppColors.primary,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  meeting.name,
                  style: AppTextStyles.h6,
                ),
                const SizedBox(height: 4),
                Text(
                  meeting.address,
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
