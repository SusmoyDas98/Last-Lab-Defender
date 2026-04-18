from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
# Global variables 
camera_pos = (800, -800, 700)
camera_look_at = (0,0,50)
axis_decision = (0, 0, 1)
window_height, window_width = 800, 1200
field_of_view = 45
GRID_LENGTH, GRID_WIDTH = 780, 780

class Last_Lab_Defender:
    def __init__(self):
        pass
    def draw_lab(self):
        pass
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
        self.draw_lab()
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
    # glutSpecialFunc(game.specialKeyListener)
    # glutMouseFunc(game.MouseListener)
    # glutIdleFunc(game.animation)
    glutMainLoop()

if __name__ == "__main__":
    main()
