import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

azimuth = 0
distance = 10
elevation = 0
up = 1
u = np.array([1, 0, 0])
v = np.array([0, 1, 0])
w = np.array([0, 0, 1])
point = np.array([.0, .0, .0])


cursorA = np.array([0,0])
cursorB = np.array([0,0])
file=None

def drawCoordinates():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([-5.,0., 0.]))
    glVertex3fv(np.array([5.,0., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,-5.]))
    glVertex3fv(np.array([0.,0.,5.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,3.,0.]))

def drawGrid():
    glColor3ub(100, 100, 100)
    for i in np.linspace(-5, 5, 25):
        glVertex3fv(np.array([-5.,0., i]))
        glVertex3fv(np.array([5.,0., i]))
        glVertex3fv(np.array([i,0., -5.]))
        glVertex3fv(np.array([i,0., 5.]))
    glEnd()

def scroll_callback(window, xoffset, yoffset):

    global distance

    distance += yoffset/3

Panning=False
Orbiting=False

def cursor_callback(window, xpos, ypos):
    global azimuth, elevation, cursorA, cursorB, Orbiting,Panning
    global point, up, w, u, v  
    if Orbiting == True:
        cursorA = cursorB
        cursorB = glfw.get_cursor_pos(window)
        ele= (cursorA[1] - cursorB[1])/150 #감도 낮춤
        elevation -= ele
        if np.cos(elevation)<0: up = -1
        elif np.cos(elevation)>0: up = 1
        azimuth += up * (cursorA[0] - cursorB[0])/150


    if Panning == True:
        cursorA = cursorB
        cursorB = glfw.get_cursor_pos(window)
        point += ( u * (cursorA[0] - cursorB[0]) + v * (cursorA[1] - cursorB[1])) / 150


def button_callback(window, button, action, mod):
    global azimuth, elevation, cursorA, cursorB, Orbiting, Panning, up

    if button==glfw.MOUSE_BUTTON_LEFT:   #좌클릭

        if action==glfw.PRESS:
            cursorB = glfw.get_cursor_pos(window) # 현 커서 위치
            Orbiting = True
        elif action==glfw.RELEASE:
            Orbiting = False #중지

 

    if button==glfw.MOUSE_BUTTON_RIGHT:  #우클릭
        if action==glfw.PRESS:
            cursorB = glfw.get_cursor_pos(window) # 현 커서 위치
            Panning = True
        elif action==glfw.RELEASE:
            Panning = False #중지

#####################################################

wireframe=1 #Z
smoothshading= -1 #S
animation=-1 #H

obj=0

varr = np.array([], 'float32')
iarr = np.array([])
ivarr = np.array([], 'float32')

treevarr= np.array([], 'float32')
treeivarr= np.array([], 'float32')
dumvarr= np.array([], 'float32')
dumivarr= np.array([], 'float32')
dukvarr= np.array([], 'float32')
dukivarr = np.array([], 'float32')

treeiarr=np.array([])
dumiarr=np.array([])
dukiarr=np.array([])


