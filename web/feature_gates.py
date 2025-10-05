#!/usr/bin/env python3
"""
APEX Feature Gating System
Manages feature access based on license tiers with visual indicators
Following APEX three-tier architecture pattern
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio

class LicenseTier(Enum):
    """License tier definitions"""
    BASIC = "basic"
    TRIAL = "trial" 
    PREMIUM = "premium"

# Feature tier definitions with metadata
FEATURE_TIERS = {
    LicenseTier.BASIC: {
        "name": "Basic (Free)",
        "features": ["core_k8s", "basic_terminal", "system_status"],
        "color": "#6c757d",  # Gray
        "icon": "🔓",
        "description": "Essential cloud operations"
    },
    LicenseTier.TRIAL: {
        "name": "Trial (30 days)", 
        "features": [
            "core_k8s", "basic_terminal", "system_status",
            "kiali_connect", "aws_sso", "gcp_auth", "live_logs"
        ],
        "color": "#17a2b8",  # Cyan
        "icon": "🆓",
        "description": "Full access during trial period"
    },
    LicenseTier.PREMIUM: {
        "name": "Premium",
        "features": ["all"],  # All features unlocked
        "color": "#28a745",  # Green  
        "icon": "👑",
        "description": "Complete enterprise feature set"
    }
}

# Individual feature definitions
FEATURE_DEFINITIONS = {
    # BASIC Features (Always available)
    "core_k8s": {
        "required_tier": LicenseTier.BASIC,
        "name": "Core K8s Operations",
        "description": "Basic kubectl commands (get pods, services, nodes)",
        "icon": "📦",
        "category": "core"
    },
    "basic_terminal": {
        "required_tier": LicenseTier.BASIC,
        "name": "Terminal Access", 
        "description": "Basic terminal with command execution",
        "icon": "⚡",
        "category": "core"
    },
    "system_status": {
        "required_tier": LicenseTier.BASIC,
        "name": "System Status",
        "description": "View system health and authentication status", 
        "icon": "📊",
        "category": "core"
    },
    
    # TRIAL+ Features
    "kiali_connect": {
        "required_tier": LicenseTier.TRIAL,
        "name": "Kiali Port Forwarding",
        "description": "Setup kubectl port forwarding for Kiali",
        "icon": "🚀", 
        "category": "gcp"
    },
    "aws_sso": {
        "required_tier": LicenseTier.TRIAL,
        "name": "AWS SSO Authentication",
        "description": "AWS Single Sign-On integration",
        "icon": "🔐",
        "category": "aws"
    },
    "gcp_auth": {
        "required_tier": LicenseTier.TRIAL,
        "name": "GCP Authentication", 
        "description": "Google Cloud Platform authentication",
        "icon": "🌐",
        "category": "gcp"
    },
    "live_logs": {
        "required_tier": LicenseTier.TRIAL,
        "name": "Live Log Streaming",
        "description": "Real-time log streaming from pods",
        "icon": "📋",
        "category": "core"
    },
    "ecs_ops": {
        "required_tier": LicenseTier.TRIAL,
        "name": "ECS Operations",
        "description": "Amazon ECS cluster and service management",
        "icon": "🚀",
        "category": "aws"
    },
    "cloudwatch_logs": {
        "required_tier": LicenseTier.TRIAL,
        "name": "CloudWatch Logs",
        "description": "AWS CloudWatch log streaming and analysis",
        "icon": "📜",
        "category": "aws"
    },
    "active_monitoring": {
        "required_tier": LicenseTier.TRIAL,
        "name": "Active Connection Monitoring",
        "description": "Monitor active connections and port forwards",
        "icon": "🔗",
        "category": "core"
    },
    
    # PREMIUM Features
    "kiali_dashboard": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "Kiali Dashboard Opening", 
        "description": "Auto-open browser tabs for Kiali dashboards",
        "icon": "🔗",
        "category": "gcp"
    },
    "rds_connect": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "RDS Database Connections",
        "description": "Direct RDS database connections with tunneling", 
        "icon": "💾",
        "category": "aws"
    },
    "ci_cd_ops": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "CI/CD Operations",
        "description": "Git integration and CI/CD pipeline management",
        "icon": "🔄", 
        "category": "advanced"
    },
    "advanced_monitoring": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "Advanced Monitoring",
        "description": "Comprehensive system monitoring and alerts",
        "icon": "📈",
        "category": "advanced"
    },
    "automation_scripts": {
        "required_tier": LicenseTier.PREMIUM, 
        "name": "Automation Scripts",
        "description": "Custom automation and deployment scripts",
        "icon": "🤖",
        "category": "advanced"
    },
    "bulk_operations": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "Bulk Operations", 
        "description": "Multi-cluster and bulk resource management",
        "icon": "⚡",
        "category": "advanced"
    },
    "data_analysis": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "Data Analysis",
        "description": "Advanced analytics and performance metrics",
        "icon": "📈",
        "category": "advanced"
    },
    "system_diagnostics": {
        "required_tier": LicenseTier.PREMIUM,
        "name": "System Diagnostics",
        "description": "Advanced system diagnostics and troubleshooting",
        "icon": "🔍",
        "category": "advanced"
    }
}

class FeatureGateManager:
    """Manages feature access based on license status"""
    
    def __init__(self):
        self.current_license = None
        self.current_tier = LicenseTier.BASIC
        
    async def update_license_status(self, license_status: Dict[str, Any]):
        """Update current license status and determine tier"""
        self.current_license = license_status
        
        if not license_status or license_status.get("status") != "active":
            self.current_tier = LicenseTier.BASIC
            return
            
        license_type = license_status.get("license_type", "").lower()
        if license_type == "trial":
            self.current_tier = LicenseTier.TRIAL
        elif license_type in ["premium", "standard", "enterprise"]:
            self.current_tier = LicenseTier.PREMIUM
        else:
            self.current_tier = LicenseTier.BASIC
    
    def update_license_status_sync(self, license_status: Dict[str, Any]):
        """Update current license status and determine tier (synchronous)"""
        self.current_license = license_status
        
        if not license_status or license_status.get("status") != "active":
            self.current_tier = LicenseTier.BASIC
            return
            
        license_type = license_status.get("license_type", "").lower()
        if license_type == "trial":
            self.current_tier = LicenseTier.TRIAL
        elif license_type in ["premium", "standard", "enterprise"]:
            self.current_tier = LicenseTier.PREMIUM
        else:
            self.current_tier = LicenseTier.BASIC
            
    def has_feature(self, feature_name: str) -> bool:
        """Check if current license has access to feature"""
        if feature_name not in FEATURE_DEFINITIONS:
            return False
            
        required_tier = FEATURE_DEFINITIONS[feature_name]["required_tier"]
        
        # Premium has all features
        if self.current_tier == LicenseTier.PREMIUM:
            return True
            
        # Check if current tier includes this feature
        current_features = FEATURE_TIERS[self.current_tier]["features"]
        return feature_name in current_features or "all" in current_features
        
    def get_feature_status(self, feature_name: str) -> Dict[str, Any]:
        """Get comprehensive feature status for UI rendering"""
        if feature_name not in FEATURE_DEFINITIONS:
            return {"available": False, "error": "Unknown feature"}
            
        feature_def = FEATURE_DEFINITIONS[feature_name]
        has_access = self.has_feature(feature_name)
        required_tier = feature_def["required_tier"]
        
        status = {
            "available": has_access,
            "feature_name": feature_def["name"],
            "description": feature_def["description"], 
            "icon": feature_def["icon"],
            "category": feature_def["category"],
            "required_tier": required_tier.value,
            "required_tier_name": FEATURE_TIERS[required_tier]["name"],
            "current_tier": self.current_tier.value,
            "current_tier_name": FEATURE_TIERS[self.current_tier]["name"]
        }
        
        if not has_access:
            status.update({
                "lock_message": f"{FEATURE_TIERS[required_tier]['icon']} {FEATURE_TIERS[required_tier]['name']} Required",
                "upgrade_prompt": f"Upgrade to {FEATURE_TIERS[required_tier]['name']} to unlock this feature",
                "tier_color": FEATURE_TIERS[required_tier]["color"]
            })
            
        return status
        
    def get_available_features(self) -> List[str]:
        """Get list of all available features for current tier"""
        if self.current_tier == LicenseTier.PREMIUM:
            return list(FEATURE_DEFINITIONS.keys())
            
        return [
            feature for feature in FEATURE_DEFINITIONS.keys()
            if self.has_feature(feature)
        ]
        
    def get_locked_features(self) -> List[str]:
        """Get list of locked features for current tier"""
        return [
            feature for feature in FEATURE_DEFINITIONS.keys()
            if not self.has_feature(feature)
        ]
        
    def get_tier_info(self, tier: Optional[LicenseTier] = None) -> Dict[str, Any]:
        """Get information about a license tier"""
        tier = tier or self.current_tier
        return FEATURE_TIERS[tier].copy()
        
    def get_upgrade_options(self) -> List[Dict[str, Any]]:
        """Get available upgrade options from current tier"""
        upgrades = []
        current_tier_value = list(LicenseTier).index(self.current_tier)
        
        for i, tier in enumerate(LicenseTier):
            if i > current_tier_value:
                tier_info = self.get_tier_info(tier)
                tier_info["tier"] = tier.value
                upgrades.append(tier_info)
                
        return upgrades
        
    def generate_feature_context(self) -> Dict[str, Any]:
        """Generate template context for feature rendering"""
        return {
            "current_tier": self.current_tier.value,
            "current_tier_info": self.get_tier_info(),
            "available_features": self.get_available_features(),
            "locked_features": self.get_locked_features(),
            "upgrade_options": self.get_upgrade_options(),
            "feature_definitions": FEATURE_DEFINITIONS,
            "license_status": self.current_license
        }

# Global feature gate manager instance
feature_gate_manager = FeatureGateManager()

# Template helper functions
def has_feature(feature_name: str) -> bool:
    """Template helper to check feature access"""
    return feature_gate_manager.has_feature(feature_name)

def get_feature_status(feature_name: str) -> Dict[str, Any]:
    """Template helper to get feature status"""
    return feature_gate_manager.get_feature_status(feature_name)

def get_tier_badge(tier_name: str) -> str:
    """Generate HTML for tier badge"""
    try:
        tier = LicenseTier(tier_name)
        info = FEATURE_TIERS[tier]
        return f'<span class="feature-badge {tier_name}" style="background: {info["color"]};">{info["icon"]} {info["name"]}</span>'
    except:
        return ""

def get_lock_overlay(feature_name: str) -> str:
    """Generate HTML for feature lock overlay"""
    status = get_feature_status(feature_name)
    if status["available"]:
        return ""
        
    return f'''
    <div class="feature-overlay locked">
        <div class="lock-message">
            <div class="lock-icon">🔒</div>
            <div class="lock-text">{status["lock_message"]}</div>
            <button class="upgrade-btn" onclick="showUpgradePrompt('{feature_name}')">Upgrade Now</button>
        </div>
    </div>
    '''

# Export for template context
template_helpers = {
    "has_feature": has_feature,
    "get_feature_status": get_feature_status, 
    "get_tier_badge": get_tier_badge,
    "get_lock_overlay": get_lock_overlay,
    "feature_gate_manager": feature_gate_manager
}