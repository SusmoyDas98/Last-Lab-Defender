from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
# Global variables 
camera_pos = (377, -450, 50)
camera_look_at = (377,77,75)
# camera_pos = (800, 800, 700)
# camera_look_at = (0,0,50)
axis_decision = (0, 0, 1)
window_height, window_width = 600, 1250
field_of_view = 50
GRID_LENGTH, GRID_WIDTH = 1275, 1275


class Last_Lab_Defender:
    def __init__(self):
        self.floor_right_max = -GRID_LENGTH//2
        self.floor_left_max = GRID_LENGTH//2
        self.floor_behind_max = -GRID_WIDTH//2
        self.floor_front_max = GRID_WIDTH//2

        # game level 
        self.game_level = 1

        # capsule informations
        self.capsule_height = GRID_LENGTH // 10
        self.capsule_radius = GRID_WIDTH // 32
        self.capsule_position  = [self.floor_left_max - 260, self.floor_front_max - 260, 10]
        self.capsule_base_position = [self.floor_left_max - 260, self.floor_front_max - 260, 0]
        self.capsule_base_height = 10

        # protagonist informations
        self.player_angle = 0
        self.player_spawn_position = (self.floor_left_max - 260, self.floor_front_max - 600, 0)
        self.player_body_height = 40
        self.player_head_radius = 20
        self.shoe_radius = 5
        self.player_leg_height = self.player_body_height
        self.player_leg_max_radius = 10
        self.player_width = 25
        self.gun_height = 45
        self.gun_facing = [0,0,0]
        self.player_speed = 10
              
        # bullets information
        self.bullet_size = 5
        self.bullet_speed = 6
        self.all_bullets = []
    

    def draw_protagonist(self):
        p_x,  p_y , p_z =  self.player_spawn_position
        glPushMatrix()
        glTranslatef(p_x, p_y,p_z)
        glRotatef(self.player_angle, 0,0, 1)


        # player body
        glPushMatrix()
        glColor3f(225/255, 225/255, 230/255)
        glTranslatef(0, 0, (2*self.player_body_height))
        glRotatef(5, 1,0,0)
        glScalef(1.2, 0.6, 1.5)
        glutSolidCube(self.player_body_height)
        glPopMatrix()  


        # shoes
        # left shoes
        glPushMatrix()
        glColor3f(0,0,0)
        glTranslatef(-10, -5, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(),self.shoe_radius,80, 80) 
        glPopMatrix()

        # left shoe
        glPushMatrix()
        glColor3f(0,0,0)
        glTranslatef(-12, 0, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(),self.shoe_radius,80, 80) 
        glPopMatrix()        
        # right shoe
        glPushMatrix()
        glColor3f(0,0,0)
        glTranslatef(+12, 0, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(),self.shoe_radius,80, 80) 
        glPopMatrix()       


        # legs
        # left leg
        glPushMatrix()
        glColor3f(60/255, 70/255, 80/255)      
        glTranslatef(-12, 0, +10) 
        gluCylinder(gluNewQuadric(),self.player_leg_max_radius*(0.5), self.player_leg_max_radius, self.player_leg_height, 50, 20)
        glPopMatrix()
        
        # right leg
        glPushMatrix()
        glColor3f(60/255, 70/255, 80/255)      
        glTranslatef(12, 0, +10) 
        gluCylinder(gluNewQuadric(),self.player_leg_max_radius*(0.5), self.player_leg_max_radius, self.player_leg_height, 50, 20)
        glPopMatrix()


        # head
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        glTranslatef(0,-12, self.player_body_height*3.2)
        gluSphere( gluNewQuadric(), self.player_head_radius, 80, 80)
        glPopMatrix()


        # hat
        glPushMatrix()
        glColor3f(51/255, 51/255, 51/255)
        glTranslatef(0,-12, self.player_body_height*3.5)
        glRotatef(-200,1,0,0)
        glScalef(1.05, 1.08, 0.6)

        gluSphere( gluNewQuadric(), self.player_head_radius, 80, 80)

        glPopMatrix()


        # hands
        # hand start 
        glPushMatrix()
        glColor3f(196/255, 196/255, 196/255)
        glTranslatef(-30, 0, self.player_body_height*2+self.player_leg_height-self.player_head_radius)
        gluSphere(gluNewQuadric(), self.player_head_radius//2, 80, 80)        
        glPopMatrix()
        # left hand
        glPushMatrix()
        glColor3f(196/255, 196/255, 196/255)
        glTranslatef(-30, 0, self.player_body_height*2+self.player_leg_height-self.player_head_radius)
        # glRotatef(-90, 0, 1,0)
        glRotatef(90, 1, 0 ,0)
        glRotate(45, 1, 0,0)
        # glRotatef(90, 0, 1,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius*0.7,self.player_leg_height, 50, 20)
        glPopMatrix()

        # left forearm
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        # glColor3f(1,1,0)
        glTranslatef(-30, -self.player_leg_height+18, self.player_body_height*2-6)
        # glRotatef(-90, 0, 1,0)
        glRotatef(90, 1, 0 ,0)
        glRotate(-25, 1, 0,0)
        glRotatef(45, 0, 1,0)
        # glRotatef(90, 0, 1,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius-2, self.player_leg_max_radius*0.5,self.player_leg_height, 50, 20)
        glPopMatrix()        


        # right arm,
        # hand start 
        glPushMatrix()
        glColor3f(196/255, 196/255, 196/255)
        glTranslatef(30, 0, self.player_body_height*2+self.player_leg_height-self.player_head_radius)
        gluSphere(gluNewQuadric(), self.player_head_radius//2, 80, 80)        
        glPopMatrix()      
        # right hand  
        glPushMatrix()
        glColor3f(196/255, 196/255, 196/255)
        glTranslatef(30, 0, self.player_body_height*2+self.player_leg_height-self.player_head_radius)
        # glRotatef(-90, 0, 1,0)
        glRotatef(90, 1, 0 ,0)
        glRotate(45, 1, 0,0)

        # glRotatef(90, 0, 1,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius*0.5,self.player_leg_height, 50, 20)
        glPopMatrix()     
           
        # right forearm
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        # glColor3f(1,1,0)
        glTranslatef(30, -self.player_leg_height+18, self.player_body_height*2-3)
        # glRotatef(-90, 0, 1,0)
        glRotatef(90, 1, 0 ,0)
        glRotate(-15, 1, 0,0)
        glRotatef(-45, 0, 1,0)
        # glRotatef(90, 0, 1,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius-2, self.player_leg_max_radius*0.5,self.player_leg_height, 50, 20)
        glPopMatrix()  


        # left hand wrist 
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        glTranslatef(0, -50, self.player_leg_height+self.player_body_height*1.5-14)
        gluSphere(gluNewQuadric(), self.player_head_radius//2, 80, 20)
        glPopMatrix()        

        
        # weapon back
        glPushMatrix()
        # glColor3f(170/255, 220/255, 255/255)
        glColor3f(self.level_weapon_head_color[0], self.level_weapon_head_color[1], self.level_weapon_head_color[2])
        glTranslatef(0, -35, self.player_leg_height+self.player_body_height*1.5)
        gluSphere(gluNewQuadric(), self.player_head_radius//2.5, 80, 20)
        glPopMatrix()        


        # Player weapon 
        glPushMatrix()
        glColor3f(self.level_weapon_head_color[0], self.level_weapon_head_color[1], self.level_weapon_head_color[2])
        glTranslatef(0, -35, self.player_leg_height+self.player_body_height*1.5)
        dir_x = math.cos(math.radians(self.player_angle-90))
        dir_y = math.sin(math.radians(self.player_angle-90))
        self.gun_facing = [p_x+ dir_x*(self.gun_height+20), p_y + dir_y*(self.gun_height+20), p_z+self.player_leg_height+self.player_body_height*1.5]
        glRotatef(90, 1, 0,0)
        gluCylinder(gluNewQuadric(), self.shoe_radius*1.5, self.shoe_radius, self.player_leg_height*2, 50, 80)
        glPopMatrix()

        # weapon handle
        glPushMatrix()
        glColor3f(self.level_weapon_handle_color[0], self.level_weapon_handle_color[1], self.level_weapon_handle_color[2])
        glTranslatef(0, -45, self.player_leg_height+self.player_body_height-5)
        glRotatef(15, 1, 0, 0)
        gluCylinder(gluNewQuadric(), self.shoe_radius*1.5, self.shoe_radius, self.player_leg_height-10, 50, 80)
        glPopMatrix()

        glPopMatrix()
        
    def bullet_movement(self):
        for i in self.all_bullets:
            bullet_coord = i["bullet_coord"]
            bullet_direction = i["bullet_direction"]
            x_move = bullet_coord[0] + self.bullet_speed * bullet_direction[0]
            y_move = bullet_coord[1] + self.bullet_speed * bullet_direction[1]
            if (-GRID_WIDTH//2 < x_move < GRID_WIDTH//2 and -GRID_WIDTH//2 < y_move < GRID_WIDTH//2) :
                bullet_coord[0] = x_move; bullet_coord[1] = y_move    
                i["bullet_coord"] =  bullet_coord
            else:                 
                self.all_bullets.remove(i)

                




    def draw_bullets(self):
        for i in range(len(self.all_bullets)):
            x, y, z = self.all_bullets[i]['bullet_coord']
            dir_x, dir_y = self.all_bullets[i]['bullet_direction'] 
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(1, 1, 0)
            glutSolidCube(self.bullet_size)
            glPopMatrix()
            glutPostRedisplay()

            

    def draw_capsule(self):
        cap_x, cap_y, cap_z = self.capsule_base_position
        glPushMatrix()
        glTranslatef(cap_x, cap_y, cap_z)        
        # glColor3f(55/255, 60/255, 65/255)
        glColor3f(90/255, 95/255, 100/255)
        # glColor3f(0,1,1)
        gluCylinder(gluNewQuadric(), self.capsule_radius*1.5, self.capsule_radius,self.capsule_base_height, 50, 20)
        glPopMatrix()

        cap_x, cap_y, cap_z = self.capsule_position
        glPushMatrix()
        glTranslatef(cap_x, cap_y, cap_z)        
        glColor3f(120/255, 255/255, 200/255)
        gluCylinder(gluNewQuadric(), self.capsule_radius, self.capsule_radius,self.capsule_height, 50, 20)

        glPopMatrix()                

    def draw_walls(self, axis_close):     
        length = GRID_LENGTH // 7
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
        for i in range(self.floor_left_max-2, self.floor_right_max+2, -GRID_LENGTH//15):
            glLineWidth(3)
            glBegin(GL_LINES)
            glColor3f(110/255, 118/255, 125/255)
            glVertex3f(i, self.floor_front_max-1 ,0)
            glColor3f(110/255, 118/255, 125/255)
            glColor3f(12/255,12/255,9/255)    
            glVertex3f(i, self.floor_behind_max+1 ,0)
            glEnd()
        for i in range(self.floor_front_max-2, self.floor_behind_max+2, -GRID_WIDTH//15):
            glBegin(GL_LINES)
            glColor3f(110/255, 118/255, 125/255)
            glVertex3f(self.floor_left_max-1 , i,0)
            glColor3f(12/255,12/255,9/255)    
            glVertex3f( self.floor_right_max+1, i ,0)
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


    def draw_elements(self):
        self.draw_lab()     
        self.weapon_upgrade()
        self.draw_capsule()
        self.draw_protagonist()
        self.draw_bullets()


    # controls
    def MouseListener(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            x, y, z = self.gun_facing
            dir_x = math.cos(math.radians(self.player_angle-90))
            dir_y = math.sin(math.radians(self.player_angle-90))
            self.all_bullets.append({
                'bullet_coord': [x, y, z],
                'bullet_direction' : [dir_x, dir_y]
            })


    def KeyboardListener(self, key, x, y):
        global field_of_view
        x, y, z = self.player_spawn_position
        if key ==b"z":
            field_of_view -= 2
        elif key == b"x":
            field_of_view += 2
        elif key == b"w":
            dir_x = math.cos(math.radians(self.player_angle-90))
            dir_y = math.sin(math.radians(self.player_angle-90))
            move_x, move_y = x+dir_x*self.player_speed, y+dir_y*self.player_speed
            self.gun_facing[0] += dir_x * self.player_speed
            self.gun_facing[1] += dir_y * self.player_speed
            if (-GRID_WIDTH//2 < self.gun_facing[0]  + self.gun_height< GRID_WIDTH//2 and  -GRID_WIDTH//2 <self.gun_facing[1]  + self.gun_height < GRID_WIDTH//2 ) and (-GRID_WIDTH//2 < move_x < GRID_WIDTH//2 and  -GRID_WIDTH//2 < move_y < GRID_WIDTH//2 ):
                x = move_x
                y = move_y
            self.player_spawn_position = (x, y, z)
        elif key == b"s":
            dir_x = math.cos(math.radians(self.player_angle-90))
            dir_y = math.sin(math.radians(self.player_angle-90))
            move_x, move_y = x-dir_x*self.player_speed, y-dir_y*self.player_speed
            self.gun_facing[0] -= dir_x * self.player_speed
            self.gun_facing[1] -= dir_y * self.player_speed
            if (-GRID_WIDTH//2 < self.gun_facing[0]  + self.gun_height< GRID_WIDTH//2 and  -GRID_WIDTH//2 <self.gun_facing[1]  + self.gun_height < GRID_WIDTH//2 ) and (-GRID_WIDTH//2 < move_x < GRID_WIDTH//2 and  -GRID_WIDTH//2 < move_y < GRID_WIDTH//2 ):
                x = move_x
                y = move_y
            self.player_spawn_position = (x, y, z)            
        elif key == b"d":
            self.player_angle -= 5
        elif key == b"a":
            self.player_angle += 5

        #  This part if for manually changing the level for checking the changes appearing
        elif key == b"n":
            self.game_level_upgrader(False)
        elif key == b"m":
            self.game_level_upgrader()

        glutPostRedisplay()
            

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

    # weapon upgrade:
    def weapon_upgrade(self):
        if self.game_level == 1:
            self.level_weapon_head_color = (170/255, 120/255, 255/255)
            self.level_weapon_handle_color = (200/255, 180/255, 255/255)
        elif self.game_level == 2:
            self.level_weapon_head_color = (0/255, 200/255, 255/255)
            self.level_weapon_handle_color = (120/255, 255/255, 255/255)
        elif self.game_level == 3:
            self.level_weapon_head_color = (255/255, 60/255, 120/255)
            self.level_weapon_handle_color = (255/255, 120/255, 180/255)  

    # level decider
    def game_level_upgrader(self, up = True):
        if up:
            self.game_level = self.game_level + 1 if self.game_level < 3 else self.game_level
        else:
            self.game_level = self.game_level - 1 if self.game_level > 0 else self.game_level
        self.weapon_upgrade()
        glutPostRedisplay()



    def animation(self):
        glutPostRedisplay()

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
        # call the functions 
        self.draw_elements()
        self.bullet_movement()
        glutSwapBuffers()





def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0,0)
    window = glutCreateWindow(b"Last Lab Defender")
    glEnable(GL_DEPTH_TEST)
    game = Last_Lab_Defender()
    glutDisplayFunc(game.showScreen)
    glutKeyboardFunc(game.KeyboardListener)
    glutSpecialFunc(game.specialKeyListener)
    glutMouseFunc(game.MouseListener)
    glutIdleFunc(game.animation)
    glutMainLoop()

if __name__ == "__main__":
    main()