def render():  #done
    global azimuth, elevation, distance
    global point, up, w, u, v
    global wireframe,smoothshading, isObj,animation

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 50)

    if wireframe==1:
       glPolygonMode( GL_FRONT_AND_BACK, GL_LINE) #wireframe
    else :
       glPolygonMode( GL_FRONT_AND_BACK, GL_FILL) #solid

    #w,u,v 계산        
    w = np.array(  [np.cos(elevation) * np.sin(azimuth),   np.sin(elevation),     np.cos(elevation)*np.cos(azimuth)]  )
    u = np.cross(np.array([0,up,0]), w) # u = Vup x w
    u /= np.sqrt(np.dot(u,u)) #normalize
    v = np.cross(u, w) # v= u x w
    v /= np.sqrt(np.dot(v,v)) #normalize
    gluLookAt(point[0]+distance*w[0], point[1]+distance*w[1], point[2]+distance*w[2],     point[0],point[1],point[2],      0,up,0) #eye(=w*distance+벡터시작점(=point)), at(=point), up

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    drawCoordinates()
    drawGrid()
    
    # light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    if animation==1:
        #tree
        drawObj()
        t=glfw.get_time()
        glTranslate(np.sin(t),0,0)
        glPushMatrix()
        glScalef(.05,.05,.05)
        glColor3ub(0,102,0)
        drawTree()
        drawObj()
        glPopMatrix()
        
        #dummy
        glPushMatrix()
        glRotatef(-0.5*t*(180/np.pi),0,1,0)
        glTranslate(2,0.5*(1-np.sin(t)),0)
        glPushMatrix()
        glColor3ub(255,13,2)
        glScalef(.01,.01,.01)
        drawDummy()
        drawObj()
        glPopMatrix()
        
        #pet
        glPushMatrix()
        glRotate(-t*(180/np.pi),0,1,0)
        glTranslate(1,1.3,0)
        glPushMatrix()
        glScale(.0005,.0005,.0005)
        glColor3ub(245,224,0)
        drawDuck()
        drawObj()
        glPopMatrix()
        glPopMatrix()
        glPopMatrix()

    else:
        # light 0
        glPushMatrix()
        lightPos = (3.,4.,5.,1.)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
        glPopMatrix()

        # light 1
        glPushMatrix()
        glRotatef(120,0,1,0)
        lightPos = (-3.,-4.,5.,0.) 
        glLightfv(GL_LIGHT1, GL_POSITION, lightPos)
        glPopMatrix()

        # light 2
        glPushMatrix()
        glRotatef(240,0,1,0)
        lightpos = (-3.,4.,-5.,1.)
        glLightfv(GL_LIGHT2, GL_POSITION, lightPos)
        glPopMatrix()

        ambientLightColor = (.1,.0,.0,1.)
        diffuseLightColor = (1.,.0,.0,1.)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLightColor)

        ambientLightColor1 = (.0,.1,.0,1.)
        diffuseLightColor1 = (.0,1.,.0,1.)
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor1)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuseLightColor1)

        ambientLightColor2 = (.0,.0,.1,1.)
        diffuseLightColor2 = (.0,.0,1.,1.)
        glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor2)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, diffuseLightColor2)

        # material reflectance for each color channel
        objectColor = (1.,1.,1.,1.)
        specularObjectColor = (1.,1.,1.,1.)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

        if obj==1:
            drawObj()
        glDisable(GL_LIGHTING)

def drawObj():
    global ivarr, iarr,varr

    if smoothshading==1:
        IVARR = ivarr
        IARR = iarr
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glNormalPointer(GL_FLOAT, 6*IVARR.itemsize, IVARR)
        glVertexPointer(3, GL_FLOAT, 6*IVARR.itemsize, ctypes.c_void_p(IVARR.ctypes.data + 3*IVARR.itemsize))
        glDrawElements(GL_TRIANGLES, IARR.size, GL_UNSIGNED_INT, IARR)

    else:
        VARR = varr
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 6*VARR.itemsize, VARR)
        glVertexPointer(3, GL_FLOAT, 6*VARR.itemsize, ctypes.c_void_p(VARR.ctypes.data + 3*VARR.itemsize))
        glDrawArrays(GL_TRIANGLES, 0, int(VARR.size/6))
        glDisable(GL_LIGHTING)

def drawTree():
    global iarr,varr,ivarr
    iarr=treeiarr
    varr=treevarr
    ivarr=treeivarr

def drawDummy():
    global iarr,varr,ivarr
    iarr=dumiarr
    varr=dumvarr
    ivarr=dumivarr

def drawDuck():
    global iarr,varr,ivarr
    iarr=dukiarr
    varr=dukvarr
    ivarr=dukivarr
    

