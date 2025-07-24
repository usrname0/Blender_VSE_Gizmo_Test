"""
BL Easy Crop v2.0.0 - 3D Viewport Test Gizmo

This is a control experiment to verify our gizmo implementation works
in the 3D viewport where gizmos are known to function properly.
"""

import bpy
from bpy.types import Gizmo, GizmoGroup
from mathutils import Vector, Matrix


class SimpleTestGizmo(Gizmo):
    """Simple test gizmo for 3D viewport"""
    bl_idname = "EASYCROP_GT_simple_test"
    
    def setup(self):
        """Setup the gizmo"""
        print("SimpleTestGizmo.setup() called")
        
    def draw(self, context):
        """Draw the gizmo"""
        print("SimpleTestGizmo.draw() called")
        
        # Set gizmo color based on state
        if self.is_highlight:
            self.color = (1.0, 0.0, 0.0)  # Red when highlighted
            self.alpha = 1.0
        else:
            self.color = (0.0, 1.0, 0.0)  # Green normally
            self.alpha = 0.8
            
        # Draw a simple circle (sphere not available in all Blender versions)
        matrix = Matrix.Scale(0.5, 4)  # Small circle
        self.draw_preset_circle(matrix, select_id=self.select_id)
    
    def invoke(self, context, event):
        """Handle gizmo click"""
        print("SimpleTestGizmo.invoke() called - Gizmo clicked!")
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event, tweak):
        """Handle gizmo drag"""
        print(f"SimpleTestGizmo.modal() called - Delta: {tweak.delta}")
        
        # Move the gizmo with mouse delta
        self.matrix_basis.translation += Vector((tweak.delta[0] * 0.01, tweak.delta[1] * 0.01, 0))
        
        return {'RUNNING_MODAL'}
    
    def exit(self, context, cancel):
        """Handle gizmo exit"""
        print(f"SimpleTestGizmo.exit() called - Cancel: {cancel}")


class SimpleTestGizmoGroup(GizmoGroup):
    """Simple test gizmo group for 3D viewport"""
    bl_idname = "EASYCROP_GGT_simple_test"
    bl_label = "Simple Test Gizmo"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D'}
    
    @classmethod
    def poll(cls, context):
        """Check if gizmo group should be active"""
        print("SimpleTestGizmoGroup.poll() called")
        
        # Only show in 3D viewport
        if not context.space_data or context.space_data.type != 'VIEW_3D':
            print("- Not in 3D viewport")
            return False
            
        # Only show when there's an active object
        if not context.active_object:
            print("- No active object")
            return False
            
        print("- Poll passed!")
        return True
    
    def setup(self, context):
        """Setup the gizmo group"""
        print("SimpleTestGizmoGroup.setup() called")
        
        # Create a single test gizmo
        gizmo = self.gizmos.new(SimpleTestGizmo.bl_idname)
        gizmo.select_id = 0
        
        # Position it at the active object's location
        if context.active_object:
            gizmo.matrix_basis = Matrix.Translation(context.active_object.location)
        
        print(f"Created {len(self.gizmos)} test gizmo(s)")
    
    def refresh(self, context):
        """Refresh gizmo positions"""
        print("SimpleTestGizmoGroup.refresh() called")
        
        # Update gizmo position to follow active object
        if context.active_object and len(self.gizmos) > 0:
            self.gizmos[0].matrix_basis = Matrix.Translation(context.active_object.location)
    
    def draw_prepare(self, context):
        """Prepare for drawing"""
        print("SimpleTestGizmoGroup.draw_prepare() called")
        self.refresh(context)


def register_3d_test_gizmo():
    """Register the 3D test gizmo classes"""
    try:
        print("=== REGISTERING 3D TEST GIZMO ===")
        
        bpy.utils.register_class(SimpleTestGizmo)
        print("✓ Registered SimpleTestGizmo")
        
        bpy.utils.register_class(SimpleTestGizmoGroup)
        print("✓ Registered SimpleTestGizmoGroup")
        
        # Verify registration
        try:
            gizmo_type = bpy.types.EASYCROP_GT_simple_test
            print("✓ SimpleTestGizmo verified in bpy.types")
        except AttributeError:
            print("✗ SimpleTestGizmo NOT found in bpy.types")
        
        try:
            gizmo_group_type = bpy.types.EASYCROP_GGT_simple_test
            print("✓ SimpleTestGizmoGroup verified in bpy.types")
        except AttributeError:
            print("✗ SimpleTestGizmoGroup NOT found in bpy.types")
            
        # Try to ensure the gizmo group type is active
        try:
            # In newer Blender versions, use the workspace tool system
            wm = bpy.context.window_manager
            if hasattr(wm, 'gizmo_group_type_ensure'):
                wm.gizmo_group_type_ensure(SimpleTestGizmoGroup.bl_idname)
                print("✓ gizmo_group_type_ensure() called successfully")
            else:
                print("ℹ gizmo_group_type_ensure() not available - this is normal")
        except Exception as e:
            print(f"✗ gizmo_group_type_ensure() failed: {e}")
            
        print("=== 3D TEST GIZMO REGISTRATION COMPLETE ===")
        return True
        
    except Exception as e:
        print(f"Failed to register 3D test gizmo: {e}")
        import traceback
        traceback.print_exc()
        return False


def unregister_3d_test_gizmo():
    """Unregister the 3D test gizmo classes"""
    try:
        print("=== UNREGISTERING 3D TEST GIZMO ===")
        
        bpy.utils.unregister_class(SimpleTestGizmoGroup)
        print("✓ Unregistered SimpleTestGizmoGroup")
        
        bpy.utils.unregister_class(SimpleTestGizmo)
        print("✓ Unregistered SimpleTestGizmo")
        
        print("=== 3D TEST GIZMO UNREGISTRATION COMPLETE ===")
        
    except Exception as e:
        print(f"Failed to unregister 3D test gizmo: {e}")