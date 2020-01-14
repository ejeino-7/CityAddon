bl_info = {
"name": "City Creator",
"author": "Jesper Nilsson",
"version": (1, 0),
"blender": (2, 80, 0),
"location": "View3D > Add > Mesh > JN3D",
"description": "Create a Quick City",
"category": "Add Mesh"
}


import bpy
from bpy.types import Operator, Panel
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import *
import math
from math import *
import copy
import sys
from bpy.props import *
import string
import random


#define X,Y,Z = 1,2,3
# Can be used for indexing
X = 0
Y = 1
Z = 2
#------
#define NULL 0
NULL = 0
# HAHA :)



# Gets material or creates a new material
# if neccesary
def material(self, name, R, G, B, spec):
    if name not in bpy.data.materials or self.wall_unique == True:
        if(name == "brick"):
            mat=bpy.data.materials.new(name)
            mat.use_nodes = True
            
            # adding three Nodes
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            
            bsdf.inputs[5].default_value = 0
            
            tex = mat.node_tree.nodes.new(type="ShaderNodeTexBrick")
            tex.inputs[1].default_value = (self.wall_R, self.wall_G, self.wall_B, 1)
            tex.inputs[2].default_value = (self.wall_R2, self.wall_G2, self.wall_B2, 1)
            tex.inputs[3].default_value = (0.1, 0.1, 0.1, 1)
            tex.inputs[4].default_value = self.brick_scale

            map = mat.node_tree.nodes.new('ShaderNodeTexCoord')
            # Connecting the nodes
            mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])
            mat.node_tree.links.new(tex.inputs['Vector'], map.outputs['UV'])

        elif(name == "color"):
            mat=bpy.data.materials.new(name)
            mat.use_nodes = True
            
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            bsdf.inputs[0].default_value = (self.wall_R, self.wall_G, self.wall_B, 1)       
            bsdf.inputs[5].default_value = 0
    
        elif(name == "window_material"):
            if name not in bpy.data.materials: 
                mat=bpy.data.materials.new(name)
                mat.diffuse_color     = ([R,G,B, 1])
                if(spec == True):
                    mat.specular_intensity = 1
                    mat.roughness = 0
            else:
                mat = bpy.data.materials[name]
        
        else:
            mat=bpy.data.materials.new(name)
            mat.diffuse_color     = ([R,G,B, 1])
            if(spec == True):
                mat.specular_intensity = 1
                mat.roughness = 0
            
    else:
        mat=bpy.data.materials[name]

    return mat

## Window
def window(self, context, lowerLeftCorner):
    
    # rim corners A,B,C,D
    ## Corner C will be placed on the origin point (0,0,0) relative to Object
    A = (0, 0, self.height + self.bottomHeight)
    B = (self.width, 0, self.height + self.bottomHeight)
    C = (0,0, self.bottomHeight) 
    D = (self.width, 0, self.bottomHeight)
       
    #    A              B   #
    #       a       b       #
    #                       #
    #                       #
    #       c       d       #
    #   C               D   #
    ## ____________________________________________
    ## creating a,b,c,d from coordinates A,B,C,D
    a = (A[X] + self.side, 0, A[Z] - self.top)
    b = (B[X] - self.side, 0, B[Z] - self.top)
    c = (C[X] + self.side, 0, C[Z] + self.bottom) 
    d = (D[X] - self.side, 0, D[Z] + self.bottom)
    ##_____________________________________________
    
    
    ## extruding in the window face
    #
    #           ai      bi
    #       a       b
    #
    #           ci      di
    #       c       d
    # -------------------------
    ai = (a[X],a[Y] + self.depth ,a[Z])
    bi = (b[X],b[Y] + self.depth ,b[Z])
    ci = (c[X],c[Y] + self.depth ,c[Z])
    di = (d[X],d[Y] + self.depth ,d[Z])
    
    
    # the 12 base verticies
    
    # index: 0  1  2  3  4  5  6  7  8   9   10  11 
    verts = [A, B, C, D, a, b, c, d, ai, bi, ci, di]
    
    
    # for faces connect A,B,a,b an so on
    # then a,ai,bi,b
    # window face will be ai,bi,ci,di
    windowFace = (8,10,11,9)
    faces = [(4,5,1,0),(2,6,4,0),(3,7,6,2),(1,5,7,3),(4,8,9,5),(5,9,11,7),(7,11,10,6),(6,10,8,4) , windowFace]
    ## -------------------------------------------------------------------------------------------------------
    ## This is how it will look when you start to program before you start thinking..
    ## Creating Horizontal and vertical rims 
    #   Horizontal
    #
    #   C           D
    #   ------------- # height / 2
    #   A           B
    #
    #   Vertical
    #   
    #   C  D
    #
    #
    #
    #
    #   A  B
    if(self.add_hor == True):
        Ah = (a[X], self.depth / 2, (self.height / 2) - self.h_thickness + self.h_offset + self.bottomHeight) 
        Bh = (b[X], self.depth / 2, Ah[Z])
        Ch = (a[X], self.depth / 2, (self.height / 2) + self.h_thickness + self.h_offset + self.bottomHeight)
        Dh = (b[X], self.depth / 2, Ch[Z])
        
        ah = (a[X], ai[Y], Ah[Z])
        bh = (b[X], ai[Y], Bh[Z])
        ch = (a[X], ai[Y], Ch[Z])
        dh = (b[X], ai[Y], Dh[Z])
        
                         # Index
        verts.append(Ah) # 12
        verts.append(Bh) # 13
        verts.append(Ch) # 14
        verts.append(Dh) # 15
        verts.append(ah) # 16
        verts.append(bh) # 17
        verts.append(ch) # 18
        verts.append(dh) # 19
        
        faces.append((12,13,15,14))
        faces.append((13,12,16,17))
        faces.append((15,13,17,19))
        faces.append((14,15,19,18))
        faces.append((12,14,18,16))
        
    if(self.add_ver == True):
        Av = ((self.width / 2) - self.v_thickness + self.v_offset, self.depth / 2 - 0.0001, c[Z])
        Bv = ((self.width / 2) + self.v_thickness + self.v_offset, self.depth / 2 - 0.0001, c[Z])
        Cv = (Av[X] , self.depth / 2 - 0.0001, a[Z])
        Dv = (Bv[X] , self.depth / 2 - 0.0001, a[Z])
        av = (Av[X], self.depth, c[Z])
        bv = (Bv[X], self.depth, c[Z])
        cv = (av[X], self.depth, a[Z])
        dv = (bv[X], self.depth, a[Z])
                         # Index will depend of if the horizontal is added
        verts.append(Av) # 12   20
        verts.append(Bv) # 13   21
        verts.append(Cv) # 14   22
        verts.append(Dv) # 15   23
        verts.append(av) # 16   24
        verts.append(bv) # 17   25
        verts.append(cv) # 18   26
        verts.append(dv) # 19   27
        if(self.add_hor == True): # If the horizional is used then it will use the second index option    
            faces.append((20,21,23,22))
            faces.append((21,20,24,25))
            faces.append((23,21,25,27))
            faces.append((22,23,27,26))
            faces.append((20,22,26,24))
        else: # use the first indexes
            faces.append((12,13,15,14))
            faces.append((13,12,16,17))
            faces.append((15,13,17,19))
            faces.append((14,15,19,18))
            faces.append((12,14,18,16))
            
    mesh = bpy.data.meshes.new(name="window")
    
    mesh.from_pydata(verts, [], faces)
   
    mesh.materials.append(material(self, "rim_material", self.wall_R, self.wall_G, self.wall_B, False))
    
    mesh.materials.append(material(self, "window_material", 0,0,0, True))
    
    mesh.materials.append(material(self, self.wall_mat, 0, 0, 0 , False))

    # assigning the correct material
    i = 0
    while(i < len(faces)):
        if(i < 4):
            mesh.polygons[i].material_index = 2
        elif(i == 8):
            mesh.polygons[i].material_index = 1
        else:
            mesh.polygons[i].material_index = 0
        i += 1
    
    
    self.window_Object = object_data_add(context, mesh, operator=self)
    self.window_Object.parent = self.empty

    # UV-unwrap
    bpy.ops.mesh.uv_texture_add()
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.editmode_toggle()

    
    return 1

def window_second(self, context, lowerLeftCorner):

    A = (self.width, 0, self.height + self.bottomHeight)
    B = (self.width + self.width2, 0, self.height + self.bottomHeight)
    C = (self.width,0, self.bottomHeight) 
    D = (self.width + self.width2, 0, self.bottomHeight)
       
  
    a = (A[X] + self.side2, 0, A[Z] - self.top2)
    b = (B[X] - self.side2, 0, B[Z] - self.top2)
    c = (C[X] + self.side2, 0, C[Z] + self.bottom2) 
    d = (D[X] - self.side2, 0, D[Z] + self.bottom2)

    ai = (a[X],a[Y] + self.depth2 ,a[Z])
    bi = (b[X],b[Y] + self.depth2 ,b[Z])
    ci = (c[X],c[Y] + self.depth2 ,c[Z])
    di = (d[X],d[Y] + self.depth2 ,d[Z])
    
    # the 12 base verticies
    # index: 0  1  2  3  4  5  6  7  8   9   10  11 
    verts = [A, B, C, D, a, b, c, d, ai, bi, ci, di]
    
    windowFace = (8,10,11,9)
    faces = [(4,5,1,0),(2,6,4,0),(3,7,6,2),(1,5,7,3),(4,8,9,5),(5,9,11,7),(7,11,10,6),(6,10,8,4) , windowFace]
    ## --------------------------------------------------------------------------------------------------------
    
    if(self.add_hor2 == True):
        Ah = (a[X], self.depth2 / 2, (self.height / 2) - self.h_thickness2 + self.h_offset2 + self.bottomHeight) 
        Bh = (b[X], self.depth2 / 2, Ah[Z])
        Ch = (a[X], self.depth2 / 2, (self.height / 2) + self.h_thickness2 + self.h_offset2 + self.bottomHeight)
        Dh = (b[X], self.depth2 / 2, Ch[Z])
        
        ah = (a[X], ai[Y], Ah[Z])
        bh = (b[X], ai[Y], Bh[Z])
        ch = (a[X], ai[Y], Ch[Z])
        dh = (b[X], ai[Y], Dh[Z])
        
                         # Index
        verts.append(Ah) # 12
        verts.append(Bh) # 13
        verts.append(Ch) # 14
        verts.append(Dh) # 15
        verts.append(ah) # 16
        verts.append(bh) # 17
        verts.append(ch) # 18
        verts.append(dh) # 19
        
        faces.append((12,13,15,14))
        faces.append((13,12,16,17))
        faces.append((15,13,17,19))
        faces.append((14,15,19,18))
        faces.append((12,14,18,16))
        
    if(self.add_ver2 == True):
        Av = ((self.width2 / 2) - self.v_thickness2 + self.v_offset2 + self.width, self.depth2 / 2 - 0.0001, c[Z])
        Bv = ((self.width2 / 2) + self.v_thickness2 + self.v_offset2 + self.width, self.depth2 / 2 - 0.0001, c[Z])
        Cv = (Av[X] , self.depth2 / 2 - 0.0001, a[Z])
        Dv = (Bv[X] , self.depth2 / 2 - 0.0001, a[Z])

        av = (Av[X], self.depth2, c[Z])
        bv = (Bv[X], self.depth2, c[Z])
        cv = (av[X], self.depth2, a[Z])
        dv = (bv[X], self.depth2, a[Z])
                         # Index will depend on if the horizontal is added
        verts.append(Av) # 12   20
        verts.append(Bv) # 13   21
        verts.append(Cv) # 14   22
        verts.append(Dv) # 15   23
        verts.append(av) # 16   24
        verts.append(bv) # 17   25
        verts.append(cv) # 18   26
        verts.append(dv) # 19   27
        if(self.add_hor2 == True): # If the horizional is used then it will use the second index option    
            faces.append((20,21,23,22))
            faces.append((21,20,24,25))
            faces.append((23,21,25,27))
            faces.append((22,23,27,26))
            faces.append((20,22,26,24))
        else: # use the first indexes
            faces.append((12,13,15,14))
            faces.append((13,12,16,17))
            faces.append((15,13,17,19))
            faces.append((14,15,19,18))
            faces.append((12,14,18,16))


    mesh = bpy.data.meshes.new(name="window2")
    
    mesh.from_pydata(verts, [], faces)
   
    mesh.materials.append(material(self, "rim_material", self.wall_R, self.wall_G, self.wall_B, False))
    
    mesh.materials.append(material(self, "window_material", 0,0,0, True))
    
    mesh.materials.append(material(self, self.wall_mat, 0, 0, 0 , False))

    # assigning the correct material
    i = 0
    while(i < len(faces)):
        if(i < 4):
            mesh.polygons[i].material_index = 2
        elif(i == 8):
            mesh.polygons[i].material_index = 1
        else:
            mesh.polygons[i].material_index = 0
        i += 1
    
   
    self.window_Object2 = object_data_add(context, mesh, operator=self)
    self.window_Object2.parent = self.empty
    
    bpy.ops.mesh.uv_texture_add()
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.editmode_toggle()
    
    return 1

