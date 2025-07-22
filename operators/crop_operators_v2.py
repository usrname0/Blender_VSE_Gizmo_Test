"""
BL Easy Crop v2.0.0 - Operators for Gizmo Support

This module contains operators that work with the gizmo system,
providing fallback functionality and tool activation.
"""

import bpy
from bpy.types import Operator
from mathutils import Vector

from ..core.geometry_utils import (
    is_strip_visible_at_frame,
    get_strip_geometry_with_flip_support
)


class EASYCROP_OT_crop_v2(bpy.types.Operator):
    """Crop strips with gizmo support (v2.0)"""
    bl_idname = "easycrop.crop_v2"
    bl_label = "Crop v2.0 (Experimental)"
    bl_description = "Activate gizmo-based crop mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not scene.sequence_editor:
            return False
        
        # Check if we're in preview mode
        space = context.space_data
        if space and space.type == 'SEQUENCE_EDITOR':
            if space.view_type not in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
                return False
        
        # Check for croppable strips
        if scene.sequence_editor.active_strip and hasattr(scene.sequence_editor.active_strip, 'crop'):
            return True
        
        for strip in context.selected_sequences:
            if hasattr(strip, 'crop'):
                return True
                
        return False
    
    def execute(self, context):
        """Execute the crop operation"""
        # This operator primarily serves to activate the tool
        # The actual cropping is handled by gizmos
        
        strip = context.scene.sequence_editor.active_strip
        current_frame = context.scene.frame_current
        
        # Check if we have a suitable active strip that's visible
        has_suitable_active = (strip and 
                              hasattr(strip, 'crop') and 
                              is_strip_visible_at_frame(strip, current_frame))
        
        if not has_suitable_active:
            # Try to find a suitable strip
            for s in context.scene.sequence_editor.sequences:
                if (hasattr(s, 'crop') and 
                    is_strip_visible_at_frame(s, current_frame) and
                    s.select):
                    # Make this strip active
                    context.scene.sequence_editor.active_strip = s
                    strip = s
                    has_suitable_active = True
                    break
        
        if not has_suitable_active:
            self.report({'INFO'}, "No suitable strip for cropping - select an image/movie strip")
            return {'CANCELLED'}
        
        # Ensure gizmos are enabled in the sequence editor
        space = context.space_data
        if hasattr(space, 'show_gizmo') and not space.show_gizmo:
            space.show_gizmo = True
            
        if hasattr(space, 'show_gizmo_tool') and not space.show_gizmo_tool:
            space.show_gizmo_tool = True
            
        if hasattr(space, 'show_gizmo_context') and not space.show_gizmo_context:
            space.show_gizmo_context = True
        
        # Activate the crop tool
        try:
            bpy.ops.wm.tool_set_by_id(name="easycrop.crop_tool_v2")
            self.report({'INFO'}, f"Crop gizmos activated for {strip.name}")
        except:
            # Fallback to manual gizmo refresh
            self.report({'INFO'}, f"Gizmo mode activated for {strip.name}")
        
        # Force redraw to show gizmos
        context.area.tag_redraw()
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        """Invoke the crop operation"""
        return self.execute(context)


