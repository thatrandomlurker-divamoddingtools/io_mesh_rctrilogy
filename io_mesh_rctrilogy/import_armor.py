import struct
import bpy
import bmesh
import os

# Vertex group dictionary
Groups = {
0: "Root",
1: "Pelvis",
2: "Spine1",
3: "Spine2",
4: "Spine3",
5: "Chest1",
6: "Chest2",
7: "Neck",
8: "Head",
9: "Nose",
10: "Jaw",
11: "D_Lip_C",
12: "D_Lip_S",
13: "Teeth_D",
14: "Tongue_1",
15: "Tongue_2",
16: "R_Cheek",
17: "L_Cheek",
18: "EyeRoot",
19: "L_Eye",
20: "R_Eye",
21: "R_Eyelid_U_Control",
22: "R_Eyelid_U",
23: "L_Eyelid_U_Control",
24: "L_Eyelid_U",
25: "R_Eyebrow_U",
26: "R_Eyebrow_C",
27: "R_Eyebrow_R",
28: "R_Eyebrow_L",
29: "L_Eyebrow_U",
30: "L_Eyebrow_C",
31: "L_Eyebrow_L",
32: "L_Eyebrow_R",
33: "L_CapStrap_1",
34: "L_CapStrap_2",
35: "R_CapStrap_1",
36: "R_CapStrap_2",
37: "U_Lip_C",
38: "U_Lip_S",
39: "L_Eyesocket_D",
40: "R_Eyesocket_D",
41: "L_Ear_1",
42: "L_Ear_2",
43: "L_Ear_3",
44: "R_Ear_1",
45: "R_Ear_2",
46: "R_Ear_3",
47: "R_Lip",
48: "L_Lip",
49: "R_Eyesocket_U",
50: "L_Eyesocket_U",
51: "Teeth_U",
52: "R_Shoulder",
53: "R_Arm",
54: "R_Elbow",
55: "R_Wrist_Twist",
56: "R_Hand",
57: "R_Index_1",
58: "R_Index_2",
59: "R_Index_3",
60: "R_Middle_1",
61: "R_Middle_2",
62: "R_Middle_3",
63: "R_Ring_1",
64: "R_Ring_2",
65: "R_Ring_3",
66: "R_Pinky_1",
67: "R_Pinky_2",
68: "R_Pinky_3",
69: "R_Thumb_1",
70: "R_Thumb_2",
71: "R_Glove_Cuff",
72: "L_Shoulder",
73: "L_Arm",
74: "L_Elbow",
75: "L_Wrist_Twist",
76: "L_Hand",
77: "L_Index_1",
78: "L_Index_2",
79: "L_Index_3",
80: "L_Middle_1",
81: "L_Middle_2",
82: "L_Middle_3",
83: "L_Ring_1",
84: "L_Ring_2",
85: "L_Ring_3",
86: "L_Pinky_1",
87: "L_Pinky_2",
88: "L_Pinky_3",
89: "L_Thumb_1",
90: "L_Thumb_2",
91: "L_Glove_Cuff",
92: "R_Leg",
93: "R_Knee",
94: "R_Foot",
95: "R_Toe_1",
96: "R_Toe_2",
97: "R_Toe_3",
98: "L_Leg",
99: "L_Knee",
100: "L_Foot",
101: "L_Toe_1",
102: "L_Toe_2",
103: "L_Toe_3",
104: "Tail_1",
105: "Tail_2",
106: "Tail_3",
107: "Tail_4",
108: "Tail_5",
109: "Tail_6",
110: "Tail_7",
}

