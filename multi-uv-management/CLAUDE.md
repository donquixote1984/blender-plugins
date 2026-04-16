# Multi UV Management - Blender Addon

## Overview

Multi UV Management is a Blender addon designed for **batch UV operations across multiple selected objects**. It provides a comprehensive interface for managing multiple UV layers simultaneously, supporting up to **4 UV slots (UV1, UV2, UV3, UV4)** per object.

The plugin enables efficient workflows for:
- **Batch UV slot switching** - Switch active UV layers across all selected objects at once
- **Batch UV creation** - Create UV layers for multiple objects simultaneously
- **Batch UV copying** - Copy UV data between different UV slots across multiple objects
- **Unified UV slot management** - Ensure all selected objects have the same UV slot structure

**Location:** UV Editor > Sidebar > Multi UV  
**Version:** 0.1.0  
**Blender Compatibility:** 3.0+

## Key Concepts

### UV Slots
Each mesh object can have up to 4 UV slots:
- **UV1** (UVMap) - Primary UV layer, always exists
- **UV2** (UVMap__NEW__2) - Secondary UV layer, optional
- **UV3** (UVMap__NEW__3) - Tertiary UV layer, optional
- **UV4** (UVMap__NEW__4) - Quaternary UV layer, optional

### Batch Operations
All operations work on **all selected mesh objects simultaneously**:
- Select multiple objects → perform operation → all objects are affected
- Object-specific data is preserved (matched by object name)
- Topology validation ensures mesh hasn't changed during copy/paste operations

## Features

### Core Functionality

1. **Tab-Based UV Slot Management**
   - 4 UV slot tabs (UV1, UV2, UV3, UV4)
   - Visual indicators for UV status (blue = active, red = missing/partial, gray = inactive)
   - Automatic UV activation when switching tabs (batch operation)
   - Warning display when selected objects have different active UVs or partial UV slots

2. **Batch UV Slot Operations**
   - **Create**: Create new UV slots for multiple objects simultaneously with automatic naming
   - **Rename**: Batch rename UV slots across all selected objects
   - **Delete**: Remove UV slots from multiple objects (UV2-UV4 only, UV1 is protected)
   - **Lock**: Protect UV slots from accidental deletion or renaming across all objects

3. **Batch UV Data Management**
   - **Copy**: Copy UV coordinates from all selected objects (stored per object by name)
   - **Paste**: Paste UV data to matching objects by name (batch operation)
   - **Restore**: Undo the last paste operation for all affected objects

