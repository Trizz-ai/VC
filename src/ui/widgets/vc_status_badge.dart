import 'package:flutter/material.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';

/// Status badge widget for displaying verification status
class VCStatusBadge extends StatelessWidget {
  final String label;
  final VCStatusType type;
  final IconData? icon;
  
  const VCStatusBadge({
    Key? key,
    required this.label,
    this.type = VCStatusType.verified,
    this.icon,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    Color backgroundColor;
    Color textColor;
    IconData displayIcon;
    
    switch (type) {
      case VCStatusType.verified:
        backgroundColor = AppColors.success.withOpacity(0.2);
        textColor = AppColors.success;
        displayIcon = icon ?? Icons.check_circle;
        break;
      case VCStatusType.pending:
        backgroundColor = AppColors.warning.withOpacity(0.2);
        textColor = AppColors.warning;
        displayIcon = icon ?? Icons.pending;
        break;
      case VCStatusType.failed:
        backgroundColor = AppColors.error.withOpacity(0.2);
        textColor = AppColors.error;
        displayIcon = icon ?? Icons.error;
        break;
      case VCStatusType.cancelled:
        backgroundColor = AppColors.cancelled.withOpacity(0.2);
        textColor = AppColors.cancelled;
        displayIcon = icon ?? Icons.cancel;
        break;
    }
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(displayIcon, size: 16, color: textColor),
          const SizedBox(width: 6),
          Text(
            label,
            style: AppTextStyles.caption.copyWith(
              color: textColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

enum VCStatusType {
  verified,
  pending,
  failed,
  cancelled,
}



