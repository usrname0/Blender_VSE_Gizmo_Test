"""
BL Easy Crop v2.0.0 - Geometry Utilities

Core geometry functions shared between v1.0 and v2.0.
These are copied from the working v1.0 implementation.
"""

import bpy
import math
from mathutils import Vector


def is_strip_visible_at_frame(strip, frame):
    """Check if a strip is visible at the given frame"""
    return (strip.frame_final_start <= frame <= strip.frame_final_end and not strip.mute)


def point_in_polygon(point, polygon):
    """Check if a point is inside a polygon using ray casting algorithm"""
    x, y = point.x, point.y
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0].x, polygon[0].y
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n].x, polygon[i % n].y
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside


def rotate_point(point, angle, origin=None):
    """Rotate a 2D point around an origin"""
    if origin is None:
        origin = Vector([0, 0])
    
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate to origin
    x = point.x - origin.x
    y = point.y - origin.y
    
    # Rotate
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # Translate back
    return Vector([new_x + origin.x, new_y + origin.y])


def get_strip_geometry_with_flip_support(strip, scene):
    """
    Calculate strip geometry accounting for Mirror X/Y checkboxes
    Returns corner positions in resolution space
    """
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    
    # Get actual strip dimensions
    strip_width = res_x
    strip_height = res_y
    
    if hasattr(strip, 'elements') and strip.elements and len(strip.elements) > 0:
        elem = strip.elements[0]
        if hasattr(elem, 'orig_width') and hasattr(elem, 'orig_height'):
            strip_width = elem.orig_width
            strip_height = elem.orig_height
    
    # Get scale and base transform
    scale_x = 1.0
    scale_y = 1.0
    offset_x = 0
    offset_y = 0
    
    if hasattr(strip, 'transform'):
        offset_x = strip.transform.offset_x
        offset_y = strip.transform.offset_y
        if hasattr(strip.transform, 'scale_x'):
            scale_x = strip.transform.scale_x
            scale_y = strip.transform.scale_y
    
    # Check for Mirror X/Y checkboxes
    flip_x = False
    flip_y = False
    
    # Check various possible flip attribute names
    for attr_name in ['use_flip_x', 'flip_x', 'mirror_x']:
        if hasattr(strip, attr_name):
            flip_x = getattr(strip, attr_name)
            break
    
    for attr_name in ['use_flip_y', 'flip_y', 'mirror_y']:
        if hasattr(strip, attr_name):
            flip_y = getattr(strip, attr_name)
            break
    
    # Get rotation angle
    angle = 0
    if hasattr(strip, 'rotation_start'):
        angle = math.radians(strip.rotation_start)
    elif hasattr(strip, 'rotation'):
        angle = strip.rotation
    elif hasattr(strip, 'transform') and hasattr(strip.transform, 'rotation'):
        angle = strip.transform.rotation
    
    # Get crop values
    crop_left = 0
    crop_right = 0
    crop_bottom = 0
    crop_top = 0
    
    if hasattr(strip, 'crop'):
        crop_left = float(strip.crop.min_x)
        crop_right = float(strip.crop.max_x)
        crop_bottom = float(strip.crop.min_y)
        crop_top = float(strip.crop.max_y)
    
    # Calculate scaled dimensions
    scaled_width = strip_width * scale_x
    scaled_height = strip_height * scale_y
    
    # Calculate position (centered by default, then offset)
    left = (res_x - scaled_width) / 2 + offset_x
    right = (res_x + scaled_width) / 2 + offset_x
    bottom = (res_y - scaled_height) / 2 + offset_y
    top = (res_y + scaled_height) / 2 + offset_y
    
    # Apply crop - crop values are in original image space, so scale them
    left += crop_left * scale_x
    right -= crop_right * scale_x
    bottom += crop_bottom * scale_y
    top -= crop_top * scale_y
    
    # Calculate pivot point for rotation
    pivot_x = res_x / 2 + offset_x
    pivot_y = res_y / 2 + offset_y
    
    # Handle flipped coordinates
    if flip_x:
        new_left = res_x - right
        new_right = res_x - left
        left = new_left
        right = new_right
        pivot_x = res_x - pivot_x
    
    if flip_y:
        new_bottom = res_y - top
        new_top = res_y - bottom
        bottom = new_bottom
        top = new_top
        pivot_y = res_y - pivot_y
    
    # Create corner vectors
    corners = [
        Vector((left, bottom)),  # Bottom-left
        Vector((left, top)),     # Top-left
        Vector((right, top)),    # Top-right
        Vector((right, bottom))  # Bottom-right
    ]
    
    # Apply rotation if needed
    if angle != 0:
        # When flipped, rotation direction is reversed
        if flip_x != flip_y:  # XOR - if only one axis is flipped
            angle = -angle
        
        center = Vector((pivot_x, pivot_y))
        rotated_corners = []
        for corner in corners:
            rotated = rotate_point(corner, angle, center)
            rotated_corners.append(rotated)
        corners = rotated_corners
    
    return corners, (pivot_x, pivot_y), (scale_x, scale_y, flip_x, flip_y)


