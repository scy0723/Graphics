import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    glLoadIdentity()
    myFrustum(-1,1, -1,1, 1,10)
    myLookAt(np.array([5,3,5]), np.array([1,1,-1]), np.array([0,1,0]))
    # Above two lines must behave exactly same as the below two lines
    #glFrustum(-1,1, -1,1, 1,10)
    #gluLookAt(5,3,5, 1,1,-1, 0,1,0)
    drawFrame()
    glColor3ub(255, 255, 255)
    drawCubeArray()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()
def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5) 
                             
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5) 
                             
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
                             
    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)
 
    glVertex3f(-0.5, 0.5, 0.5) 
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5) 
    glVertex3f(-0.5,-0.5, 0.5) 
                             
    glVertex3f( 0.5, 0.5,-0.5) 
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)
    glEnd()
    
def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i,j,-k-1)
                glScalef(.5,.5,.5)
                drawUnitCube()
                glPopMatrix()

def myFrustum(left, right, bottom, top, near, far):
    FM=np.identity(4)
    
    FM[0][0] = 2 * near / (right - left)
    FM[0][1] = 0 
    FM[0][2] = 0 
    FM[0][3] = 0 
 
    FM[1][0] = 0 
    FM[1][1] = 2 * near / (top - bottom)
    FM[1][2] = 0 
    FM[1][3] = 0 
 
    FM[2][0] = (right + left) / (right - left) 
    FM[2][1] = (top + bottom) / (top - bottom) 
    FM[2][2] = -(far + near) / (far - near)
    FM[2][3] = -1
 
    FM[3][0] = 0 
    FM[3][1] = 0 
    FM[3][2] = -2 * far * near / (far - near)
    FM[3][3] = 0

    glMultMatrixf(FM)

def myLookAt(eye, at, up):
    wnorm= np.sqrt(np.dot((eye-at),(eye-at)))
    w=(eye-at)/wnorm

    upm=np.cross(up,w)
    unorm=np.sqrt(np.dot(upm,upm))
    u=upm/unorm

    v=np.cross(w,u)
    
    LM=np.identity(4)
    
    LM[0][0] = u[0]
    LM[0][1] = u[1] 
    LM[0][2] = u[2]
    LM[0][3] = 0
 
    LM[1][0] = v[0]
    LM[1][1] = v[1]
    LM[1][2] = v[2]
    LM[1][3] = 0
 
    LM[2][0] = w[0]
    LM[2][1] = w[1]
    LM[2][2] = w[2]
    LM[2][3] = 0
 
    LM[3][0] = eye[0] 
    LM[3][1] = eye[1]
    LM[3][2] = eye[2]
    LM[3][3] = 1
    LM=np.linalg.inv(LM)
    glMultMatrixf(LM)

def main():
    global gVertexArraySeparate

    if not glfw.init():
        return
    window = glfw.create_window(480,480,'2019055078', None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

            

