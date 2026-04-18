# Shader Editor Pie Menu

A Blender addon that adds a pie menu (Tab key) in the Shader Editor:

- **SD Texture Import** - Import Substance Designer PBR textures and auto-connect to Principled BSDF (Base Color, Normal, Roughness, AO, Metallic, Opacity)
- **Mix Color** - Create a Mix Color node (Multiply mode) and connect selected nodes. Replaces original node's output connections
- **Increase Tile** - Add a Value node (default 2.0) to selected Mapping node's Scale input. Only enabled when Mapping node is selected
- **Mix UV Texture** - Create UVMap → Mapping → Image Texture → Mix Color chain. If a color node is selected, connects it to Mix A input and replaces its output connections

## Build

Run `python build.py` after code changes to generate the installation package.
