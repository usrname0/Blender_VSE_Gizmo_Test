"""
BL Easy Crop v2.0.0 - Gizmo Group Implementation

This module contains the experimental gizmo group for crop functionality.
Based on research into Blender's gizmo system and sequence editor integration.
"""

import bpy
import gpu
import math
from bpy.types import Gizmo, GizmoGroup
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader

from ..core.geometry_utils import (
    get_strip_geometry_with_flip_support,
    is_strip_visible_at_frame
)


class CropGizmo(Gizmo):
    """Individual crop handle gizmo"""
    bl_idname = "EASYCROP_GT_crop_handle"
    
    def __init__(self):
        self.handle_type = 'corner'  # 'corner' or 'edge'
        self.handle_index = 0
        self.strip = None
        self.custom_shape = None
        
    def setup(self):
        """Setup the gizmo"""
        if not hasattr(self, 'custom_shape') or self.custom_shape is None:
            # Create a simple square shape for the handle
            verts = [
                Vector((-1, -1, 0)),
                Vector((1, -1, 0)), 
                Vector((1, 1, 0)),
                Vector((-1, 1, 0))
            ]
            edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
            faces = [(0, 1, 2, 3)]
            
            self.custom_shape = self.new_custom_shape('TRIS', verts, edges, faces)
    
    def draw(self, context):
        """Draw the gizmo handle"""
        # Set gizmo color based on state
        if self.is_highlight:
            self.color = (1.0, 1.0, 1.0)
            self.alpha = 1.0
        else:
            self.color = (1.0, 1.0, 1.0)
            self.alpha = 0.7
            
        # Scale based on zoom level
        scale = 8.0 / context.region.view2d.view[0]  # Approximate scale
        matrix = Matrix.Scale(scale, 4)
        
        if hasattr(self, 'custom_shape') and self.custom_shape:
            self.draw_custom_shape(self.custom_shape, matrix=matrix)
        else:
            # Fallback to preset shape
            self.draw_preset_box(matrix, select_id=self.select_id)
    
    def invoke(self, context, event):
        """Handle gizmo click"""
        print(f"Crop gizmo {self.handle_index} clicked")
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event, tweak):
        """Handle gizmo drag"""
        if not self.strip or not hasattr(self.strip, 'crop'):
            return {'FINISHED'}
            
        # Get mouse delta
        delta = tweak.delta
        
        # Convert to crop space and apply changes
        # This is a simplified version - real implementation would need
        # proper coordinate transformation
        if self.handle_type == 'corner':
            if self.handle_index == 0:  # Bottom-left
                self.strip.crop.min_x += int(delta[0])
                self.strip.crop.min_y += int(delta[1])
            elif self.handle_index == 1:  # Top-left  
                self.strip.crop.min_x += int(delta[0])
                self.strip.crop.max_y -= int(delta[1])
            elif self.handle_index == 2:  # Top-right
                self.strip.crop.max_x -= int(delta[0])
                self.strip.crop.max_y -= int(delta[1])
            elif self.handle_index == 3:  # Bottom-right
                self.strip.crop.max_x -= int(delta[0])
                self.strip.crop.min_y += int(delta[1])
        
        # Clamp values
        self.strip.crop.min_x = max(0, self.strip.crop.min_x)
        self.strip.crop.max_x = max(0, self.strip.crop.max_x)
        self.strip.crop.min_y = max(0, self.strip.crop.min_y)
        self.strip.crop.max_y = max(0, self.strip.crop.max_y)
        
        # Force redraw
        context.area.tag_redraw()
        
        return {'RUNNING_MODAL'}
    
    def exit(self, context, cancel):
        """Handle gizmo exit"""
        if cancel and hasattr(self, 'original_crop'):
            # Restore original values if cancelled
            if self.strip and hasattr(self.strip, 'crop'):
                self.strip.crop.min_x = self.original_crop[0]
                self.strip.crop.max_x = self.original_crop[1] 
                self.strip.crop.min_y = self.original_crop[2]
                self.strip.crop.max_y = self.original_crop[3]


