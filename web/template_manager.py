#!/usr/bin/env python3
"""
APEX Template Manager
Manages Jinja2 templates with feature gate integration
Following APEX three-tier architecture pattern
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .feature_gates import feature_gate_manager, template_helpers

class APEXTemplateManager:
    """Template manager with feature gating support"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        # Default to web/templates directory
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
            
        self.template_dir = template_dir
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register feature gate helpers as global functions
        self._register_template_helpers()
        
    def _register_template_helpers(self):
        """Register feature gate helpers and other template functions"""
        # Feature gate helpers
        self.env.globals.update(template_helpers)
        
        # Additional template helpers
        self.env.globals.update({
            'get_tier_info': self._get_tier_info,
            'render_component': self._render_component,
            'include_feature_css': self._include_feature_css,
            'get_upgrade_options': self._get_upgrade_options
        })
        
        # Custom filters
        self.env.filters.update({
            'feature_class': self._feature_class_filter,
            'tier_badge': self._tier_badge_filter
        })
    
    def _get_tier_info(self, tier_name: Optional[str] = None):
        """Template helper to get tier information"""
        if tier_name:
            from .feature_gates import LicenseTier, FEATURE_TIERS
            try:
                tier = LicenseTier(tier_name)
                return FEATURE_TIERS[tier]
            except:
                return None
        return feature_gate_manager.get_tier_info()
    
    def _render_component(self, component_path: str, **context):
        """Template helper to render a component with context"""
        try:
            template = self.env.get_template(f"components/{component_path}")
            return template.render(**context)
        except Exception as e:
            return f"<!-- Component render error: {component_path} - {str(e)} -->"
    
    def _include_feature_css(self):
        """Include feature gate CSS"""
        return '<link rel="stylesheet" href="/static/css/components/shared/feature_gates.css">'
    
    def _get_upgrade_options(self):
        """Get upgrade options for current user"""
        return feature_gate_manager.get_upgrade_options()
    
    def _feature_class_filter(self, feature_name: str) -> str:
        """Jinja2 filter to get CSS class for feature state"""
        status = feature_gate_manager.get_feature_status(feature_name)
        if not status["available"]:
            return "locked"
        
        tier = status["required_tier"]
        if tier == "premium":
            return "feature-premium"
        elif tier == "trial":
            return "feature-trial"
        else:
            return ""
    
    def _tier_badge_filter(self, tier_name: str) -> str:
        """Jinja2 filter to generate tier badge HTML"""
        from .feature_gates import get_tier_badge
        return get_tier_badge(tier_name)
    
    def get_template_context(self, license_status=None):
        """Get template context with feature gates (synchronous)"""
        # Update feature gates with license status
        if license_status:
            feature_gate_manager.update_license_status_sync(license_status)
        
        # Generate feature context
        feature_context = feature_gate_manager.generate_feature_context()
        feature_context.update(template_helpers)
        
        return feature_context
    
    def render_template(self, template_name: str, **context) -> str:
        """Render a template with feature gate context (synchronous)"""
        # Add feature gate context to template context
        feature_context = feature_gate_manager.generate_feature_context()
        context.update(feature_context)
        
        # Add template helpers directly to context (for safety)
        context.update(template_helpers)
        
        # Load and render template
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def has_feature(self, feature_name: str, available_features=None) -> bool:
        """Check if a feature is available"""
        if available_features is None:
            available_features = feature_gate_manager.get_available_features()
        return feature_name in available_features
    
    async def render_template_async(self, template_name: str, **context) -> str:
        """Render a template with feature gate context (async)"""
        # Get current license status and update feature gates
        license_controller = context.get('license_controller')
        if license_controller:
            try:
                license_status = await license_controller.get_license_status()
                await feature_gate_manager.update_license_status(license_status)
            except Exception as e:
                print(f"Warning: Could not update license status for templates: {e}")
        
        return self.render_template(template_name, **context)
    
    def render_component(self, component_path: str, **context) -> str:
        """Render a specific component"""
        try:
            template = self.env.get_template(f"components/{component_path}")
            
            # Add feature context
            feature_context = feature_gate_manager.generate_feature_context()
            context.update(feature_context)
            context.update(template_helpers)
            
            return template.render(**context)
        except Exception as e:
            return f"<!-- Component error: {component_path} - {str(e)} -->"

# Global template manager instance
template_manager = APEXTemplateManager()

# Convenience alias
TemplateManager = APEXTemplateManager

# Template rendering functions for FastAPI
async def render_main_template(**context) -> str:
    """Render the main APEX template with feature gates"""
    return await template_manager.render_template("main.html", **context)

async def render_component_template(component_path: str, **context) -> str:
    """Render a component template"""
    return template_manager.render_component(component_path, **context)

# Feature gate status endpoint helper
def get_current_feature_status() -> Dict[str, Any]:
    """Get current feature gate status for API endpoints"""
    return {
        "current_tier": feature_gate_manager.current_tier.value,
        "available_features": feature_gate_manager.get_available_features(),
        "locked_features": feature_gate_manager.get_locked_features(),
        "upgrade_options": feature_gate_manager.get_upgrade_options(),
        "license_status": feature_gate_manager.current_license
    }