def window_third(self, context, lowerLeftCorner):

    A = (self.width + self.width2, 0, self.height + self.bottomHeight)
    B = (self.width + self.width2 + self.width3, 0, self.height + self.bottomHeight)
    C = (self.width + self.width2,0, self.bottomHeight) 
    D = (self.width + self.width2 + self.width3, 0, self.bottomHeight)
       
  
    a = (A[X] + self.side3, 0, A[Z] - self.top3)
    b = (B[X] - self.side3, 0, B[Z] - self.top3)
    c = (C[X] + self.side3, 0, C[Z] + self.bottom3) 
    d = (D[X] - self.side3, 0, D[Z] + self.bottom3)

    ai = (a[X],a[Y] + self.depth3 ,a[Z])
    bi = (b[X],b[Y] + self.depth3 ,b[Z])
    ci = (c[X],c[Y] + self.depth3 ,c[Z])
    di = (d[X],d[Y] + self.depth3 ,d[Z])
    
    # the 12 base verticies
    # index: 0  1  2  3  4  5  6  7  8   9   10  11 
    verts = [A, B, C, D, a, b, c, d, ai, bi, ci, di]
    
    windowFace = (8,10,11,9)
    faces = [(4,5,1,0),(2,6,4,0),(3,7,6,2),(1,5,7,3),(4,8,9,5),(5,9,11,7),(7,11,10,6),(6,10,8,4) , windowFace]
    ## --------------------------------------------------------------------------------------------------------

    if(self.add_hor3 == True):
        Ah = (a[X], self.depth3 / 2, (self.height / 2) - self.h_thickness3 + self.h_offset3 + self.bottomHeight) 
        Bh = (b[X], self.depth3 / 2, Ah[Z])
        Ch = (a[X], self.depth3 / 2, (self.height / 2) + self.h_thickness3 + self.h_offset3 + self.bottomHeight)
        Dh = (b[X], self.depth3 / 2, Ch[Z])
        
        ah = (a[X], ai[Y], Ah[Z])
        bh = (b[X], ai[Y], Bh[Z])
        ch = (a[X], ai[Y], Ch[Z])
        dh = (b[X], ai[Y], Dh[Z])
        
                         # Index
        verts.append(Ah) # 12
        verts.append(Bh) # 13
        verts.append(Ch) # 14
        verts.append(Dh) # 15
        verts.append(ah) # 16
        verts.append(bh) # 17
        verts.append(ch) # 18
        verts.append(dh) # 19
        
        faces.append((12,13,15,14))
        faces.append((13,12,16,17))
        faces.append((15,13,17,19))
        faces.append((14,15,19,18))
        faces.append((12,14,18,16))
        
    if(self.add_ver3 == True):
        Av = ((self.width3 / 2) - self.v_thickness3 + self.v_offset3 + self.width + self.width2, self.depth3 / 2 - 0.0001, c[Z])
        Bv = ((self.width3 / 2) + self.v_thickness3 + self.v_offset3 + self.width + self.width2, self.depth3 / 2 - 0.0001, c[Z])
        Cv = (Av[X] , self.depth3 / 2 - 0.0001, a[Z])
        Dv = (Bv[X] , self.depth3 / 2 - 0.0001, a[Z])

        av = (Av[X], self.depth3, c[Z])
        bv = (Bv[X], self.depth3, c[Z])
        cv = (av[X], self.depth3, a[Z])
        dv = (bv[X], self.depth3, a[Z])
                         # Index will depend of if the horizontal is added
        verts.append(Av) # 12   20
        verts.append(Bv) # 13   21
        verts.append(Cv) # 14   22
        verts.append(Dv) # 15   23
        verts.append(av) # 16   24
        verts.append(bv) # 17   25
        verts.append(cv) # 18   26
        verts.append(dv) # 19   27
        if(self.add_hor3 == True): # If the horizional is used then it will use the second index option    
            faces.append((20,21,23,22))
            faces.append((21,20,24,25))
            faces.append((23,21,25,27))
            faces.append((22,23,27,26))
            faces.append((20,22,26,24))
        else: # use the first indexes
            faces.append((12,13,15,14))
            faces.append((13,12,16,17))
            faces.append((15,13,17,19))
            faces.append((14,15,19,18))
            faces.append((12,14,18,16))
            
    mesh = bpy.data.meshes.new(name="window3")
    
    mesh.from_pydata(verts, [], faces)
   
    mesh.materials.append(material(self, "rim_material", self.wall_R, self.wall_G, self.wall_B, False))
    
    mesh.materials.append(material(self, "window_material", 0,0,0, True))
    
    mesh.materials.append(material(self, self.wall_mat, 0, 0, 0 , False))

    # assigning the correct material
    i = 0
    while(i < len(faces)):
        if(i < 4):
            mesh.polygons[i].material_index = 2
        elif(i == 8):
            mesh.polygons[i].material_index = 1
        else:
            mesh.polygons[i].material_index = 0
        i += 1
    
   
    self.window_Object3 = object_data_add(context, mesh, operator=self)
    self.window_Object3.parent = self.empty

    bpy.ops.mesh.uv_texture_add()
    bpy.ops.object.editmode_toggle()
    bpy.ops.uv.cube_project(cube_size=1)
    bpy.ops.object.editmode_toggle()
    
    return 1

## Balcony
def balcony(self, context):
    
    # The Balcony will be a little bit trickier
    #
    #   bottom plane will look like
    #   distance between A and AA will be b_thickness    
    #               
    #   A  AA     BB  B     (A is the base corner)
    #
    #
    #
    #   E  CC     DD  F      
    #   C  G      H   D
    
    
    A = (self.b_offset + (self.width / 2) - (self.b_width / 2), 0, self.bottomHeight)
    B = (A[X] + self.b_width, 0, self.bottomHeight)
    C = (A[X], self.b_depth * -1, self.bottomHeight)
    D = (B[X], self.b_depth * -1, self.bottomHeight)
    
    E = (C[X], C[Y] + self.b_thickness, C[Z])
    F = (D[X], D[Y] + self.b_thickness, D[Z])
    G = (C[X] + self.b_thickness, C[Y], C[Z])
    H = (D[X] - self.b_thickness, D[Y], D[Z])
    
    AA = (A[X] + self.b_thickness, A[Y], A[Z])
    BB = (B[X] - self.b_thickness, B[Y], B[Z])
    CC = (C[X] + self.b_thickness, C[Y] + self.b_thickness, C[Z])
    DD = (D[X] - self.b_thickness, D[Y] + self.b_thickness, D[Z]) 

    # extruding the face up
    a = (A[X], A[Y], self.bottomHeight + self.b_thickness)
    b = (B[X], B[Y], self.bottomHeight + self.b_thickness)
    c = (C[X], C[Y], self.bottomHeight + self.b_thickness)
    d = (D[X], D[Y], self.bottomHeight + self.b_thickness)
    
    e = (E[X], E[Y], E[Z] + self.b_thickness)
    f = (F[X], F[Y], F[Z] + self.b_thickness)
    g = (G[X], G[Y], G[Z] + self.b_thickness)
    h = (H[X], H[Y], H[Z] + self.b_thickness)
    
    aa = (AA[X], AA[Y], self.bottomHeight + self.b_thickness)
    bb = (BB[X], BB[Y], self.bottomHeight + self.b_thickness)
    cc = (CC[X], CC[Y], self.bottomHeight + self.b_thickness)
    dd = (DD[X], DD[Y], self.bottomHeight + self.b_thickness)
    # so this will build the bottom block
    
    # and then the top verts
    at = (A[X], A[Y], a[Z] + self.b_height)
    bt = (B[X], B[Y], b[Z] + self.b_height)
    ct = (C[X], C[Y], c[Z] + self.b_height)
    dt = (D[X], D[Y], d[Z] + self.b_height)
    
    et = (e[X], e[Y], ct[Z])
    ft = (f[X], f[Y], dt[Z])
    gt = (g[X], g[Y], ct[Z])
    ht = (h[X], h[Y], dt[Z])
    
    aat = (AA[X], AA[Y], aa[Z] + self.b_height)
    bbt = (BB[X], BB[Y], bb[Z] + self.b_height)
    cct = (CC[X], CC[Y], cc[Z] + self.b_height)
    ddt = (DD[X], DD[Y], dd[Z] + self.b_height)
    
    #   for the case where there is a hole in the balcony walls there need to be 4 extra verts per column
    c1  = (c[X], c[Y], ct[Z] - self.b_thickness)
    g1  = (g[X], g[Y], gt[Z] - self.b_thickness)
    cc1 = (cc[X], cc[Y], cct[Z] - self.b_thickness)
    e1  = (e[X], e[Y], et[Z] - self.b_thickness)
    
    d1  = (d[X], d[Y], dt[Z] - self.b_thickness)
    h1  = (h[X], h[Y], ht[Z] - self.b_thickness)
    dd1 = (dd[X], dd[Y], ddt[Z] - self.b_thickness)
    f1  = (f[X], f[Y], ft[Z] - self.b_thickness) 
    
    # plus 4 verts close to the wall
    a1  = (a[X], a[Y], at[Z] - self.b_thickness)
    aa1 = (aa[X], aa[Y], aat[Z] - self.b_thickness)
    b1  = (b[X], b[Y], bt[Z] - self.b_thickness)
    bb1 = (bb[X], bb[Y], bbt[Z] - self.b_thickness) 

    #  index: 0  1  2  3  4  5  6  7  8   9   10  11  12 13 14 15 16 17 18 19 20  21  22  23  24  25  26  27  28  29  30  31  32   33   34   35   36  37  38  39  40  41  42  43  44   45   46   47 
    #verts = [A, B, C, D, E, F, G, H, AA, BB, CC, DD, a, b, c, d, e, f, g, h, aa, bb, cc, dd, at, bt, ct, dt, et, ft, gt, ht, aat, bbt, cct, ddt, a1, b1, c1, d1, e1, f1, g1, h1, aa1, bb1, cc1, dd1 ]
    # connecting faces, NOTE : no need to create the face that will point into the wall 
    if(self.b_look == False):
        verts = [A, B, C, D, E, F, G, H, AA, BB, CC, DD, a, b, c, d, e, f, g, h, aa, bb, cc, dd, at, bt, ct, dt, et, ft, gt, ht, aat, bbt, cct, ddt] 
    #            baseplane                                                                     lower rim                                                                                     top plane inside the balcony   Extrution up                                                                                                                                           # top face                   
        faces = [(0,8,10,4), (4,10,6,2), (10,11,7,6), (11,5,3,7), (9,1,5,11), (8,9,11,10),     (12,0,4,16), (16,4,2,14), (14,2,6,18), (18,6,7,19), (19,7,3,15), (15,3,5,17), (17,5,1,13),    (20,22,23,21),                 (12,16,28,24), (16,14,26,28), (14,18,30,26), (18,19,31,30), (19,15,27,31), (15,17,29,27), (17,13,25,29), (22,20,32,34), (23,22,34,35), (21,23,35,33),  (24,28,34,32), (28,26,30,34), (30,31,35,34), (31,27,29,35), (29,25,33,35) ]
    else:
        verts = [A, B, C, D, E, F, G, H, AA, BB, CC, DD, a, b, c, d, e, f, g, h, aa, bb, cc, dd, at, bt, ct, dt, et, ft, gt, ht, aat, bbt, cct, ddt, a1, b1, c1, d1, e1, f1, g1, h1, aa1, bb1, cc1, dd1 ]
    #            baseplane                                                                     lower rim                                                                                     balcony floor                                                     Extruding pillars                                                                                                           # top face                                                                      top rim
        faces = [(0,8,10,4), (4,10,6,2), (10,11,7,6), (11,5,3,7), (9,1,5,11), (8,9,11,10),     (12,0,4,16), (16,4,2,14), (14,2,6,18), (18,6,7,19), (19,7,3,15), (15,3,5,17), (17,5,1,13),    (20,22,23,21), (17,13,21,23), (18,19,23,22), (12,16,22,20),      (22,16,28,34), (16,14,26,28), (14,18,30,26), (18,22,34,30), (17,23,35,29), (23,19,31,35), (19,15,27,31), (15,17,29,27),      (24,28,34,32), (28,26,30,34), (30,31,35,34), (31,27,29,35), (29,25,33,35),      (36,40,28,24), (40,38,26,28), (38,42,30,26), (42,43,31,30), (43,39,27,31), (39,41,29,27), (41,37,25,29),   (46,44,32,34), (47,46,34,35), (45,47,35,33),     (37,41,47,45), (46,47,43,42), (44,46,40,36)    ]

    mesh = bpy.data.meshes.new(name="balcony_baseBlock")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material(self, "balcony", self.wall_R, self.wall_G, self.wall_B, False))
    
    self.balcony_Object = object_data_add(context, mesh, operator=self)
    self.balcony_Object.parent = self.empty
    