class EASYCROP_OT_activate_tool_v2(bpy.types.Operator):
    """Activate crop tool v2.0 - gizmo version"""
    bl_idname = "easycrop.activate_tool_v2"
    bl_label = "Activate Crop Tool v2.0"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    @classmethod
    def poll(cls, context):
        return (context.scene.sequence_editor is not None and
                context.space_data and 
                context.space_data.type == 'SEQUENCE_EDITOR' and
                context.space_data.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'})
    
    def execute(self, context):
        """Execute tool activation"""
        # Ensure gizmos are enabled
        space = context.space_data
        if hasattr(space, 'show_gizmo'):
            space.show_gizmo = True
            
        if hasattr(space, 'show_gizmo_tool'):
            space.show_gizmo_tool = True
            
        # Try to activate the tool
        try:
            bpy.ops.wm.tool_set_by_id(name="easycrop.crop_tool_v2")
            self.report({'INFO'}, "Crop tool v2.0 activated")
        except Exception as e:
            self.report({'WARNING'}, f"Failed to activate tool: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)


class EASYCROP_OT_test_gizmo_system(bpy.types.Operator):
    """Test if gizmo system is working in sequence editor"""
    bl_idname = "easycrop.test_gizmo_system"
    bl_label = "Test Gizmo System"
    bl_description = "Test if gizmos work in the sequence editor"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test gizmo functionality"""
        space = context.space_data
        
        if not space or space.type != 'SEQUENCE_EDITOR':
            self.report({'ERROR'}, "Not in sequence editor")
            return {'CANCELLED'}
            
        # Check gizmo properties
        gizmo_props = []
        for prop in ['show_gizmo', 'show_gizmo_tool', 'show_gizmo_context', 'show_gizmo_navigate']:
            if hasattr(space, prop):
                value = getattr(space, prop)
                gizmo_props.append(f"{prop}: {value}")
            else:
                gizmo_props.append(f"{prop}: NOT FOUND")
        
        # Check if we're in preview mode
        view_type = getattr(space, 'view_type', 'UNKNOWN')
        
        # Check sequence editor
        seq_editor = context.scene.sequence_editor
        active_strip = seq_editor.active_strip if seq_editor else None
        
        # Report findings
        report_lines = [
            f"Space type: {space.type}",
            f"View type: {view_type}",
            f"Has sequence editor: {seq_editor is not None}",
            f"Active strip: {active_strip.name if active_strip else 'None'}",
            f"Active strip has crop: {hasattr(active_strip, 'crop') if active_strip else False}",
            "",
            "Gizmo properties:"
        ]
        report_lines.extend(gizmo_props)
        
        # Try to check if gizmo groups are registered
        try:
            wm = context.window_manager
            gizmo_groups = []
            # This is a hack to see if our gizmo group is available
            for attr in dir(wm):
                if 'gizmo' in attr.lower():
                    gizmo_groups.append(attr)
            
            if gizmo_groups:
                report_lines.extend(["", "Window manager gizmo attributes:"])
                report_lines.extend(gizmo_groups[:5])  # Limit output
        except:
            pass
        
        # Print detailed report to console
        print("=" * 50)
        print("BL Easy Crop v2.0.0 - Gizmo System Test")
        print("=" * 50)
        for line in report_lines:
            print(line)
        print("=" * 50)
        
        # Show summary in UI
        if view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'} and seq_editor and active_strip:
            self.report({'INFO'}, "Gizmo test complete - check console for details")
        else:
            self.report({'WARNING'}, "Not in suitable context for gizmos")
        
        return {'FINISHED'}


class EASYCROP_OT_toggle_gizmos(bpy.types.Operator):
    """Toggle gizmos in sequence editor"""
    bl_idname = "easycrop.toggle_gizmos"
    bl_label = "Toggle Gizmos"
    bl_description = "Toggle gizmo visibility in sequence editor"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Toggle gizmo visibility"""
        space = context.space_data
        
        if not space or space.type != 'SEQUENCE_EDITOR':
            self.report({'ERROR'}, "Not in sequence editor")
            return {'CANCELLED'}
        
        # Toggle main gizmo visibility
        if hasattr(space, 'show_gizmo'):
            space.show_gizmo = not space.show_gizmo
            status = "enabled" if space.show_gizmo else "disabled"
            self.report({'INFO'}, f"Gizmos {status}")
            
            # Also enable tool gizmos if enabling main gizmos
            if space.show_gizmo and hasattr(space, 'show_gizmo_tool'):
                space.show_gizmo_tool = True
                
        else:
            self.report({'ERROR'}, "Gizmo properties not found")
            return {'CANCELLED'}
        
        context.area.tag_redraw()
        return {'FINISHED'}


class EASYCROP_OT_fallback_crop(bpy.types.Operator):
    """Fallback crop operator using modal approach"""
    bl_idname = "easycrop.fallback_crop"
    bl_label = "Fallback Crop"
    bl_description = "Fallback to v1.0 modal crop if gizmos don't work"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not scene.sequence_editor:
            return False
        
        # Check if we're in preview mode
        space = context.space_data
        if space and space.type == 'SEQUENCE_EDITOR':
            if space.view_type not in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
                return False
        
        # Check for croppable strips
        if scene.sequence_editor.active_strip and hasattr(scene.sequence_editor.active_strip, 'crop'):
            return True
        
        return False
    
    def execute(self, context):
        """Execute fallback crop"""
        self.report({'INFO'}, "Fallback crop not implemented - use v1.0 addon")
        return {'CANCELLED'}
    
    def invoke(self, context, event):
        """Invoke fallback crop"""
        # In a real implementation, this would call the v1.0 modal operator
        # For now, just inform the user
        self.report({'INFO'}, "Gizmo crop failed - install v1.0 addon for modal crop")
        return {'CANCELLED'}