4. **Multi-Object Support & Unification**
   - Batch operations across multiple selected objects
   - Object-specific UV data storage (matched by object name)
   - Topology validation (checks mesh hasn't changed)
   - **UV slot unification**: Create missing UV slots to ensure all objects have the same structure
   - Handles objects with different UV slot counts gracefully

5. **Internationalization**
   - English (default)
   - Simplified Chinese (zh_CN)
   - Traditional Chinese (zh_TW)

## Code Structure

### Module Organization

```
src/
├── __init__.py      # Addon registration and scene properties
├── operators.py     # All operator classes for user actions
├── ui.py           # Main panel UI definition
├── utils.py        # Helper functions for UV status checks
└── i18n.py         # Internationalization translations
```

### Key Components

#### 1. **__init__.py** - Addon Entry Point
- Registers all classes and scene properties
- Defines addon metadata (bl_info)
- Manages addon lifecycle (register/unregister)

**Scene Properties:**
- `multiuv_active_tab`: Currently selected tab (UV1-UV4)
- `multiuv_rename_mode`: Boolean for rename mode state
- `multiuv_rename_index`: Index of UV being renamed
- `multiuv_rename_value`: New name during rename operation
- `multiuv_lock_uv1-4`: Lock states for each UV layer
- `multiuv_clipboard`: Dictionary storing copied UV data
- `multiuv_backup`: Dictionary storing UV data before paste

#### 2. **operators.py** - User Actions
Contains all operator classes:

- `MULTIUV_OT_SwitchTab`: Switch tabs and activate UV layers
- `MULTIUV_OT_CreateUV`: Create new UV layers
- `MULTIUV_OT_RenameUV`: Enter rename mode
- `MULTIUV_OT_ConfirmRename`: Apply rename
- `MULTIUV_OT_CancelRename`: Cancel rename
- `MULTIUV_OT_DeleteUV`: Delete UV layers
- `MULTIUV_OT_CopyUV`: Copy UV data to clipboard
- `MULTIUV_OT_PasteUV`: Paste UV data from clipboard
- `MULTIUV_OT_RestoreUV`: Restore previous UV data

#### 3. **ui.py** - User Interface
Defines the main panel with:
- Dynamic tab buttons with visual states
- Context-sensitive button enabling/disabling
- Warning messages for edge cases
- Rename mode UI (text input + confirm/cancel)

#### 4. **utils.py** - Helper Functions
Utility functions for:
- `get_uv_status()`: Check if UV exists on all/some/no objects
- `get_uv_name_for_tab()`: Get UV name or "multiple names"
- `is_uv_active()`: Check if UV is active on all objects
- `has_different_active_uv()`: Detect mismatched active UVs

#### 5. **i18n.py** - Translations
Translation dictionaries for UI text in multiple languages.

## Use Cases

### Case 1: Basic UV Layer Management
**Scenario:** Artist needs to create and manage multiple UV layers for a single object.

**Steps:**
1. Select object in UV Editor
2. Click UV1 tab (automatically active)
3. Click UV2 tab → shows red (no UV exists)
4. Click "Create" → UV2 is created and activated
5. UV2 tab turns blue (active)

### Case 2: Batch UV Creation
**Scenario:** Multiple objects need the same UV layer structure.

**Steps:**
1. Select multiple objects
2. Click UV2 tab
3. Click "Create" → UV2 created for all objects
4. Repeat for UV3, UV4 as needed

### Case 3: Copy UV Between Layers
**Scenario:** Copy UV1 layout to UV2 for all selected objects.

**Steps:**
1. Select objects
2. Click UV1 tab
3. Click "Copy" → UV1 data stored
4. Click UV2 tab
5. Click "Paste" → UV1 data applied to UV2

### Case 4: Rename UV Layers
**Scenario:** Rename UV layers to match pipeline naming conventions.

**Steps:**
1. Select objects
2. Click UV2 tab
3. Click "Rename"
4. Enter new name (e.g., "Lightmap")
5. Click ✓ to confirm or ✕ to cancel

### Case 5: Lock Protection
**Scenario:** Protect important UV layers from accidental modification.

**Steps:**
1. Select objects
2. Click UV1 tab
3. Click "Lock" (🔒 icon appears)
4. Rename and Delete buttons become disabled
5. Click "Lock" again to unlock

### Case 6: Undo Paste Mistake
**Scenario:** Accidentally pasted wrong UV data.

**Steps:**
1. After paste operation
2. Click "Restore"
3. UV data reverts to state before paste

### Case 7: Multi-Object with Different Active UVs
**Scenario:** Selected objects have different UV layers active.

**Behavior:**
- Warning message appears: "Selected objects have different active UV"
- Only tabs that exist on ALL objects are clickable
- Other tabs are disabled
- No tab shows blue (active) state

### Case 8: No Selection
**Scenario:** No objects selected.

**Behavior:**
- All tabs show gray (default state)
- All buttons are disabled or show appropriate state
- No warnings displayed

## Tab Visual States

### Tab Colors
- **Blue (depress)**: UV layer exists and is currently active
- **Red (alert)**: Selected tab but UV layer doesn't exist
- **Gray (normal)**: Default state (not active or no selection)

### Tab State Logic
```
IF no objects selected:
    → All tabs gray

ELSE IF objects have different active UVs:
    → Warning displayed
    → Only tabs with UV on ALL objects are enabled
    → All tabs gray (no blue highlight)

ELSE IF tab selected AND UV doesn't exist:
    → Tab shows red

ELSE IF UV exists AND is active:
    → Tab shows blue

ELSE:
    → Tab shows gray
```

## Button States

### UV1 Tab
- **Rename**: Enabled if UV exists and not locked
- **Lock**: Enabled if UV exists

### UV2, UV3, UV4 Tabs
- **Create**: Enabled only if UV doesn't exist
- **Rename**: Enabled if UV exists and not locked
- **Delete**: Enabled if UV exists and not locked
- **Lock**: Enabled if UV exists

### Copy/Paste/Restore Row
- **Copy**: Enabled if UV exists
- **Paste**: Always enabled (shows warning if no clipboard data)
- **Restore**: Always enabled (shows warning if no backup data)

## UV Naming Convention

- **UV1 (index 0)**: `UVMap`
- **UV2 (index 1)**: `UVMap__NEW__2`
- **UV3 (index 2)**: `UVMap__NEW__3`
- **UV4 (index 3)**: `UVMap__NEW__4`

When multiple objects have different names, the UI displays "multiple names".

## Data Storage

### Clipboard Format
```python
{
    "ObjectName": {
        'uv_data': [(x1, y1), (x2, y2), ...],  # UV coordinates per loop
        'uv_index': 1,                          # Source UV index
        'loop_count': 1234                      # For validation
    }
}
```

### Backup Format
Same as clipboard format, created automatically before paste operations.

## Limitations

1. **Lock Functionality**: Lock only prevents operations through the addon UI. It does not prevent:
   - Manual UV editing in edit mode
   - Unwrap operations
   - Other addons or scripts from modifying UVs

2. **Object Matching**: Copy/Paste matches objects by name. Renamed objects won't match their clipboard data.

3. **Topology Validation**: Paste/Restore operations check loop count. If mesh topology changes (vertices added/removed), the operation will be skipped for that object.

4. **Maximum UV Layers**: Addon supports 4 UV layers. Blender itself supports more, but they won't be accessible through this addon.

## Development Notes

### Adding New Features
1. Add operator class to `operators.py`
2. Register class in `__init__.py` classes tuple
3. Add UI button in `ui.py`
4. Add translations to `i18n.py`

### Testing Checklist
- [ ] Single object operations
- [ ] Multi-object operations
- [ ] Objects with different UV counts
- [ ] Objects with different active UVs
- [ ] Lock/unlock functionality
- [ ] Copy/paste/restore workflow
- [ ] Rename with multiple names
- [ ] Tab switching and activation
- [ ] No selection state
- [ ] Internationalization

### Common Issues
- **Tabs not updating**: Check if `area.tag_redraw()` is called after operations
- **Wrong UV activated**: Verify `uv_index` calculation (tab number - 1)
- **Paste not working**: Check object names match and topology hasn't changed
- **Lock not working**: Lock only affects addon buttons, not Blender operations


## Credits

Developed for Blender 3.0+ with Python 3.x.

## License

[Add your license information here]
