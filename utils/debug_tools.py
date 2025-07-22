"""
BL Easy Crop v2.0.0 - Debug Tools

Debug operators and utilities for testing gizmo functionality.
"""

import bpy
from bpy.types import Operator, Panel


class EASYCROP_OT_debug_gizmo_registration(bpy.types.Operator):
    """Debug: Check if gizmo classes are properly registered"""
    bl_idname = "easycrop.debug_gizmo_registration"
    bl_label = "Debug Gizmo Registration"
    bl_description = "Check if gizmo classes are registered correctly"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Check gizmo registration status"""
        report_lines = ["=== Gizmo Registration Debug ==="]
        
        # Check if our gizmo classes exist
        try:
            from ..gizmos.crop_gizmo_group import CropGizmo, CropGizmoGroup
            report_lines.append("✓ Gizmo classes imported successfully")
            
            # Check if they're registered with Blender
            try:
                gizmo_type = bpy.types.EASYCROP_GT_crop_handle
                report_lines.append("✓ CropGizmo registered with Blender")
            except AttributeError:
                report_lines.append("✗ CropGizmo NOT registered with Blender")
            
            try:
                gizmo_group_type = bpy.types.EASYCROP_GGT_crop_gizmo
                report_lines.append("✓ CropGizmoGroup registered with Blender")
            except AttributeError:
                report_lines.append("✗ CropGizmoGroup NOT registered with Blender")
                
        except ImportError as e:
            report_lines.append(f"✗ Failed to import gizmo classes: {e}")
        
        # Check workspace tool registration
        try:
            tool_type = bpy.types.EASYCROP_TOOL_crop_v2
            report_lines.append("✓ Crop tool registered")
        except AttributeError:
            report_lines.append("✗ Crop tool NOT registered")
        
        # Print to console
        for line in report_lines:
            print(line)
        
        self.report({'INFO'}, "Gizmo registration check complete - see console")
        return {'FINISHED'}


class EASYCROP_OT_final_gizmo_test(bpy.types.Operator):
    """Final test with proper sequence editor gizmo context"""
    bl_idname = "easycrop.final_gizmo_test"
    bl_label = "Final Gizmo Test"
    bl_description = "Test gizmos with proper sequence editor context settings"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test with all proper context settings"""
        print("=== FINAL GIZMO TEST ===")
        
        space = context.space_data
        if not space or space.type != 'SEQUENCE_EDITOR':
            self.report({'ERROR'}, "Must be in sequence editor")
            return {'CANCELLED'}
        
        print(f"Space type: {space.type}")
        print(f"View type: {space.view_type}")
        
        # Enable ALL gizmo settings that might be needed
        try:
            print("Setting all gizmo properties...")
            space.show_gizmo = True
            space.show_gizmo_tool = True
            space.show_gizmo_context = True  # This might be the key!
            space.show_gizmo_navigate = True
            print("✓ All gizmo properties enabled")
        except Exception as e:
            print(f"Failed to set gizmo properties: {e}")
        
        # Now try to register and ensure our test gizmo
        try:
            # Clean registration
            try:
                bpy.utils.unregister_class(SimpleTestGizmoGroup)
                bpy.utils.unregister_class(SimpleTestGizmo)
            except:
                pass
            
            bpy.utils.register_class(SimpleTestGizmo)
            bpy.utils.register_class(SimpleTestGizmoGroup)
            print("✓ Registered simple test gizmo classes")
            
            # Ensure with context
            wm = context.window_manager
            wm.gizmo_group_type_ensure(SimpleTestGizmoGroup.bl_idname)
            print("✓ Ensured gizmo group with full context")
            
            # Force multiple redraws
            context.area.tag_redraw()
            if hasattr(context, 'region'):
                context.region.tag_redraw()
            # Remove the workspace tag_redraw - it doesn't exist
            
            self.report({'INFO'}, "Final test complete - check for poll messages and red box")
            
        except Exception as e:
            print(f"Final test failed: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_debug_context_gizmos(bpy.types.Operator):
    """Debug all context gizmo settings"""
    bl_idname = "easycrop.debug_context_gizmos"
    bl_label = "Debug Context Gizmos"
    bl_description = "Show all gizmo context settings"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Debug context gizmo settings"""
        space = context.space_data
        if not space:
            self.report({'ERROR'}, "No space data")
            return {'CANCELLED'}
        
        print("=== GIZMO CONTEXT DEBUG ===")
        print(f"Space type: {space.type}")
        
        # Check all gizmo-related properties
        gizmo_props = [
            'show_gizmo',
            'show_gizmo_tool', 
            'show_gizmo_context',
            'show_gizmo_navigate'
        ]
        
        print("Current gizmo settings:")
        for prop in gizmo_props:
            if hasattr(space, prop):
                value = getattr(space, prop)
                print(f"  {prop}: {value}")
            else:
                print(f"  {prop}: NOT AVAILABLE")
        
        # Also check workspace tool
        if hasattr(context, 'workspace'):
            print(f"Active workspace: {context.workspace.name}")
        
        if hasattr(context, 'mode'):
            print(f"Context mode: {context.mode}")
            
        # Check active tool
        wm = context.window_manager
        if hasattr(wm, 'tools'):
            print(f"Window manager has tools: True")
        else:
            print(f"Window manager has tools: False")
        
        self.report({'INFO'}, "Context debug complete - see console")
        return {'FINISHED'}


class SimpleTestGizmo(bpy.types.Gizmo):
    """Very simple test gizmo that should always be visible"""
    bl_idname = "EASYCROP_GT_simple_test"
    
    def draw(self, context):
        """Draw a simple box at a fixed position"""
        print("SimpleTestGizmo.draw() called!")
        
        # Set bright color so it's visible
        self.color = (1.0, 0.0, 0.0)  # Bright red
        self.alpha = 1.0
        
        # Use a simple preset shape at a fixed size
        from mathutils import Matrix
        matrix = Matrix.Translation((0, 0, 0)) @ Matrix.Scale(50, 4)
        self.draw_preset_box(matrix, select_id=self.select_id)
    
    def invoke(self, context, event):
        """Handle clicks"""
        print("SimpleTestGizmo clicked!")
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event, tweak):
        """Handle drag"""
        print(f"SimpleTestGizmo dragged: {tweak.delta}")
        return {'RUNNING_MODAL'}


class SimpleTestGizmoGroup(bpy.types.GizmoGroup):
    """Simple test gizmo group"""
    bl_idname = "EASYCROP_GGT_simple_test"
    bl_label = "Simple Test Gizmo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'PREVIEW'
    bl_options = {'3D'}
    
    @classmethod
    def poll(cls, context):
        """Always show if in sequence editor preview"""
        print("SimpleTestGizmoGroup.poll() called")
        
        if not context.space_data or context.space_data.type != 'SEQUENCE_EDITOR':
            print("- Not in sequence editor")
            return False
            
        if context.space_data.view_type not in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            print("- Not in preview mode")
            return False
            
        print("- Simple test poll passed!")
        return True
    
    def setup(self, context):
        """Setup the test gizmo"""
        print("SimpleTestGizmoGroup.setup() called")
        
        # Create one simple test gizmo
        gizmo = self.gizmos.new(SimpleTestGizmo.bl_idname)
        gizmo.select_id = 0
        
        # Position it at the center of the preview
        from mathutils import Matrix
        gizmo.matrix_basis = Matrix.Translation((0, 0, 0))
        
        print(f"Created simple test gizmo: {gizmo}")
    
    def refresh(self, context):
        """Refresh gizmo positions"""
        print("SimpleTestGizmoGroup.refresh() called")
        
        # Keep gizmo at center
        if len(self.gizmos) > 0:
            gizmo = self.gizmos[0]
            from mathutils import Matrix
            gizmo.matrix_basis = Matrix.Translation((0, 0, 0))
    
    def draw_prepare(self, context):
        """Prepare for drawing"""
        print("SimpleTestGizmoGroup.draw_prepare() called")
        self.refresh(context)


class EASYCROP_OT_test_simple_gizmo(bpy.types.Operator):
    """Test the simple gizmo system"""
    bl_idname = "easycrop.test_simple_gizmo"
    bl_label = "Test Simple Gizmo"
    bl_description = "Register and test a very simple gizmo"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Register the simple test gizmo"""
        try:
            # Try to unregister first in case they're already registered
            try:
                bpy.utils.unregister_class(SimpleTestGizmoGroup)
                bpy.utils.unregister_class(SimpleTestGizmo)
                print("Unregistered existing simple test gizmo classes")
            except:
                pass
            
            # Register the simple gizmo classes
            bpy.utils.register_class(SimpleTestGizmo)
            bpy.utils.register_class(SimpleTestGizmoGroup)
            print("✓ Registered simple test gizmo classes")
            
            # Try to ensure it
            wm = context.window_manager
            wm.gizmo_group_type_ensure(SimpleTestGizmoGroup.bl_idname)
            print("✓ Ensured simple test gizmo group")
            
            # Force redraw
            context.area.tag_redraw()
            
            self.report({'INFO'}, "Simple test gizmo registered - check console for poll/setup messages")
            
        except Exception as e:
            print(f"✗ Failed to register simple test gizmo: {e}")
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_cleanup_simple_gizmo(bpy.types.Operator):
    """Clean up the simple test gizmo"""
    bl_idname = "easycrop.cleanup_simple_gizmo"
    bl_label = "Cleanup Simple Gizmo"
    bl_description = "Unregister the simple test gizmo"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Unregister the simple test gizmo"""
        try:
            # Unregister the simple gizmo classes
            bpy.utils.unregister_class(SimpleTestGizmoGroup)
            bpy.utils.unregister_class(SimpleTestGizmo)
            print("✓ Unregistered simple test gizmo classes")
            
            # Force redraw
            context.area.tag_redraw()
            
            self.report({'INFO'}, "Simple test gizmo cleaned up")
            
        except Exception as e:
            print(f"✗ Failed to cleanup simple test gizmo: {e}")
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_debug_gizmo_detailed(bpy.types.Operator):
    """Detailed gizmo debug - test various region types"""
    bl_idname = "easycrop.debug_gizmo_detailed"
    bl_label = "Debug Gizmo Detailed"
    bl_description = "Test different region types and poll conditions"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test different approaches to gizmo registration"""
        print("=" * 60)
        print("DETAILED GIZMO DEBUG")
        print("=" * 60)
        
        # Test if poll is ever called
        try:
            from ..gizmos.crop_gizmo_group import CropGizmoGroup
            print(f"✓ CropGizmoGroup imported: {CropGizmoGroup}")
            print(f"✓ bl_idname: {CropGizmoGroup.bl_idname}")
            print(f"✓ bl_space_type: {CropGizmoGroup.bl_space_type}")
            print(f"✓ bl_region_type: {CropGizmoGroup.bl_region_type}")
            print(f"✓ bl_options: {CropGizmoGroup.bl_options}")
            
            # Test poll manually
            print("\n--- Testing poll manually ---")
            poll_result = CropGizmoGroup.poll(context)
            print(f"Manual poll result: {poll_result}")
            
            # Test if the gizmo group is in the window manager
            print("\n--- Testing window manager ---")
            wm = context.window_manager
            
            # Try to find gizmo-related attributes
            gizmo_attrs = [attr for attr in dir(wm) if 'gizmo' in attr.lower()]
            print(f"Window manager gizmo attributes: {gizmo_attrs}")
            
            # Try to ensure the gizmo group
            try:
                wm.gizmo_group_type_ensure(CropGizmoGroup.bl_idname)
                print(f"✓ gizmo_group_type_ensure succeeded")
            except Exception as e:
                print(f"✗ gizmo_group_type_ensure failed: {e}")
            
            # Check if it exists in bpy.types now
            try:
                gizmo_type = getattr(bpy.types, "EASYCROP_GT_crop_handle", None)
                print(f"CropGizmo in bpy.types: {gizmo_type}")
                
                gizmo_group_type = getattr(bpy.types, "EASYCROP_GGT_crop_gizmo", None)
                print(f"CropGizmoGroup in bpy.types: {gizmo_group_type}")
                
                tool_type = getattr(bpy.types, "EASYCROP_TOOL_crop_v2", None)
                print(f"Tool in bpy.types: {tool_type}")
                
                # Try alternative ways to find gizmos
                print("\n--- Alternative gizmo detection ---")
                from ..gizmos.crop_gizmo_group import CropGizmo, CropGizmoGroup
                
                # Check if we can find subclasses
                try:
                    gizmo_subclasses = bpy.types.Gizmo.__subclasses__()
                    crop_gizmos = [g for g in gizmo_subclasses if 'crop' in g.__name__.lower() or 'EASYCROP' in g.__name__]
                    print(f"Gizmo subclasses with 'crop': {crop_gizmos}")
                    
                    gizmo_group_subclasses = bpy.types.GizmoGroup.__subclasses__()
                    crop_gizmo_groups = [g for g in gizmo_group_subclasses if 'crop' in g.__name__.lower() or 'EASYCROP' in g.__name__]
                    print(f"GizmoGroup subclasses with 'crop': {crop_gizmo_groups}")
                    
                except Exception as e:
                    print(f"Failed to check subclasses: {e}")
                
                # Try bl_rna_get_subclass method
                try:
                    crop_gizmo_via_rna = bpy.types.Gizmo.bl_rna_get_subclass('EASYCROP_GT_crop_handle')
                    print(f"CropGizmo via bl_rna_get_subclass: {crop_gizmo_via_rna}")
                    
                    crop_group_via_rna = bpy.types.GizmoGroup.bl_rna_get_subclass('EASYCROP_GGT_crop_gizmo')
                    print(f"CropGizmoGroup via bl_rna_get_subclass: {crop_group_via_rna}")
                    
                except Exception as e:
                    print(f"bl_rna_get_subclass failed: {e}")
                
            except Exception as e:
                print(f"Error checking bpy.types: {e}")
            
        except Exception as e:
            print(f"✗ Error during detailed debug: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 60)
        self.report({'INFO'}, "Detailed gizmo debug complete - see console")
        return {'FINISHED'}


class EASYCROP_OT_test_region_types(bpy.types.Operator):
    """Test different region types for gizmos"""
    bl_idname = "easycrop.test_region_types"
    bl_label = "Test Region Types"
    bl_description = "Test different region types for gizmo registration"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test different region types"""
        from bpy.types import GizmoGroup
        
        print("=" * 50)
        print("TESTING REGION TYPES")
        print("=" * 50)
        
        # Test different region types by creating temporary gizmo groups
        region_types_to_test = ['WINDOW', 'PREVIEW', 'UI', 'TOOLS', 'TOOL_PROPS']
        
        for region_type in region_types_to_test:
            print(f"\n--- Testing region_type: '{region_type}' ---")
            
            try:
                # Create a test gizmo group class dynamically
                class TestGizmoGroupClass(GizmoGroup):
                    bl_idname = f"TEST_GGT_{region_type.lower()}"
                    bl_label = f"Test {region_type}"
                    bl_space_type = 'SEQUENCE_EDITOR'
                    bl_region_type = region_type
                    bl_options = {'3D'}  # Remove PERSISTENT to test if that was the issue
                    
                    @classmethod
                    def poll(cls, context):
                        return True
                    
                    def setup(self, context):
                        pass
                    
                    def refresh(self, context):
                        pass
                
                # Try to register it
                bpy.utils.register_class(TestGizmoGroupClass)
                print(f"✓ Registered test gizmo group with region_type '{region_type}'")
                
                # Check if it appears in bpy.types
                test_id = f"TEST_GGT_{region_type.lower()}"
                if hasattr(bpy.types, test_id):
                    print(f"✓ Found in bpy.types: {getattr(bpy.types, test_id)}")
                else:
                    print(f"✗ NOT found in bpy.types")
                
                # Clean up
                try:
                    bpy.utils.unregister_class(TestGizmoGroupClass)
                    print(f"✓ Unregistered test class")
                except:
                    print(f"✗ Failed to unregister test class")
                    
            except Exception as e:
                print(f"✗ Failed to test region_type '{region_type}': {e}")
        
        print("=" * 50)
        self.report({'INFO'}, "Region type test complete - see console")
        return {'FINISHED'}


class EASYCROP_OT_debug_gizmo_poll(bpy.types.Operator):
    """Debug: Test gizmo group poll conditions"""
    bl_idname = "easycrop.debug_gizmo_poll"
    bl_label = "Debug Gizmo Poll"
    bl_description = "Test if gizmo group poll conditions are met"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test gizmo poll conditions"""
        report_lines = ["=== Gizmo Poll Debug ==="]
        
        try:
            from ..gizmos.crop_gizmo_group import CropGizmoGroup
            
            # Test poll conditions step by step
            space = context.space_data
            report_lines.append(f"Space type: {space.type if space else 'None'}")
            
            if space and space.type == 'SEQUENCE_EDITOR':
                report_lines.append("✓ In sequence editor")
                
                view_type = getattr(space, 'view_type', 'UNKNOWN')
                report_lines.append(f"View type: {view_type}")
                
                if view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
                    report_lines.append("✓ In preview mode")
                else:
                    report_lines.append("✗ Not in preview mode")
                
                # Check sequence editor
                seq_editor = context.scene.sequence_editor
                if seq_editor:
                    report_lines.append("✓ Has sequence editor")
                    
                    active_strip = seq_editor.active_strip
                    if active_strip:
                        report_lines.append(f"✓ Has active strip: {active_strip.name}")
                        
                        if hasattr(active_strip, 'crop'):
                            report_lines.append("✓ Active strip has crop")
                            
                            # Check visibility
                            from ..core.geometry_utils import is_strip_visible_at_frame
                            current_frame = context.scene.frame_current
                            if is_strip_visible_at_frame(active_strip, current_frame):
                                report_lines.append("✓ Strip visible at current frame")
                            else:
                                report_lines.append("✗ Strip NOT visible at current frame")
                        else:
                            report_lines.append("✗ Active strip has no crop")
                    else:
                        report_lines.append("✗ No active strip")
                else:
                    report_lines.append("✗ No sequence editor")
            else:
                report_lines.append("✗ Not in sequence editor")
            
            # Test actual poll
            poll_result = CropGizmoGroup.poll(context)
            report_lines.append(f"Final poll result: {poll_result}")
            
        except Exception as e:
            report_lines.append(f"✗ Error during poll test: {e}")
        
        # Print to console
        for line in report_lines:
            print(line)
        
        self.report({'INFO'}, "Gizmo poll test complete - see console")
        return {'FINISHED'}


class EASYCROP_OT_debug_force_gizmo_refresh(bpy.types.Operator):
    """Debug: Force gizmo refresh"""
    bl_idname = "easycrop.debug_force_gizmo_refresh"
    bl_label = "Force Gizmo Refresh"
    bl_description = "Force refresh of gizmo system"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Force gizmo refresh"""
        try:
            # Try to refresh the workspace
            if hasattr(context, 'workspace'):
                context.workspace.tag_redraw()
            
            # Force area redraw
            if context.area:
                context.area.tag_redraw()
            
            # Try to refresh gizmo groups
            wm = context.window_manager
            if hasattr(wm, 'gizmo_group_type_ensure'):
                try:
                    wm.gizmo_group_type_ensure("EASYCROP_GGT_crop_gizmo")
                    self.report({'INFO'}, "Gizmo group refresh attempted")
                except Exception as e:
                    self.report({'WARNING'}, f"Gizmo refresh failed: {e}")
            else:
                self.report({'INFO'}, "Forced area redraw")
                
        except Exception as e:
            self.report({'ERROR'}, f"Refresh failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


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


class EASYCROP_PT_debug_panel(Panel):
    """Debug panel for gizmo testing"""
    bl_label = "Easy Crop v2.0 Debug"
    bl_idname = "EASYCROP_PT_debug_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Crop Debug"
    
    @classmethod
    def poll(cls, context):
        return (context.space_data and 
                context.space_data.type == 'SEQUENCE_EDITOR')
    
    def draw(self, context):
        layout = self.layout
        
        # Warning box
        box = layout.box()
        box.label(text="⚠ Experimental v2.0.0", icon='ERROR')
        box.label(text="Debug tools for gizmo testing")
        
        layout.separator()
        
        # Debug operators
        col = layout.column(align=True)
        col.label(text="Debug Tools:")
        col.operator("easycrop.debug_gizmo_registration", text="Check Registration")
        col.operator("easycrop.debug_gizmo_poll", text="Test Poll Conditions")
        col.operator("easycrop.debug_force_gizmo_refresh", text="Force Refresh")
        
        # Enhanced debug tools
        col.separator()
        col.operator("easycrop.debug_gizmo_detailed", text="Detailed Debug")
        col.operator("easycrop.test_region_types", text="Test Region Types")
        
        # Simple gizmo test
        col.separator()
        col.label(text="Simple Gizmo Test:")
        col.operator("easycrop.test_simple_gizmo", text="Test Simple Gizmo")
        col.operator("easycrop.cleanup_simple_gizmo", text="Cleanup Test Gizmo")
        
        # Minimal VSE gizmo test
        col.separator()
        col.label(text="Minimal VSE Gizmo:")
        col.operator("easycrop.test_minimal_vse_gizmo", text="Test Minimal VSE")
        col.operator("easycrop.cleanup_minimal_vse_gizmo", text="Cleanup Minimal VSE")
        
        # NEW MISSING TESTS - The ones we haven't tried yet!
        col.separator()
        col.label(text="🚨 MISSING TESTS:")
        box = col.box()
        box.label(text="Tests we haven't tried yet!", icon='ERROR')
        box.operator("easycrop.test_tool_activation_gizmos", text="1. Tool Activation Test")
        box.operator("easycrop.test_target_properties_gizmo", text="2. Target Properties Test") 
        box.operator("easycrop.cleanup_target_props_gizmo", text="Cleanup Target Props")
        
        # FINAL SCIENCE TEST
        col.separator()
        col.label(text="🔬 FINAL SCIENCE TEST:")
        box = col.box()
        box.operator("easycrop.debug_context_gizmos", text="1. Debug Context")
        box.operator("easycrop.final_gizmo_test", text="2. FINAL GIZMO TEST")
        box.label(text="Enable show_gizmo_context!", icon='HELP')
        
        layout.separator()
        
        # Gizmo controls - now using the correct operator names
        col = layout.column(align=True)
        col.label(text="Gizmo Controls:")
        col.operator("easycrop.test_gizmo_system", text="Test Gizmo System")
        col.operator("easycrop.toggle_gizmos", text="Toggle Gizmos")
        
        layout.separator()
        
        # Current status
        space = context.space_data
        if space:
            box = layout.box()
            box.label(text="Current Status:")
            box.label(text=f"View: {getattr(space, 'view_type', 'Unknown')}")
            
            if hasattr(space, 'show_gizmo'):
                box.label(text=f"Gizmos: {'On' if space.show_gizmo else 'Off'}")
            
            if hasattr(space, 'show_gizmo_tool'):
                box.label(text=f"Tool Gizmos: {'On' if space.show_gizmo_tool else 'Off'}")
            
            seq_editor = context.scene.sequence_editor
            if seq_editor and seq_editor.active_strip:
                box.label(text=f"Active: {seq_editor.active_strip.name}")
                if hasattr(seq_editor.active_strip, 'crop'):
                    crop = seq_editor.active_strip.crop
                    box.label(text=f"Crop: L{crop.min_x} R{crop.max_x} B{crop.min_y} T{crop.max_y}")


class EASYCROP_OT_debug_coordinate_test(bpy.types.Operator):
    """Debug: Test coordinate transformations"""
    bl_idname = "easycrop.debug_coordinate_test"
    bl_label = "Test Coordinates"
    bl_description = "Test coordinate transformation functions"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test coordinate transformations"""
        seq_editor = context.scene.sequence_editor
        if not seq_editor or not seq_editor.active_strip:
            self.report({'ERROR'}, "No active strip")
            return {'CANCELLED'}
        
        strip = seq_editor.active_strip
        if not hasattr(strip, 'crop'):
            self.report({'ERROR'}, "Active strip has no crop")
            return {'CANCELLED'}
        
        try:
            from ..core.geometry_utils import get_strip_geometry_with_flip_support
            
            scene = context.scene
            corners, (pivot_x, pivot_y), (scale_x, scale_y, flip_x, flip_y) = get_strip_geometry_with_flip_support(strip, scene)
            
            print("=== Coordinate Test ===")
            print(f"Strip: {strip.name}")
            print(f"Pivot: ({pivot_x:.1f}, {pivot_y:.1f})")
            print(f"Scale: ({scale_x:.2f}, {scale_y:.2f})")
            print(f"Flip: X={flip_x}, Y={flip_y}")
            print("Corners:")
            for i, corner in enumerate(corners):
                print(f"  {i}: ({corner.x:.1f}, {corner.y:.1f})")
            
            if strip.crop:
                print(f"Crop: L{strip.crop.min_x} R{strip.crop.max_x} B{strip.crop.min_y} T{strip.crop.max_y}")
            
            self.report({'INFO'}, "Coordinate test complete - see console")
            
        except Exception as e:
            self.report({'ERROR'}, f"Coordinate test failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_debug_create_test_strip(bpy.types.Operator):
    """Debug: Create a test strip for gizmo testing"""
    bl_idname = "easycrop.debug_create_test_strip"
    bl_label = "Create Test Strip"
    bl_description = "Create a test color strip for gizmo testing"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Create a test strip"""
        scene = context.scene
        
        # Ensure we have a sequence editor
        if not scene.sequence_editor:
            scene.sequence_editor_create()
        
        # Create a color strip
        try:
            current_frame = scene.frame_current
            
            # Add color strip
            bpy.ops.sequencer.effect_strip_add(
                type='COLOR',
                frame_start=current_frame,
                frame_end=current_frame + 100,
                channel=1
            )
            
            # Get the created strip
            strip = scene.sequence_editor.active_strip
            if strip:
                strip.name = "Test Strip for Gizmos"
                strip.color = (0.8, 0.4, 0.2)  # Orange color
                
                # Add some crop values for testing
                if hasattr(strip, 'crop'):
                    strip.crop.min_x = 50
                    strip.crop.max_x = 50
                    strip.crop.min_y = 30
                    strip.crop.max_y = 30
                
                self.report({'INFO'}, f"Created test strip: {strip.name}")
            else:
                self.report({'ERROR'}, "Failed to create test strip")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create test strip: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_debug_gizmo_matrix_test(bpy.types.Operator):
    """Debug: Test gizmo matrix calculations"""
    bl_idname = "easycrop.debug_gizmo_matrix_test"
    bl_label = "Test Gizmo Matrices"
    bl_description = "Test gizmo matrix calculations and positioning"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test gizmo matrix calculations"""
        try:
            from mathutils import Matrix, Vector
            
            print("=== Gizmo Matrix Test ===")
            
            # Test basic matrix operations
            print("Testing basic matrix operations...")
            
            # Translation matrix
            pos = Vector((100, 200, 0))
            trans_matrix = Matrix.Translation(pos)
            print(f"Translation matrix for {pos}: {trans_matrix}")
            
            # Scale matrix
            scale = 2.0
            scale_matrix = Matrix.Scale(scale, 4)
            print(f"Scale matrix for {scale}: {scale_matrix}")
            
            # Combined matrix
            combined = trans_matrix @ scale_matrix
            print(f"Combined matrix: {combined}")
            
            # Test with sequence editor coordinates
            if context.region and context.region.view2d:
                view2d = context.region.view2d
                
                # Test coordinate conversion
                screen_pos = (100, 100)
                view_pos = view2d.region_to_view(*screen_pos)
                back_to_screen = view2d.view_to_region(*view_pos)
                
                print(f"Screen {screen_pos} -> View {view_pos} -> Screen {back_to_screen}")
            
            self.report({'INFO'}, "Matrix test complete - see console")
            
        except Exception as e:
            self.report({'ERROR'}, f"Matrix test failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_test_minimal_vse_gizmo(bpy.types.Operator):
    """Test a minimal VSE gizmo based on working patterns"""
    bl_idname = "easycrop.test_minimal_vse_gizmo"
    bl_label = "Test Minimal VSE Gizmo"
    bl_description = "Test a minimal gizmo that mimics working VSE gizmos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test minimal VSE gizmo approach"""
        try:
            from mathutils import Matrix
            
            print("=== MINIMAL VSE GIZMO TEST ===")
            
            # Define minimal gizmo classes
            class MinimalVSEGizmo(bpy.types.Gizmo):
                bl_idname = 'MINIMAL_VSE_GT_test'
                
                def draw(self, context):
                    print("MinimalVSEGizmo.draw() called!")
                    self.color = (1.0, 0.0, 0.0)  # Red
                    self.alpha = 1.0
                    matrix = Matrix.Scale(20, 4)
                    self.draw_preset_box(matrix, select_id=self.select_id)
                
                def invoke(self, context, event):
                    print("MinimalVSEGizmo.invoke() called!")
                    return {'RUNNING_MODAL'}
            
            class MinimalVSEGizmoGroup(bpy.types.GizmoGroup):
                bl_idname = 'MINIMAL_VSE_GGT_test'
                bl_label = 'Minimal VSE Test'
                bl_space_type = 'SEQUENCE_EDITOR'
                bl_region_type = 'PREVIEW'
                bl_options = {'3D'}  # Matching working VSE gizmos
                
                @classmethod
                def poll(cls, context):
                    print('MinimalVSEGizmoGroup.poll() called!')
                    if not context.space_data or context.space_data.type != 'SEQUENCE_EDITOR':
                        print('- Not in sequence editor')
                        return False
                    if context.space_data.view_type != 'PREVIEW':
                        print('- Not in preview mode')
                        return False
                    print('- Minimal poll passed!')
                    return True
                
                def setup(self, context):
                    print('MinimalVSEGizmoGroup.setup() called!')
                    gizmo = self.gizmos.new(MinimalVSEGizmo.bl_idname)
                    gizmo.select_id = 0
                    gizmo.matrix_basis = Matrix.Translation((0, 0, 0))
                    print(f'- Created minimal gizmo: {gizmo}')
            
            # Clean up any existing registration
            try:
                bpy.utils.unregister_class(getattr(bpy.types, 'MINIMAL_VSE_GGT_test', None))
                bpy.utils.unregister_class(getattr(bpy.types, 'MINIMAL_VSE_GT_test', None))
            except:
                pass
            
            # Register the minimal gizmo classes
            bpy.utils.register_class(MinimalVSEGizmo)
            print("✓ Registered MinimalVSEGizmo")
            
            bpy.utils.register_class(MinimalVSEGizmoGroup)
            print("✓ Registered MinimalVSEGizmoGroup")
            
            # Enable all gizmo settings if in sequence editor
            if context.space_data and context.space_data.type == 'SEQUENCE_EDITOR':
                space = context.space_data
                space.show_gizmo = True
                space.show_gizmo_tool = True
                if hasattr(space, 'show_gizmo_context'):
                    space.show_gizmo_context = True
                    print("✓ Enabled show_gizmo_context")
                print("✓ Enabled all gizmo settings")
            
            # Try to ensure the gizmo group
            wm = context.window_manager
            wm.gizmo_group_type_ensure('MINIMAL_VSE_GGT_test')
            print("✓ Ensured minimal VSE gizmo group")
            
            # Force redraw
            context.area.tag_redraw()
            
            self.report({'INFO'}, "Minimal VSE gizmo test complete - check for poll/draw calls")
            
        except Exception as e:
            print(f"✗ Minimal VSE gizmo test failed: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_test_tool_activation_gizmos(bpy.types.Operator):
    """Test if gizmos only work when tool is actively selected"""
    bl_idname = "easycrop.test_tool_activation_gizmos"
    bl_label = "Test Tool Activation"
    bl_description = "Test if gizmos activate only when the crop tool is selected"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test tool activation hypothesis"""
        try:
            print("=== TOOL ACTIVATION GIZMO TEST ===")
            
            # Check current tool
            if hasattr(context, 'workspace') and hasattr(context.workspace, 'tools'):
                try:
                    # Try to get current tool info
                    wm = context.window_manager
                    print(f"Window manager type: {type(wm)}")
                    
                    # Check if our tool is registered
                    try:
                        tool_type = getattr(bpy.types, 'EASYCROP_TOOL_crop_v2', None)
                        print(f"Tool class found: {tool_type}")
                        
                        if tool_type:
                            print(f"Tool bl_idname: {tool_type.bl_idname}")
                            print(f"Tool bl_widget: {getattr(tool_type, 'bl_widget', 'NOT SET')}")
                            print(f"Tool bl_widget_group: {getattr(tool_type, 'bl_widget_group', 'NOT SET')}")
                    except Exception as e:
                        print(f"Error checking tool: {e}")
                    
                except Exception as e:
                    print(f"Error accessing workspace tools: {e}")
            
            # Try to activate the tool explicitly
            print("\n--- Attempting to activate crop tool ---")
            try:
                # Method 1: Direct tool activation
                bpy.ops.wm.tool_set_by_id(name="easycrop.crop_tool_v2")
                print("✓ Tool activation command sent")
                
                # Wait a moment and check if gizmos activate
                import time
                time.sleep(0.1)
                
                # Force redraw
                context.area.tag_redraw()
                print("✓ Area redrawn")
                
            except Exception as e:
                print(f"✗ Tool activation failed: {e}")
            
            # Check if poll gets called now
            print("\n--- Checking for poll calls after tool activation ---")
            print("Look for 'CropGizmoGroup.poll() called' messages")
            
            # Also try ensuring gizmo group after tool activation
            try:
                wm = context.window_manager
                wm.gizmo_group_type_ensure("EASYCROP_GGT_crop_gizmo")
                print("✓ Re-ensured gizmo group after tool activation")
            except Exception as e:
                print(f"✗ Failed to re-ensure gizmo group: {e}")
            
            self.report({'INFO'}, "Tool activation test complete - check console for poll messages")
            
        except Exception as e:
            print(f"✗ Tool activation test failed: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_test_target_properties_gizmo(bpy.types.Operator):
    """Test gizmos with proper target property binding"""
    bl_idname = "easycrop.test_target_properties_gizmo"
    bl_label = "Test Target Properties"
    bl_description = "Test gizmos with target_set_prop() binding"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Test target property binding"""
        try:
            from mathutils import Matrix
            
            print("=== TARGET PROPERTIES GIZMO TEST ===")
            
            # Create a test gizmo with target properties
            class TargetPropsGizmo(bpy.types.Gizmo):
                bl_idname = 'TARGET_PROPS_GT_test'
                
                def setup(self):
                    print("TargetPropsGizmo.setup() called!")
                    
                    # Try to set up target properties if we have an active strip
                    scene = bpy.context.scene
                    if scene.sequence_editor and scene.sequence_editor.active_strip:
                        strip = scene.sequence_editor.active_strip
                        if hasattr(strip, 'crop'):
                            try:
                                # This is the key test - binding to actual properties
                                self.target_set_prop("offset", strip.crop, "min_x")
                                print("✓ Set target property: strip.crop.min_x")
                            except Exception as e:
                                print(f"✗ Failed to set target property: {e}")
                
                def draw(self, context):
                    print("TargetPropsGizmo.draw() called!")
                    self.color = (0.0, 1.0, 0.0)  # Green
                    self.alpha = 1.0
                    matrix = Matrix.Scale(25, 4)
                    self.draw_preset_box(matrix, select_id=self.select_id)
                
                def invoke(self, context, event):
                    print("TargetPropsGizmo.invoke() called!")
                    return {'RUNNING_MODAL'}
            
            class TargetPropsGizmoGroup(bpy.types.GizmoGroup):
                bl_idname = 'TARGET_PROPS_GGT_test'
                bl_label = 'Target Props Test'
                bl_space_type = 'SEQUENCE_EDITOR'
                bl_region_type = 'PREVIEW'
                bl_options = {'3D'}
                
                @classmethod
                def poll(cls, context):
                    print('TargetPropsGizmoGroup.poll() called!')
                    # Minimal poll to see if target properties help
                    return (context.space_data and 
                            context.space_data.type == 'SEQUENCE_EDITOR' and
                            context.space_data.view_type == 'PREVIEW')
                
                def setup(self, context):
                    print('TargetPropsGizmoGroup.setup() called!')
                    gizmo = self.gizmos.new(TargetPropsGizmo.bl_idname)
                    gizmo.select_id = 0
                    gizmo.matrix_basis = Matrix.Translation((0, 0, 0))
            
            # Clean up existing
            try:
                bpy.utils.unregister_class(getattr(bpy.types, 'TARGET_PROPS_GGT_test', None))
                bpy.utils.unregister_class(getattr(bpy.types, 'TARGET_PROPS_GT_test', None))
            except:
                pass
            
            # Register
            bpy.utils.register_class(TargetPropsGizmo)
            bpy.utils.register_class(TargetPropsGizmoGroup)
            print("✓ Registered target properties test gizmos")
            
            # Enable gizmo settings
            if context.space_data and context.space_data.type == 'SEQUENCE_EDITOR':
                space = context.space_data
                space.show_gizmo = True
                space.show_gizmo_tool = True
                if hasattr(space, 'show_gizmo_context'):
                    space.show_gizmo_context = True
                print("✓ Enabled gizmo settings")
            
            # Ensure
            wm = context.window_manager
            wm.gizmo_group_type_ensure('TARGET_PROPS_GGT_test')
            print("✓ Ensured target properties gizmo group")
            
            context.area.tag_redraw()
            
            self.report({'INFO'}, "Target properties test complete - check for poll/setup calls")
            
        except Exception as e:
            print(f"✗ Target properties test failed: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_cleanup_target_props_gizmo(bpy.types.Operator):
    """Clean up target properties test gizmo"""
    bl_idname = "easycrop.cleanup_target_props_gizmo"
    bl_label = "Cleanup Target Props"
    bl_description = "Remove target properties test gizmo"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Clean up target properties gizmo"""
        try:
            try:
                bpy.utils.unregister_class(getattr(bpy.types, 'TARGET_PROPS_GGT_test', None))
                print("✓ Unregistered TargetPropsGizmoGroup")
            except:
                pass
            
            try:
                bpy.utils.unregister_class(getattr(bpy.types, 'TARGET_PROPS_GT_test', None))
                print("✓ Unregistered TargetPropsGizmo")
            except:
                pass
            
            context.area.tag_redraw()
            self.report({'INFO'}, "Target properties cleanup complete")
            
        except Exception as e:
            print(f"✗ Cleanup failed: {e}")
            self.report({'ERROR'}, f"Failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class EASYCROP_OT_cleanup_minimal_vse_gizmo(bpy.types.Operator):
    """Clean up the minimal VSE gizmo test"""
    bl_idname = "easycrop.cleanup_minimal_vse_gizmo"
    bl_label = "Cleanup Minimal VSE Gizmo"
    bl_description = "Remove the minimal VSE gizmo test"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        """Clean up minimal VSE gizmo"""
        try:
            # Try to unregister the classes
            try:
                gizmo_group_type = getattr(bpy.types, 'MINIMAL_VSE_GGT_test', None)
                if gizmo_group_type:
                    bpy.utils.unregister_class(gizmo_group_type)
                    print("✓ Unregistered MinimalVSEGizmoGroup")
            except Exception as e:
                print(f"Warning: Failed to unregister gizmo group: {e}")
            
            try:
                gizmo_type = getattr(bpy.types, 'MINIMAL_VSE_GT_test', None)
                if gizmo_type:
                    bpy.utils.unregister_class(gizmo_type)
                    print("✓ Unregistered MinimalVSEGizmo")
            except Exception as e:
                print(f"Warning: Failed to unregister gizmo: {e}")
            
            # Force redraw
            context.area.tag_redraw()
            
            self.report({'INFO'}, "Minimal VSE gizmo cleanup complete")
            
        except Exception as e:
            print(f"✗ Cleanup failed: {e}")
            self.report({'ERROR'}, f"Cleanup failed: {e}")
            return {'CANCELLED'}
        
        return {'FINISHED'}


# Register debug classes
debug_classes = [
    EASYCROP_OT_debug_gizmo_registration,
    EASYCROP_OT_debug_gizmo_poll,
    EASYCROP_OT_debug_force_gizmo_refresh,
    EASYCROP_OT_debug_coordinate_test,
    EASYCROP_OT_debug_create_test_strip,
    EASYCROP_OT_debug_gizmo_matrix_test,
    EASYCROP_OT_test_gizmo_system,
    EASYCROP_OT_toggle_gizmos,
    EASYCROP_OT_debug_gizmo_detailed,  # Enhanced debug operators
    EASYCROP_OT_test_region_types,     # Region type tester
    EASYCROP_OT_test_simple_gizmo,     # Simple gizmo test
    EASYCROP_OT_cleanup_simple_gizmo,  # Simple gizmo cleanup
    EASYCROP_OT_final_gizmo_test,      # FINAL TEST - The Science!
    EASYCROP_OT_debug_context_gizmos,  # Context debugging
    EASYCROP_OT_test_minimal_vse_gizmo,     # Minimal VSE gizmo test
    EASYCROP_OT_cleanup_minimal_vse_gizmo,  # Minimal VSE gizmo cleanup
    EASYCROP_OT_test_tool_activation_gizmos,     # Tool activation test
    EASYCROP_OT_test_target_properties_gizmo,   # Target properties test
    EASYCROP_OT_cleanup_target_props_gizmo,     # Target properties cleanup
    EASYCROP_PT_debug_panel,
]


def register_debug_classes():
    """Register debug classes"""
    for cls in debug_classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Failed to register debug class {cls.__name__}: {e}")


def unregister_debug_classes():
    """Unregister debug classes"""
    for cls in reversed(debug_classes):
        try:
            bpy.utils.unregister_class(cls)
        except:
            pass