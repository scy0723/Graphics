import glfw
from OpenGL.GL import *
import numpy as np

list=[4]

def render():
	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	glBegin(GL_LINES)
	glColor3ub(255, 0, 0)
	glVertex2fv(np.array([0.,0.]))
	glVertex2fv(np.array([1.,0.]))
	glColor3ub(0, 255, 0)
	glVertex2fv(np.array([0.,0.]))
	glVertex2fv(np.array([0.,1.]))
	glEnd()
	glColor3ub(255, 255, 255)
	###########################
	
	global list
	for i in reversed(list):
		if i==0:
			glTranslatef(-0.1,0,0)
		elif i==1:
			glTranslatef(.1,0,0)
		elif i==2:
			glRotatef(10,1,0,1)
		elif i==3:
			glRotatef(-10,1,0,1)
		elif i==4:
			continue
	###########################
	drawTriangle()

def drawTriangle():
	glBegin(GL_TRIANGLES)
	glVertex2fv(np.array([0.,.5]))
	glVertex2fv(np.array([0.,0.]))
	glVertex2fv(np.array([.5,0.]))
	glEnd()

def key_callback(window,key,scancode,action,mods):
	global list
	if key==glfw.KEY_Q:
		if action==glfw.PRESS:
			list.append(0)
	
	if key==glfw.KEY_E:
		if action==glfw.PRESS:
			list.append(1)

	if key==glfw.KEY_A:
		if action==glfw.PRESS:
			list.append(2)

	if key==glfw.KEY_D:
		if action==glfw.PRESS:
			list.append(3)
	
	if key==glfw.KEY_1:
		if action==glfw.PRESS:
			list.clear()
			list.append(4)

def main():
	if not glfw.init():
		return
	window=glfw.create_window(480,480,"2019055078",None,None)
	if not window:
		glfw.terminate()
		return
	glfw.set_key_callback(window,key_callback)
	glfw.make_context_current(window)
	glfw.swap_interval(1)

	while not glfw.window_should_close(window):
		glfw.poll_events()
		render()
		glfw.swap_buffers(window)
	
	glfw.terminate()
	
if __name__=="__main__":
	main()
