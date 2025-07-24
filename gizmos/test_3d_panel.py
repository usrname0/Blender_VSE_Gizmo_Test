"""
3D Viewport N-Panel for testing gizmos
"""

import bpy
from bpy.types import Panel, Operator


class EASYCROP_OT_test_3d_gizmo(Operator):
    """Test the 3D viewport gizmo system"""
    bl_idname = "easycrop.test_3d_gizmo"
    bl_label = "Test 3D Gizmo"
    bl_description = "Test if gizmos work in the 3D viewport"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        self.report({'INFO'}, "Testing 3D gizmo system...")
        
        # Import and register the test gizmo
        try:
            from .test_3d_gizmo import register_3d_test_gizmo, unregister_3d_test_gizmo
            
            # Clean up first
            try:
                unregister_3d_test_gizmo()
            except:
                pass
            
            # Register fresh
            success = register_3d_test_gizmo()
            
            if success:
                self.report({'INFO'}, "3D test gizmo registered! Select an object to see it.")
                print("\n🎯 3D GIZMO TEST ACTIVE")
                print("Select any object in the 3D viewport to see the green sphere gizmo")
                print("Watch the console for debug messages when interacting with it")
            else:
                self.report({'ERROR'}, "Failed to register 3D test gizmo")
                
        except Exception as e:
            self.report({'ERROR'}, f"Failed to test 3D gizmo: {e}")
            print(f"3D Gizmo test error: {e}")
            import traceback
            traceback.print_exc()
        
        return {'FINISHED'}


class EASYCROP_OT_cleanup_3d_gizmo(Operator):
    """Clean up the 3D test gizmo"""
    bl_idname = "easycrop.cleanup_3d_gizmo"
    bl_label = "Cleanup 3D Gizmo"
    bl_description = "Remove the 3D test gizmo"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        try:
            from .test_3d_gizmo import unregister_3d_test_gizmo
            unregister_3d_test_gizmo()
            self.report({'INFO'}, "3D test gizmo cleaned up")
            print("✓ 3D test gizmo removed")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to cleanup: {e}")
            
        return {'FINISHED'}


class EASYCROP_OT_compare_gizmos(Operator):
    """Compare VSE vs 3D gizmo behavior"""
    bl_idname = "easycrop.compare_gizmos"
    bl_label = "Compare Gizmo Systems"
    bl_description = "Run a comparison test between VSE and 3D viewport gizmos"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        print("\n" + "="*60)
        print("🔬 GIZMO SYSTEM COMPARISON TEST")
        print("="*60)
        
        # Test 3D viewport gizmo
        print("\n📋 Testing 3D Viewport Gizmo:")
        try:
            from .test_3d_gizmo import register_3d_test_gizmo, unregister_3d_test_gizmo
            
            # Clean and register 3D gizmo
            try:
                unregister_3d_test_gizmo()
            except:
                pass
                
            success_3d = register_3d_test_gizmo()
            print(f"✓ 3D Gizmo Registration: {'SUCCESS' if success_3d else 'FAILED'}")
            
        except Exception as e:
            print(f"✗ 3D Gizmo Test Error: {e}")
            success_3d = False
        
        # Test VSE gizmo  
        print("\n📋 Testing VSE Gizmo:")
        try:
            from .crop_gizmo_group import register_gizmo_classes, unregister_gizmo_classes
            
            # Clean and register VSE gizmo
            try:
                unregister_gizmo_classes()
            except:
                pass
                
            success_vse = register_gizmo_classes()
            print(f"✓ VSE Gizmo Registration: {'SUCCESS' if success_vse else 'FAILED'}")
            
        except Exception as e:
            print(f"✗ VSE Gizmo Test Error: {e}")
            success_vse = False
        
        # Summary
        print("\n📊 COMPARISON RESULTS:")
        print(f"- 3D Viewport Gizmos: {'✅ Working' if success_3d else '❌ Failed'}")
        print(f"- VSE Gizmos: {'✅ Working' if success_vse else '❌ Failed'}")
        
        if success_3d and success_vse:
            print("\n🎯 NEXT STEPS:")
            print("1. Switch to 3D viewport, select object → Should see green sphere")
            print("2. Switch to VSE, select strip → Should see crop handles")
            print("3. Monitor console for poll()/setup()/draw() calls")
            print("4. Compare which system actually activates its gizmos")
        elif success_3d and not success_vse:
            print("\n🔍 CONCLUSION: VSE gizmos are specifically broken")
            print("- 3D gizmos register successfully")
            print("- VSE gizmos fail to register or activate")
        elif not success_3d and not success_vse:
            print("\n🔍 CONCLUSION: General gizmo system issue")
            print("- Neither system works properly")
        else:
            print("\n🔍 CONCLUSION: Unexpected result - investigate further")
        
        print("="*60)
        
        if success_3d or success_vse:
            self.report({'INFO'}, "Comparison test complete - check console for results")
        else:
            self.report({'ERROR'}, "Both gizmo systems failed - check console")
            
        return {'FINISHED'}


