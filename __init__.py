"""
BL Easy Crop v2.0.0 - Gizmo Experiment

This is an experimental version that attempts to use Blender's gizmo system
instead of modal operators for crop functionality. This serves as a stepping
stone toward a more complex "Free Transform" extension.

WARNING: This is experimental code that may not work as expected.
The gizmo system in the sequence editor is poorly documented and relatively new.
"""

bl_info = {
    "name": "BL Easy Crop v2.0.0 (Experimental)",
    "description": "Experimental gizmo-based cropping for Blender's Video Sequence Editor",
    "author": "Adapted from VSE Transform Tools",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "Sequencer > Preview > Toolbar",
    "warning": "Experimental - Gizmo implementation may not work",
    "doc_url": "",
    "tracker_url": "",
    "category": "Sequencer"
}

import bpy
from bpy.types import Operator, Panel, Menu, WorkSpaceTool
from mathutils import Vector
import bmesh

# Import core functionality with error handling
try:
    from .gizmos.crop_gizmo_group import (
        CropGizmoGroup,
        register_gizmo_classes,
        unregister_gizmo_classes
    )
    from .gizmos.test_3d_gizmo import (
        register_3d_test_gizmo,
        unregister_3d_test_gizmo
    )
    from .gizmos.test_3d_panel import (
        register_test_panel,
        unregister_test_panel
    )
    from .operators.crop_operators_v2 import (
        EASYCROP_OT_crop_v2,
        EASYCROP_OT_activate_tool_v2,
        EASYCROP_OT_test_gizmo_system,
        EASYCROP_OT_toggle_gizmos
    )
    from .core.geometry_utils import (
        is_strip_visible_at_frame,
        get_strip_geometry_with_flip_support
    )
    from .utils.debug_tools import (
        register_debug_classes,
        unregister_debug_classes
    )
    gizmos_imported = True
except ImportError as e:
    print(f"BL Easy Crop v2.0.0: Import error: {e}")
    gizmos_imported = False
    # Define dummy functions to prevent NameError with matching return types
    def register_gizmo_classes():
        return False  # Match the real function's return type
    def unregister_gizmo_classes():
        pass  # Match the real function (returns None)
    def register_3d_test_gizmo():
        return False  # Match the real function's return type
    def unregister_3d_test_gizmo():
        pass  # Match the real function (returns None)
    def register_test_panel():
        return False  # Match the real function's return type
    def unregister_test_panel():
        pass  # Match the real function (returns None)
    def register_debug_classes():
        pass  # Match the real function (returns None)
    def unregister_debug_classes():
        pass  # Match the real function (returns None)
    # Define dummy functions for missing geometry utils with matching signatures
    def is_strip_visible_at_frame(strip, frame):
        return True  # Always return True as fallback
    def get_strip_geometry_with_flip_support(strip, scene):
        return [], (0, 0), (1, 1, False, False)  # Return expected tuple structure


class EASYCROP_TOOL_crop_v2(WorkSpaceTool):
    """Experimental gizmo-based crop tool"""
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_context_mode = 'PREVIEW'
    
    bl_idname = "easycrop.crop_tool_v2"
    bl_label = "Crop v2.0 (Experimental)"
    bl_description = "Experimental gizmo-based crop tool"
    bl_icon = "ops.sequencer.blade"
    bl_widget = "EASYCROP_GGT_crop_gizmo"
    bl_widget_group = "EASYCROP_GGT_crop_gizmo"
    
    # Simple keymap to stop warnings
    bl_keymap = (
        ("easycrop.crop_v2", {"type": 'X', "value": 'PRESS'}, {}),
    )
    
    @staticmethod  
    def draw_settings(context, layout, tool):
        """Tool settings UI"""
        seq_editor = context.scene.sequence_editor
        if not seq_editor:
            layout.label(text="No sequence editor")
            return
            
        active_strip = seq_editor.active_strip
        current_frame = context.scene.frame_current
        
        if active_strip and hasattr(active_strip, 'crop'):
            if is_strip_visible_at_frame(active_strip, current_frame):
                layout.label(text=f"Active: {active_strip.name}", icon='CHECKMARK')
                layout.label(text="• Drag gizmo handles to crop")
                layout.label(text="• Select other strips to switch")
                
                # Show current crop values
                if active_strip.crop:
                    row = layout.row(align=True)
                    row.prop(active_strip.crop, "min_x", text="L")
                    row.prop(active_strip.crop, "max_x", text="R")
                    row = layout.row(align=True)
                    row.prop(active_strip.crop, "min_y", text="B")
                    row.prop(active_strip.crop, "max_y", text="T")
            else:
                layout.label(text="Strip not at current frame")
        else:
            layout.label(text="Select a croppable strip")
            
        # Experimental warning
        layout.separator()
        box = layout.box()
        box.label(text="⚠ Experimental Version", icon='ERROR')
        box.label(text="Gizmos may not work as expected")


