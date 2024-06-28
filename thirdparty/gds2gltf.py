#!/usr/bin/env python3
"""
This program converts a GDSII 2D layout file to a glTF 3D file

USAGE:
    - edit the "layerstack" variable in the "CONFIGURATION" section below
    - run "gdsiigtlf file.gds"
OUTPUT:
    - the files file.gds.gltf

The program takes one argument, a path to a GDSII file. It reads shapes from
each layer of the GDSII file, converts them to polygon boundaries, then makes
a triangle mesh for each GDSII layer by extruding the polygons to given sizes.

All units, including the units of the exported file, are the GDSII file's
user units (often microns).
"""

import sys  # read command-line arguments
import os  # for file path checking
import gdspy  # open gds file
import numpy as np  # fast math on lots of points
import triangle  # triangulate polygons
import pygltflib
from pygltflib import BufferFormat
from pygltflib.validator import validate, summary

# get the input file name
if len(sys.argv) < 2:  # sys.argv[0] is the name of the program
    print("Error: need exactly one file as a command line argument.")
    sys.exit(0)
gdsii_file_path = sys.argv[1]

# Check if the file exists
if not os.path.isfile(gdsii_file_path):
    print(f"Error: The file {gdsii_file_path} does not exist.")
    sys.exit(1)

print(f"Reading GDSII file {gdsii_file_path}...")

########## CONFIGURATION (EDIT THIS PART) #####################################

# choose which GDSII layers to use
layerstack = {
    (235, 4): {'name': 'substrate', 'zmin': -2, 'zmax': 0, 'color': [0.2, 0.2, 0.2, 1.0]},
    (64, 20): {'name': 'nwell', 'zmin': -0.5, 'zmax': 0.01, 'color': [0.4, 0.4, 0.4, 1.0]},
    (65, 20): {'name': 'diff', 'zmin': -0.12, 'zmax': 0.02, 'color': [0.9, 0.9, 0.9, 1.0]},
    (66, 20): {'name': 'poly', 'zmin': 0, 'zmax': 0.18, 'color': [0.75, 0.35, 0.46, 1.0]},
    (66, 44): {'name': 'licon', 'zmin': 0, 'zmax': 0.936, 'color': [0.2, 0.2, 0.2, 1.0]},
    (67, 20): {'name': 'li1', 'zmin': 0.936, 'zmax': 1.136, 'color': [1.0, 0.81, 0.55, 1.0]},
    (67, 44): {'name': 'mcon', 'zmin': 1.011, 'zmax': 1.376, 'color': [0.2, 0.2, 0.2, 1.0]},
    (68, 20): {'name': 'met1', 'zmin': 1.376, 'zmax': 1.736, 'color': [0.16, 0.38, 0.83, 1.0]},
    (68, 44): {'name': 'via', 'zmin': 1.736, 'zmax': 2, 'color': [0.2, 0.2, 0.2, 1.0]},
    (69, 20): {'name': 'met2', 'zmin': 2, 'zmax': 2.36, 'color': [0.65, 0.75, 0.9, 1.0]},
    (69, 44): {'name': 'via2', 'zmin': 2.36, 'zmax': 2.786, 'color': [0.2, 0.2, 0.2, 1.0]},
    (70, 20): {'name': 'met3', 'zmin': 2.786, 'zmax': 3.631, 'color': [0.2, 0.62, 0.86, 1.0]},
    (70, 44): {'name': 'via3', 'zmin': 3.631, 'zmax': 4.0211, 'color': [0.2, 0.2, 0.2, 1.0]},
    (71, 20): {'name': 'met4', 'zmin': 4.0211, 'zmax': 4.8661, 'color': [0.15, 0.11, 0.38, 1.0]},
    (71, 44): {'name': 'via4', 'zmin': 4.8661, 'zmax': 5.371, 'color': [0.2, 0.2, 0.2, 1.0]},
    (72, 20): {'name': 'met5', 'zmin': 5.371, 'zmax': 6.6311, 'color': [0.4, 0.4, 0.4, 1.0]},
}

########## INPUT ##############################################################

print('Reading GDSII file {}...'.format(gdsii_file_path))
gdsii = gdspy.GdsLibrary()
gdsii.read_gds(gdsii_file_path, units='import')

gltf = pygltflib.GLTF2()
scene = pygltflib.Scene()
gltf.scenes.append(scene)
buffer = pygltflib.Buffer()
gltf.buffers.append(buffer)

for layer in layerstack:
    mainMaterial = pygltflib.Material()
    mainMaterial.doubleSided = False
    mainMaterial.name = layerstack[layer]['name']
    mainMaterial.pbrMetallicRoughness = {
        "baseColorFactor": layerstack[layer]['color'],
        "metallicFactor": 0.5,
        "roughnessFactor": 0.5
    }
    gltf.materials.append(mainMaterial)

binaryBlob = bytes()

