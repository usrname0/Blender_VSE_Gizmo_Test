# BL Easy Crop v2.0.0 - Experimental Gizmo Version

## Project Structure

```
BL_EasyCrop_v2/
├── __init__.py                 # Main init file with bl_info and registration
├── blender_manifest.toml       # Extension manifest (update version to 2.0.0)
├── README_v2.md               # Documentation for v2.0
│
├── core/                      # Core functionality shared between versions
│   ├── __init__.py
│   └── geometry_utils.py      # Geometry calculations and utilities
│
├── gizmos/                    # Gizmo system implementation
│   ├── __init__.py
│   └── crop_gizmo_group.py    # Gizmo group and individual gizmos
│
├── operators/                 # Operators for tool activation and fallbacks
│   ├── __init__.py
│   └── crop_operators_v2.py   # v2.0 operators with gizmo support
│
└── utils/                     # Additional utilities
    ├── __init__.py
    └── debug_tools.py         # Debug operators for testing gizmos
```

## Key Differences from v1.0

1. **Gizmo-Based Interaction**: Uses Blender's gizmo system instead of modal operators
2. **Tool Integration**: Properly integrates with Blender's tool system
3. **Experimental Status**: Clearly marked as experimental with warnings
4. **Debug Tools**: Includes operators to test gizmo functionality
5. **Fallback Options**: Provides fallback mechanisms if gizmos don't work

## Installation Notes

- Install as a separate addon alongside v1.0
- Uses different keybindings (X instead of C) to avoid conflicts
- Requires Blender 4.0+ for best gizmo support
- May not work as expected due to undocumented gizmo API

## Development Notes

This version serves as:
1. **Learning Exercise**: Understanding Blender's gizmo system
2. **Foundation**: For future "Free Transform" extension
3. **Experiment**: Testing sequence editor gizmo capabilities
4. **Fallback**: If successful, could replace v1.0 approach

## Expected Challenges

1. **Gizmo Positioning**: Converting between coordinate spaces
2. **Event Handling**: Proper mouse interaction with gizmos
3. **Visual Feedback**: Drawing gizmos in sequence editor context
4. **Tool Integration**: Proper tool activation and deactivation
5. **Context Sensitivity**: Making gizmos appear only when appropriate

## Testing Strategy

1. Start with basic gizmo registration and visibility
2. Test coordinate transformation and positioning
3. Add mouse interaction and property binding
4. Implement visual feedback and handle drawing
5. Add tool integration and polish

## Success Criteria

- Gizmos appear when crop tool is selected
- Gizmos position correctly on strip corners/edges
- Mouse interaction modifies crop properties
- No conflicts with existing functionality
- Smooth user experience comparable to v1.0