class EASYCROP_OT_clear_crop_v2(bpy.types.Operator):
    """Clear crop from selected strips (v2.0)"""
    bl_idname = "easycrop.clear_crop_v2"
    bl_label = "Clear Crop v2.0"
    bl_description = "Clear crop from all selected strips"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if not context.scene.sequence_editor:
            return False
        
        # Check if any selected strips have crop capability
        for strip in context.selected_sequences:
            if hasattr(strip, 'crop'):
                return True
        return False
    
    def execute(self, context):
        cleared_count = 0
        
        for strip in context.selected_sequences:
            if hasattr(strip, 'crop') and strip.crop:
                # Reset all crop values to 0
                strip.crop.min_x = 0
                strip.crop.max_x = 0
                strip.crop.min_y = 0
                strip.crop.max_y = 0
                cleared_count += 1
        
        if cleared_count > 0:
            self.report({'INFO'}, f"Cleared crop from {cleared_count} strip(s)")
        else:
            self.report({'INFO'}, "No strips with crop found")
        
        return {'FINISHED'}


# Menu functions
def menu_func_strip_transform_v2(self, context):
    """Add Easy Crop v2.0 to Strip > Transform menu"""
    if context.space_data.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
        self.layout.separator()
        self.layout.operator_context = 'INVOKE_REGION_PREVIEW'
        self.layout.operator("easycrop.crop_v2", text="Crop v2.0 (Experimental)")


def menu_func_image_transform_v2(self, context):
    """Add Easy Crop v2.0 to Image > Transform menu"""
    if context.space_data.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
        self.layout.separator()
        self.layout.operator_context = 'INVOKE_REGION_PREVIEW'
        self.layout.operator("easycrop.crop_v2", text="Crop v2.0 (Experimental)")


def menu_func_image_clear_v2(self, context):
    """Add Clear Crop v2.0 to Image > Clear menu"""
    if context.space_data.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
        self.layout.operator("easycrop.clear_crop_v2", text="Crop v2.0")


# Registration
classes = [
    EASYCROP_OT_clear_crop_v2,
]

# Add gizmo and debug classes if successfully imported
if gizmos_imported:
    classes.extend([
        # Main functionality would be added here, but we need to register
        # gizmos separately due to their special requirements
    ])

addon_keymaps = []