## WALL
def wall(self, context, lowerLeftCorner):
    window(self, context, lowerLeftCorner)
    self.array_width = self.window_Object.modifiers.new(name='width', type='ARRAY') 
    self.array_height = self.window_Object.modifiers.new(name='height', type='ARRAY')
    
    self.array_width.relative_offset_displace = (1,0,0)
    self.array_height.relative_offset_displace = (0,0,1)
    
    self.array_width.count = self.columns
    self.array_height.count = self.rows
    

def wall_advanced(self, context, lowerLeftCorner):
    # Height array will use relative offset, the width array will be calculated
    
    window(self, context, lowerLeftCorner)
    window_second(self, context, lowerLeftCorner)
    self.array_width = self.window_Object.modifiers.new(name='width', type='ARRAY') 
    self.array_height = self.window_Object.modifiers.new(name='height', type='ARRAY')
    self.array_width.use_constant_offset = True
    self.array_width.use_relative_offset = False

    self.array_width2 = self.window_Object2.modifiers.new(name='width', type='ARRAY') 
    self.array_height2 = self.window_Object2.modifiers.new(name='height', type='ARRAY')
    self.array_width2.use_constant_offset = True
    self.array_width2.use_relative_offset = False
    
    if(self.adv_window_count == 3):
        window_third(self, context, lowerLeftCorner)
        self.array_width3 = self.window_Object3.modifiers.new(name='width', type='ARRAY') 
        self.array_height3 = self.window_Object3.modifiers.new(name='height', type='ARRAY')
        self.array_width3.use_constant_offset = True
        self.array_width3.use_relative_offset = False
        
        self.array_width.constant_offset_displace  = (self.width + self.width2 + self.width3, 0, 0)
        self.array_width2.constant_offset_displace = (self.width + self.width2 + self.width3, 0, 0)
        self.array_width3.constant_offset_displace = (self.width + self.width2 + self.width3, 0, 0)
        
        
    
    else:
        self.array_width.constant_offset_displace = (self.width + self.width2, 0, 0)
        self.array_width2.constant_offset_displace = (self.width + self.width2, 0, 0)
   
    self.array_height.relative_offset_displace  = (0,0,1)
    self.array_height2.relative_offset_displace = (0,0,1)

    if(self.end_wind1 == True):
        self.array_width.count = self.columns + 1
    else:
        self.array_width.count = self.columns
        
    self.array_height.count = self.rows
    self.array_width2.count = self.columns
    self.array_height2.count = self.rows
        
    if(self.adv_window_count == 3):
        self.array_height3.relative_offset_displace = (0,0,1)
        self.array_width3.count = self.columns
        self.array_height3.count = self.rows    
    
    
        
     

    
    
    
