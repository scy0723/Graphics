import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.

Matrix1,Matrix2=[],[]
switch=0

def createVertexAndIndexArrayIndexed():
    varr = np.array([
            ( -0.5773502691896258 , 0.5773502691896258 ,  0.5773502691896258 ),
            ( -1 ,  1 ,  1 ), # v0
            ( 0.8164965809277261 , 0.4082482904638631 ,  0.4082482904638631 ),
            (  1 ,  1 ,  1 ), # v1
            ( 0.4082482904638631 , -0.4082482904638631 ,  0.8164965809277261 ),
            (  1 , -1 ,  1 ), # v2
            ( -0.4082482904638631 , -0.8164965809277261 ,  0.4082482904638631 ),
            ( -1 , -1 ,  1 ), # v3
            ( -0.4082482904638631 , 0.4082482904638631 , -0.8164965809277261 ),
            ( -1 ,  1 , -1 ), # v4
            ( 0.4082482904638631 , 0.8164965809277261 , -0.4082482904638631 ),
            (  1 ,  1 , -1 ), # v5
            ( 0.5773502691896258 , -0.5773502691896258 , -0.5773502691896258 ),
            (  1 , -1 , -1 ), # v6
            ( -0.8164965809277261 , -0.4082482904638631 , -0.4082482904638631 ),
            ( -1 , -1 , -1 ), # v7
            ], 'float32')
    iarr = np.array([
            (0,2,1),
            (0,3,2),
            (4,5,6),
            (4,6,7),
            (0,1,5),
            (0,5,4),
            (3,6,2),
            (3,7,6),
            (1,2,6),
            (1,6,5),
            (0,7,3),
            (0,4,7),
            ])
    return varr, iarr

def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize, ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([3.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,3.]))
    glEnd()

def XYZEulerToRotMat(e):
    xang,yang,zang=e[0],e[1],e[2]
    Rx = np.array([[1,0,0],
                   [0, np.cos(xang), -np.sin(xang)],
                   [0, np.sin(xang), np.cos(xang)]])
    Ry = np.array([[np.cos(yang), 0, np.sin(yang)],
                   [0,1,0],
                   [-np.sin(yang), 0, np.cos(yang)]])
    Rz = np.array([[np.cos(zang), -np.sin(zang), 0],
                   [np.sin(zang), np.cos(zang), 0],
                   [0,0,1]])
    return Rx @ Ry @ Rz

def interpolateXYZEuler(e1,e2,t):
    E=lerp(e1,e2,t)
    R=XYZEulerToRotMat(E)
    return R

def l2norm(v):
    return np.sqrt(np.dot(v, v))

def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)

def lerp(v1, v2, t):
    return (1-t)*v1 + t*v2

def exp(rv):
   theta = l2norm(rv)
   rv = normalized(rv)
   ux = rv[0]
   uy = rv[1]
   uz = rv[2]
   sin_t = np.sin(theta)
   cos_t = np.cos(theta)
   R = np.array([[cos_t+(ux**2)*(1-cos_t),
                  ux*uy*(1-cos_t)-uz*sin_t,
                  ux*uz*(1-cos_t)+uy*sin_t],
               [uy*ux*(1-cos_t)+uz*sin_t,
                cos_t+(uy**2)*(1-cos_t),
                uy*uz*(1-cos_t)-ux*sin_t],
               [uz*ux*(1-cos_t)-uy*sin_t,
                uz*uy*(1-cos_t)+ux*sin_t,
                cos_t+(uz**2)*(1-cos_t)]
                ])
   return R

def log(R):
    th= np.arccos((R[0,0]+R[1,1]+R[2,2]-1)/2)
    varr = np.array([   
        (R[2,1]-R[1,2])/(2*np.sin(th)),
        (R[0,2]-R[2,0])/(2*np.sin(th)),
        (R[1,0]-R[0,1])/(2*np.sin(th))])
    v=normalized(varr)
    return th*v

def slerp(R1,R2,t):
    varr = R1 @ exp(t * log(R1.T @ R2) )
    return varr


