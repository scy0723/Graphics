import glfw
from OpenGL.GL import*
import numpy as np
import math

time=3

def render(time):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)
    angle=np.pi/6
    radius=1
    for i in range(0,12):
        glVertex2f(np.cos(i*angle)*radius,np.sin(i*angle)*radius)
    glEnd()
    
    glBegin(GL_LINES)
    glVertex2f(0,0)
    glVertex2f(np.cos(time*angle)*0.7,np.sin(time*angle)*0.7)
    glEnd()

def key_callback(window,key,scancode,action,mods):
    global time
    
    if key==glfw.KEY_1:
        if action==glfw.PRESS:
            time=14
    if key==glfw.KEY_2:
        if action==glfw.PRESS:
            time=13
    if key==glfw.KEY_3:
        if action==glfw.PRESS:
            time=12
    if key==glfw.KEY_4:
        if action==glfw.PRESS:
            time=11
    if key==glfw.KEY_5:
        if action==glfw.PRESS:
            time=10
    if key==glfw.KEY_6:
        if action==glfw.PRESS:
            time=9
    if key==glfw.KEY_7:
        if action==glfw.PRESS:
            time=8
    if key==glfw.KEY_8:
        if action==glfw.PRESS:
            time=7
    if key==glfw.KEY_9:
        if action==glfw.PRESS:
            time=6
    if key==glfw.KEY_0:
        if action==glfw.PRESS:
            time=5
    if key==glfw.KEY_Q:
        if action==glfw.PRESS:
            time=4
    if key==glfw.KEY_W:
        if action==glfw.PRESS:
            time=3     


def main():
    global currentMode
    if not glfw.init():
        return
    window=glfw.create_window(480,480,"2019055078",None,None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window,key_callback)
    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        render(time)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__=="__main__":
    main()
                                    