## Roof
def roof(self, context):
        
    
    #       B       D
    #
    #
    #
    #   --->A       C
    # base corner
    #
    
    A = (0, 0, self.height * self.rows + self.bottomHeight)
    B = (0, self.width * self.columns, self.height * self.rows + self.bottomHeight)
    C = (self.width * self.columns, 0 ,self.height * self.rows + self.bottomHeight)
    D = (self.width * self.columns, self.width * self.columns, self.height * self.rows + self.bottomHeight)
    
   
    #       B           D
    #         b      d     
    #                  
    #
    #         a      c
    #       A           C
  
    a = (self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
    b = (self.roof_rt, self.width * self.columns- self.roof_rt, self.height * self.rows + self.bottomHeight)
    c = (self.width * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
    d = (self.width * self.columns - self.roof_rt, self.width * self.columns - self.roof_rt, self.height * self.rows + self.bottomHeight)

    # A,B,C,D,a,b,c,d will be the baseplane
    # and will have an "extruded" edge 
    # this will be AA,BB,CC,DD,aa,bb,cc,dd
    
    
    AA = (0, 0, self.height * self.rows + self.roof_height + self.bottomHeight)
    BB = (0, self.width * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
    CC = (self.width * self.columns, 0 ,self.height * self.rows + self.roof_height + self.bottomHeight)
    DD = (self.width * self.columns, self.width * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
    
    
    aa = (self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
    bb = (self.roof_rt, self.width * self.columns- self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
    cc = (self.width * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
    dd = (self.width * self.columns - self.roof_rt, self.width * self.columns - self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
    ## ------------------------------------------
    
    #        0 1 2 3 4 5 6 7 8  9  10 11 12 13 14 15
    verts = [A,B,C,D,a,b,c,d,AA,BB,CC,DD,aa,bb,cc,dd]
    
    # connecting into faces

    # outer sidefaces of the rim                   # top of rim                                                          # inside face of rim                               # floor face
    faces = [(1,0,8,9), (3,1,9,11), (2,3,11,10), (0,2,10,8), (9,8,12,13), (11,9,13,15), (10,11,15,14), (8,10,14,12),    (5,4,12,13), (7,5,13,15), (7,6,14,15), (6,4,12,14),  (4,6,7,5)   ]

    # creating the mesh  
    mesh = bpy.data.meshes.new(name="roof")
    
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material(self, "roof_material", self.wall_R, self.wall_G, self.wall_B, False))

    roof = object_data_add(context, mesh, operator=self)
    roof.parent = self.empty
    
def roof_advanced(self, context):
 
    if(self.end_wind1 == True):         
        if(self.adv_window_count == 3):    
            A = (0, 0, self.height * self.rows + self.bottomHeight)
            B = (0, (self.width + self.width2 + self.width3) * self.columns + self.width, self.height * self.rows + self.bottomHeight)
            C = ((self.width + self.width2 + self.width3) * self.columns + self.width, 0 ,self.height * self.rows + self.bottomHeight)
            D = ((self.width + self.width2 + self.width3) * self.columns + self.width, (self.width + self.width2 + self.width3) * self.columns + self.width, self.height * self.rows + self.bottomHeight)
            
            a = (self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            b = (self.roof_rt, (self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.bottomHeight)
            c = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, self.roof_rt, self.height * self.rows + self.bottomHeight)
            d = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, (self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.bottomHeight)

            AA = (0, 0, self.height * self.rows + self.roof_height + self.bottomHeight)
            BB = (0, (self.width + self.width2 + self.width3) * self.columns + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            CC = ((self.width + self.width2 + self.width3) * self.columns + self.width, 0 ,self.height * self.rows + self.roof_height + self.bottomHeight)
            DD = ((self.width + self.width2 + self.width3) * self.columns + self.width, (self.width + self.width2 + self.width3) * self.columns + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            
            
            aa = (self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            bb = (self.roof_rt, (self.width + self.width2 + self.width3) * self.columns- self.roof_rt + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            cc = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            dd = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, (self.width + self.width2 + self.width3) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
        
        else:
            A = (0, 0, self.height * self.rows + self.bottomHeight)
            B = (0, (self.width + self.width2) * self.columns + self.width, self.height * self.rows + self.bottomHeight)
            C = ((self.width + self.width2) * self.columns + self.width, 0 ,self.height * self.rows + self.bottomHeight)
            D = ((self.width + self.width2) * self.columns + self.width, (self.width + self.width2) * self.columns + self.width, self.height * self.rows + self.bottomHeight)
            
            a = (self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            b = (self.roof_rt, (self.width + self.width2) * self.columns- self.roof_rt + self.width, self.height * self.rows + self.bottomHeight)
            c = ((self.width + self.width2) * self.columns - self.roof_rt + self.width, self.roof_rt, self.height * self.rows + self.bottomHeight)
            d = ((self.width + self.width2) * self.columns - self.roof_rt + self.width, (self.width + self.width2) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.bottomHeight)

            AA = (0, 0, self.height * self.rows + self.roof_height + self.bottomHeight)
            BB = (0, (self.width + self.width2) * self.columns + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            CC = ((self.width + self.width2) * self.columns + self.width, 0 ,self.height * self.rows + self.roof_height + self.bottomHeight)
            DD = ((self.width + self.width2) * self.columns + self.width, (self.width + self.width2) * self.columns + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            
            
            aa = (self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            bb = (self.roof_rt, (self.width + self.width2) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
            cc = ((self.width + self.width2) * self.columns - self.roof_rt + self.width, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            dd = ((self.width + self.width2) * self.columns - self.roof_rt + self.width, (self.width + self.width2) * self.columns - self.roof_rt + self.width, self.height * self.rows + self.roof_height + self.bottomHeight)
        
    else:
        if(self.adv_window_count == 3):    
            A = (0, 0, self.height * self.rows + self.bottomHeight)
            B = (0, (self.width + self.width2 + self.width3) * self.columns, self.height * self.rows + self.bottomHeight)
            C = ((self.width + self.width2 + self.width3) * self.columns, 0 ,self.height * self.rows + self.bottomHeight)
            D = ((self.width + self.width2 + self.width3) * self.columns, (self.width + self.width2 + self.width3) * self.columns, self.height * self.rows + self.bottomHeight)
            
            a = (self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            b = (self.roof_rt, (self.width + self.width2 + self.width3) * self.columns- self.roof_rt, self.height * self.rows + self.bottomHeight)
            c = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            d = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt, (self.width + self.width2 + self.width3) * self.columns - self.roof_rt, self.height * self.rows + self.bottomHeight)

            AA = (0, 0, self.height * self.rows + self.roof_height + self.bottomHeight)
            BB = (0, (self.width + self.width2 + self.width3) * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
            CC = ((self.width + self.width2 + self.width3) * self.columns, 0 ,self.height * self.rows + self.roof_height + self.bottomHeight)
            DD = ((self.width + self.width2 + self.width3) * self.columns, (self.width + self.width2 + self.width3) * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
            
            
            aa = (self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            bb = (self.roof_rt, (self.width + self.width2 + self.width3) * self.columns- self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            cc = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            dd = ((self.width + self.width2 + self.width3) * self.columns - self.roof_rt, (self.width + self.width2 + self.width3) * self.columns - self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
        
        else:
            A = (0, 0, self.height * self.rows + self.bottomHeight)
            B = (0, (self.width + self.width2) * self.columns, self.height * self.rows + self.bottomHeight)
            C = ((self.width + self.width2) * self.columns, 0 ,self.height * self.rows + self.bottomHeight)
            D = ((self.width + self.width2) * self.columns, (self.width + self.width2) * self.columns, self.height * self.rows + self.bottomHeight)
            
            a = (self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            b = (self.roof_rt, (self.width + self.width2) * self.columns- self.roof_rt, self.height * self.rows + self.bottomHeight)
            c = ((self.width + self.width2) * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.bottomHeight)
            d = ((self.width + self.width2) * self.columns - self.roof_rt, (self.width + self.width2) * self.columns - self.roof_rt, self.height * self.rows + self.bottomHeight)

            AA = (0, 0, self.height * self.rows + self.roof_height + self.bottomHeight)
            BB = (0, (self.width + self.width2) * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
            CC = ((self.width + self.width2) * self.columns, 0 ,self.height * self.rows + self.roof_height + self.bottomHeight)
            DD = ((self.width + self.width2) * self.columns, (self.width + self.width2) * self.columns, self.height * self.rows + self.roof_height + self.bottomHeight)
            
            
            aa = (self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            bb = (self.roof_rt, (self.width + self.width2) * self.columns- self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            cc = ((self.width + self.width2) * self.columns - self.roof_rt, self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
            dd = ((self.width + self.width2) * self.columns - self.roof_rt, (self.width + self.width2) * self.columns - self.roof_rt, self.height * self.rows + self.roof_height + self.bottomHeight)
        
    #        0 1 2 3 4 5 6 7 8  9  10 11 12 13 14 15
    verts = [A,B,C,D,a,b,c,d,AA,BB,CC,DD,aa,bb,cc,dd]

    
        
        
    # connecting into faces
    # outer sidefaces of the rim                   # top of rim                                                          # inside face of rim                               # floor face
    faces = [(1,0,8,9), (3,1,9,11), (2,3,11,10), (0,2,10,8), (9,8,12,13), (11,9,13,15), (10,11,15,14), (8,10,14,12),    (5,4,12,13), (7,5,13,15), (7,6,14,15), (6,4,12,14),  (4,6,7,5)   ]

    # creating the mesh  
    mesh = bpy.data.meshes.new(name="roof")
    
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material(self, "roof_material", self.wall_R, self.wall_G, self.wall_B, False))

    roof = object_data_add(context, mesh, operator=self)
    roof.parent = self.empty
        
    
## BaseBlock
def baseBlock(self, context):

    # a simple cube
    
    # A,B,C,D is baseplane, a,b,c,d is "extruded" up
    #
    #           C           D
    #          
    #       A           B
    #           c           d
    #
    #       a           b
    
    A = (0,0, self.bottomHeight)
    B = (self.width * self.columns, 0, self.bottomHeight)
    C = (0, self.width * self.columns, self.bottomHeight)
    D = (self.width * self.columns, self.width * self.columns, self.bottomHeight)
    
    a = (0, 0, 0)
    b = (self.width * self.columns, 0, 0)
    c = (0, self.width * self.columns, 0)
    d = (self.width * self.columns, self.width * self.columns, 0)

    #        0 1 2 3 4 5 6 7
    verts = [A,B,C,D,a,b,c,d]

    # connect the faces
    faces = [(1,0,4,5),(2,3,7,6),(0,2,6,4),(3,1,5,7)]
    # 
    mesh = bpy.data.meshes.new(name="base")
    
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material(self, "baseBlock_material", self.wall_R, self.wall_G, self.wall_B, False))
    
    base = object_data_add(context, mesh, operator=self)
    
    base.parent = self.empty
    base.location = self.lowerLeftCorner

def baseBlock_advanced(self, context):

    if(self.end_wind1 == True):
        if(self.adv_window_count == 3):
            A = (0,0, self.bottomHeight)
            B = ((self.width + self.width2 + self.width3) * self.columns + self.width, 0, self.bottomHeight)
            C = (0, (self.width + self.width2 + self.width3) * self.columns + self.width, self.bottomHeight)
            D = ((self.width + self.width2 + self.width3) * self.columns + self.width, (self.width + self.width2 + self.width3) * self.columns + self.width, self.bottomHeight)
            
            a = (0, 0, 0)
            b = ((self.width + self.width2 + self.width3) * self.columns + self.width, 0, 0)
            c = (0, (self.width + self.width2 + self.width3) * self.columns + self.width, 0)
            d = ((self.width + self.width2 + self.width3) * self.columns + self.width, (self.width + self.width2 + self.width3) * self.columns + self.width, 0)
        else:
            A = (0,0, self.bottomHeight)
            B = ((self.width + self.width2) * self.columns + self.width, 0, self.bottomHeight)
            C = (0, (self.width + self.width2) * self.columns + self.width, self.bottomHeight)
            D = ((self.width + self.width2) * self.columns + self.width, (self.width + self.width2) * self.columns + self.width, self.bottomHeight)
            
            a = (0, 0, 0)
            b = ((self.width + self.width2) * self.columns + self.width, 0, 0)
            c = (0, (self.width + self.width2) * self.columns + self.width, 0)
            d = ((self.width + self.width2) * self.columns + self.width, (self.width + self.width2) * self.columns + self.width, 0)
            
    else:    
        if(self.adv_window_count == 3):
            A = (0,0, self.bottomHeight)
            B = ((self.width + self.width2 + self.width3) * self.columns, 0, self.bottomHeight)
            C = (0, (self.width + self.width2 + self.width3) * self.columns, self.bottomHeight)
            D = ((self.width + self.width2 + self.width3) * self.columns, (self.width + self.width2 + self.width3) * self.columns, self.bottomHeight)
            
            a = (0, 0, 0)
            b = ((self.width + self.width2 + self.width3) * self.columns, 0, 0)
            c = (0, (self.width + self.width2 + self.width3) * self.columns, 0)
            d = ((self.width + self.width2 + self.width3) * self.columns, (self.width + self.width2 + self.width3) * self.columns, 0)
        else:
            A = (0,0, self.bottomHeight)
            B = ((self.width + self.width2) * self.columns, 0, self.bottomHeight)
            C = (0, (self.width + self.width2) * self.columns, self.bottomHeight)
            D = ((self.width + self.width2) * self.columns, (self.width + self.width2) * self.columns, self.bottomHeight)
            
            a = (0, 0, 0)
            b = ((self.width + self.width2) * self.columns, 0, 0)
            c = (0, (self.width + self.width2) * self.columns, 0)
            d = ((self.width + self.width2) * self.columns, (self.width + self.width2) * self.columns, 0)
    
    
        
    #        0 1 2 3 4 5 6 7
    verts = [A,B,C,D,a,b,c,d]
    

    # connect the faces
    faces = [(1,0,4,5),(2,3,7,6),(0,2,6,4),(3,1,5,7)]
    # 
    mesh = bpy.data.meshes.new(name="base")
    
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material(self, "baseBlock_material", self.wall_R, self.wall_G, self.wall_B, False))
    
    base = object_data_add(context, mesh, operator=self)
    
    base.parent = self.empty
    base.location = self.lowerLeftCorner
        
    
    

## HOUSE -----------------------------------------
def createHouse(self, context, lowerLeftCorner):
    self.corners = []    

    #                           3        2
    #
    #
    #
    #       base corner ------> 0        1
    #
    self.corners.append(self.lowerLeftCorner)
    
    cx = self.lowerLeftCorner[X] 
    cy = self.lowerLeftCorner[Y] 
    cz = self.lowerLeftCorner[Z]
    
    ## Creating the corners will depend on how many different windows there are and the width of them
    if(self.advanced == True):
        if(self.end_wind1 == True):
            if(self.adv_window_count == 3): 
                self.corners.append((cx + self.columns * (self.width + self.width2 + self.width3) + self.width, cy, cz ))
                self.corners.append((cx + self.columns * (self.width + self.width2 + self.width3) + self.width, cy + self.columns * (self.width + self.width2 + self.width3) + self.width, cz))
                self.corners.append((cx, cy + self.columns * (self.width + self.width2 + self.width3) + self.width, cz ))
            else:
                self.corners.append((cx + self.columns * (self.width + self.width2) + self.width, cy, cz ))
                self.corners.append((cx + self.columns * (self.width + self.width2) + self.width, cy + self.columns * (self.width + self.width2) + self.width, cz))
                self.corners.append((cx, cy + self.columns * (self.width + self.width2) + self.width, cz ))
        
        else:    
            if(self.adv_window_count == 3): 
                self.corners.append((cx + self.columns * (self.width + self.width2 + self.width3), cy, cz ))
                self.corners.append((cx + self.columns * (self.width + self.width2 + self.width3), cy + self.columns * (self.width + self.width2 + self.width3) , cz))
                self.corners.append((cx, cy + self.columns * (self.width + self.width2 + self.width3), cz ))
            else:
                self.corners.append((cx + self.columns * (self.width + self.width2), cy, cz ))
                self.corners.append((cx + self.columns * (self.width + self.width2), cy + self.columns * (self.width + self.width2) , cz))
                self.corners.append((cx, cy + self.columns * (self.width + self.width2), cz ))                

    else:    
        self.corners.append((cx + self.columns * self.width, cy, cz ))
        self.corners.append((cx + self.columns * self.width, cy + self.columns * self.width , cz))
        self.corners.append((cx, cy + self.columns * self.width, cz ))
    
    # note copy of object and using the same data will
    # not use the same modifier. it will create a new one
    # with the same name         ## Why did i write this !? setting the data will fix the problem
    a = self.window_Object.copy()
    a.data = self.window_Object.data
 
    b = self.window_Object.copy()
    b.data = self.window_Object.data        
    
    c = self.window_Object.copy()
    c.data = self.window_Object.data
    
         
    a.location = self.corners[1]
    a.rotation_euler = (0,0, pi / 2) # 90 degrees
    b.location = self.corners[2]
    b.rotation_euler = (0,0,pi) # 180 degrees
    c.location = self.corners[3]
    c.rotation_euler = (0,0, 3/2* pi) # 270 degrees
    
    self.windows = [self.window_Object, a,b,c]        
        
    context.collection.objects.link(a)
    context.collection.objects.link(b)
    context.collection.objects.link(c)

    # for the advanced mode
    
    if(self.advanced == True):
        a = self.window_Object2.copy()
        a.data = self.window_Object2.data
     
        b = self.window_Object2.copy()
        b.data = self.window_Object2.data       
        
        c = self.window_Object2.copy()
        c.data = self.window_Object2.data

        a.location = self.corners[1]
        a.rotation_euler = (0,0, pi / 2) # 90 degrees
        b.location = self.corners[2]
        b.rotation_euler = (0,0,pi) # 180 degrees
        c.location = self.corners[3]
        c.rotation_euler = (0,0, 3/2* pi) # 270 degrees

        context.collection.objects.link(a)
        context.collection.objects.link(b)
        context.collection.objects.link(c)
        
        if(self.adv_window_count == 3):
            a = self.window_Object3.copy()
            a.data = self.window_Object3.data
         
            b = self.window_Object3.copy()
            b.data = self.window_Object3.data       
            
            c = self.window_Object3.copy()
            c.data = self.window_Object3.data
                
            a.location = self.corners[1]
            a.rotation_euler = (0,0, pi / 2) # 90 degrees
            b.location = self.corners[2]
            b.rotation_euler = (0,0,pi) # 180 degrees
            c.location = self.corners[3]
            c.rotation_euler = (0,0, 3/2* pi) # 270 degrees
        
            context.collection.objects.link(a)
            context.collection.objects.link(b)
            context.collection.objects.link(c)       

    ## Adding the balconys    
    if(self.balcony == True):
        balcony(self, context)
        
        
        self.b_array_width = self.balcony_Object.modifiers.new(name='b_width', type='ARRAY')
        self.b_array_width.use_constant_offset = True
        self.b_array_width.use_relative_offset = False
        row_width = self.width * self.array_width.count
        
        # Setting the distance between the balconys
        self.b_array_width.constant_offset_displace = (self.b_distance, 0 ,0)
        
            
            
        self.b_array_height = self.balcony_Object.modifiers.new(name='b_height', type='ARRAY')
        self.b_array_height.use_constant_offset = True
        self.b_array_height.use_relative_offset = False
        self.b_array_height.constant_offset_displace = (0,0, self.height)
        
        self.b_array_width.count = self.b_frequence
        self.b_array_height.count = self.rows
    
    
        # Same as for the walls
        b_a = self.balcony_Object.copy()
        b_a.data = self.balcony_Object.data
     
        b_b = self.balcony_Object.copy()
        b_b.data = self.balcony_Object.data        
        
        b_c = self.balcony_Object.copy()
        b_c.data = self.balcony_Object.data
        
        b_a.location = self.corners[1]
        b_a.rotation_euler = (0,0, pi / 2) # 90 degrees
        b_b.location = self.corners[2]
        b_b.rotation_euler = (0,0,pi) # 180 degrees
        b_c.location = self.corners[3]
        b_c.rotation_euler = (0,0, 3/2* pi) # 270 degrees
        
        context.collection.objects.link(b_a)
        context.collection.objects.link(b_b)
        context.collection.objects.link(b_c)
        
    return 1



def house(self, context, lowerLeftCorner):
    
    if(self.advanced == False):
       bpy.ops.object.empty_add(type='PLAIN_AXES', location=(self.emptyLocation), radius=self.width * self.columns)
     
    else:
        if(self.adv_window_count == 2):
            if(self.end_wind1 == True):
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=(self.emptyLocation), radius=self.width * (self.columns + 1)+ self.width2 * self.columns)
            else:
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=(self.emptyLocation), radius=self.width * self.columns + self.width2 * self.columns)
        else: # wind_count == 3
            if(self.end_wind1 == True):
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=(self.emptyLocation), radius=self.width * (self.columns + 1)+ self.width2 * self.columns + self.width3 * self.columns)
            else:
                bpy.ops.object.empty_add(type='PLAIN_AXES', location=(self.emptyLocation), radius=self.width * self.columns + self.width2 * self.columns + self.width3 * self.columns)
    self.empty = bpy.context.selected_objects[0]
    self.empty.name = "CITY_GEN_EMPTY"
    
    if(self.advanced == True):
        wall_advanced(self, context, lowerLeftCorner)
        createHouse(self, context, self.lowerLeftCorner)   
        roof_advanced(self, context)
        baseBlock_advanced(self, context)
    else:  
        wall(self, context, lowerLeftCorner)
        createHouse(self, context, self.lowerLeftCorner)   
        roof(self, context)
        baseBlock(self, context)

        
    
      
    
    

def set_preset(self, context):
    
    if(self.preset == '1'):
            
        self.preset = " "
        self.advanced = True
        self.adv_window_count = 2
        self.end_wind1 = True
        
        self.height = 3
        self.width = 3
        self.top = 0.76
        self.bottom = 0.76
        self.side = 0.34
        self.depth = 0.1
        
        self.add_hor = False
        self.add_ver = True
        self.v_thickness = 0.1
        self.v_offset = 0
        
        self.width2 = 3
        self.top2 = 0.31
        self.bottom2 = 0.1
        self.side2 = 0.97
        self.depth2 = 0.1
        
        self.add_hor2 = False
        self.add_ver2 = False
        
        self.rows = 13
        self.columnns = 2
        self.bottomHeight = 3
        self.roof_height = 0.7
        self.roof_rt = 0.2
        
        self.balcony = True
        self.b_look = False
        self.b_width = 2.56
        self.b_height = 0.94
        self.b_depth = 1.46
        self.b_thickness = 0.04
        self.b_frequence = 2
        self.b_distance = 6.0
        self.b_offset = 3.0
        
        self.wall_mat = 'brick'
        self.wall_unique = True
        self.brick_scale = 5
        self.wall_R = 0.07
        self.wall_G = 0.03
        self.wall_B = 0
        self.wall_R2 = 0.33
        self.wall_G2 = 0.15
        self.wall_B2 = 0


    elif(self.preset == '2'):

        self.preset = " "
        self.advanced = True
        self.adv_window_count = 2
        self.end_wind1 = True
        
        self.height = 3
        self.width = 2.61
        self.top = 0.76
        self.bottom = 0.76
        self.side = 0.34
        self.depth = 0.1
        
        self.add_hor = True
        self.h_thickness = 0.04
        self.h_offset = 0.1
        self.add_ver = True
        self.v_thickness = 0.4
        self.v_offset = 0
        
        self.width2 = 3
        self.top2 = 0.67
        self.bottom2 = 1.36
        self.side2 = 0.97
        self.depth2 = 0.1
        
        self.add_hor2 = False
        self.add_ver2 = False
        
        self.rows = 7
        self.columnns = 3
        self.bottomHeight = 1.8
        self.roof_height = 0.7
        self.roof_rt = 0.2
        
        self.balcony = False
        
        self.wall_mat = 'color'
        self.wall_unique = True
        self.wall_R = 0.16
        self.wall_G = 0.09
        self.wall_B = 0.03
      
    elif(self.preset == '3'):
        
        self.preset = " "
        self.advanced = True
        self.adv_window_count = 3
        self.end_wind1 = True
        
        self.height = 3
        self.width = 2.61
        self.top = 0.07
        self.bottom = 0.64
        self.side = 0.34
        self.depth = 0.1
        
        self.add_hor = False
        self.add_ver = False
        
        self.width2 = 3
        self.top2 = 0.43
        self.bottom2 = 1.69
        self.side2 = 0.97
        self.depth2 = 0.1
        
        self.add_hor2 = False
        self.add_ver2 = False
        
        self.width3 = 3
        self.top3 = 0.1
        self.bottom3 = 0.61
        self.side3 = 0.1
        self.depth3 = 0.1
        
        self.add_hor3 = False
        self.add_ver3 = False
        
        self.rows = 12
        self.columnns = 2
        self.bottomHeight = 2.8
        self.roof_height = 0.7
        self.roof_rt = 0.2
        
        self.balcony = False
        
        self.wall_mat = 'color'
        self.wall_unique = True
        self.brick_scale = 5
        self.wall_R = 0.16
        self.wall_G = 0.15
        self.wall_B = 0.12
        
        
    elif(self.preset == '4'):
        
        self.preset = " "
        self.advanced = False

        
        self.height = 2.04
        self.width = 4.2
        self.top = 0.46
        self.bottom = 0.25
        self.side = 0.1
        self.depth = 0.1
        
        self.add_hor = False
        self.add_ver = True
        self.v_thickness = 0.19
        self.v_offset = 0.60
        
        
        self.rows = 22
        self.columnns = 3
        
        self.bottomHeight = 3.46
        self.roof_height = 0.2
        self.roof_rt = 0.2
        
        self.balcony = False
        
        self.wall_mat = 'brick'
        self.wall_unique = True
        self.brick_scale = 0.12
        self.wall_R = 0.28
        self.wall_G = 0.45
        self.wall_B = 0.72
        self.wall_R2 = 0.21
        self.wall_G2 = 0.51
        self.wall_B2 = 0.90
        
    elif(self.preset == '5'):
        
        self.preset = " "
        self.advanced = True
        self.adv_window_count = 2
        self.end_wind1 = True
        
        self.height = 3.03
        self.width = 4.2
        self.top = 0.46
        self.bottom = 0.25
        self.side = 0.1
        self.depth = 0.1
        
        self.add_hor = True
        self.h_thickness = 0.1
        self.h_offset = -0.72
        self.add_ver = True
        self.v_thickness = 0.13
        self.v_offset = 0.60
        
        self.width2 = 2.22
        self.top2 = 0.25
        self.bottom2 = 0.1
        self.side2 = 0.61
        self.depth2 = 0.1
        
        self.add_hor2 = False
        self.add_ver2 = False
        
        self.rows = 19
        self.columnns = 2
        self.bottomHeight = 3.46
        self.roof_height = 0.4
        self.roof_rt = 0.2
        
        self.balcony = True
        self.b_look = True
        self.b_width = 1.84
        self.b_height = 1
        self.b_depth = 1
        self.b_thickness = 0.1
        self.b_frequence = 2
        self.b_distance = 6.32
        self.b_offset = 3.18
        
        self.wall_mat = 'brick'
        self.wall_unique = True
        self.brick_scale = 0.03
        self.wall_R = 0.40
        self.wall_G = 0.45
        self.wall_B = 0.54
        self.wall_R2 = 1.0
        self.wall_G2 = 0.78
        self.wall_B2 = 0.0
        
    ## Presets Done :) 


## Addon UI    

class OBJECT_OT_add_object_house(Operator, AddObjectHelper):
    """Create a new House Object"""
    bl_idname = "mesh.house_generator"
    bl_label = "House"
    bl_description = "Generate a House"
    bl_options = {'REGISTER', 'UNDO'}

    wall = NULL
    corners = NULL
    windows = NULL
    
    lowerLeftCorner = NULL
    
    array_width = NULL
    array_height = NULL
    # for the advanced settings, the other 2 window will have separate arrays
    array_width2 = NULL
    array_height2 = NULL
    array_width3 = NULL
    array_height3 = NULL
    
    b_array_width = NULL
    b_array_height = NULL

    window_Object = NULL
    window_Object2 = NULL
    window_Object3 = NULL

    balcony_Object = NULL
    
    empty = NULL
    emptyLocation = NULL

    height :    FloatProperty(name='Height',             min=1,max= 500, default= 3, description='window height')
    width  :    FloatProperty(name='Width',              min=1,max= 100, default= 3, description='window width')
    top    :    FloatProperty(name='Top Space',          min=0.01,max=100, default= 0.1, description='top space')
    bottom :    FloatProperty(name='Bottom Space',       min=0.01,max=100, default= 0.1, description='bottom space')
    side   :    FloatProperty(name='Side Space',         min=0.01,max=100, default= 0.1, description='side space')
    depth  :    FloatProperty(name='Depth',              min=0.01,max=200, default= 0.1, description='window depth')

    add_hor:    BoolProperty(name='Add Horizontal Rim',     default=False, description='Add a Horizontal Rim in the Window')
    add_ver:    BoolProperty(name='Add Vertical Rim',       default=False, description='Add a Vertical Rim in the Window')
    h_thickness:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Horizontal Rim')
    v_thickness:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Vertical Rim')
    h_offset   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Horizontal Rim')
    v_offset   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Vertical Rim')
    
    rows    :   IntProperty(name='Floors',               min=1, max=10000, default= 14, description='Number of Floors')
    columns :   IntProperty(name='Columns',              min=1, max=10000, default= 2, description='Window Columns')

    bottomHeight : FloatProperty(name='Bottom Height',   min=0.01, max=100, default=4, description='Height of the Base')
    
    roof_height : FloatProperty(name='Roof rim Height',     min=0.01, max=100, default=0.2, description='Height of Roof rim')
    roof_rt     : FloatProperty(name='Roof rim Thickness',  min=0.01, max=100, default=0.2, description='Thickness of the Roof rim')
    
    balcony     :    BoolProperty(name='Add balcony',               default=False, description='Add a balcony')
    b_width     :    FloatProperty(name='Balcony width',            min=0.1,max= 500, default= 1, description='Balcony width')
    b_height    :    FloatProperty(name='Balcony height',           min=0.1,max= 100, default= 1, description='Balcony height')
    b_depth     :    FloatProperty(name='Balcony depth',            min=0.01,max=100, default= 1, description='Balcony depth')    
    b_thickness :    FloatProperty(name='Balcony thickness',        min=0.01,max= 100, default= 0.1, description='Balcony thickness')
    b_frequence :    IntProperty(name='Balcony Frequence',          min=1, max=1000, default= 2, description='Amount of balconys per floor')
    b_distance  :    FloatProperty(name='Distance between Balconys',min=0.0, max=1000, default= 2, description='Distance Between the balconys')
    b_offset    :    FloatProperty(name='Offset',min=-1000, max=1000, default= 0, description='Offset for the balcony')
    b_look      :    BoolProperty(name='Add Hole in rim',                               default=False, description='Add a hole in the rim')
    
    
    advanced    :    BoolProperty(name='Advanced mode', default=False, description='Advanced Settings')
    ## for advanced mode
    adv_window_count :   IntProperty(name='2-3 Different windows', min=2, max=3, default= 2, description='How many different windows')
    end_wind1  :     BoolProperty(name='end with window 1', default=False, description='End the wall with the first window')

    width2  :    FloatProperty(name='Width',              min=1,max= 100, default= 3, description='window width')
    top2    :    FloatProperty(name='Top Space',          min=0.01,max=100, default= 0.1, description='top space')
    bottom2 :    FloatProperty(name='Bottom Space',       min=0.01,max=100, default= 0.1, description='bottom space')
    side2   :    FloatProperty(name='Side Space',         min=0.01,max=100, default= 0.1, description='side space')
    depth2  :    FloatProperty(name='Depth',              min=0.01,max=200, default= 0.1, description='window depth')

    add_hor2:   BoolProperty(name='Add Horizontal Rim',     default=False, description='Add a Horizontal Rim in the Window')
    add_ver2:   BoolProperty(name='Add Vertical Rim',       default=False, description='Add a Vertical Rim in the Window')
    h_thickness2:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Horizontal Rim')
    v_thickness2:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Vertical Rim')
    h_offset2   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Horizontal Rim')
    v_offset2   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Vertical Rim')
    
    width3  :    FloatProperty(name='Width',              min=1,max= 100, default= 3, description='window width')
    top3    :    FloatProperty(name='Top Space',          min=0.01,max=100, default= 0.1, description='top space')
    bottom3 :    FloatProperty(name='Bottom Space',       min=0.01,max=100, default= 0.1, description='bottom space')
    side3   :    FloatProperty(name='Side Space',         min=0.01,max=100, default= 0.1, description='side space')
    depth3  :    FloatProperty(name='Depth',              min=0.01,max=200, default= 0.1, description='window depth')
    
    add_hor3:   BoolProperty(name='Add Horizontal Rim',     default=False, description='Add a Horizontal Rim in the Window')
    add_ver3:   BoolProperty(name='Add Vertical Rim',       default=False, description='Add a Vertical Rim in the Window')
    h_thickness3:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Horizontal Rim')
    v_thickness3:FloatProperty(name='thickness',   min=0.01, max=100, default=0.1, description='Thickness of the Vertical Rim')
    h_offset3   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Horizontal Rim')
    v_offset3   :FloatProperty(name='Offset',   min=-100, max=100, default=0, description='Offset for the Vertical Rim')

    
    wall_mat    : EnumProperty(items =(('brick',"brick",""),('color',"color","")),name="Wall Material",default='brick') 
    
    wall_unique : BoolProperty(name='Use only on this', default=False, description='Creates a new Material and uses only on this House')
    
    brick_scale : FloatProperty(name='Brick Scale',   min=0, max=1000, default=5, description='Brick Scale')
    # colors in RGB
    wall_R : FloatProperty(name='Red',   min=0, max=1, default=0.07, description='Color')
    wall_G : FloatProperty(name='Green',   min=0, max=1, default=0.03, description='Color')
    wall_B : FloatProperty(name='Blue',   min=0, max=1, default=0, description='Color')
    
    wall_R2 : FloatProperty(name='Red2',   min=0, max=1, default=0.33, description='Color')
    wall_G2 : FloatProperty(name='Green2',   min=0, max=1, default=0.15, description='Color')
    wall_B2 : FloatProperty(name='Blue2',   min=0, max=1, default=0, description='Color')
    

    preset  :   EnumProperty(items =((' '," ",""),('1',"1",""),('2',"2",""),('3',"3",""),('4',"4",""),('5',"5","")),name="Preset",default=' ')
    
    
    
    
    
    def draw(self, context):
        layout = self.layout
        
        ## Alot of code for setting presets
        row = layout.row()
        row.prop(self, 'preset')
        
        row = layout.row()
        row.label(text="Use different windows") 
        box = layout.box()
        box.prop(self, 'advanced')
        if(self.advanced == True):
            box.prop(self, 'adv_window_count')
            box.prop(self, 'end_wind1')

        row = layout.row()
        row.label(text="Window 1")
        box = layout.box()
        box.prop(self, 'height')
        box.prop(self, 'width')
        box.prop(self, 'top')
        box.prop(self, 'bottom')
        box.prop(self, 'side')
        box.prop(self, 'depth')

        box.prop(self, 'add_hor')
        if(self.add_hor == True):
            box.prop(self, 'h_thickness')
            box.prop(self, 'h_offset')
            
        box.prop(self, 'add_ver')
        if(self.add_ver == True):
            box.prop(self, 'v_thickness')
            box.prop(self, 'v_offset')
            
    
        if(self.advanced == True):
            if(self.adv_window_count == 2):
                row = layout.row()
                row.label(text="Window 2")
                box = layout.box()  
                box.prop(self, 'width2')
                box.prop(self, 'top2')
                box.prop(self, 'bottom2')
                box.prop(self, 'side2')
                box.prop(self, 'depth2')

                box.prop(self, 'add_hor2')
                if(self.add_hor2 == True):
                    box.prop(self, 'h_thickness2')
                    box.prop(self, 'h_offset2')
                    
                box.prop(self, 'add_ver2')
                if(self.add_ver2 == True):
                    box.prop(self, 'v_thickness2')
                    box.prop(self, 'v_offset2')
            else:
                row = layout.row()
                row.label(text="Window 2")
                box = layout.box()
                box.prop(self, 'width2')
                box.prop(self, 'top2')
                box.prop(self, 'bottom2')
                box.prop(self, 'side2')
                box.prop(self, 'depth2')
                box.prop(self, 'add_hor2')
                if(self.add_hor2 == True):
                    box.prop(self, 'h_thickness2')
                    box.prop(self, 'h_offset2')
                    
                box.prop(self, 'add_ver2')
                if(self.add_ver2 == True):
                    box.prop(self, 'v_thickness2')
                    box.prop(self, 'v_offset2')  
                  
                row = layout.row()
                row.label(text="Window 3")
                box = layout.box()
                box.prop(self, 'width3')
                box.prop(self, 'top3')
                box.prop(self, 'bottom3')
                box.prop(self, 'side3')
                box.prop(self, 'depth3')
                box.prop(self, 'add_hor3')
                if(self.add_hor3 == True):
                    box.prop(self, 'h_thickness3')
                    box.prop(self, 'h_offset3')
                    
                box.prop(self, 'add_ver3')
                if(self.add_ver3 == True):
                    box.prop(self, 'v_thickness3')
                    box.prop(self, 'v_offset3')
                
        row = layout.row()
        row.label(text="Floors and columnns")
        box = layout.box()
        box.prop(self, 'rows')
        box.prop(self, 'columns')
        
        row = layout.row()
        row.label(text="Bottom block")
        box = layout.box()
        box.prop(self, 'bottomHeight')
        
        row = layout.row()
        row.label(text="Roof")
        box = layout.box()
        box.prop(self, 'roof_height')
        box.prop(self, 'roof_rt')
        
        row = layout.row()
        row.label(text="Balcony")
        box = layout.box()
        box.prop(self, 'balcony')

        if(self.balcony == True):
            box.prop(self, 'b_look')
            box.prop(self, 'b_width')
            box.prop(self, 'b_height')
            box.prop(self, 'b_depth')
            box.prop(self, 'b_thickness')
            box.prop(self, 'b_frequence')
            box.prop(self, 'b_distance')
            box.prop(self, 'b_offset')

        row = layout.row()
        row.label(text="Wall material")
        box = layout.box()
        box.prop(self, 'wall_mat')
        box.prop(self, 'wall_unique')
        box.prop(self, 'wall_R')
        box.prop(self, 'wall_G')
        box.prop(self, 'wall_B')
        if(self.wall_mat == "brick"):
            box.prop(self, 'wall_R2')
            box.prop(self, 'wall_G2')
            box.prop(self, 'wall_B2')
            box.prop(self, 'brick_scale')
                
    def execute(self, context):
        if(self.preset is not ' '):
            set_preset(self, context)
        
        bpy.context.scene.cursor.location = (0,0,0)
        self.lowerLeftCorner = bpy.context.scene.cursor.location
        self.emptyLocation = bpy.context.scene.cursor.location 
        house(self, context, self.lowerLeftCorner)
        
        
        
    
        
        return {'FINISHED'}










def material_city(self, name, R, G, B, spec):
    if name not in bpy.data.materials:
        
        mat=bpy.data.materials.new(name)
        mat.diffuse_color     = ([R,G,B, 1])
        
        if(name == "road_mat"):
            mat.use_nodes = True
            
            # adding three Nodes
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            tex = mat.node_tree.nodes.new(type="ShaderNodeTexNoise")
            tex.inputs[1].default_value = 100000000
            
            bump = mat.node_tree.nodes.new('ShaderNodeBump')
            bump.inputs[0].default_value = 0.8
            bump.inputs[1].default_value = 0.2
            
            # Connecting the nodes
            mat.node_tree.links.new(bsdf.inputs['Normal'], bump.outputs['Normal'])
            mat.node_tree.links.new(bump.inputs['Height'], tex.outputs['Fac'])
            

        if(name == "car_mat"):
            mat.use_nodes = True

            # create and connect colorramp to bsdf
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            ramp = mat.node_tree.nodes.new(type="ShaderNodeValToRGB")
            mat.node_tree.links.new(bsdf.inputs[0], ramp.outputs[0])

            # create the random obj into node
            obj_rand = mat.node_tree.nodes.new(type="ShaderNodeObjectInfo")
            mat.node_tree.links.new(ramp.inputs[0], obj_rand.outputs[3])

            ramp.color_ramp.elements[0].color = (0, 0, 1, 1)
            ramp.color_ramp.elements[1].color = (0, 1, 0, 1)

            
        if(spec == True):
            mat.specular_intensity = 1
            mat.roughness = 0

    else:
        mat=bpy.data.materials[name]

    return mat




#
#   Function that sorts a list of object based on the scale
#       Running in O(n^2), needs to be fixed
#       No it don't need to be fixed since it is not used :)
#
def sort(array):
    l = len(array)
    
    for i in range(l):
        for j in range(0, l-i-1):
            
            if(array[j].empty_display_size > array[j+1].empty_display_size):
                array[j], array[j+1] = array[j+1], array[j]
            


def car(self, context):

    # ABCDEFGH is the base and abcdefgh is extruded up
    #
    #
    #
    #     e  f        g  h
    #     E  F        G  H
    #   a  b        c  d
    #   A  B        C  D
    #
    length = self.car_size
    width = self.car_size / 3

    A = (-1 * width / 2, length / 2, 0)
    B = (-1 * width / 2, length / 4, 0)
    C = (-1 * width / 2, -1 * length / 4, 0)

    D = (-1 * width / 2, -1 * length / 2, 0)

    E = (width / 2, length / 2, 0)
    F = (width / 2, length / 4, 0)
    G = (width / 2, -1 * length / 4, 0)
    H = (width / 2, -1 * length / 2, 0)

    a = (A[X], A[Y], width / 2)
    b = (B[X], B[Y], width / 2)
    c = (C[X], C[Y], width / 2)
    d = (D[X], D[Y], width / 2)
    e = (E[X], E[Y], width / 2)
    f = (F[X], F[Y], width / 2)
    g = (G[X], G[Y], width / 2)
    h = (H[X], H[Y], width / 2)
  

    # Roof will be opqr connected with b,c,f,g
    o =(b[X], b[Y], width)
    p =(c[X], c[Y], width)
    q =(f[X], f[Y], width)
    r =(g[X], g[Y], width)

    ## index:0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19
    verts = [A,B,C,D,E,F,G,H,a,b,c, d, e, f, g, h, o, p, q, r]
    ## connecting faces                                                                             BOTTOM FIN       TOP FACES                   oprq
    faces = [(0,1,9,8), (1,2,10,9), (2,3,11,10), (3,7,15,11), (7,6,14,15), (6,5,13,14), (5,4,12,13), (4,0,8,12),    (13,12,8,9), (15,14,10,11), (16,17,19,18),      (9,10,17
    ,16), (10,14,19,17), (14,13,18,19), (13,9,16,18)] 
    
    mesh = bpy.data.meshes.new(name="city_car")
    mesh.from_pydata(verts, [], faces)

    mesh.materials.append(material_city(self, "car_mat", 0, 0, 0, False))
    mesh.materials.append(material_city(self, "car_window", 0, 0, 0, True))

    # set car windows
    mesh.polygons[12].material_index = 1
    mesh.polygons[14].material_index = 1
    

    self.car_object = object_data_add(context, mesh, operator=self)

    self.car_object.hide_set(True)



def place_cars(self, context, empty, entrance_space):
    
    car1 = self.car_object.copy()
    car1.data = self.car_object.data
    car2 = self.car_object.copy()
    car2.data = self.car_object.data
    car3 = self.car_object.copy()
    car3.data = self.car_object.data
    car4 = self.car_object.copy()
    car4.data = self.car_object.data
    
    
    #   Cars will be placed like this, and then rotated
    #  
    #     2    1    o <------ empty at house corner
    #               
    #               3 
    #       
    #               4        

    car1.location = (empty.location[X] - self.pavement_w - (self.road_width / 4), empty.location[Y], empty.location[Z] - self.pavement_h)
    car2.location = (empty.location[X] - self.pavement_w - (3 * self.road_width / 4), empty.location[Y], empty.location[Z] - self.pavement_h)
    
    car3.location = (empty.location[X], empty.location[Y] - self.pavement_w - (self.road_width / 4), empty.location[Z] - self.pavement_h)
    car4.location = (empty.location[X], empty.location[Y] - self.pavement_w - (3 * self.road_width / 4), empty.location[Z] - self.pavement_h)

    car2.rotation_euler = (0,0, pi)
    car3.rotation_euler = (0,0, pi / 2)
    car4.rotation_euler = (0,0, -1 * pi / 2)

    context.collection.objects.link(car1)
    context.collection.objects.link(car2)
    context.collection.objects.link(car3)
    context.collection.objects.link(car4)
    
    ## The code will duplicate the cars, and each car will be its own
    # object, therefore the random material trick will work
    next = self.car_dist
    while (next < empty.empty_display_size + entrance_space):
        
        
        c1 = car1.copy()
        c1.data = car1.data
        c1.location = (car1.location[X], car1.location[Y] + next, car1.location[Z])
                    
        c2 = car2.copy()
        c2.data = car2.data
        c2.location = (car2.location[X], car2.location[Y] + next, car2.location[Z])
        
        context.collection.objects.link(c1)
        context.collection.objects.link(c2)
        
        if(next < empty.empty_display_size): # car 3 and 4 will not be effected by the entrance space   
            c3 = car3.copy()
            c3.data = car3.data
            c3.location = (car3.location[X] + next, car3.location[Y], car3.location[Z])
            
            c4 = car4.copy()
            c4.data = car4.data
            c4.location = (car4.location[X] + next, car4.location[Y], car4.location[Z])
        
            context.collection.objects.link(c3)
            context.collection.objects.link(c4)
        
        next += self.car_dist
    

def streetLamp(self, context):
    
    # Origin will be at center of 8 base verts
    base_verts = []
    base_verts_extruded = []
    base_verts_extruded_extruded_in = []
    top_verts = []
  
    lamp_edge_verts = []    
    
    faces = []
    verts = []
    
    scale_thick = 0.1 * self.lamp_size
    scale_thin = 0.06 * self.lamp_size
    mid_height = 3 * self.lamp_size
    top_height = 10 * self.lamp_size
    
    angle = 0
    
    # Generates Circles
    for i in range(0, 8):
        base_verts.append((cos(angle) * scale_thick, sin(angle) * scale_thick, 0))
        base_verts_extruded.append((cos(angle) * scale_thick, sin(angle) * scale_thick, mid_height))
        base_verts_extruded_extruded_in.append((cos(angle) * scale_thin, sin(angle) * scale_thin, mid_height))
        top_verts.append((cos(angle) * scale_thin, sin(angle) * scale_thin, top_height))

        lamp_edge_verts.append((cos(angle) * scale_thin * 4, sin(angle) * scale_thin * 6, top_height + 0.4))
         
        angle += pi / 4
        
    #       0            8                     16                                24          32 
    verts = base_verts + base_verts_extruded + base_verts_extruded_extruded_in + top_verts + lamp_edge_verts
    
    
    # Connect the faces
    for i in range(0, 8):
        # % 8 will make that when i == 7 it will connect to vert[0] since 8 % 8 = 0
        i1 = (i+1) % 8
        
        faces.append((i, i1, i1 + 8, i + 8))
        faces.append((i + 8, i1 + 8, i1 + 16, i + 16))
        faces.append((i + 16, i1 + 16, i1 + 24, i + 24))
        
        faces.append((i + 24, i1 + 24, i1 + 32, i + 32))    
    
    
    # adding the mesh
    mesh = bpy.data.meshes.new(name="street_lamp")
    mesh.from_pydata(verts, [], faces)

    self.lamp_object = object_data_add(context, mesh, operator=self)

    self.lamp_object.hide_set(True)
    


def place_lamps(self, context, empty, entrance_space):
    
    l1 = self.lamp_object.copy()
    l1.data = self.lamp_object.data
    l2 = self.lamp_object.copy()
    l2.data = self.lamp_object.data
    l3 = self.lamp_object.copy()
    l3.data = self.lamp_object.data
    l4 = self.lamp_object.copy()
    l4.data = self.lamp_object.data

    l1.location = (empty.location[X] - self.pavement_w / 2, empty.location[Y], empty.location[Z])
    
    l2.location = (empty.location[X], empty.location[Y] + empty.empty_display_size + entrance_space - self.pavement_w / 2, empty.location[Z])
    
    l3.location = (l1.location[X] - self.road_width - self.pavement_w , empty.location[Y], empty.location[Z])
    
    l4.location = (empty.location[X] + empty.empty_display_size, empty.location[Y] - self.pavement_w / 2, empty.location[Z])


    l2.rotation_euler = (0,0, -1 * pi / 2)
    l3.rotation_euler = (0,0, pi)
    l4.rotation_euler = (0,0, pi / 2)
    
    
    l1_array = l1.modifiers.new(name='modf', type='ARRAY')
    l2_array = l2.modifiers.new(name='modf', type='ARRAY')
    l3_array = l3.modifiers.new(name='modf', type='ARRAY')
    l4_array = l4.modifiers.new(name='modf', type='ARRAY')
    
    l1_array.use_constant_offset = True
    l1_array.use_relative_offset = False
    l2_array.use_constant_offset = True
    l2_array.use_relative_offset = False
    l3_array.use_constant_offset = True
    l3_array.use_relative_offset = False
    l4_array.use_constant_offset = True
    l4_array.use_relative_offset = False
    
    l1_array.count = floor(empty.empty_display_size / self.lamp_distance)
    l1_array.constant_offset_displace = (0, self.lamp_distance, 0) 
    
    l2_array.count = floor(empty.empty_display_size / self.lamp_distance)
    l2_array.constant_offset_displace = (0, self.lamp_distance, 0) 
    
    l3_array.count = floor(empty.empty_display_size / self.lamp_distance)
    l3_array.constant_offset_displace = (0, -1 * self.lamp_distance, 0) 
    
    l4_array.count = floor(empty.empty_display_size / self.lamp_distance)
    l4_array.constant_offset_displace = (0, self.lamp_distance, 0) 
    
    context.collection.objects.link(l1)
    context.collection.objects.link(l2)
    context.collection.objects.link(l3)
    context.collection.objects.link(l4)
    
    
    
    
    
    
    
def addRoad(self, context, empty, entrance_space):
    
    #                   PAVEMENT
    #
    #           J   K                L
    #                  EntranceArea
    #           E   C()              D()
    #          
    #
    #
    #
    #                   
    #                 () < -----------()------- House corner
    #           F   A                B
    #          
    #           G   H                I
    #          
    #
    
    A = (0,0,0)
    B = (empty.empty_display_size, 0, 0)
    C = (0, empty.empty_display_size, 0)
    D = (empty.empty_display_size, empty.empty_display_size, 0)
    
    E = (C[X] - self.pavement_w, C[Y], 0)
    F = (A[X] - self.pavement_w, A[Y], 0)
    G = (A[X] - self.pavement_w, A[Y] - self.pavement_w, 0)
    H = (A[X], A[Y] - self.pavement_w, 0)
    I = (B[X], B[Y] - self.pavement_w, 0)
    
    J = (E[X], E[Y] + entrance_space, 0)
    K = (C[X], J[Y], 0)
    L = (D[X], J[Y], 0)
    
    

    #   K,L,J, E,F,G,H,I will be extruded down named k,l,j,e,f,g,h,i
    #   and will be used to connect the road and the vertical cut of the pavement
    
    #            ROAD
    #
    #  m     j   k               l
    #
    #  n     e
    #
    #
    #
    #
    #  o     f
    #
    #  p     g   h               i
    #
    #
    #  q     r   s               t       
    #

    e = (E[X], E[Y], self.pavement_h * -1)
    f = (F[X], F[Y], self.pavement_h * -1)
    g = (G[X], G[Y], self.pavement_h * -1)
    h = (H[X], H[Y], self.pavement_h * -1)
    i = (I[X], I[Y], self.pavement_h * -1)
    j = (J[X], J[Y], self.pavement_h * -1)
    k = (K[X], K[Y], self.pavement_h * -1)
    l = (L[X], L[Y], self.pavement_h * -1)
    
    m = (j[X] - self.road_width, j[Y], self.pavement_h * -1)
    n = (j[X] - self.road_width, e[Y], self.pavement_h * -1)
    o = (j[X] - self.road_width, f[Y], self.pavement_h * -1)
    p = (j[X] - self.road_width, g[Y], self.pavement_h * -1)
    q = (j[X] - self.road_width, g[Y] - self.road_width, self.pavement_h * -1)
    
    r = (g[X], q[Y], self.pavement_h * -1)
    s = (h[X], q[Y], self.pavement_h * -1)
    t = (i[X], q[Y], self.pavement_h * -1)
    
    # Then extruding up m,n,o,p to M,N,O,P to create the pavement on the opposite side
    
    #       Left opposite pavement
    #
    #      W      M
    #
    #      U      N
    #
    #                               
    #               
    #      T      O
    #
    #
    #      V      P  
    
    M = (m[X], m[Y], 0)
    N = (n[X], n[Y], 0)
    O = (o[X], o[Y], 0)
    P = (p[X], p[Y], 0)
    
    W = (M[X] - self.pavement_w, M[Y], 0)
    U = (N[X] - self.pavement_w, N[Y], 0)
    T = (O[X] - self.pavement_w, O[Y], 0)
    V = (P[X] - self.pavement_w, P[Y], 0)
    
    # To fill the last gaps extrude down V,W and create one new called vr to extend the last road piece
    
    v  = (V[X], V[Y], self.pavement_h * -1)
    w  = (W[X], W[Y], self.pavement_h * -1)
    vr = (V[X], V[Y] - self.road_width, self.pavement_h * -1)
    
    # index  0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38
    verts = [A,B,C,D,E,F,G,H,I,J,K, L, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, M, N, O, P, W, U, T, V, v, w, vr]
    
    
    
    #       Pavement and entrace area                                  Extruding down                                                                  The Road                                                                                                Extrude up left Pavement                      Left Pavement                               Last gaps
    faces = [(1,0,7,8), (0,5,6,7), (0,2,4,5), (2,10,9,4), (2,3,11,10), (10,11,19,18), (4,9,17,12), (5,4,12,13), (6,5,13,14), (7,6,14,15), (8,7,15,16), (12,17,20,21), (12,21,22,13), (14,13,22,23),(14,23,24,25), (15,14,25,26), (16,15,26,27), (24,23,36,38), (21,20,28,29), (22,21,29,30), (23,22,30,31), (29,28,32,33), (30,29,33,34), (30,34,35,31), (31,35,36,23),(32,28,20,37), (9,10,18,17)]
    
    
    # adding the mesh
    mesh = bpy.data.meshes.new(name="road_corner")
    mesh.from_pydata(verts, [], faces)
    
    # Material
    mesh.materials.append(material_city(self, "road_mat", 0.018, 0.018, 0.018, False))
    mesh.materials.append(material_city(self, "pavement_mat", 0.49, 0.49, 0.49, False))
    
    i = 0
    while(i < len(faces)):
        
        if(i > 10 and i < 18): #Road
            mesh.polygons[i].material_index = 0
        else: # Pavement
            mesh.polygons[i].material_index = 1
            
        i += 1
    
    object = object_data_add(context, mesh, operator=self)
    object.parent = empty
    
    if(self.street_lamp == True):
        place_lamps(self, context, empty, entrance_space)
    
    if(self.use_cars == True):
        place_cars(self, context, empty, entrance_space)


def layout(self, context):

    # Keep track of current x position 
    pos_x = 0
    pos_y = 0
    
    # boolean to check if it is the first row or not
    #first_row = True

    width_counter = 0
    largest_size = 0
    
    # For laying out in a square the number
    # of houses columns * rows = Total amount of houses
    # variable wc will be square root of amount of houses rounded up
    wc = sqrt(len(self.house_emptys))
    if((wc - int(wc) != 0)):
        wc = int(wc) + 1
    else:
        wc = int(wc)
  
    
    # to keep track of current position in 2-D array
    pos_x_count = 0
    pos_y_count = 0

    current_row = []
    for empty in self.house_emptys:
        
        empty.location = (pos_x, pos_y, 0)
         
        width_counter += 1
        pos_x += empty.empty_display_size + self.road_width + self.pavement_w * 2
        
        current_row.append(empty)
        
        if(empty.empty_display_size > largest_size):
            largest_size = empty.empty_display_size
        
        if(width_counter >= wc):
            
            # Creates roads for each house at 
            # current road
            for e in current_row:
                addRoad(self, context, e, largest_size - e.empty_display_size + self.pavement_w) 
            
            # Resets variables
            pos_x = 0
            pos_y += largest_size + self.road_width + self.pavement_w * 2 
            width_counter = 0
            largest_size = 0
            current_row = []
            # -----------------
            
    # For the last Row                
    for e in current_row:
        addRoad(self, context, e, largest_size - e.empty_display_size + self.pavement_w)
                  
    
            
    # to avoid issues when Re-doing        
    pos_x = 0
    pos_y = 0


        
class OBJECT_OT_add_object_city(Operator, AddObjectHelper):
    """Create a new City"""
    bl_idname = "mesh.city_generator"
    bl_label = "City"
    bl_description = "Generate a City from Houses"
    bl_options = {'REGISTER', 'UNDO'}


    house_emptys = []
    lamp_object = NULL
    car_object = NULL
    
    road_width : FloatProperty(name='Road Width',        min=0.0001, max=10000.0, default=10.0, description='Width of the roads between the buildings')
    pavement_h : FloatProperty(name='Pavement Height',   min=0.0001, max=10000.0, default=0.2, description='Height of the Pavement')
    pavement_w : FloatProperty(name='Pavement Width',    min=0.0001, max=10000.0, default=1.8, description='Width of the Pavement')
    
    street_lamp  : BoolProperty(name='Add Street Lamps', default = False, description='Add street lamps')
    lamp_size    : FloatProperty(name='Street Lamp Size',    min=0.0001, max=10000.0, default=0.5, description='Size of the Street lamps')
    lamp_distance: FloatProperty(name='Distance between Street lamps',    min=0.0001, max=10000.0, default=1, description='Distance Between the Street lamps')

    use_cars : BoolProperty(name='Add Cars', default = False, description='Add Cars')
    car_size : FloatProperty(name='Car size',    min=0.0001, max=10000.0, default=2.2, description='Size of the cars')
    car_dist : FloatProperty(name='Distance between Cars',    min=0.0001, max=10000.0, default=4, description='Distance Between the cars')

    
    seed : IntProperty(name='Seed Value', default=1, min = 1, max = 255, description='Seed value for the shuffling') 
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.label(text="avaliable houses = " + str(len(self.house_emptys))) 
        
        box = layout.box()
        box.prop(self, 'seed')
        
        box = layout.box()
        box.prop(self, 'road_width')
        box.prop(self, 'pavement_h')
        box.prop(self, 'pavement_w')
        
        box = layout.box()
        box.prop(self, 'street_lamp')
        if(self.street_lamp == True):
            box.prop(self, 'lamp_size')
            box.prop(self, 'lamp_distance')
            
        box = layout.box()
        box.prop(self, 'use_cars')    
        if(self.use_cars == True):
            box.prop(self, 'car_size')
            box.prop(self, 'car_dist')
            
                   
    def execute(self, context):
        bpy.context.scene.cursor.location = (0,0,0)
        
        if(self.street_lamp == True):
            streetLamp(self, context)
        
        if(self.use_cars == True):
            car(self, context)


        # After reading some documentation I think this will solve
        # the structRNA crash since the array can contain old objs
        self.house_emptys.clear()   
         
        for obj in bpy.data.objects:
            if "CITY_GEN_EMPTY" in obj.name:
                # adding all avaliable house emptys to the array
                # number of avaliable houses can be found by using the lenght
                # of the array
                self.house_emptys.append(obj)
               
        if(len(self.house_emptys) > 0):
            random.seed(self.seed)
            random.shuffle(self.house_emptys)
            
            layout(self, context)    
        

        
        return {'FINISHED'}





#
# Operator for duplicating avaliable houses
#
class WM_OT_DUPLICATE(Operator, AddObjectHelper):
    bl_idname = "wm.duplicate"
    bl_label = "Duplicate avaliable houses"
    bl_options = {'REGISTER', 'UNDO'}
    
    #def draw(self, context):
        
    def execute(self, context):
        
        # Needs to make a copy, else it will continue
        # looping over the new ones created
        # A reason to hate Python i guess
        current_objs = list(bpy.data.objects)
        
        # Searches through all objects and copies if the name matches
        # Will change the positions for all the houses
        pos = 0
        for obj in current_objs:
            if "CITY_GEN_EMPTY" in obj.name:   
                new_empty = obj.copy()
                context.collection.objects.link(new_empty)
                for o in obj.children:
                    o_copy = o.copy()
                    context.collection.objects.link(o_copy)
                    o_copy.parent = new_empty
                
                obj.location = (pos, 0 ,0)
                new_empty.location = (obj.location.x, obj.location.y + obj.empty_display_size + 1, obj.location.z)
                pos += obj.empty_display_size + 1
        
        return {'FINISHED'}



class LayoutPanel(bpy.types.Panel):
    """Creates a Panel in the VIEW_3D in object mode"""
    bl_label = "The City Generator"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Create city"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        
        layout.label(text="Create a new house")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("mesh.house_generator")


        layout.label(text="Duplicate the houses")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("wm.duplicate")
        
        layout.label(text="Generate a City")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("mesh.city_generator")

      


## THE HOUSE
def add_object_button_house(self, context):
    self.layout.operator(
        OBJECT_OT_add_object_house.bl_idname,
        text="House",
        icon='PLUGIN')

## THE CITY
def add_object_button_city(self, context):
    self.layout.operator(
        OBJECT_OT_add_object_city.bl_idname,
        text="City",
        icon='PLUGIN')

## DUPLICATE HOUSES
def add_object_button_dup(self, context):
    self.layout.operator("wm.duplicate",
        icon='PLUGIN')


def register():
    bpy.utils.register_class(LayoutPanel)
    
    bpy.utils.register_class(OBJECT_OT_add_object_house)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button_house)
    
    bpy.utils.register_class(OBJECT_OT_add_object_city)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button_city)
    
    bpy.utils.register_class(WM_OT_DUPLICATE)
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button_dup)



def unregister():
    bpy.utils.unregister_class(LayoutPanel)
    
    bpy.utils.unregister_class(OBJECT_OT_add_object_house)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button_house)
    
    bpy.utils.unregister_class(OBJECT_OT_add_object_city)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button_city)
    
    bpy.utils.unregister_class(WM_OT_DUPLICATE)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button_dup)


if __name__ == "__main__":
    register()





    