def render(ang):
    global gCamAng, gCamHeight
    global Matrix1, Matrix2,switch
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1,10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng),gCamHeight,5*np.cos(gCamAng), 0,0,0, 0,1,0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3.,4.,5.,1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1.,1.,1.,1.)
    ambientLightColor = (.1,.1,.1,1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    

    ##111111111111111111111111111111111111111111111111111111
    euler1 = np.array([np.radians(20),np.radians(30),np.radians(30)])
    R1 = np.identity(4)  # in XYZ Euler angles
    R1_3 = XYZEulerToRotMat(euler1)   # in rotation matrix
    R1[:3,:3] = R1_3
    J1 = R1
    
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)

    objectColor = (1.,0.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R2 = np.identity(4)
    T1 = np.identity(4)
    T1[0][3] = 1.

    euler2=np.array([np.radians(15),np.radians(30),np.radians(25)])
    R2_3 = XYZEulerToRotMat(euler2)   # in rotation matrix
    R2[:3,:3] = R2_3
    J2 = R1 @ T1 @ R2

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glTranslatef(1,0,0)
    glPopMatrix()
    glPopMatrix()

    #222222222222222222222222222222222222222222222222222222
    euler3=np.array([np.radians(45),np.radians(60),np.radians(40)])
    R3 = np.identity(4)  # in XYZ Euler angles
    R3_3 = XYZEulerToRotMat(euler3)   # in rotation matrix
    R3[:3,:3] = R3_3
    J1 = R3
    
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    
    objectColor = (1.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R4 = np.identity(4)
    T1 = np.identity(4)
    T1[0][3] = 1.

    euler4= np.array([np.radians(25),np.radians(40),np.radians(40)])
    R4_3 = XYZEulerToRotMat(euler4)   # in rotation matrix
    R4[:3,:3] = R4_3
    J2 = R3 @ T1 @ R4

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glTranslatef(1,0,0)
    glPopMatrix()
    glPopMatrix()

    #333333333333333333333333333333333333333333333333333333333
    euler5= np.array([np.radians(60),np.radians(70),np.radians(50)])
    R5 = np.identity(4)  # in XYZ Euler angles
    R5_3 = XYZEulerToRotMat(euler5)   # in rotation matrix
    R5[:3,:3] = R5_3
    J1 = R5
    
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    
    objectColor = (0.,1.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
      
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R6 = np.identity(4)
    T1 = np.identity(4)
    T1[0][3] = 1.

    euler6= np.array([np.radians(40),np.radians(60),np.radians(50)])
    R6_3 = XYZEulerToRotMat(euler6)   # in rotation matrix
    R6[:3,:3] = R6_3
    J2 = R5 @ T1 @ R6

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glTranslatef(1,0,0)
    glPopMatrix()
    glPopMatrix()

    #444444444444444444444444444444444444444444444444444444444
    euler7= np.array([np.radians(80),np.radians(85),np.radians(70)])
    R7 = np.identity(4)  # in XYZ Euler angles
    R7_3 = XYZEulerToRotMat(euler7)   # in rotation matrix
    R7[:3,:3] = R7_3
    J1 = R7
    
    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)

    objectColor = (0.,0.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    R8 = np.identity(4)
    T1 = np.identity(4)
    T1[0][3] = 1.

    euler8= np.array([np.radians(55),np.radians(80),np.radians(65)])
    R8_3 = XYZEulerToRotMat(euler8)   # in rotation matrix
    R8[:3,:3] = R8_3
    J2 = R7 @ T1 @ R8

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glTranslatef(1,0,0)
    glPopMatrix()
    glPopMatrix()


    #iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
    t = (ang % 90) / 90.
    objectColor = (1.,1.,1.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    

##red -> yellow

    RtoY1= np.identity(4)
    slerp1 = slerp(R1_3, R3_3, t)
    glPushMatrix()
    RtoY1[:3,:3] = slerp1

    RtoY2 = np.identity(4)
    slerp2 = slerp(R2_3, R4_3, t)
    glPushMatrix()
    slerp11=np.identity(4)
    slerp22=np.identity(4)
    slerp11[:3,:3]=slerp1
    slerp22[:3,:3]=slerp2
    RtoY2= slerp11@T1@slerp22
    glPopMatrix()


##yellow -> green

    YtoG1 = np.identity(4)
    slerp1 = slerp(R3_3, R5_3, t)
    glPushMatrix()
    YtoG1[:3,:3] = slerp1

    YtoG2 = np.identity(4)
    slerp2 = slerp(R4_3, R6_3, t)
    glPushMatrix()
    slerp11=np.identity(4)
    slerp22=np.identity(4)
    slerp11[:3,:3]=slerp1
    slerp22[:3,:3]=slerp2
    YtoG2= slerp11@T1@slerp22
    glPopMatrix()
    

##green -> blue
    GtoB1 = np.identity(4)
    slerp1 = slerp(R5_3, R7_3, t)
    glPushMatrix()
    GtoB1[:3,:3] = slerp1

    GtoB2 = np.identity(4)
    slerp2 = slerp(R6_3, R8_3, t)
    glPushMatrix()
    slerp11=np.identity(4)
    slerp22=np.identity(4)
    slerp11[:3,:3]=slerp1
    slerp22[:3,:3]=slerp2
    GtoB2= slerp11@T1@slerp22
    glPopMatrix()

    if t==1 or t==0:  #each cycle
        switch+=1
    if switch%3==0:
        Matrix1=RtoY1
        Matrix2=RtoY2
    elif switch%3==1:
        Matrix1=YtoG1
        Matrix2=YtoG2
    else:
        Matrix1=GtoB1
        Matrix2=GtoB2

            
    glMultMatrixf(Matrix1.T)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()

    glMultMatrixf(Matrix2.T)
    glTranslatef(0.5,0,0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()

    glPopMatrix()

    glDisable(GL_LIGHTING)


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key==glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key==glfw.KEY_2:
            gCamHeight += .1
        elif key==glfw.KEY_W:
            gCamHeight += -.1

gVertexArrayIndexed = None
gIndexArray = None

def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640,640,'2019055078', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    count=0 
    while not glfw.window_should_close(window):
        glfw.poll_events()
        ang = count % 360
        render(ang)
        count += 1

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

