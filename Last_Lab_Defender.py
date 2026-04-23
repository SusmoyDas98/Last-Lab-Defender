from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
# Global variables 
camera_pos = (-800, -800, 700)
camera_look_at = (0,0,50)
axis_decision = (0, 0, 1)
window_height, window_width = 800, 1200
field_of_view = 80
GRID_LENGTH, GRID_WIDTH = 1275, 1275


class Last_Lab_Defender:
    def __init__(self):
        self.floor_right_max = -GRID_LENGTH//2
        self.floor_left_max = GRID_LENGTH//2
        self.floor_behind_max = -GRID_WIDTH//2
        self.floor_front_max = GRID_WIDTH//2

    def draw_walls(self, axis_close):     
        length = GRID_LENGTH // 8
        width = GRID_WIDTH // 13         
        grid_wall_height = length   

        if axis_close == "+x":
            # wall on x
            # glColor3f(78/255,203/255,298/255)
            glBegin(GL_QUADS)        
            glColor3f(4/255,5/255,5/255)    
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31/255,33/255,34/255)    
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)        
            glEnd()          
        elif axis_close == "+y" :
            # wall on y
            # glColor3f(85/255,201/255,122/255)
            glBegin(GL_QUADS)        
            glColor3f(34/255,36/255,37/255)    
            glVertex3f(self.floor_left_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glColor3f(78/255,82/255,86/255)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_front_max, grid_wall_height)
            glEnd()
        elif axis_close == "-y" :
            # wall on -y
            # glColor3f(78/255,127/255,198/255)
            glBegin(GL_QUADS)        
            glColor3f(4/255,5/255,5/255)    
            glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31/255,33/255,34/255)    
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_behind_max, grid_wall_height)       
            glEnd()     
        elif axis_close == "-x":
            # wall on -x side
            glBegin(GL_QUADS)
            glColor3f(34/255,36/255,37/255)            
            glVertex3f(self.floor_left_max, self.floor_front_max, 0)
            glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
            glColor3f(78/255,82/255,86/255)
            glVertex3f(self.floor_left_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_front_max, grid_wall_height)      
            glEnd()  

    def draw_lab(self):
        # drawing the floor
        glBegin(GL_QUADS)
        # glColor3f(139/255, 145/255, 150/255)
        glColor3f(135/255, 175/255, 145/255)
        glVertex3f(self.floor_left_max,self.floor_front_max, 0)
        glColor3f(61/255, 66/255, 70/255)
        # glColor3f(34/255,56/255,37/255) 
        glVertex3f(self.floor_right_max,self.floor_front_max, 0)
        # glColor3f(41/255, 42/255, 45/255)
        glColor3f(2/255,2/255,9/255)    
        glVertex3f(self.floor_right_max,self.floor_behind_max, 0)
        glColor3f(61/255, 66/255, 70/255)
        # glColor3f(34/255,56/255,37/255) 
        glVertex3f(self.floor_left_max,self.floor_behind_max, 0)
        glEnd()
        # drawing the grids
        for i in range(self.floor_left_max-1, self.floor_right_max+1, -GRID_LENGTH//15):
            glBegin(GL_LINES)
            glColor3f(110/255, 118/255, 125/255)
            glVertex3f(i, self.floor_front_max-1 ,0)
            glColor3f(12/255,12/255,9/255)    
            glVertex3f(i, self.floor_behind_max+1 ,0)
            glEnd()
        for i in range(self.floor_front_max-1, self.floor_behind_max, -GRID_WIDTH//15):
            glBegin(GL_LINES)
            glColor3f(110/255, 118/255, 125/255)
            glVertex3f(self.floor_left_max-1 , i,0)
            glColor3f(12/255,12/255,9/255)    
            glVertex3f( self.floor_right_max-1, i ,0)
            glEnd()            
        # drawing the walls
        x, y ,z = camera_pos
        wall_distance_from_camera = {
            "+x" : math.sqrt(((x + GRID_WIDTH//2)**2) + ((y-0)**2) + ((z-0)**2)),
            "+y" : math.sqrt(((x - 0)**2) + ((y- GRID_LENGTH//2)**2) + ((z-0)**2)),
            "-y":math.sqrt(((x - 0)**2) + ((y + GRID_LENGTH//2)**2) + ((z-0)**2)),
            "-x":math.sqrt(((x - GRID_WIDTH//2)**2) + ((y-0)**2) + ((z-0)**2)),            
        }
        wall_distance_from_camera = dict(sorted(wall_distance_from_camera.items(),key = lambda item:item[1],  reverse=True))
        for  key, value in wall_distance_from_camera.items():
            self.draw_walls(key)

    def specialKeyListener(self, key, x, y):
        global camera_pos ,field_of_view
        x, y, z = camera_pos
        if key == GLUT_KEY_LEFT:
            angle_of_rotation = math.radians(1)
            old_x = x
            old_y = y
            x = old_x*math.cos(angle_of_rotation) - old_y*math.sin(angle_of_rotation)
            y = old_x*math.sin(angle_of_rotation) + old_y*math.cos(angle_of_rotation)

        elif key == GLUT_KEY_RIGHT:
            angle_of_rotation = math.radians(-1)
            old_x = x
            old_y = y
            x = old_x*math.cos(angle_of_rotation) - old_y*math.sin(angle_of_rotation)
            y = old_x*math.sin(angle_of_rotation) + old_y*math.cos(angle_of_rotation)

        elif key == GLUT_KEY_UP:
            z += 5
        elif key == GLUT_KEY_DOWN:
            z -= 5
        camera_pos = (x, y, z)
        glutPostRedisplay()


    def draw_elements(self):
        self.draw_lab()        
    def setupCamera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(field_of_view, window_width/window_height, 0.1, 2500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y, z = camera_pos
        look_x, look_y,look_z = camera_look_at
        respect_to_x, respect_to_y, respect_to_z = axis_decision
        gluLookAt(x, y, z,
                  look_x, look_y,look_z,
                  respect_to_x, respect_to_y, respect_to_z)        
    def showScreen(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, window_width, window_height)
        self.setupCamera()     
        self.draw_elements()
        glutSwapBuffers()





def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0,0)
    window = glutCreateWindow(b"Last Lab Defender")
    # glEnable(GL_DEPTH_TEST)
    game = Last_Lab_Defender()
    glutDisplayFunc(game.showScreen)
    # glutKeyboardFunc(game.KeyboardListener)
    glutSpecialFunc(game.specialKeyListener)
    # glutMouseFunc(game.MouseListener)
    # glutIdleFunc(game.animation)
    glutMainLoop()

if __name__ == "__main__":
    main()
