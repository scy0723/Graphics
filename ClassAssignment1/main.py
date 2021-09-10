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
Ortho=-1
Orbiting = False
Panning = False
cursorA = np.array([0,0])
cursorB = np.array([0,0])

def render():
    global azimuth, elevation, distance
    global point, up, w, u, v
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    #pers. vs. ortho.
    if Ortho ==-1: 
        gluPerspective(45, 1, 1, 50)
    else:
        glOrtho(-distance/2,distance/2,-distance/2,distance/2,-distance*2,distance*2)
        
    #w,u,v 계산        
    w = np.array(  [np.cos(elevation) * np.sin(azimuth),   np.sin(elevation),     np.cos(elevation)*np.cos(azimuth)]  )
    u = np.cross(np.array([0,up,0]), w) # u = Vup x w
    u /= np.sqrt(np.dot(u,u)) #normalize
    v = np.cross(u, w) # v= u x w
    v /= np.sqrt(np.dot(v,v)) #normalize
    gluLookAt(point[0]+distance*w[0], point[1]+distance*w[1], point[2]+distance*w[2],     point[0],point[1],point[2],      0,up,0) #eye(=w*distance+벡터시작점(=point)), at(=point), up

    drawCoordinates()
    drawGrid()

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



def cursor_callback(window, xpos, ypos):
    
    global azimuth, elevation, cursorA, cursorB, Orbiting
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

def key_callback(window, key, scancode, action, mods):
    global  Ortho
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_V:
            Ortho*=-1 #전환

   
def scroll_callback(window, xoffset, yoffset):
    global distance
    distance += yoffset/3

    
def main():
    if not glfw.init():
        return
    window = glfw.create_window(800,800,"Class_Assignment1", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.set_mouse_button_callback(window, button_callback)
    glfw.set_cursor_pos_callback(window, cursor_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.make_context_current(window)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()
if __name__ == "__main__":
    main()