def drop_callback(window,path):  #done

    global ivarr, iarr, varr, obj
    file = open(path[0])
    obj=1
    tvarr = []
    tnarr = []
    inarr = []
    varr = []
    iarr = []
    ivarr = []
    
    total = 0;
    three = 0
    four = 0
    more = 0

    while True:
        line = file.readline()
        if not line:
            break
        parsedline = line.split()
        if len(parsedline)==0:
            continue
        if parsedline[0] == 'v':
            list.append(tvarr, (float(parsedline[1]), float(parsedline[2]), float(parsedline[3])))
            list.append(inarr, np.array([0,0,0], 'float32'))
        elif parsedline[0] == 'vn':
            list.append(tnarr, (float(parsedline[1]), float(parsedline[2]), float(parsedline[3])))
        elif parsedline[0] == 'f':
            fv = 0
            t = 0
            fn = -1
            p = parsedline[1].split('/')
            fv = p[0]
            if len(p)>=3:
                fn = p[2]
            fv = int(fv)
            fn = int(fn)
            sv = None
            sn = None
            face_normal = np.array([0.,0.,0.])
            cnt = 0
            it = ()
            total += 1

            for pl in parsedline[2:]:
                a = 0
                b = 0
                c = -1
                p = pl.split('/')
                a = p[0]
                if len(p)>=3:
                    c = p[2]
                a = int(a)
                c = int(c)
                if (sv != None) and (sn != None):
                    list.append(varr, tuple(np.array(tnarr[fn-1])/np.sqrt(np.dot(np.array(tnarr[fn-1]), np.array(tnarr[fn-1])))))
                    list.append(varr, tvarr[fv-1])
                    it += (fv-1,)

                    list.append(varr, tuple(np.array(tnarr[sn-1])/np.sqrt(np.dot(np.array(tnarr[sn-1]), np.array(tnarr[sn-1])))))
                    list.append(varr, tvarr[sv-1])                   
                    it += (sv-1,)
 
                    list.append(varr, tuple(np.array(tnarr[c-1])/np.sqrt(np.dot(np.array(tnarr[c-1]), np.array(tnarr[c-1])))))
                    list.append(varr, tvarr[a-1])
                    it += (a-1,)

                    face_normal = np.cross(np.array(tvarr[sv - 1]) - np.array(tvarr[fv - 1]), np.array(tvarr[a - 1]) - np.array(tvarr[fv - 1]))
                    face_normal /= np.sqrt(np.dot(face_normal, face_normal))

                    inarr[sv-1] += face_normal

                    list.append(iarr, it)
                    it = ()
                    cnt += 1
                sv = a
                sn = c
            inarr[fv-1] += face_normal
            inarr[sv-1] += face_normal
            if cnt ==1:
                three += 1
            elif cnt == 2:
                four += 1
            else:
                more += 1

    varr = np.array(varr, 'float32')
    for i in range(len(tvarr)):
        d = np.sqrt(np.dot(inarr[i], inarr[i]))
        if d == 0:
            d = 1
        list.append(ivarr, tuple(inarr[i]/d))
        list.append(ivarr, tvarr[i])  
    ivarr = np.array(ivarr, 'float32')
    iarr = np.array(iarr)

    print('File name : ' + path[0])
    print('Total number of faces : '+str(total))
    print('Total number of faces with 3 vertices : '+str(three))
    print('Total number of faces with 4 vertices : '+str(four))
    print('Total number of faces with n vertices : '+str(more))
    print("--------------------------------------------------")

def calculateAnimation():

    global treevarr,treeivarr,dumvarr,dukvarr,dukvarr,treeiarr,dumiarr,dukiarr
    
    file=open("./tree.obj",'r')
    treevarr, treeiarr,treeivarr=drawAnimation(file)

    file=open("./dummy.obj",'r')
    dumvarr,dumiarr,dumivarr=drawAnimation(file)

    file=open("./duck.obj",'r')
    dukvarr,dukiarr,dukivarr=drawAnimation(file)