print('Extracting polygons...')

meshes_lib = {}

for cell in gdsii.cells.values():  # loop through cells to read paths and polygons
    layers = {}  # array to hold all geometry, sorted into layers

    print("\nProcessing cell: ", cell.name)

    if cell.name == '$$$CONTEXT_INFO$$$':
        continue  # skip this cell

    print("\tpaths loop. total paths:", len(cell.paths))
    for path in cell.paths:
        lnum = (path.layers[0], path.datatypes[0])  # GDSII layer number
        if not lnum in layerstack.keys():
            continue

        layers[lnum] = [] if not lnum in layers else layers[lnum]
        for poly in path.get_polygons():
            layers[lnum].append((poly, None, False))

    print("\tpolygons loop. total polygons:", len(cell.polygons))
    for polygon in cell.polygons:
        lnum = (polygon.layers[0], polygon.datatypes[0])
        if not lnum in layerstack.keys():
            continue

        layers[lnum] = [] if not lnum in layers else layers[lnum]
        for poly in polygon.polygons:
            layers[lnum].append((poly, None, False))

    print('\tTriangulating polygons...')

    num_triangles = {}
    for layer_number, polygons in layers.items():
        if not layer_number in layerstack.keys():
            continue

        num_triangles[layer_number] = 0

        for index, (polygon, _, _) in enumerate(polygons):
            num_polygon_points = len(polygon)
            area = 0
            for i, v1 in enumerate(polygon):
                v2 = polygon[(i + 1) % num_polygon_points]
                area += (v2[0] - v1[0]) * (v2[1] + v1[1])

            clockwise = area > 0

            delta = 0.00001
            points_i = polygon
            points_j = np.roll(points_i, -1, axis=0)
            points_k = np.roll(points_i, 1, axis=0)
            normal_ij = np.stack((points_j[:, 1] - points_i[:, 1], points_i[:, 0] - points_j[:, 0]), axis=1)
            normal_ik = np.stack((points_i[:, 1] - points_k[:, 1], points_k[:, 0] - points_i[:, 0]), axis=1)
            length_ij = np.linalg.norm(normal_ij, axis=1)
            length_ik = np.linalg.norm(normal_ik, axis=1)
            normal_ij /= np.stack((length_ij, length_ij), axis=1)
            normal_ik /= np.stack((length_ik, length_ik), axis=1)
            if clockwise:
                normal_ij = -1 * normal_ij
                normal_ik = -1 * normal_ik
            polygon = points_i - delta * normal_ij - delta * normal_ik

            point_array = np.arange(num_polygon_points)
            edges = np.transpose(np.stack((point_array, np.roll(point_array, 1))))
            triangles = triangle.triangulate(dict(vertices=polygon, segments=edges), opts='p')

            if not 'triangles' in triangles.keys():
                triangles['triangles'] = []

            num_triangles[layer_number] += num_polygon_points * 2 + len(triangles['triangles']) * 2
            polygons[index] = (polygon, triangles, clockwise)

        zmin = layerstack[layer_number]['zmin']
        zmax = layerstack[layer_number]['zmax']
        layername = layerstack[layer_number]['name']
        node_name = cell.name + "_" + layername

        gltf_positions = []
        gltf_indices = []
        indices_offset = 0
        for i, (_, poly_data, clockwise) in enumerate(polygons):
            p_positions_top = np.insert(poly_data['vertices'], 2, zmax, axis=1)
            p_positions_bottom = np.insert(poly_data['vertices'], 2, zmin, axis=1)
            p_positions = np.concatenate((p_positions_top, p_positions_bottom))
            p_indices_top = poly_data['triangles']
            p_indices_bottom = np.flip((p_indices_top + len(p_positions_top)), axis=1)
            ind_list_top = np.arange(len(p_positions_top))
            ind_list_bottom = np.arange(len(p_positions_top)) + len(p_positions_top)

            if (clockwise):
                ind_list_top = np.flip(ind_list_top, axis=0)
                ind_list_bottom = np.flip(ind_list_bottom, axis=0)

            p_indices_right = np.stack(
                (ind_list_bottom, np.roll(ind_list_bottom, -1, axis=0), np.roll(ind_list_top, -1, axis=0)), axis=1)
            p_indices_left = np.stack((np.roll(ind_list_top, -1, axis=0), ind_list_top, ind_list_bottom), axis=1)
            p_indices = np.concatenate((p_indices_top, p_indices_bottom, p_indices_right, p_indices_left))

            if (len(gltf_positions) == 0):
                gltf_positions = p_positions
            else:
                gltf_positions = np.append(gltf_positions, p_positions, axis=0)
            if (len(gltf_indices) == 0):
                gltf_indices = p_indices
            else:
                gltf_indices = np.append(gltf_indices, p_indices + indices_offset, axis=0)
            indices_offset += len(p_positions)

        indices_binary_blob = gltf_indices.astype(np.uint32).flatten().tobytes()
        positions_binary_blob = gltf_positions.astype(np.float32).tobytes()

        bufferView1 = pygltflib.BufferView()
        bufferView1.buffer = 0
        bufferView1.byteOffset = len(binaryBlob)
        bufferView1.byteLength = len(indices_binary_blob)
        bufferView1.target = pygltflib.ELEMENT_ARRAY_BUFFER
        gltf.bufferViews.append(bufferView1)

        accessor1 = pygltflib.Accessor()
        accessor1.bufferView = len(gltf.bufferViews) - 1
        accessor1.byteOffset = 0
        accessor1.componentType = pygltflib.UNSIGNED_INT
        accessor1.type = pygltflib.SCALAR
        accessor1.count = gltf_indices.size
        accessor1.max = [int(gltf_indices.max())]
        accessor1.min = [int(gltf_indices.min())]
        gltf.accessors.append(accessor1)

        binaryBlob = binaryBlob + indices_binary_blob

        bufferView2 = pygltflib.BufferView()
        bufferView2.buffer = 0
        bufferView2.byteOffset = len(binaryBlob)
        bufferView2.byteLength = len(positions_binary_blob)
        bufferView2.target = pygltflib.ARRAY_BUFFER
        gltf.bufferViews.append(bufferView2)

        positions_count = len(gltf_positions)
        accessor2 = pygltflib.Accessor()
        accessor2.bufferView = len(gltf.bufferViews) - 1
        accessor2.byteOffset = 0
        accessor2.componentType = pygltflib.FLOAT
        accessor2.count = positions_count
        accessor2.type = pygltflib.VEC3
        accessor2.max = gltf_positions.max(axis=0).tolist()
        accessor2.min = gltf_positions.min(axis=0).tolist()
        gltf.accessors.append(accessor2)

        binaryBlob = binaryBlob + positions_binary_blob

        mesh = pygltflib.Mesh()
        mesh_primitive = pygltflib.Primitive()
        mesh_primitive.indices = len(gltf.accessors) - 2
        mesh_primitive.attributes.POSITION = len(gltf.accessors) - 1
        mesh_primitive.material = list(layerstack).index(layer_number)
        mesh.primitives.append(mesh_primitive)

        gltf.meshes.append(mesh)
        meshes_lib[node_name] = len(gltf.meshes) - 1

