import bpy

# Create a test material
mat = bpy.data.materials.new(name="TestMaterial")
mat.use_nodes = True
node_tree = mat.node_tree

# Clear existing nodes
node_tree.nodes.clear()

# Create Mix node
mix_node = node_tree.nodes.new('ShaderNodeMix')
mix_node.data_type = 'RGBA'
mix_node.blend_type = 'MULTIPLY'

print("\n=== Mix Node Structure ===")
print(f"Node type: {mix_node.type}")
print(f"Node name: {mix_node.name}")

print("\nInputs:")
for i, inp in enumerate(mix_node.inputs):
    print(f"  [{i}] name='{inp.name}' identifier='{inp.identifier}' type={inp.type}")

print("\nOutputs:")
for i, out in enumerate(mix_node.outputs):
    print(f"  [{i}] name='{out.name}' identifier='{out.identifier}' type={out.type}")

# Create two image texture nodes for testing
img1 = node_tree.nodes.new('ShaderNodeTexImage')
img2 = node_tree.nodes.new('ShaderNodeTexImage')

print("\n=== Image Texture Node Outputs ===")
for i, out in enumerate(img1.outputs):
    print(f"  [{i}] name='{out.name}' identifier='{out.identifier}' type={out.type}")

# Try to connect
print("\n=== Testing Connections ===")
try:
    # Try connecting by index
    link = node_tree.links.new(img1.outputs[0], mix_node.inputs[6])
    print(f"SUCCESS: Connected img1.outputs[0] to mix_node.inputs[6]")
except Exception as e:
    print(f"FAILED index 6: {e}")

try:
    link = node_tree.links.new(img2.outputs[0], mix_node.inputs[7])
    print(f"SUCCESS: Connected img2.outputs[0] to mix_node.inputs[7]")
except Exception as e:
    print(f"FAILED index 7: {e}")

# Clean up
bpy.data.materials.remove(mat)
print("\n=== Test Complete ===")
