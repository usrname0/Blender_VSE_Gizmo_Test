"""
BL Easy Crop v2.0.0 - Core Module

Core functionality shared between versions, including geometry utilities
and common functions used by both gizmo and operator implementations.
"""

from . import geometry_utils

# Import the main functions for external use
from .geometry_utils import (
    is_strip_visible_at_frame,
    get_strip_geometry_with_flip_support,
    get_strip_crop_bounds,
    screen_to_crop_space,
    crop_to_screen_space,
    validate_crop_values,
    point_in_polygon,
    rotate_point
)

__all__ = [
    'geometry_utils',
    'is_strip_visible_at_frame',
    'get_strip_geometry_with_flip_support', 
    'get_strip_crop_bounds',
    'screen_to_crop_space',
    'crop_to_screen_space',
    'validate_crop_values',
    'point_in_polygon',
    'rotate_point'
]
