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

path = ''
cnt = 0
Character = None
animate = -1


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

class Joint:
	def __init__(self):
		self.channels = []
		self.offset = []
		self.parent = None
		self.children = []
		self.frames = []
		self.idx = [0, 0]
		self.rot = np.identity(4)
		self.tran = np.identity(4)
		self.oldTran = np.identity(4)
		self.Tran2 = np.identity(4)
		self.local = np.identity(4)
		self.world = np.array([0, 0, 0, 0])

	def update(self, frame):
		for index, channel in enumerate(self.channels):
			tmpF = self.frames[frame][index]
			M = np.identity(4)			
			if channel=='Xposition':
				self.tran[0, 3] = tmpF
			elif channel=='Yposition':
				self.tran[1, 3] = tmpF
			elif channel=='Zposition':
				self.tran[2, 3] = tmpF
			elif channel=='Xrotation':
				M[1, 1] = np.cos(np.radians(tmpF))
				M[1, 2] = -np.sin(np.radians(tmpF))
				M[2, 1] = np.sin(np.radians(tmpF))
				M[2, 2] = np.cos(np.radians(tmpF))
				self.rot = np.dot(self.rot, M)
			elif channel=='Yrotation':
				M[0, 0] = np.cos(np.radians(tmpF))
				M[0, 2] = np.sin(np.radians(tmpF))
				M[2, 0] = -np.sin(np.radians(tmpF))
				M[2, 2] = np.cos(np.radians(tmpF))
				self.rot = np.dot(self.rot, M)
			elif channel=='Zrotation':
				M[0, 0] = np.cos(np.radians(tmpF))
				M[0, 1] = -np.sin(np.radians(tmpF))
				M[1, 0] = np.sin(np.radians(tmpF))
				M[1, 1] = np.cos(np.radians(tmpF))
				self.rot = np.dot(self.rot, M)
		if self.parent:
			self.local = np.dot(self.parent.Tran2, self.oldTran)
		else:
			self.local = np.dot(self.oldTran, self.Tran2)

		self.world = np.array([self.local[0, 3],
					self.local[1, 3],
					self.local[2, 3],
					self.local[3, 3]])
		self.Tran2 = np.dot(self.local, self.rot)		

		for child in self.children:
			child.update(frame)

class BVH:
	global path

	def __init__(self, gPath):
		self.__root = None
		self.__stack = []
		self.frametime = 0.
		self.frames = 0
		self.channel_count = 0
		self.motions = []
		self.name = []
		self.loader(gPath)

	@property
	def root(self):
		return self.__root

	def loader(self, path):
		f = open(path)
		lines = f.readlines()
		
		parent = None
		now = None
		motion = 0

		for line in lines[1:len(lines)]:
			values = line.split()
			if len(values) == 0:
				continue
			
			if values[0] in ["ROOT", "JOINT", "End"]:
				if now:
					parent = now
				now = Joint()
				self.name.append(values[1])

				if len(self.__stack) == 0:
					self.__root = now
				self.__stack.append(now)

				now.parent = parent
				if now.parent:
					now.parent.children.append(now)
			
			elif "OFFSET" in values[0]:
				offset = []
				for i in range(1, len(values)):
					offset.append(float(values[i]))
				now.offset = offset
				for i in range(0, 2):
					now.oldTran[i, 3] = offset[i]
			
			elif "CHANNELS" in values[0]:
				now.channels = values[2:len(values)]
				now.idx[0] = self.channel_count
				now.idx[1] = self.channel_count + len(now.channels)
				self.channel_count += len(now.channels)

			elif "{" in values[0]:
				pass

			elif "}" in values[0]:
				now = now.parent
				if now:
					parent = now.parent

			elif "MOTION" in values[0]:
				motion = 1
			
			elif "Frames:" in values[0]:
				self.frames = int(values[1])
			
			elif "Frame" in values[0]:
				self.frametime = float(values[2])
		
			elif motion == 1:
				tmp = [float(val) for val in values]
				self.channel_data(self.__root, tmp)
				vals = []
				for val in values:
					vals.append(float(val))
				self.motions.append(vals)

	def channel_data(self, joint, data):
		joint.frames.append(data[:len(joint.channels)])
		data = data[len(joint.channels):]

		for child in joint.children:
			data = self.channel_data(child, data)
		return data