def register():
    """Register the addon"""
    if not gizmos_imported:
        print("BL Easy Crop v2.0.0: Failed to import gizmo components")
        print("This is expected - gizmo system is experimental")
        # Still register basic functionality
    
    # Register basic classes first
    for cls in classes:
        if cls is not None:
            try:
                bpy.utils.register_class(cls)
                print(f"BL Easy Crop v2.0.0: Registered {cls.__name__}")
            except Exception as e:
                print(f"BL Easy Crop v2.0.0: Failed to register {cls.__name__}: {e}")
    
    # Register gizmo classes separately if available
    if gizmos_imported:
        try:
            register_gizmo_classes()
            print("BL Easy Crop v2.0.0: Registered gizmo classes")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Failed to register gizmo classes: {e}")
        
        # Register operators
        try:
            bpy.utils.register_class(EASYCROP_OT_crop_v2)
            bpy.utils.register_class(EASYCROP_OT_activate_tool_v2)
            bpy.utils.register_class(EASYCROP_OT_test_gizmo_system)
            bpy.utils.register_class(EASYCROP_OT_toggle_gizmos)
            print("BL Easy Crop v2.0.0: Registered operators")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Failed to register operators: {e}")
        
        # Register debug tools
        try:
            register_debug_classes()
            print("BL Easy Crop v2.0.0: Registered debug tools")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Failed to register debug tools: {e}")
        
        # Register 3D test gizmo for comparison
        try:
            register_3d_test_gizmo()
            print("BL Easy Crop v2.0.0: Registered 3D test gizmo")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Failed to register 3D test gizmo: {e}")
        
        # Register test panel
        try:
            register_test_panel()
            print("BL Easy Crop v2.0.0: Registered test panel")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Failed to register test panel: {e}")
    
    # Register keymaps for fallback functionality
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Preview region keymaps - use different key (X) to avoid conflicts
        km = kc.keymaps.new(name="SequencerPreview", space_type="SEQUENCE_EDITOR", region_type="WINDOW")
        
        if gizmos_imported:
            # Experimental crop operator - X key (different from v1.0)
            kmi = km.keymap_items.new("easycrop.crop_v2", 'X', 'PRESS')
            addon_keymaps.append((km, kmi))
        
        # Clear crop operator - Shift+X key
        kmi_clear = km.keymap_items.new("easycrop.clear_crop_v2", 'X', 'PRESS', shift=True)
        addon_keymaps.append((km, kmi_clear))
        
        # General sequencer context
        km2 = kc.keymaps.new(name="Sequencer", space_type="SEQUENCE_EDITOR")
        
        if gizmos_imported:
            kmi2 = km2.keymap_items.new("easycrop.crop_v2", 'X', 'PRESS')
            addon_keymaps.append((km2, kmi2))
        
        kmi2_clear = km2.keymap_items.new("easycrop.clear_crop_v2", 'X', 'PRESS', shift=True)
        addon_keymaps.append((km2, kmi2_clear))
    
    # Register the tool (only if gizmos work)
    if gizmos_imported:
        try:
            bpy.utils.register_tool(EASYCROP_TOOL_crop_v2, after={"builtin.transform"}, separator=True)
            print("BL Easy Crop v2.0.0: Registered gizmo tool")
        except Exception as e:
            print(f"BL Easy Crop v2.0.0: Tool registration failed: {e}")
            try:
                bpy.utils.register_tool(EASYCROP_TOOL_crop_v2)
                print("BL Easy Crop v2.0.0: Registered gizmo tool (fallback)")
            except Exception as e2:
                print(f"BL Easy Crop v2.0.0: Tool registration completely failed: {e2}")
    
    # Add menu items
    try:
        bpy.types.SEQUENCER_MT_strip_transform.append(menu_func_strip_transform_v2)
        bpy.types.SEQUENCER_MT_image_transform.append(menu_func_image_transform_v2)
        bpy.types.SEQUENCER_MT_image_clear.append(menu_func_image_clear_v2)
        print("BL Easy Crop v2.0.0: Added menu items")
    except Exception as e:
        print(f"BL Easy Crop v2.0.0: Menu integration failed: {e}")


def unregister():
    """Unregister the addon"""
    print("BL Easy Crop v2.0.0: Unregistering...")
    
    # Remove menu items
    try:
        bpy.types.SEQUENCER_MT_strip_transform.remove(menu_func_strip_transform_v2)
        bpy.types.SEQUENCER_MT_image_transform.remove(menu_func_image_transform_v2)
        bpy.types.SEQUENCER_MT_image_clear.remove(menu_func_image_clear_v2)
    except:
        pass
    
    # Unregister the tool
    if gizmos_imported:
        try:
            bpy.utils.unregister_tool(EASYCROP_TOOL_crop_v2)
        except:
            pass
    
    # Remove keymaps
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            pass
    addon_keymaps.clear()
    
    # Unregister debug tools
    if gizmos_imported:
        try:
            unregister_debug_classes()
        except:
            pass
        
        # Unregister operators
        try:
            bpy.utils.unregister_class(EASYCROP_OT_toggle_gizmos)
            bpy.utils.unregister_class(EASYCROP_OT_test_gizmo_system)
            bpy.utils.unregister_class(EASYCROP_OT_activate_tool_v2)
            bpy.utils.unregister_class(EASYCROP_OT_crop_v2)
        except:
            pass
        
        # Unregister gizmo classes
        try:
            unregister_gizmo_classes()
        except:
            pass
        
        # Unregister test panel
        try:
            unregister_test_panel()
        except:
            pass
        
        # Unregister 3D test gizmo
        try:
            unregister_3d_test_gizmo()
        except:
            pass
    
    # Unregister basic classes
    for cls in reversed(classes):
        if cls is not None:
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass
    
    print("BL Easy Crop v2.0.0: Unregistered")


if __name__ == "__main__":
    register()