def get_strip_crop_bounds(strip, scene):
    """
    Get the current crop bounds for a strip in screen space
    Returns (min_x, max_x, min_y, max_y) in screen coordinates
    """
    if not strip or not hasattr(strip, 'crop'):
        return None
        
    corners, (pivot_x, pivot_y), (scale_x, scale_y, flip_x, flip_y) = get_strip_geometry_with_flip_support(strip, scene)
    
    # Find bounding box of corners
    min_x = min(corner.x for corner in corners)
    max_x = max(corner.x for corner in corners)
    min_y = min(corner.y for corner in corners)
    max_y = max(corner.y for corner in corners)
    
    return (min_x, max_x, min_y, max_y)


def screen_to_crop_space(screen_pos, strip, scene, context):
    """
    Convert screen position to crop coordinate space
    Returns (crop_x, crop_y) in strip's original image space
    """
    if not context.region or not strip:
        return None
        
    view2d = context.region.view2d
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    
    # Convert screen to view space
    view_pos = view2d.region_to_view(screen_pos[0], screen_pos[1])
    
    # Convert to resolution space (centered)
    res_x_pos = view_pos[0] + res_x / 2
    res_y_pos = view_pos[1] + res_y / 2
    
    # Get strip transform parameters
    scale_x = 1.0
    scale_y = 1.0
    offset_x = 0
    offset_y = 0
    
    if hasattr(strip, 'transform'):
        offset_x = strip.transform.offset_x
        offset_y = strip.transform.offset_y
        if hasattr(strip.transform, 'scale_x'):
            scale_x = strip.transform.scale_x
            scale_y = strip.transform.scale_y
    
    # Convert to crop space (strip's original image coordinates)
    crop_x = (res_x_pos - res_x / 2 - offset_x) / scale_x
    crop_y = (res_y_pos - res_y / 2 - offset_y) / scale_y
    
    return (crop_x, crop_y)


def crop_to_screen_space(crop_pos, strip, scene, context):
    """
    Convert crop coordinate space to screen position
    Returns (screen_x, screen_y) in screen space
    """
    if not context.region or not strip:
        return None
        
    view2d = context.region.view2d
    res_x = scene.render.resolution_x
    res_y = scene.render.resolution_y
    
    # Get strip transform parameters
    scale_x = 1.0
    scale_y = 1.0
    offset_x = 0
    offset_y = 0
    
    if hasattr(strip, 'transform'):
        offset_x = strip.transform.offset_x
        offset_y = strip.transform.offset_y
        if hasattr(strip.transform, 'scale_x'):
            scale_x = strip.transform.scale_x
            scale_y = strip.transform.scale_y
    
    # Convert from crop space to resolution space
    res_x_pos = crop_pos[0] * scale_x + res_x / 2 + offset_x
    res_y_pos = crop_pos[1] * scale_y + res_y / 2 + offset_y
    
    # Convert to view space (centered)
    view_x = res_x_pos - res_x / 2
    view_y = res_y_pos - res_y / 2
    
    # Convert to screen space
    screen_pos = view2d.view_to_region(view_x, view_y, clip=False)
    
    return screen_pos


def validate_crop_values(strip):
    """
    Validate and clamp crop values to reasonable bounds
    """
    if not strip or not hasattr(strip, 'crop') or not strip.crop:
        return
        
    # Get strip dimensions
    strip_width = 1920  # Default
    strip_height = 1080  # Default
    
    if hasattr(strip, 'elements') and strip.elements and len(strip.elements) > 0:
        elem = strip.elements[0]
        if hasattr(elem, 'orig_width') and hasattr(elem, 'orig_height'):
            strip_width = elem.orig_width
            strip_height = elem.orig_height
    
    # Clamp crop values
    strip.crop.min_x = max(0, min(strip.crop.min_x, strip_width - 1))
    strip.crop.max_x = max(0, min(strip.crop.max_x, strip_width - 1))
    strip.crop.min_y = max(0, min(strip.crop.min_y, strip_height - 1))
    strip.crop.max_y = max(0, min(strip.crop.max_y, strip_height - 1))
    
    # Ensure we don't crop more than the image size
    if strip.crop.min_x + strip.crop.max_x >= strip_width:
        strip.crop.max_x = max(0, strip_width - strip.crop.min_x - 1)
        
    if strip.crop.min_y + strip.crop.max_y >= strip_height:
        strip.crop.max_y = max(0, strip_height - strip.crop.min_y - 1)