class CropGizmoGroup(GizmoGroup):
    """Gizmo group for crop handles"""
    bl_idname = "EASYCROP_GGT_crop_gizmo"
    bl_label = "Crop Gizmo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'PREVIEW'  # Use PREVIEW for VSE as per bug fix
    bl_options = {'3D'}  # Remove PERSISTENT - this was causing the error!
    
    @classmethod
    def poll(cls, context):
        """Check if gizmo group should be active"""
        # Debug print to see if poll is being called
        print("CropGizmoGroup.poll() called")
        
        # Check if we're in the right context
        if not context.space_data or context.space_data.type != 'SEQUENCE_EDITOR':
            print("- Not in sequence editor")
            return False
            
        if context.space_data.view_type not in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            print("- Not in preview mode")
            return False
            
        # Check if we have a sequence editor
        scene = context.scene
        if not scene.sequence_editor:
            print("- No sequence editor")
            return False
            
        # Check if we have an active strip with crop capability
        active_strip = scene.sequence_editor.active_strip
        if not active_strip:
            print("- No active strip")
            return False
            
        if not hasattr(active_strip, 'crop'):
            print("- Active strip has no crop")
            return False
            
        # Check if strip is visible at current frame
        current_frame = scene.frame_current
        if not is_strip_visible_at_frame(active_strip, current_frame):
            print("- Strip not visible at current frame")
            return False
            
        print("- Poll passed!")
        return True
    
    def setup(self, context):
        """Setup the gizmo group"""
        print("CropGizmoGroup.setup() called")
        
        # Clear any existing gizmos
        self.gizmos.clear()
        
        # Create corner handle gizmos
        for i in range(4):
            gizmo = self.gizmos.new(CropGizmo.bl_idname)
            gizmo.handle_type = 'corner'
            gizmo.handle_index = i
            gizmo.select_id = i
            
            # Set up target properties - this links the gizmo to data
            # In a real implementation, this would bind to crop properties
            # For now, we'll handle updates in the modal method
            
        # Create edge handle gizmos  
        for i in range(4):
            gizmo = self.gizmos.new(CropGizmo.bl_idname)
            gizmo.handle_type = 'edge'
            gizmo.handle_index = i
            gizmo.select_id = i + 4
            
        print(f"Created {len(self.gizmos)} crop gizmos")
    
    def refresh(self, context):
        """Refresh gizmo positions"""
        scene = context.scene
        if not scene.sequence_editor:
            return
            
        active_strip = scene.sequence_editor.active_strip
        if not active_strip or not hasattr(active_strip, 'crop'):
            return
            
        # Get strip geometry
        try:
            corners, (pivot_x, pivot_y), (scale_x, scale_y, flip_x, flip_y) = get_strip_geometry_with_flip_support(active_strip, scene)
        except:
            print("Failed to get strip geometry")
            return
            
        # Calculate edge midpoints
        edge_midpoints = []
        for i in range(4):
            next_i = (i + 1) % 4
            midpoint = (corners[i] + corners[next_i]) / 2
            edge_midpoints.append(midpoint)
        
        # Position corner gizmos
        for i, gizmo in enumerate(self.gizmos[:4]):
            if i < len(corners):
                # Convert to gizmo space (this is approximate)
                pos = corners[i]
                gizmo.matrix_basis = Matrix.Translation((pos.x, pos.y, 0))
                gizmo.strip = active_strip
                
        # Position edge gizmos
        for i, gizmo in enumerate(self.gizmos[4:8]):
            if i < len(edge_midpoints):
                pos = edge_midpoints[i]
                gizmo.matrix_basis = Matrix.Translation((pos.x, pos.y, 0))
                gizmo.strip = active_strip
    
    def draw_prepare(self, context):
        """Prepare for drawing"""
        # Update gizmo positions
        self.refresh(context)


# Register the gizmo classes
def register_gizmo_classes():
    """Register gizmo-related classes"""
    try:
        bpy.utils.register_class(CropGizmo)
        print("BL Easy Crop v2.0.0: Registered CropGizmo")
        bpy.utils.register_class(CropGizmoGroup)
        print("BL Easy Crop v2.0.0: Registered CropGizmoGroup")
        
        # Try to verify registration
        try:
            gizmo_type = bpy.types.EASYCROP_GT_crop_handle
            print("BL Easy Crop v2.0.0: ✓ CropGizmo verified in bpy.types")
        except AttributeError:
            print("BL Easy Crop v2.0.0: ✗ CropGizmo NOT found in bpy.types")
        
        try:
            gizmo_group_type = bpy.types.EASYCROP_GGT_crop_gizmo
            print("BL Easy Crop v2.0.0: ✓ CropGizmoGroup verified in bpy.types")
        except AttributeError:
            print("BL Easy Crop v2.0.0: ✗ CropGizmoGroup NOT found in bpy.types")
            
        return True
    except Exception as e:
        print(f"BL Easy Crop v2.0.0: Failed to register gizmo classes: {e}")
        import traceback
        traceback.print_exc()
        return False


def unregister_gizmo_classes():
    """Unregister gizmo-related classes"""
    try:
        bpy.utils.unregister_class(CropGizmoGroup)
        print("BL Easy Crop v2.0.0: Unregistered CropGizmoGroup")
    except:
        pass
    try:
        bpy.utils.unregister_class(CropGizmo)
        print("BL Easy Crop v2.0.0: Unregistered CropGizmo")
    except:
        pass