gltf.set_binary_blob(binaryBlob)
buffer.byteLength = len(binaryBlob)
gltf.convert_buffers(BufferFormat.DATAURI)


def add_cell_node(c, parent_node, prefix):
    for ref in c.references:
        instance_node = pygltflib.Node()
        instance_node.extras = {}
        instance_node.extras["type"] = ref.ref_cell.name
        if ref.properties.get(61) == None:
            instance_node.name = "???"
        else:
            instance_node.name = ref.properties[61]

        print(prefix, instance_node.name, "(", ref.ref_cell.name + ")")
        instance_node.translation = [ref.origin[0], ref.origin[1], 0]
        if ref.rotation != None:
            if ref.rotation == 90:
                instance_node.rotation = [0, 0, 0.7071068, 0.7071068]
            elif ref.rotation == 180:
                instance_node.rotation = [0, 0, 1, 0]
            elif ref.rotation == 270:
                instance_node.rotation = [0, 0, 0.7071068, -0.7071068]
        if ref.x_reflection:
            instance_node.scale = [1, -1, 1]

        for layer in layerstack.values():
            lib_name = ref.ref_cell.name + "_" + layer['name']
            if meshes_lib.get(lib_name) != None:
                layer_node = pygltflib.Node()
                layer_node.name = lib_name
                layer_node.mesh = meshes_lib[lib_name]
                gltf.nodes.append(layer_node)
                instance_node.children.append(len(gltf.nodes) - 1)

        if len(ref.ref_cell.references) > 0:
            add_cell_node(ref.ref_cell, instance_node, prefix + "\t")

        gltf.nodes.append(instance_node)
        parent_node.children.append(len(gltf.nodes) - 1)


main_cell = gdsii.top_level()[0]

root_node = pygltflib.Node()
root_node.name = main_cell.name
gltf.nodes.append(root_node)

print("\nBuilding Scenegraph:")
print(root_node.name)

add_cell_node(main_cell, root_node, "\t")

for layer in layerstack.values():
    lib_name = main_cell.name + "_" + layer['name']
    if meshes_lib.get(lib_name) != None:
        layer_node = pygltflib.Node()
        layer_node.name = lib_name
        layer_node.mesh = meshes_lib[lib_name]
        gltf.nodes.append(layer_node)
        root_node.children.append(len(gltf.nodes) - 1)

scene.nodes.append(0)
gltf.scene = 0

print("\nWriting glTF file……")
gltf.save(gdsii_file_path + ".gltf")

print('Done.')