class EASYCROP_PT_gizmo_test(Panel):
    """Panel for testing gizmo functionality"""
    bl_label = "Gizmo Tests"
    bl_idname = "EASYCROP_PT_gizmo_test"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "EasyCrop"
    
    def draw(self, context):
        layout = self.layout
        
        # Title
        box = layout.box()
        box.label(text="🔬 Gizmo System Tests", icon='TOOL_SETTINGS')
        
        # 3D Viewport Tests
        col = layout.column(align=True)
        col.label(text="3D Viewport:", icon='VIEW3D')
        col.operator("easycrop.test_3d_gizmo", icon='PLAY')
        col.operator("easycrop.cleanup_3d_gizmo", icon='TRASH')
        
        layout.separator()
        
        # Comparison Test
        col = layout.column(align=True)
        col.label(text="Comparison:", icon='ARROW_LEFTRIGHT')
        col.operator("easycrop.compare_gizmos", icon='SORT_ASC')
        
        layout.separator()
        
        # Instructions
        box = layout.box()
        box.label(text="📋 Test Instructions:", icon='INFO')
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="1. Click 'Test 3D Gizmo'")
        col.label(text="2. Select any object")
        col.label(text="3. Look for green sphere")
        col.label(text="4. Check console output")
        
        # Current status
        layout.separator()
        box = layout.box()
        box.label(text="Expected Results:", icon='CHECKMARK')
        col = box.column(align=True)
        col.scale_y = 0.8
        
        if context.active_object:
            col.label(text="✓ Object selected", icon='CHECKMARK')
        else:
            col.label(text="⚠ No object selected", icon='ERROR')
            
        col.label(text="Watch console for:")
        col.label(text="• poll() calls")
        col.label(text="• setup() calls") 
        col.label(text="• draw() calls")


def register_test_panel():
    """Register the test panel classes"""
    try:
        bpy.utils.register_class(EASYCROP_OT_test_3d_gizmo)
        bpy.utils.register_class(EASYCROP_OT_cleanup_3d_gizmo) 
        bpy.utils.register_class(EASYCROP_OT_compare_gizmos)
        bpy.utils.register_class(EASYCROP_PT_gizmo_test)
        print("✓ Registered gizmo test panel")
        return True
    except Exception as e:
        print(f"Failed to register test panel: {e}")
        return False


def unregister_test_panel():
    """Unregister the test panel classes"""
    try:
        bpy.utils.unregister_class(EASYCROP_PT_gizmo_test)
        bpy.utils.unregister_class(EASYCROP_OT_compare_gizmos)
        bpy.utils.unregister_class(EASYCROP_OT_cleanup_3d_gizmo)
        bpy.utils.unregister_class(EASYCROP_OT_test_3d_gizmo)
        print("✓ Unregistered gizmo test panel")
    except Exception as e:
        print(f"Failed to unregister test panel: {e}")