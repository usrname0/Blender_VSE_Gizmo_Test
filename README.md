# BL Easy Crop 2 gizmo (Not working. Do not use.)

This Blender extension is not for use and is an experiment for a gizmo-based version of a cropping tool in Blender's VSE.  A bunch of quick-and-dirty gizmo debugging tools can be seen in the VSE n-panel and also in the 3d Viewport n-panel.

TLDR 3d Viewport test gizmo succeeded!  VSE test gizmo failed.

If I'm missing anything silly or someone has advice let me know.  I'd still like to get a custom VSE gizmo working on general principles.  

Anthropic's Claude is smarter than me so I will paste his summary of our scientific progress on VSE gizmos below:

# Science (Claude)

VSE Gizmo Investigation Summary

  Problem Statement: Custom gizmos fail to activate in Blender's Video Sequence Editor despite successful
  registration.

  Test Methodology: Multiple approaches tested including minimal gizmos, tool integration, target property
  binding, various region types, and different poll strategies.

  Consistent Results Across All Tests:

  Registration Phase - Success:
  - All gizmo classes register successfully
  - gizmo_group_type_ensure() completes without error
  - All VSE gizmo context settings enabled (show_gizmo_context, etc.)
  - Tool activation commands execute successfully

  Activation Phase - Complete Failure:
  - Zero poll() method calls across all test variations
  - Zero setup() or draw() method calls
  - Complete system silence despite proper configuration

  Control Test - 3D Viewport:
  - Identical gizmo implementation works perfectly in 3D viewport
  - Full lifecycle: poll(), setup(), draw(), invoke(), modal() all function
  - Confirms gizmo code and implementation approach are correct

  Technical Conclusion:
  VSE custom gizmos suffer from an architectural limitation in Blender's gizmo system. While the VSE contains
  gizmo infrastructure (context properties, registration support), the underlying activation system does not
  poll or initialize custom gizmo groups in the sequence editor context.