def drawAnimation(file):  #done
    global ivarr, iarr, varr, obj
    obj=1
    tvarr = []
    tnarr = []
    inarr = []
    varr = []
    iarr = []
    ivarr = []
    total = 0;
    three = 0
    four = 0
    more = 0


    while True:
        line = file.readline()
        if not line:
            break
        parsedline = line.split()
        if len(parsedline)==0:
            continue
        if parsedline[0] == 'v':
            list.append(tvarr, (float(parsedline[1]), float(parsedline[2]), float(parsedline[3])))
            list.append(inarr, np.array([0,0,0], 'float32'))
        elif parsedline[0] == 'vn':
            list.append(tnarr, (float(parsedline[1]), float(parsedline[2]), float(parsedline[3])))
        elif parsedline[0] == 'f':
            fv = 0
            t = 0
            fn = -1
            p = parsedline[1].split('/')
            fv = p[0]
            if len(p)>=3:
                fn = p[2]
            fv = int(fv)
            fn = int(fn)
            sv = None
            sn = None
            face_normal = np.array([0.,0.,0.])
            cnt = 0
            it = ()
            total += 1

        
            for pl in parsedline[2:]:
                a = 0
                b = 0
                c = -1
                p = pl.split('/')
                a = p[0]
                if len(p)>=3:
                    c = p[2]
                a = int(a)
                c = int(c)
                if (sv != None) and (sn != None):
                    list.append(varr, tuple(np.array(tnarr[fn-1])/np.sqrt(np.dot(np.array(tnarr[fn-1]), np.array(tnarr[fn-1])))))
                    list.append(varr, tvarr[fv-1])
                    it += (fv-1,)

                    list.append(varr, tuple(np.array(tnarr[sn-1])/np.sqrt(np.dot(np.array(tnarr[sn-1]), np.array(tnarr[sn-1])))))
                    list.append(varr, tvarr[sv-1])                   
                    it += (sv-1,)

                    list.append(varr, tuple(np.array(tnarr[c-1])/np.sqrt(np.dot(np.array(tnarr[c-1]), np.array(tnarr[c-1])))))
                    list.append(varr, tvarr[a-1])
                    it += (a-1,)

                    face_normal = np.cross(np.array(tvarr[sv - 1]) - np.array(tvarr[fv - 1]), np.array(tvarr[a - 1]) - np.array(tvarr[fv - 1]))
                    face_normal /= np.sqrt(np.dot(face_normal, face_normal))

                    inarr[sv-1] += face_normal

                    list.append(iarr, it)
                    it = ()
                    cnt += 1
                sv = a
                sn = c
            inarr[fv-1] += face_normal
            inarr[sv-1] += face_normal
            if cnt == 1:
                three += 1
            elif cnt == 2:
                four += 1
            else:
                more += 1
                
    varr = np.array(varr, 'float32')
    for i in range(len(tvarr)):
        d = np.sqrt(np.dot(inarr[i], inarr[i]))
        if d == 0:
            d = 1
        list.append(ivarr, tuple(inarr[i]/d))
        list.append(ivarr, tvarr[i])  
    ivarr = np.array(ivarr, 'float32')

    iarr = np.array(iarr)
    return varr, iarr, ivarr
 

def key_callback(window, key, scancode, action, mods):
    global wireframe
    global smoothshading , animation
    if action == glfw.PRESS:
        if key == glfw.KEY_Z: #wireframe/solid
            wireframe *= -1
        if key == glfw.KEY_S: #shading
            smoothshading *= -1
        if key == glfw.KEY_H: #animation
            animation *= -1
            calculateAnimation()

 

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800,800,"Class_Assignment2", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_drop_callback(window,drop_callback)

    glfw.make_context_current(window)
    glfw.swap_interval(0)
 
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