def drawModel(joint, cnt, draw):
	global animate, Character 
	
	pos = [0, 0, 0]
	R = np.identity(4)
	offset = np.array([float(joint.offset[0]),
			float(joint.offset[1]),
			float(joint.offset[2])])

	if animate == 1:
		for i in range(0, len(joint.channels)):
			channel = joint.channels[i]
			tmp = Character .motions[cnt][joint.idx[0] + i]
			R2 = np.identity(4)

			if channel.lower() == "xposition":
				pos[0] = tmp
			elif channel.lower() == "yposition":
				pos[1] = tmp
			elif channel.lower() == "zposition":
				pos[2] = tmp

			if channel.lower() == "xrotation":
				R2[1, 1] = np.cos(np.radians(tmp))
				R2[1, 2] = -np.sin(np.radians(tmp))
				R2[2, 1] = np.sin(np.radians(tmp))
				R2[2, 2] = np.cos(np.radians(tmp))
				R = np.dot(R, R2)
			elif channel.lower() == "yrotation":
				R2[0, 0] = np.cos(np.radians(tmp))
				R2[0, 2] = np.sin(np.radians(tmp))
				R2[2, 0] = -np.sin(np.radians(tmp))
				R2[2, 2] = np.cos(np.radians(tmp))
				R = np.dot(R, R2)
			elif channel.lower() == "zrotation":
				R2[0, 0] = np.cos(np.radians(tmp))
				R2[0, 1] = -np.sin(np.radians(tmp))
				R2[1, 0] = np.sin(np.radians(tmp))
				R2[1, 1] = np.cos(np.radians(tmp))
				R = np.dot(R, R2)

	glPushMatrix()
	glTranslatef(pos[0], pos[1], pos[2])

	if draw == 1:
		drawCube(joint.offset)

	glTranslatef(joint.offset[0], joint.offset[1], joint.offset[2])
	glMultMatrixf(R.T)

	for child in joint.children:
		drawModel(child, cnt, 1)
	glPopMatrix()

def drawCube(offset):
	glBegin(GL_QUADS)

	origin = np.array([0, 0, 0])
	offset = np.array(offset)
	upY = np.array([0., 1, 0.])
	p = [[[0]] * 4, [0] * 4]
	
	v1 = origin - offset
	v1 = v1 / (np.sqrt(np.dot(v1, v1)))

	v2 = np.cross(v1, upY)
	v2 = v2 / (np.sqrt(np.dot(v2, v2)))
	v2 *= 1.
	
	v3 = np.cross(v1, v2)
	v3 = v3 / (np.sqrt(np.dot(v3, v3)))
	v3 *= 1.

	p[0][0] = origin + v2
	p[1][0] = offset + v2
	
	p[0][1] = origin + v3
	p[1][1] = offset + v3
	
	p[0][2] = origin - v2
	p[1][2] = offset - v2
	
	p[0][3] = origin - v3
	p[1][3] = offset - v3

	for i in range(0, 2):
		glNormal3f(v1[0], v1[0], v1[0])
		for pos in p[i]:
			glVertex3f(pos[0], pos[1], pos[2])

	n1 = v2 + v3
	n1 = n1 / (np.sqrt(np.dot(n1, n1)))

	n2 = v2 - v3
	n2 = n2 / (np.sqrt(np.dot(n2, n2)))

	for i in range(0, 4):
		j = i + 1
		
		if i == 0:
			glNormal3f(n1[0], n1[1], n1[2])
		elif i == 1:
			glNormal3f(n2[0], n2[1], n2[2])
		elif i == 2:
			glNormal3f(-n1[0], -n1[1], -n1[2])
		else:
			glNormal3f(-n2[0], -n2[1], -n2[2])
			j = 0

		glVertex3f(p[0][i][0], p[0][i][1], p[0][i][2])
		glVertex3f(p[1][i][0], p[1][i][1], p[1][i][2])
		glVertex3f(p[1][j][0], p[1][j][1], p[1][j][2])
		glVertex3f(p[0][j][0], p[0][j][1], p[0][j][2])

	glEnd()

def drop_callback(window, _path):
    global path, cnt, animate, Character 

    path = ''.join(_path)
    cnt = 0
    animate = -1
    Character  = BVH(path)
    print_inform()

def print_inform():
    global path, Character 

    print("1.File name: " + path)
    print("2.Number of frames: " + str(Character .frames))
    print("3.FPS: " + str(1/Character .frametime))
    print("4.Number of joints: " + str(len(Character .name)))
    print("5.List of all joint names:")
    
    for name in Character .name:
        print(name ,end=" ")

def key_callback(window, key, scancode, action, mods):
    global cnt, animate
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_SPACE:
            if animate == 1:
                cnt = 0
            animate *= -1

def render(cnt):  #done
    global azimuth, elevation, distance
    global point, up, w, u, v
    global Character , animate

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 50)

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
    glEnable(GL_NORMALIZE)
    
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
    lightPos = (-3.,4.,-5.,1.)
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
    objectColor = (250.,150.,0.,1.)
    specularObjectColor = (1.,1.,1.,1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    if Character :
        glPushMatrix()
        
        if cnt == Character.frames:
            cnt = 0
        glScale(.02,.02,.02)
        drawModel(Character.root, cnt % Character.frames, 0)
        
        glPopMatrix()

    glDisable(GL_LIGHTING)


def key_callback(window, key, scancode, action, mods):
    global cnt, animate
    if action == glfw.PRESS:
        if key == glfw.KEY_SPACE:
            if animate == 1:
                cnt = 0
            animate *= -1

def main():
    global animate, cnt
    if not glfw.init():
        return

    window = glfw.create_window(800,800,"Class_Assignment3", None, None)
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
        render(cnt)
        glfw.swap_buffers(window)
        if animate == 1:
            cnt += 1
    glfw.terminate()

if __name__ == "__main__":
    main()