# my own code, written from previous knowledge about the BC1 encoding format, learned from wikipedia
def DecodeBC1(stream, width, height):
    decData = []
    for h in range(height // 4):
        R1 = []
        R2 = []
        R3 = []
        R4 = []
        for w in range(width // 4):
            palette = []
            C0s = struct.unpack("<H", stream.read(2))[0]
            C1s = struct.unpack("<H", stream.read(2))[0]
            C0b = format(C0s, 'b').zfill(16)
            C1b = format(C1s, 'b').zfill(16)
            C0 = (int(C0b[0:5], 2) * 0x8, int(C0b[5:11], 2) * 0x4, int(C0b[11:], 2) * 0x8, 255)
            C1 = (int(C1b[0:5], 2) * 0x8, int(C1b[5:11], 2) * 0x4, int(C1b[11:], 2) * 0x8, 255)
            if C0s > C1s:
                C2 = (int((C0[0] * (2/3)) + (C1[0] * (1/3))), int((C0[1] * (2/3)) + (C1[1] * (1/3))), int((C0[2] * (2/3)) + (C1[2] * (1/3))), 255)
                C3 = (int((C0[0] * (1/3)) + (C1[0] * (2/3))), int((C0[1] * (1/3)) + (C1[1] * (2/3))), int((C0[2] * (1/3)) + (C1[2] * (2/3))), 255)
                palette.extend([C0, C1, C2, C3])
            else:
                C2 = (int((C0[0] * 0.5) + (C1[0] * 0.5)), int((C0[1] * 0.5) + (C1[1] * 0.5)), int((C0[2] * 0.5) + (C1[2] * 0.5)), 255)
                C3 = (0, 0, 0, 0)
                palette.extend([C0, C1, C2, C3])
            # indices
            IndexInt = struct.unpack(">I", stream.read(4))[0]
            IndexBits = format(IndexInt, 'b').zfill(32)
            Indices = [[int(IndexBits[0:2], 2), int(IndexBits[2:4], 2), int(IndexBits[4:6], 2), int(IndexBits[6:8], 2)], [int(IndexBits[8:10], 2), int(IndexBits[10:12], 2), int(IndexBits[12:14], 2), int(IndexBits[14:16], 2)], [int(IndexBits[16:18], 2), int(IndexBits[18:20], 2), int(IndexBits[20:22], 2), int(IndexBits[22:24], 2)], [int(IndexBits[24:26], 2), int(IndexBits[26:28], 2), int(IndexBits[28:30], 2), int(IndexBits[30:32], 2)]]
            R1.extend([palette[Indices[0][3]][0] / 255, palette[Indices[0][3]][1] / 255, palette[Indices[0][3]][2] / 255, palette[Indices[0][3]][3] / 255])
            R1.extend([palette[Indices[0][2]][0] / 255, palette[Indices[0][2]][1] / 255, palette[Indices[0][2]][2] / 255, palette[Indices[0][2]][3] / 255])
            R1.extend([palette[Indices[0][1]][0] / 255, palette[Indices[0][1]][1] / 255, palette[Indices[0][1]][2] / 255, palette[Indices[0][1]][3] / 255])
            R1.extend([palette[Indices[0][0]][0] / 255, palette[Indices[0][0]][1] / 255, palette[Indices[0][0]][2] / 255, palette[Indices[0][0]][3] / 255])
            R2.extend([palette[Indices[1][3]][0] / 255, palette[Indices[1][3]][1] / 255, palette[Indices[1][3]][2] / 255, palette[Indices[1][3]][3] / 255])
            R2.extend([palette[Indices[1][2]][0] / 255, palette[Indices[1][2]][1] / 255, palette[Indices[1][2]][2] / 255, palette[Indices[1][2]][3] / 255])
            R2.extend([palette[Indices[1][1]][0] / 255, palette[Indices[1][1]][1] / 255, palette[Indices[1][1]][2] / 255, palette[Indices[1][1]][3] / 255])
            R2.extend([palette[Indices[1][0]][0] / 255, palette[Indices[1][0]][1] / 255, palette[Indices[1][0]][2] / 255, palette[Indices[1][0]][3] / 255])
            R3.extend([palette[Indices[2][3]][0] / 255, palette[Indices[2][3]][1] / 255, palette[Indices[2][3]][2] / 255, palette[Indices[2][3]][3] / 255])
            R3.extend([palette[Indices[2][2]][0] / 255, palette[Indices[2][2]][1] / 255, palette[Indices[2][2]][2] / 255, palette[Indices[2][2]][3] / 255])
            R3.extend([palette[Indices[2][1]][0] / 255, palette[Indices[2][1]][1] / 255, palette[Indices[2][1]][2] / 255, palette[Indices[2][1]][3] / 255])
            R3.extend([palette[Indices[2][0]][0] / 255, palette[Indices[2][0]][1] / 255, palette[Indices[2][0]][2] / 255, palette[Indices[2][0]][3] / 255])
            R4.extend([palette[Indices[3][3]][0] / 255, palette[Indices[3][3]][1] / 255, palette[Indices[3][3]][2] / 255, palette[Indices[3][3]][3] / 255])
            R4.extend([palette[Indices[3][2]][0] / 255, palette[Indices[3][2]][1] / 255, palette[Indices[3][2]][2] / 255, palette[Indices[3][2]][3] / 255])
            R4.extend([palette[Indices[3][1]][0] / 255, palette[Indices[3][1]][1] / 255, palette[Indices[3][1]][2] / 255, palette[Indices[3][1]][3] / 255])
            R4.extend([palette[Indices[3][0]][0] / 255, palette[Indices[3][0]][1] / 255, palette[Indices[3][0]][2] / 255, palette[Indices[3][0]][3] / 255])
        decData.extend(reversed(R1))
        decData.extend(reversed(R2))
        decData.extend(reversed(R3))
        decData.extend(reversed(R4))
    return list(reversed(decData))

def DecodeBC3(stream, width, height):
    decData = []
    for h in range(height // 4):
        R1 = []
        R2 = []
        R3 = []
        R4 = []
        for w in range(width // 4):
            AlPal = []
            A0 = stream.read(1)[0]
            A1 = stream.read(1)[0]
            if A0 > A1:
                A2 = (6*A0 + 1*A1) // 7
                A3 = (5*A0 + 2*A1) // 7
                A4 = (4*A0 + 3*A1) // 7
                A5 = (3*A0 + 4*A1) // 7
                A6 = (2*A0 + 5*A1) // 7
                A7 = (1*A0 + 6*A1) // 7
                AlPal.extend([A0, A1, A2, A3, A4, A5, A6, A7])
            else:
                A2 = (4*A0 + 1*A1) // 5
                A3 = (3*A0 + 2*A1) // 5
                A4 = (2*A0 + 3*A1) // 5
                A5 = (1*A0 + 4*A1) // 5
                A6 = 0
                A7 = 255
                AlPal.extend([A0, A1, A2, A3, A4, A5, A6, A7])
            AlB0 = format(stream.read(1)[0], 'b').zfill(8)
            AlB1 = format(stream.read(1)[0], 'b').zfill(8)
            AlB2 = format(stream.read(1)[0], 'b').zfill(8)
            AlB3 = format(stream.read(1)[0], 'b').zfill(8)
            AlB4 = format(stream.read(1)[0], 'b').zfill(8)
            AlB5 = format(stream.read(1)[0], 'b').zfill(8)
            AlBits = AlB2 + AlB1 + AlB0 + AlB5 + AlB4 + AlB3
            AlIndices = [[int(AlBits[0:3], 2), int(AlBits[3:6], 2), int(AlBits[6:9], 2), int(AlBits[9:12], 2)], [int(AlBits[12:15], 2), int(AlBits[15:18], 2), int(AlBits[18:21], 2), int(AlBits[21:24], 2)], [int(AlBits[24:27], 2), int(AlBits[27:30], 2), int(AlBits[30:33], 2), int(AlBits[33:36], 2)], [int(AlBits[36:39], 2), int(AlBits[39:42], 2), int(AlBits[42:45], 2), int(AlBits[45:48], 2)]]
            palette = []
            C0s = struct.unpack("<H", stream.read(2))[0]
            C1s = struct.unpack("<H", stream.read(2))[0]
            C0b = format(C0s, 'b').zfill(16)
            C1b = format(C1s, 'b').zfill(16)
            C0 = (int(C0b[0:5], 2) * 0x8, int(C0b[5:11], 2) * 0x4, int(C0b[11:], 2) * 0x8, 255)
            C1 = (int(C1b[0:5], 2) * 0x8, int(C1b[5:11], 2) * 0x4, int(C1b[11:], 2) * 0x8, 255)
            if C0s > C1s:
                C2 = (int((C0[0] * (2/3)) + (C1[0] * (1/3))), int((C0[1] * (2/3)) + (C1[1] * (1/3))), int((C0[2] * (2/3)) + (C1[2] * (1/3))), 255)
                C3 = (int((C0[0] * (1/3)) + (C1[0] * (2/3))), int((C0[1] * (1/3)) + (C1[1] * (2/3))), int((C0[2] * (1/3)) + (C1[2] * (2/3))), 255)
                palette.extend([C0, C1, C2, C3])
            else:
                C2 = (int((C0[0] * 0.5) + (C1[0] * 0.5)), int((C0[1] * 0.5) + (C1[1] * 0.5)), int((C0[2] * 0.5) + (C1[2] * 0.5)), 255)
                C3 = (0, 0, 0, 0)
                palette.extend([C0, C1, C2, C3])
            # indices
            IndexInt = struct.unpack(">I", stream.read(4))[0]
            IndexBits = format(IndexInt, 'b').zfill(32)
            Indices = [[int(IndexBits[0:2], 2), int(IndexBits[2:4], 2), int(IndexBits[4:6], 2), int(IndexBits[6:8], 2)], [int(IndexBits[8:10], 2), int(IndexBits[10:12], 2), int(IndexBits[12:14], 2), int(IndexBits[14:16], 2)], [int(IndexBits[16:18], 2), int(IndexBits[18:20], 2), int(IndexBits[20:22], 2), int(IndexBits[22:24], 2)], [int(IndexBits[24:26], 2), int(IndexBits[26:28], 2), int(IndexBits[28:30], 2), int(IndexBits[30:32], 2)]]
            R1.extend([palette[Indices[0][3]][0] / 255, palette[Indices[0][3]][1] / 255, palette[Indices[0][3]][2] / 255, AlPal[AlIndices[1][3]] / 255])
            R1.extend([palette[Indices[0][2]][0] / 255, palette[Indices[0][2]][1] / 255, palette[Indices[0][2]][2] / 255, AlPal[AlIndices[1][2]] / 255])
            R1.extend([palette[Indices[0][1]][0] / 255, palette[Indices[0][1]][1] / 255, palette[Indices[0][1]][2] / 255, AlPal[AlIndices[1][1]] / 255])
            R1.extend([palette[Indices[0][0]][0] / 255, palette[Indices[0][0]][1] / 255, palette[Indices[0][0]][2] / 255, AlPal[AlIndices[1][0]] / 255])
            R2.extend([palette[Indices[1][3]][0] / 255, palette[Indices[1][3]][1] / 255, palette[Indices[1][3]][2] / 255, AlPal[AlIndices[0][3]] / 255])
            R2.extend([palette[Indices[1][2]][0] / 255, palette[Indices[1][2]][1] / 255, palette[Indices[1][2]][2] / 255, AlPal[AlIndices[0][2]] / 255])
            R2.extend([palette[Indices[1][1]][0] / 255, palette[Indices[1][1]][1] / 255, palette[Indices[1][1]][2] / 255, AlPal[AlIndices[0][1]] / 255])
            R2.extend([palette[Indices[1][0]][0] / 255, palette[Indices[1][0]][1] / 255, palette[Indices[1][0]][2] / 255, AlPal[AlIndices[0][0]] / 255])
            R3.extend([palette[Indices[2][3]][0] / 255, palette[Indices[2][3]][1] / 255, palette[Indices[2][3]][2] / 255, AlPal[AlIndices[3][3]] / 255])
            R3.extend([palette[Indices[2][2]][0] / 255, palette[Indices[2][2]][1] / 255, palette[Indices[2][2]][2] / 255, AlPal[AlIndices[3][2]] / 255])
            R3.extend([palette[Indices[2][1]][0] / 255, palette[Indices[2][1]][1] / 255, palette[Indices[2][1]][2] / 255, AlPal[AlIndices[3][1]] / 255])
            R3.extend([palette[Indices[2][0]][0] / 255, palette[Indices[2][0]][1] / 255, palette[Indices[2][0]][2] / 255, AlPal[AlIndices[3][0]] / 255])
            R4.extend([palette[Indices[3][3]][0] / 255, palette[Indices[3][3]][1] / 255, palette[Indices[3][3]][2] / 255, AlPal[AlIndices[2][3]] / 255])
            R4.extend([palette[Indices[3][2]][0] / 255, palette[Indices[3][2]][1] / 255, palette[Indices[3][2]][2] / 255, AlPal[AlIndices[2][2]] / 255])
            R4.extend([palette[Indices[3][1]][0] / 255, palette[Indices[3][1]][1] / 255, palette[Indices[3][1]][2] / 255, AlPal[AlIndices[2][1]] / 255])
            R4.extend([palette[Indices[3][0]][0] / 255, palette[Indices[3][0]][1] / 255, palette[Indices[3][0]][2] / 255, AlPal[AlIndices[2][0]] / 255])
        decData.extend(reversed(R1))
        decData.extend(reversed(R2))
        decData.extend(reversed(R3))
        decData.extend(reversed(R4))
    return list(reversed(decData))

def ReadArmor(context, Path, Mode, searchForSkeleton):
    if Mode == "VITA":
        with open(Path, 'rb') as f:
            MeshInfoOffset = struct.unpack('<I', f.read(4))[0]
            TexHeaderOffset = struct.unpack('<I', f.read(4))[0]
            TextureCount = struct.unpack('<I', f.read(4))[0]
            f.seek(MeshInfoOffset)
            SubmeshCount = struct.unpack('<I', f.read(4))[0]
            ReflectionSubmeshCount = struct.unpack('<I', f.read(4))[0]
            SubmeshInfoOffset = struct.unpack('<I', f.read(4))[0]
            ReflectionSubmeshInfoOffset = struct.unpack('<I', f.read(4))[0]
            VertOffset = struct.unpack('<I', f.read(4))[0]
            FaceOffset = struct.unpack('<I', f.read(4))[0]
            VertCount = struct.unpack('<H', f.read(2))[0]
            ReflectVertCount = struct.unpack('<H', f.read(2))[0]
            f.seek(SubmeshInfoOffset)
            SMInfos = []
            RSMInfos = []
            Positions = []
            Normals = []
            UVs = []
            BoneIndices = []
            BoneWeights = []
            MatLookup = {}
            mesh = bpy.data.meshes.new(Path.split('/')[-1].split('.')[0])
            for i in range(SubmeshCount):
                TexIndex = struct.unpack('<I', f.read(4))[0]
                StartFaceIndex = struct.unpack('<I', f.read(4))[0]
                FaceCount = struct.unpack('<I', f.read(4))[0]
                Unk = struct.unpack('<I', f.read(4))[0]
                mat = bpy.data.materials.new(f'texturedmesh_{i}')
                MatLookup[f'texturedmesh_{i}'] = i
                mesh.materials.append(mat)
                SMInfos.append([i, TexIndex, StartFaceIndex, FaceCount, Unk])
            for i in range(ReflectionSubmeshCount):
                TexIndex = struct.unpack('<I', f.read(4))[0]
                StartFaceIndex = struct.unpack('<I', f.read(4))[0]
                FaceCount = struct.unpack('<I', f.read(4))[0]
                Unk = struct.unpack('<I', f.read(4))[0]
                mat = bpy.data.materials.new(f'reflectmesh_{i}')
                MatLookup[f'reflectmesh_{i}'] = i + SubmeshCount
                mesh.materials.append(mat)
                RSMInfos.append([i, TexIndex, StartFaceIndex, FaceCount, Unk])
            # read verts
            f.seek(VertOffset)
            for i in range(VertCount):
                PosPreCorrect = struct.unpack('<fff', f.read(12))
                Positions.append((PosPreCorrect[1], -PosPreCorrect[0], PosPreCorrect[2]))
                nBytes = struct.unpack('bbbb', f.read(4))
                Normals.append((nBytes[1] / 127, -nBytes[0] / 127, nBytes[2] / 127))
                UVs.append(struct.unpack('<ff', f.read(8)))
                wBytes = struct.unpack('BBBB', f.read(4))
                if wBytes[0] == 255:
                    BoneWeights.append((1.0, 0.0, 0.0, 0.0))
                else:
                    BoneWeights.append((wBytes[0]/256, wBytes[1]/256, wBytes[2]/256, wBytes[3]/256))
                BoneIndices.append(struct.unpack('BBBB', f.read(4)))
            # reflect verts
            for i in range(ReflectVertCount):
                PosPreCorrect = struct.unpack('<fff', f.read(12))
                Positions.append((PosPreCorrect[1], -PosPreCorrect[0], PosPreCorrect[2]))
                nBytes = struct.unpack('bbbb', f.read(4))
                Normals.append((nBytes[1] / 127, -nBytes[0] / 127, nBytes[2] / 127))
                UVs.append((0.0, 0.0))
                wBytes = struct.unpack('BBBB', f.read(4))
                if wBytes[0] == 255:
                    BoneWeights.append((1.0, 0.0, 0.0, 0.0))
                else:
                    BoneWeights.append((wBytes[0]/256, wBytes[1]/256, wBytes[2]/256, wBytes[3]/256))
                BoneIndices.append(struct.unpack('BBBB', f.read(4)))
            bm = bmesh.new()
            for pos in Positions:
                bm.verts.new(pos)
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            # create faces
            uv = bm.loops.layers.uv.new()  # init the uv map
            for sm in SMInfos:
                for i in range(sm[3] // 3):
                    indices = struct.unpack('<hhh', f.read(6))
                    face = bm.faces.new([bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]]])
                    for loop in face.loops:
                        loop[uv].uv = (UVs[loop.vert.index][0], -UVs[loop.vert.index][1])
                    face.smooth = True
                    face.material_index = MatLookup[f'texturedmesh_{sm[0]}']
            for rsm in RSMInfos:
                for i in range(rsm[3] // 3):
                    indices = struct.unpack('<hhh', f.read(6))
                    face = bm.faces.new([bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]]])
                    for loop in face.loops:
                        loop[uv].uv = (UVs[loop.vert.index][0], -UVs[loop.vert.index][1])
                    face.smooth = True
                    face.material_index = MatLookup[f'reflectmesh_{rsm[0]}']
            bm.to_mesh(mesh)
            bm.free()
            mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(Normals)
            obj = bpy.data.objects.new(Path.split('/')[-1].split('.')[0], mesh)
            # load vertex weights
            for i in range(VertCount + ReflectVertCount):
                bidx = BoneIndices[i]
                bwts = BoneWeights[i]
                for idx, wt in zip(bidx, bwts):
                    vg = obj.vertex_groups.get(Groups[idx])
                    if vg == None:
                        vg = obj.vertex_groups.new(name=Groups[idx])
                    vg.add([i], wt, 'ADD')
            bpy.context.scene.collection.objects.link(obj)
            
    elif Mode == "PS3":
        with open(Path, 'rb') as f:
            MeshInfoOffset = struct.unpack('>I', f.read(4))[0]
            TexHeaderOffset = struct.unpack('>I', f.read(4))[0]
            TextureCount = struct.unpack('>I', f.read(4))[0]
            TexDict = {}
            # load textures
            with open(Path.split('.')[0] + '.vram', 'rb') as vram:
                f.seek(TexHeaderOffset)
                for i in range(TextureCount):
                    TexDataOffset = struct.unpack('>I', f.read(4))[0]
                    UnkByte1 = f.read(1)[0]
                    MipCount = f.read(1)[0]
                    UnkBytes1 = f.read(18)
                    Resolution = struct.unpack('>HH', f.read(4))
                    UnkBytes2 = f.read(8)
                    vram.seek(TexDataOffset)
                    
                    if UnkBytes1[4] == 1:
                        ImageData = DecodeBC1(vram, Resolution[0], Resolution[1])
                        img = bpy.data.images.new(name=f"{Path.split('/')[-1].split('.')[0]}_{i}", width=Resolution[0], height=Resolution[1])
                        TexDict[i] = img.name
                        img.pixels = ImageData
                    elif UnkBytes1[4] == 3:
                        ImageData = DecodeBC3(vram, Resolution[0], Resolution[1])
                        img = bpy.data.images.new(name=f"{Path.split('/')[-1].split('.')[0]}_{i}", width=Resolution[0], height=Resolution[1])
                        TexDict[i] = img.name
                        img.pixels = ImageData
            f.seek(MeshInfoOffset)
            SubmeshCount = struct.unpack('>I', f.read(4))[0]
            ReflectionSubmeshCount = struct.unpack('>I', f.read(4))[0]
            SubmeshInfoOffset = struct.unpack('>I', f.read(4))[0]
            ReflectionSubmeshInfoOffset = struct.unpack('>I', f.read(4))[0]
            VertOffset = struct.unpack('>I', f.read(4))[0]
            FaceOffset = struct.unpack('>I', f.read(4))[0]
            VertCount = struct.unpack('>H', f.read(2))[0]
            ReflectVertCount = struct.unpack('>H', f.read(2))[0]
            f.seek(SubmeshInfoOffset)
            SMInfos = []
            RSMInfos = []
            Positions = []
            Normals = []
            UVs = []
            BoneIndices = []
            BoneWeights = []
            MatLookup = {}
            mesh = bpy.data.meshes.new(Path.split('/')[-1].split('.')[0])
            for i in range(SubmeshCount):
                TexIndex = struct.unpack('>I', f.read(4))[0]
                StartFaceIndex = struct.unpack('>I', f.read(4))[0]
                FaceCount = struct.unpack('>I', f.read(4))[0]
                Unk = struct.unpack('>I', f.read(4))[0]
                mat = bpy.data.materials.new(f'texturedmesh_{i}')
                mat.use_nodes=True
                matOutput = mat.node_tree.nodes.get('Material Output')
                pBSDFNode = mat.node_tree.nodes.get('Principled BSDF')

                matTex = mat.node_tree.nodes.new('ShaderNodeTexImage')
                matTex.image = bpy.data.images[TexDict[TexIndex]]

                mat.node_tree.links.new(matTex.outputs[0], pBSDFNode.inputs[0])
                MatLookup[f'texturedmesh_{i}'] = i
                mesh.materials.append(mat)
                SMInfos.append([i, TexIndex, StartFaceIndex, FaceCount, Unk])
            for i in range(ReflectionSubmeshCount):
                TexIndex = struct.unpack('>I', f.read(4))[0]
                StartFaceIndex = struct.unpack('>I', f.read(4))[0]
                FaceCount = struct.unpack('>I', f.read(4))[0]
                Unk = struct.unpack('>I', f.read(4))[0]
                mat = bpy.data.materials.new(f'reflectmesh_{i}')
                mat.use_nodes=True
                MatLookup[f'reflectmesh_{i}'] = i + SubmeshCount
                mesh.materials.append(mat)
                RSMInfos.append([i, TexIndex, StartFaceIndex, FaceCount, Unk])
            # read verts
            f.seek(VertOffset)
            for i in range(VertCount):
                PosPreCorrect = struct.unpack('>fff', f.read(12))
                Positions.append((PosPreCorrect[1], -PosPreCorrect[0], PosPreCorrect[2]))
                NorPreCorrect = struct.unpack('>fff', f.read(12))
                Normals.append((NorPreCorrect[1], -NorPreCorrect[0], NorPreCorrect[2]))
                UVs.append(struct.unpack('>ff', f.read(8)))
                wBytes = struct.unpack('BBBB', f.read(4))
                if wBytes[0] == 255:
                    BoneWeights.append((1.0, 0.0, 0.0, 0.0))
                else:
                    BoneWeights.append((wBytes[0]/256, wBytes[1]/256, wBytes[2]/256, wBytes[3]/256))
                BoneIndices.append(struct.unpack('BBBB', f.read(4)))
            # reflect verts
            for i in range(ReflectVertCount):
                PosPreCorrect = struct.unpack('>fff', f.read(12))
                Positions.append((PosPreCorrect[1], -PosPreCorrect[0], PosPreCorrect[2]))
                NorPreCorrect = struct.unpack('>fff', f.read(12))
                Normals.append((NorPreCorrect[1], -NorPreCorrect[0], NorPreCorrect[2]))
                UVs.append((0.0, 0.0))
                wBytes = struct.unpack('BBBB', f.read(4))
                if wBytes[0] == 255:
                    BoneWeights.append((1.0, 0.0, 0.0, 0.0))
                else:
                    BoneWeights.append((wBytes[0]/256, wBytes[1]/256, wBytes[2]/256, wBytes[3]/256))
                BoneIndices.append(struct.unpack('BBBB', f.read(4)))
            bm = bmesh.new()
            for pos in Positions:
                bm.verts.new(pos)
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            f.seek(FaceOffset)
            # create faces
            uv = bm.loops.layers.uv.new()  # init the uv map
            for sm in SMInfos:
                for i in range(sm[3] // 3):
                    indices = struct.unpack('>hhh', f.read(6))
                    print(indices)
                    face = bm.faces.new([bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]]])
                    for loop in face.loops:
                        loop[uv].uv = (UVs[loop.vert.index][0], -UVs[loop.vert.index][1])
                    face.smooth = True
                    face.material_index = MatLookup[f'texturedmesh_{sm[0]}']
            for rsm in RSMInfos:
                for i in range(rsm[3] // 3):
                    indices = struct.unpack('>hhh', f.read(6))
                    face = bm.faces.new([bm.verts[indices[0]], bm.verts[indices[1]], bm.verts[indices[2]]])
                    for loop in face.loops:
                        loop[uv].uv = (UVs[loop.vert.index][0], -UVs[loop.vert.index][1])
                    face.smooth = True
                    face.material_index = MatLookup[f'reflectmesh_{rsm[0]}']
            bm.to_mesh(mesh)
            bm.free()
            mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(Normals)
            obj = bpy.data.objects.new(Path.split('/')[-1].split('.')[0], mesh)
            bpy.context.scene.collection.objects.link(obj)
            # load vertex weights
            for i in range(VertCount + ReflectVertCount):
                bidx = BoneIndices[i]
                bwts = BoneWeights[i]
                for idx, wt in zip(bidx, bwts):
                    vg = obj.vertex_groups.get(Groups[idx])
                    if vg == None:
                        vg = obj.vertex_groups.new(name=Groups[idx])
                    vg.add([i], wt, 'ADD')
            if searchForSkeleton:
                # try to get the engine from level0
                path = os.path.split(Path)[0]
                # Just about everything here was learned from studying https://github.com/RatchetModding/Replanetizer
                with open(f"{path}/../../level0/engine.ps3", 'rb') as eng:
                    MobyPointer = struct.unpack(">I", eng.read(4))[0]
                    eng.seek(MobyPointer)
                    print(MobyPointer)
                    MobyCount = struct.unpack(">I", eng.read(4))[0]
                    RatchetOffset = 0
                    for i in range(MobyCount):  # try to find ratchet's moby. should always be 0 but you never know
                          MobyId = struct.unpack(">I", eng.read(4))[0]
                          if MobyId == 0:
                             RatchetOffset = struct.unpack(">I", eng.read(4))[0]
                             break
                    eng.seek(RatchetOffset)
                    # parse the moby and find the skeleton
                    mdlOffset = struct.unpack(">I", eng.read(4))[0]  # will always be 0 because ratchet's model is stored outside the engine in rac 2 and 3
                    null1 = struct.unpack(">I", eng.read(4))[0]
                    boneCount = eng.read(1)[0]
                    lpBoneCount = eng.read(1)[0]
                    extraNotNeededHere = eng.read(10)
                    BoneMatrixOffset = struct.unpack(">I", eng.read(4))[0]
                    BoneInfoOffset = struct.unpack(">I", eng.read(4))[0]
                    eng.seek(RatchetOffset+BoneInfoOffset)
                    arm = bpy.data.armatures.new(name="RatchetArmature")
                    armObj = bpy.data.objects.new(name="RatchetArmature", object_data=arm)
                    bpy.context.scene.collection.objects.link(armObj)
                    bpy.context.view_layer.objects.active = armObj
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                    for i in range(boneCount):
                        pos = struct.unpack(">fff", eng.read(12))
                        BoneLocation = (pos[1] * 0.0009785088, -pos[0] * 0.0009785088, pos[2] * 0.0009785088)  # weird scale but it works
                        unk0c = struct.unpack(">h", eng.read(2))[0]
                        Parent = struct.unpack(">h", eng.read(2))[0] // 0x40
                        # add bone
                        bone = arm.edit_bones.new(Groups[i])
                        bone.head = BoneLocation
                        bone.tail = (BoneLocation[0], BoneLocation[1] + 1.0, BoneLocation[2])
                        if unk0c == 0x7000:
                            bone.parent = arm.edit_bones[Groups[Parent]]
                            bone.head[0] += arm.edit_bones[Groups[Parent]].head[0]
                            bone.head[1] += arm.edit_bones[Groups[Parent]].head[1]
                            bone.head[2] += arm.edit_bones[Groups[Parent]].head[2]
                            bone.tail[0] = bone.head[0]
                            bone.tail[1] = bone.head[1] + 0.1
                            bone.tail[2] = bone.head[2]
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    obj.parent = armObj
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_add(type='ARMATURE')
                    obj.modifiers[0].object=armObj
    return {'FINISHED'}