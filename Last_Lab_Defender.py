from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLUT import GLUT_BITMAP_TIMES_ROMAN_24
import time

# Global variables 
camera_pos = (1000, 1000, 800)
# camera_pos = (600, -600,400)
# camera_pos = (0, -250, 120)
# camera_pos = (80, -150, 90)
# camera_pos = (-300, -200, 50)
# camera_pos = (0, 0, 800)
camera_look_at = (327,77,75)
axis_decision = (0, 0, 1)
window_height, window_width = 630, 1270
field_of_view = 90
GRID_LENGTH, GRID_WIDTH = 2250, 2250

class Last_Lab_Defender:
    def __init__(self):
        self.floor_right_max = -GRID_LENGTH//2
        self.floor_left_max = GRID_LENGTH//2
        self.floor_behind_max = -GRID_WIDTH//2
        self.floor_front_max = GRID_WIDTH//2
        self.initiate_all()

    def initiate_all(self):
        
        # game intro
        self.intro_starting_time = None
        self.game_started = False
        self.ongoing_game_restarted = False
        self.game_intro_ongoing = True 
        self.into_skipped = False
        self.intro_stage = 1


        # time related 
        self.level_1_time_limit = 10 #  60 seconds
        self.level_2_time_limit = 10 #  60 seconds
        self.start_time = time.time()
        self.remaining_time = self.level_1_time_limit
        self.time_passed = 0

        # game level 
        self.game_level = 1
        self.transition_pause = False
        self.transition_start = None

        # kill count
        self.total_kills = 0
        self.level_1_kill_limit = 30
        self.level_2_kill_limit = 40
        self.level_1_limit_crossed = False
        self.level_2_limit_crossed = False        

        # capsule informations (Positioned near the top-left positive axes)
        self.capsule_height = GRID_LENGTH // 10
        self.capsule_radius = GRID_WIDTH // 32
        self.capsule_position  = [self.floor_left_max - 260, self.floor_front_max - 260, 10]
        self.capsule_base_position = [self.floor_left_max - 260, self.floor_front_max - 260, 0]
        self.capsule_base_height = 10
        self.capsule_health = 10


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
        self.bullet_size = 6
        self.bullet_speed = 16
        self.all_bullets = []
        
        # --- ENEMY & PLAYER STATE VARIABLES ---
        self.player_health = 5  # "life line"
        self.normal_enemies_killed = 0
        
        self.enemies = []
        
        # SLOWER ENEMY SPEED
        self.enemy_speed = 0.75 
        
        # Increased Enemy Size
        self.enemy_body_radius = 35 
        self.enemy_head_radius = 25 
        
        # Floor alignment: Base Z is their radius so they sit exactly on the floor
        self.enemy_base_z = self.enemy_body_radius   

        # --- CONTINUOUS SPAWN TIMER ---
        # Tracks the last time a new enemy was timed-spawned (5-second interval)
        self.last_spawn_time = time.time()

        # --- ENEMY PROJECTILE STATE (Level 2+) ---
        # List of active enemy bullets; each entry is a dict identical in shape
        # to self.all_bullets so the same movement pattern can be reused.
        self.enemy_bullets = []
        # Enemy bullets travel slower than the player's bullets for fairness.
        # Reduced from 5 → 3.5 (~30% nerf) to widen the player's reaction window.
        self.enemy_bullet_speed = 3.5   # player bullet_speed is 16
        # Size of the rendered enemy bullet cube
        self.enemy_bullet_size = 8

        # --- CENTRALISED VOLLEY COORDINATOR (Level 2+) ---
        # Instead of every enemy firing independently (which causes bullet-hell),
        # a global timer selects 2-3 random normal enemies to fire a coordinated
        # volley every volley_interval seconds.
        self.enemy_volley_timer = time.time()
        self.volley_interval = 2.0  # seconds between volleys

        # --- PLAYER HIT TOLERANCE (Level 2+ damage mitigation) ---
        # Instead of losing HP on every single bullet hit, the player must
        # accumulate 5 hits before 1 HP is actually deducted.  This prevents
        # the rapid health drain visible in the Level 2 combat log.
        self.player_hit_tolerance = 0

        # --- LEVEL 3 FINAL BOSS STATE ---
        self.boss_spawned = False
        self.cannonballs = []
        self.cannonball_speed = 1.5
        self.cannonball_size = 45  # Increased drawing scale/radius
        self.consecutive_cannonballs_destroyed = 0

        #player-view
        self.first_person_view = False    

    def game_intro_1(self):
        global camera_pos, camera_look_at
        camera_pos = (900, 700,650)
        camera_look_at = (300, 200, 150)
        x = window_width//2-620
        top = window_height//2
        bottom = 30
        y_center = (top+bottom)//2
        # transition text
        transition_text = f"Our protagonist is the last of the guardians assigned for shielding a capsule containing a secret bio substance. "
        self.draw_text(x ,y_center + 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"Some aliens have already made it all the way to this realm in search of this. "
        self.draw_text(x  , y_center, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"They have obliterated all sorts of defenses and terminated all the guardians except the protagonist "
        self.draw_text(x  , y_center - 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)                
    def game_intro_2(self):
        global camera_pos,camera_look_at
        camera_pos = (-200, 650, 250)
        camera_look_at = (300, 200, 120)
        x = window_width//2-620
        top = window_height//2
        bottom = 30
        y_center = (top+bottom)//2
        # transition text
        transition_text = f"Aliens  have already made it all the way to this realm in search of the capsule "
        self.draw_text(x ,y_center + 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"They have obliterated all sorts of defenses  in their  path and terminated all the guardians. "
        self.draw_text(x  , y_center, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"Only the protagonist survives, who is now stuck with the capsule inside the room"
        self.draw_text(x  , y_center - 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)     
    def game_intro_3(self):
        global camera_pos, camera_look_at
        camera_pos = (320, 80, 170)
        camera_look_at = (300, 200, 140)
        x = window_width//2-620
        top = window_height//2
        bottom = 30
        y_center = (top+bottom)//2
        # transition text
        transition_text = f"Now our protagonist has to defend the capsule at any cost using a gunlike weapon to neutralize the enemies. "
        self.draw_text(x ,y_center + 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"Our guardian’s suit can automatically extract lifeline regenerating substances by killing some special aliens colored in red. "
        self.draw_text(x  , y_center, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"Furthermore, after a certain number of kills, his weapon can automatically upgrade to a better version with more efficiency."
        self.draw_text(x  , y_center - 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)     
    def game_intro_4(self):
        global camera_pos, camera_look_at
        camera_pos = (350, 250, 180)
        camera_look_at = (300,200,120)
        x = window_width//2-620
        top = window_height//2
        bottom = 30
        y_center = (top+bottom)//2
        # transition text
        transition_text = f"Aliens  sending the weak unarmed aliens initially to test the power of the threat "
        self.draw_text(x ,y_center + 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f"Within a timeframe if the protagonist proves to be resilient enough, they will send a more potent armed regiment."
        self.draw_text(x  , y_center, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)        
        transition_text = f" If the guardian remains unweavered, then the final boss of the aliens will take matters into its own hands."
        self.draw_text(x  , y_center - 60, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)   
    def game_intro(self):
        global camera_pos
        elapsed_time = time.time() - self.intro_starting_time
        if elapsed_time >= 4:
            self.intro_stage += 1
            self.intro_starting_time = time.time() 
        if self.intro_stage > 4:
            self.game_intro_ongoing = False
            self.game_started = True
            self.start_time = time.time()
            camera_pos = (1000, 1000, 800)
            self.first_person_view = True
            return
        # if elapsed_time > 6:
        #     return         
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()


        glDisable(GL_DEPTH_TEST)
        glColor3f(0.05,0.05,0.05)
        glColor3f(0.0, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(0, window_height//2)
        glVertex2f(window_width, window_height//2)
        glColor3f(0.1,0.4,0.1)        
        # glColor3f(0.0, 0.9, 0.7)
        glVertex2f(window_width, 30)
        glVertex2f(0, 30)
        glEnd()

        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        if self.intro_stage == 1:
            self.game_intro_1()
        elif  self.intro_stage == 2:
            self.game_intro_2()
        elif self.intro_stage == 3:
            self.game_intro_3()
        
        elif self.intro_stage == 4:
            self.game_intro_4()
        




    def time_control(self):
        self.time_passed  = time.time() - self.start_time
        current_limit = self.level_1_time_limit if self.game_level == 1 else self.level_2_time_limit
        self.remaining_time = max(0, current_limit - self.time_passed)
        if self.remaining_time <= 0 and not self.transition_pause:
            # showing transition  between levels
            self.transition_pause = True
            self.transition_start = time.time()

            self.enemies.clear()
            self.enemy_bullets.clear()
            self.all_bullets.clear()
            self.cannonballs.clear()
            # self.game_level_upgrader()
            # self.start_time = time.time()

    def display_time(self):
        if self.remaining_time > 59:
            time_left = "01:00"
            time_text = f"Remaining Time: {time_left}"
        else:
            time_left = int(self.remaining_time)
            time_text= f"Remaining Time: 00:{time_left}"

        self.draw_text(window_width - 250, window_height - 30, time_text )
    
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
        glRotatef(90, 1, 0 ,0)
        glRotate(45, 1, 0,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius*0.7,self.player_leg_height, 50, 20)
        glPopMatrix()

        # left forearm
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        glTranslatef(-30, -self.player_leg_height+18, self.player_body_height*2-6)
        glRotatef(90, 1, 0 ,0)
        glRotate(-25, 1, 0,0)
        glRotatef(45, 0, 1,0)
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
        glRotatef(90, 1, 0 ,0)
        glRotate(45, 1, 0,0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius*0.5,self.player_leg_height, 50, 20)
        glPopMatrix()     
           
        # right forearm
        glPushMatrix()
        glColor3f(240/255, 204/255, 173/255)
        glTranslatef(30, -self.player_leg_height+18, self.player_body_height*2-3)
        glRotatef(90, 1, 0 ,0)
        glRotate(-15, 1, 0,0)
        glRotatef(-45, 0, 1,0)
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
        glColor3f(90/255, 95/255, 100/255)
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
            glBegin(GL_QUADS)        
            glColor3f(4/255,5/255,5/255)    
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31/255,33/255,34/255)    
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)        
            glEnd()          
        elif axis_close == "+y" :
            glBegin(GL_QUADS)        
            glColor3f(34/255,36/255,37/255)    
            glVertex3f(self.floor_left_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glColor3f(78/255,82/255,86/255)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_front_max, grid_wall_height)
            glEnd()
        elif axis_close == "-y" :
            glBegin(GL_QUADS)        
            glColor3f(4/255,5/255,5/255)    
            glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31/255,33/255,34/255)    
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_behind_max, grid_wall_height)       
            glEnd()     
        elif axis_close == "-x":
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
        glColor3f(135/255, 175/255, 145/255)
        glVertex3f(self.floor_left_max,self.floor_front_max, 0)
        glColor3f(61/255, 66/255, 70/255)
        glVertex3f(self.floor_right_max,self.floor_front_max, 0)
        glColor3f(2/255,2/255,9/255)    
        glVertex3f(self.floor_right_max,self.floor_behind_max, 0)
        glColor3f(61/255, 66/255, 70/255)
        glVertex3f(self.floor_left_max,self.floor_behind_max, 0)
        glEnd()
        # drawing the grids
        for i in range(self.floor_left_max-2, self.floor_right_max+2, -GRID_LENGTH//15):
            glLineWidth(3)
            glBegin(GL_LINES)
            glColor3f(110/255, 118/255, 125/255)
            glVertex3f(i, self.floor_front_max-1 ,0)
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

    # --- ENEMY METHODS ---

    def get_random_spawn_coordinates(self):

        cap_x, cap_y, _ = self.capsule_position

        # Radius within which no enemy may spawn (protects the capsule start zone)
        exclusion_radius = 500

        # Minimum separation between a new spawn and every existing enemy
        min_enemy_separation = self.enemy_body_radius * 2.5

        # Safety cap so we never loop forever in a crowded arena
        max_attempts = 50

        # Keep a small margin from the walls so the enemy body never clips them
        margin = int(self.enemy_body_radius)
        x_min = self.floor_right_max + margin   # floor_right_max is the NEGATIVE X bound
        x_max = self.floor_left_max  - margin   # floor_left_max  is the POSITIVE X bound
        y_min = self.floor_behind_max + margin  # floor_behind_max is the NEGATIVE Y bound
        y_max = self.floor_front_max  - margin  # floor_front_max  is the POSITIVE Y bound

        for attempt in range(max_attempts):
            # --- Step 1: pick a random point anywhere in the arena ---
            ex = random.uniform(x_min, x_max)
            ey = random.uniform(y_min, y_max)

            # --- Step 2: exclusion-zone check (distance from capsule) ---
            dist_to_capsule = math.sqrt((ex - cap_x) ** 2 + (ey - cap_y) ** 2)
            if dist_to_capsule < exclusion_radius:
                # Too close to the capsule — try again
                continue

            # --- Step 3: overlap check against every active enemy ---
            too_close_to_enemy = False
            for existing_enemy in self.enemies:
                dist_to_enemy = math.sqrt(
                    (ex - existing_enemy['x']) ** 2 +
                    (ey - existing_enemy['y']) ** 2
                )
                if dist_to_enemy < min_enemy_separation:
                    too_close_to_enemy = True
                    break  # No need to check remaining enemies

            if too_close_to_enemy:
                # Overlaps an existing enemy — try again
                continue

            # Valid position found — return immediately
            return int(ex), int(ey)

        # Fallback: if every attempt failed (very crowded arena), return the
        # last generated point so spawning doesn't silently break.
        print(f"[SpawnWarning] Could not find a non-overlapping spawn after {max_attempts} attempts.")
        return int(ex), int(ey)

    def spawn_enemies(self):

        if self.game_level == 1:

            #Initial burst: fill an empty arena immediately
            if len(self.enemies) == 0:
                num_enemies = random.randint(6, 8)
                for _ in range(num_enemies):
                    ex, ey = self.get_random_spawn_coordinates()
                    self.enemies.append({
                        'x': ex, 'y': ey,
                        'z': self.enemy_base_z,
                        'base_z': self.enemy_base_z,          # Floor level
                        'run_cycle': random.uniform(0.0, 5.0),# Stagger animation
                        'type': 'normal',
                        'body_r': self.enemy_body_radius,
                        'head_r': self.enemy_head_radius,
                        # Teal/Ocean Blue: hex #007D8C → normalized floats
                        'color': (0.0, 125/255.0, 140/255.0)
                    })
                # Reset the timer so the first timed spawn waits a full 5 s
                # from when the initial burst was created, not from game start.
                self.last_spawn_time = time.time()

            # ── Continuous time-based spawn: 1 enemy every 5 seconds ──────────
            current_time = time.time()
            if current_time - self.last_spawn_time >= 5.0:
                ex, ey = self.get_random_spawn_coordinates()
                self.enemies.append({
                    'x': ex, 'y': ey,
                    'z': self.enemy_base_z,
                    'base_z': self.enemy_base_z,
                    'run_cycle': random.uniform(0.0, 5.0),
                    'type': 'normal',
                    'body_r': self.enemy_body_radius,
                    'head_r': self.enemy_head_radius,
                    'color': (0.0, 125/255.0, 140/255.0)
                })
                # Reset the spawn clock for the next 5-second window
                self.last_spawn_time = current_time
                print(f"[Spawn] Timed enemy spawned. Total active enemies: {len(self.enemies)}")

            # ── Special enemy: triggered every 20 normal kills ─────────────────
            if self.normal_enemies_killed >= 20:
                self.normal_enemies_killed -= 20  # Consume the 20-kill credit

                ex, ey = self.get_random_spawn_coordinates()
                self.enemies.append({
                    'x': ex, 'y': ey,
                    'z': self.enemy_base_z * 1.5,
                    'base_z': self.enemy_base_z * 1.5,
                    'run_cycle': random.uniform(0.0, 5.0),
                    'type': 'special',
                    'body_r': self.enemy_body_radius * 1.5,
                    'head_r': self.enemy_head_radius * 1.5,
                    'color': (1.0, 0.0, 0.0)   # Red — visually distinct
                })
                print(f"[Spawn] Special enemy spawned after 20 kills! Active enemies: {len(self.enemies)}")

        elif self.game_level == 2:
            # ═══════════════════════════════════════════════════════════════
            # LEVEL 2 SPAWN LOGIC
            # Same structure as Level 1 but enemies carry a shoot_timer and
            # use a darker navy colour (#004B54) to signal the difficulty jump.
            # Special enemies remain red and never receive a shoot_timer.
            # ═══════════════════════════════════════════════════════════════

            # ── Level 2 colour constants ───────────────────────────────────────
            # Mint / Emerald Green: hex #1bc476 → normalised floats
            L2_NORMAL_COLOR = (27/255.0, 196/255.0, 118/255.0)

            # ── Initial burst ──────────────────────────────────────────────────
            if len(self.enemies) == 0:
                num_enemies = random.randint(7, 10)  # Slightly larger wave in L2
                for _ in range(num_enemies):
                    ex, ey = self.get_random_spawn_coordinates()
                    self.enemies.append({
                        'x': ex, 'y': ey,
                        'z': self.enemy_base_z,
                        'base_z': self.enemy_base_z,
                        'run_cycle': random.uniform(0.0, 5.0),
                        'type': 'normal',
                        'body_r': self.enemy_body_radius,
                        'head_r': self.enemy_head_radius,
                        'color': L2_NORMAL_COLOR
                        # No individual shoot_timer — firing is handled by the
                        # centralised volley coordinator in update_enemy_combat().
                    })
                self.last_spawn_time = time.time()

            # ── Continuous timed spawn ─────────────────────────────────────────
            current_time = time.time()
            if current_time - self.last_spawn_time >= 5.0:
                ex, ey = self.get_random_spawn_coordinates()
                self.enemies.append({
                    'x': ex, 'y': ey,
                    'z': self.enemy_base_z,
                    'base_z': self.enemy_base_z,
                    'run_cycle': random.uniform(0.0, 5.0),
                    'type': 'normal',
                    'body_r': self.enemy_body_radius,
                    'head_r': self.enemy_head_radius,
                    'color': L2_NORMAL_COLOR
                    # No individual shoot_timer — volley coordinator handles firing.
                })
                self.last_spawn_time = current_time
                print(f"[L2 Spawn] Timed enemy spawned. Active: {len(self.enemies)}")

            # ── Special enemy (every 20 normal kills, still red, no gun) ───────
            if self.normal_enemies_killed >= 20:
                self.normal_enemies_killed -= 20

                ex, ey = self.get_random_spawn_coordinates()
                self.enemies.append({
                    'x': ex, 'y': ey,
                    'z': self.enemy_base_z * 1.5,
                    'base_z': self.enemy_base_z * 1.5,
                    'run_cycle': random.uniform(0.0, 5.0),
                    'type': 'special',           # Special enemies do NOT shoot
                    'body_r': self.enemy_body_radius * 1.5,
                    'head_r': self.enemy_head_radius * 1.5,
                    'color': (1.0, 0.0, 0.0)     # Always red, no shoot_timer
                })
                print(f"[L2 Spawn] Special enemy spawned! Active: {len(self.enemies)}")

        elif self.game_level == 3:
            # ═══════════════════════════════════════════════════════════════
            # LEVEL 3 SPAWN LOGIC: FINAL BOSS
            # ═══════════════════════════════════════════════════════════════
            if not self.boss_spawned and len(self.enemies) == 0:
                ex, ey = self.get_random_spawn_coordinates()
                self.enemies.append({
                    'x': ex, 'y': ey,
                    'z': self.enemy_base_z * 2.5,
                    'base_z': self.enemy_base_z * 2.5,
                    'run_cycle': 0.0,
                    'type': 'boss',
                    'body_r': self.enemy_body_radius * 2.5,
                    'head_r': self.enemy_head_radius * 2.5,
                    'color': (94/255.0, 4/255.0, 135/255.0) # Dark Purple
                })
                self.boss_spawned = True
                print("Final Boss Spawned!")

    def enemy_movement(self):
        target_x, target_y, _ = self.capsule_position
        player_x, player_y, _ = self.player_spawn_position
        enemies_to_remove = []
        
        for e_idx, enemy in enumerate(self.enemies):
            dx = target_x - enemy['x']
            dy = target_y - enemy['y']
            distance = math.sqrt(dx**2 + dy**2)
            
            # Cylinder Collision Detection: Vanish if touching the cylinder
            if distance < (self.capsule_radius + enemy['body_r']):
                enemies_to_remove.append(e_idx)
                self.capsule_health = max(0, self.capsule_health - 1)
                print(f"Capsule hit! Remaining health: {self.capsule_health}")
                continue # Skip moving this enemy as it's being removed
            
            # Player Collisioon Detection: Vanish if touching the player
            dx_p = player_x - enemy['x']
            dy_p = player_y - enemy['y']
            distance_p = math.sqrt(dx_p**2 + dy_p**2)
            if distance_p < (self.player_width + enemy['body_r']):
                enemies_to_remove.append(e_idx)
                self.player_health = max(0, self.player_health - 1)
                print(f"Player hit! Remaining health: {self.player_health}")
                continue # Skip moving this enemy as it's being removed

            # Normalize vector and move enemy towards the capsule
            if enemy['type'] == 'boss':
                # --- Final Boss Movement Correction ---
                # Strictly lock depth (Y-axis) to the far back wall and sweep horizontally (X-axis)
                
                margin = int(enemy['body_r'])
                x_min = self.floor_right_max + margin
                x_max = self.floor_left_max - margin
                
                # Lock base Y to the far back wall (opposite the player/capsule)
                base_y = self.floor_behind_max + margin + 100 # Add a small buffer

                # 1. Lateral Sweep (X-Axis Macro-Movement)
                if 'boss_direction_x' not in enemy:
                    enemy['boss_direction_x'] = 1  # 1 for right, -1 for left
                    enemy['y'] = base_y            # Initialize Y to locked back wall

                # Base horizontal sweep speed
                base_sweep_speed = self.enemy_speed * 1.5
                
                # 2. Evasive Strafing (Micro-Movement)
                enemy['run_cycle'] += 0.05
                
                # Erratic stuttering effect applied to the X sweep speed
                # math.cos() oscillates between -1 and 1, creating a juke/stutter effect
                speed_wobble = math.cos(enemy['run_cycle'] * 1.5) * base_sweep_speed * 1.2
                
                # Calculate new X position (Macro sweep + Micro wobble)
                new_x = enemy['x'] + (enemy['boss_direction_x'] * base_sweep_speed) + speed_wobble
                
                # Boundary bouncing (Toggle direction at edges)
                if new_x > x_max:
                    new_x = x_max
                    enemy['boss_direction_x'] = -1
                elif new_x < x_min:
                    new_x = x_min
                    enemy['boss_direction_x'] = 1
                    
                enemy['x'] = new_x
                
                # 3. Strict Depth Lock (Y-Axis Restraint)
                # A very slight depth wobble (+/- 20 units) to enhance the evasive feel
                # while strictly clamping the macro Y position so it never advances.
                depth_wobble = math.sin(enemy['run_cycle'] * 2.0) * 20.0
                enemy['y'] = base_y + depth_wobble

                # Bobbing animation (Z-axis)
                enemy['z'] = enemy['base_z'] + abs(math.sin(enemy['run_cycle'] * 2)) * 20
            else:
                if distance > 0:
                    enemy['x'] += (dx / distance) * self.enemy_speed
                    enemy['y'] += (dy / distance) * self.enemy_speed

                    # Bobbing animation (both levels)
                    enemy['run_cycle'] += 0.08
                    bounce_height = abs(math.sin(enemy['run_cycle'])) * 15
                    enemy['z'] = enemy['base_z'] + bounce_height

        # Safely remove enemies that hit the cylinder or player
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(self.enemies):
                self.enemies.pop(i)

    def bullet_enemy_collision(self):
        bullets_to_remove = []
        enemies_to_remove = []

        for b_idx, bullet in enumerate(self.all_bullets):
            bx, by, bz = bullet['bullet_coord']
            
            for e_idx, enemy in enumerate(self.enemies):
                if e_idx in enemies_to_remove: 
                    continue
                
                # Using 2D (X/Y) distance for collision so chest-high bullets 
                # hit ground-level enemies perfectly without flying over them
                dist_2d = math.sqrt((bx - enemy['x'])**2 + (by - enemy['y'])**2)
                
                if dist_2d < (enemy['body_r'] + self.bullet_size):
                    bullets_to_remove.append(b_idx)
                    enemies_to_remove.append(e_idx)
                    
                    if enemy['type'] == 'special':
                        if self.player_health < 5:
                            self.player_health += 1
                            print(f"Special Enemy Killed! Health increased to {self.player_health}")
                            
                    else:
                        self.normal_enemies_killed += 1
                    # increases the kill count 
                    self.total_kills += 1                        
                    if self.game_level == 1 and self.total_kills >= self.level_1_kill_limit:
                        self.level_1_limit_crossed = True
                    elif self.game_level == 2 and self.total_kills >= self.level_2_kill_limit:
                        self.level_2_limit_crossed = True                    
                    break  

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.all_bullets):
                self.all_bullets.pop(i)
                
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(self.enemies):
                self.enemies.pop(i)

    def display_kill_count(self):
        limit = self.level_1_kill_limit if self.game_level == 1 else self.level_2_kill_limit
        kill_text = f"Level {self.game_level} total Kills: {self.total_kills}/{limit}" 
        self.draw_text(window_width - 250, window_height - 60, kill_text)


    def draw_enemies(self):
        for enemy in self.enemies:
            ex, ey, ez = enemy['x'], enemy['y'], enemy['z']
            
            # Unpack color components for reuse across body parts
            cr, cg, cb = enemy['color']
            br = enemy['body_r']   # body radius — used as the arm scaling reference
            hr = enemy['head_r']   # head radius

            # ── Base push: all geometry inherits this translation so
            #    arms bob up/down with the existing run_cycle animation ──
            glPushMatrix()
            glTranslatef(ex, ey, ez)

            # ── Body (Sphere) ─────────────────────────────────────────
            glColor3f(cr, cg, cb)
            gluSphere(gluNewQuadric(), br, 30, 30)

            # ── Head (Sphere, raised above body) ──────────────────────
            glPushMatrix()
            glTranslatef(0, 0, br + hr - 5)
            glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)   # slightly darker shade
            gluSphere(gluNewQuadric(), hr, 30, 30)

            # --- Head Appendages ---
            if enemy['type'] == 'boss':
                # Two distinctly large horns for the massive Boss head
                h_base_r = hr * 0.4
                h_top_r  = hr * 0.1
                h_height = hr * 1.5
            else:
                h_base_r = hr * 0.22
                h_top_r  = 0.01
                h_height = hr * 0.8

            # Horn 1
            glPushMatrix()
            glTranslatef(-hr * 0.5, 0, hr * 0.6)
            glRotatef(-40, 0, 1, 0)
            glRotatef(-10, 1, 0, 0)
            gluCylinder(gluNewQuadric(), h_base_r, h_top_r, h_height, 15, 5)
            glPopMatrix()

            # Horn 2
            glPushMatrix()
            glTranslatef(hr * 0.5, 0, hr * 0.6)
            glRotatef(40, 0, 1, 0)
            glRotatef(-10, 1, 0, 0)
            gluCylinder(gluNewQuadric(), h_base_r, h_top_r, h_height, 15, 5)
            glPopMatrix()

            glPopMatrix()

            # ── Arm geometry parameters (scaled from body radius) ──────
            # shoulder_offset: how far left/right the shoulder sits from centre
            shoulder_offset = br * 1.1
            # shoulder_z: height of the shoulder joint on the body sphere
            shoulder_z     = br * 0.4
            # upper-arm length mirrors protagonist's player_leg_height ratio
            upper_arm_len  = br * 1.1
            # cylinder radii taper like the protagonist's arm
            arm_r_top      = br * 0.22   # top (shoulder end) radius
            arm_r_bot      = br * 0.15   # bottom (elbow end) radius
            forearm_r_top  = br * 0.18
            forearm_r_bot  = br * 0.11
            hand_r         = hr * 0.35   # hand sphere size

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # LEFT ARM  (negative X side, matching protagonist structure)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            # elbow offset (shared by both arms)
            elbow_z = -upper_arm_len * 0.65
            elbow_y = -upper_arm_len * 0.75

            # --- LEFT ARM (negative X side, matching protagonist structure) ---

            # Left shoulder joint sphere
            glPushMatrix()
            glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
            glTranslatef(-shoulder_offset, 0, shoulder_z)
            gluSphere(gluNewQuadric(), arm_r_top * 1.2, 20, 20)
            glPopMatrix()

            # Left upper-arm cylinder (rotated to hang downward at ~45 deg)
            glPushMatrix()
            glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
            glTranslatef(-shoulder_offset, 0, shoulder_z)
            glRotatef(90, 1, 0, 0)    # point cylinder along -Y (downward)
            glRotatef(45, 1, 0, 0)    # add 45 deg forward swing (protagonist match)
            gluCylinder(gluNewQuadric(), arm_r_top, arm_r_bot, upper_arm_len, 20, 5)
            glPopMatrix()

            # Left forearm
            glPushMatrix()
            glColor3f(cr * 0.85, cg * 0.85, cb * 0.85)
            glTranslatef(-shoulder_offset, elbow_y, elbow_z)
            glRotatef(90, 1, 0, 0)
            glRotatef(-25, 1, 0, 0)   # slight outward splay (protagonist match)
            glRotatef(45, 0, 1, 0)    # lateral twist
            gluCylinder(gluNewQuadric(), forearm_r_top, forearm_r_bot, upper_arm_len, 20, 5)
            glPopMatrix()

            # Left hand sphere at the wrist tip
            glPushMatrix()
            glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)
            glTranslatef(-shoulder_offset, elbow_y - upper_arm_len * 0.7, elbow_z - upper_arm_len * 0.5)
            gluSphere(gluNewQuadric(), hand_r, 20, 20)
            glPopMatrix()

            # --- RIGHT ARM (positive X side, mirrored) ---

            # Right shoulder joint sphere
            glPushMatrix()
            glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
            glTranslatef(shoulder_offset, 0, shoulder_z)
            gluSphere(gluNewQuadric(), arm_r_top * 1.2, 20, 20)
            glPopMatrix()

            # Right upper-arm cylinder
            glPushMatrix()
            glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
            glTranslatef(shoulder_offset, 0, shoulder_z)
            glRotatef(90, 1, 0, 0)
            glRotatef(45, 1, 0, 0)
            gluCylinder(gluNewQuadric(), arm_r_top, arm_r_bot, upper_arm_len, 20, 5)
            glPopMatrix()

            # Right forearm
            glPushMatrix()
            glColor3f(cr * 0.85, cg * 0.85, cb * 0.85)
            glTranslatef(shoulder_offset, elbow_y, elbow_z)
            glRotatef(90, 1, 0, 0)
            glRotatef(-15, 1, 0, 0)   # slightly different splay (protagonist match)
            glRotatef(-45, 0, 1, 0)   # mirror lateral twist
            gluCylinder(gluNewQuadric(), forearm_r_top, forearm_r_bot, upper_arm_len, 20, 5)
            glPopMatrix()

            # Right hand sphere
            glPushMatrix()
            glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)
            glTranslatef(shoulder_offset, elbow_y - upper_arm_len * 0.7, elbow_z - upper_arm_len * 0.5)
            gluSphere(gluNewQuadric(), hand_r, 20, 20)
            glPopMatrix()

            # ── Level 2 Gun Barrel (right hand, normal enemies only) ───────────
            # Gated behind game_level >= 2 AND enemy type check so that:
            #   • Level 1 enemies are visually unchanged.
            #   • Special enemies (red healers) never carry a weapon.
            if enemy['type'] == 'boss':
                # Boss Legs
                leg_len = br * 1.5
                leg_r = br * 0.3
                
                # Left Leg
                glPushMatrix()
                glColor3f(cr * 0.7, cg * 0.7, cb * 0.7)
                glTranslatef(-br * 0.5, 0, -br * 0.8)
                glRotatef(90, 1, 0, 0)
                gluCylinder(gluNewQuadric(), leg_r, leg_r*0.8, leg_len, 20, 5)
                glPopMatrix()

                # Right Leg
                glPushMatrix()
                glColor3f(cr * 0.7, cg * 0.7, cb * 0.7)
                glTranslatef(br * 0.5, 0, -br * 0.8)
                glRotatef(90, 1, 0, 0)
                gluCylinder(gluNewQuadric(), leg_r, leg_r*0.8, leg_len, 20, 5)
                glPopMatrix()
                
                # Massive Cannon on right hand
                cannon_base_r = hand_r * 1.5
                cannon_tip_r = hand_r * 1.2
                cannon_length = br * 2.0
                wrist_x = shoulder_offset
                wrist_y = elbow_y - upper_arm_len * 0.7
                wrist_z = elbow_z - upper_arm_len * 0.5

                glPushMatrix()
                glColor3f(0.15, 0.15, 0.15)
                glTranslatef(wrist_x, wrist_y, wrist_z)
                glRotatef(-90, 1, 0, 0)
                gluCylinder(gluNewQuadric(), cannon_base_r, cannon_tip_r, cannon_length, 20, 5)
                glPopMatrix()
            elif self.game_level >= 2 and enemy['type'] != 'special':
                # Gun barrel: a thin gluCylinder attached at the wrist tip,
                # pointing forward (along +Y in the enemy's local space).
                gun_base_r  = hand_r * 0.45   # matches arm taper style
                gun_tip_r   = hand_r * 0.25
                gun_length  = br * 1.4         # barrel extends past the hand

                # Anchor at the same wrist-tip position as the right hand sphere
                wrist_x = shoulder_offset
                wrist_y = elbow_y - upper_arm_len * 0.7
                wrist_z = elbow_z - upper_arm_len * 0.5

                glPushMatrix()
                # Dark metallic grey for the weapon
                glColor3f(0.25, 0.25, 0.28)
                glTranslatef(wrist_x, wrist_y, wrist_z)
                # Rotate so the cylinder points along -Y (forward direction)
                # gluCylinder naturally points along +Z, so we rotate -90° around X
                glRotatef(-90, 1, 0, 0)
                gluCylinder(gluNewQuadric(), gun_base_r, gun_tip_r, gun_length, 12, 4)
                glPopMatrix()

            glPopMatrix()  # base enemy transform

    def update_enemy_combat(self):

        if self.game_level >= 2:
            if self.game_level == 3:
                current_time = time.time()
                if current_time - self.enemy_volley_timer < self.volley_interval * 1.5:
                    return
                self.enemy_volley_timer = current_time
                
                bosses = [e for e in self.enemies if e['type'] == 'boss']
                if not bosses:
                    return
                boss = bosses[0]
                
                px, py, _ = self.player_spawn_position
                ex_pos, ey_pos = boss['x'], boss['y']
                bz = boss['base_z']
                shoot_dx = px - ex_pos
                shoot_dy = py - ey_pos
                shoot_dist = math.sqrt(shoot_dx ** 2 + shoot_dy ** 2)
                if shoot_dist > 0:
                    shoot_dx /= shoot_dist
                    shoot_dy /= shoot_dist
                    self.cannonballs.append({
                        'coord': [ex_pos, ey_pos, bz],
                        'direction': [shoot_dx, shoot_dy],
                        'health': 5
                    })
                print(f"[Boss] Fired Cannonball. Active: {len(self.cannonballs)}")
                return

            current_time = time.time()
            if current_time - self.enemy_volley_timer < self.volley_interval:
                return  # Volley cooldown hasn't elapsed yet

            # ── Reset the global volley timer ──────────────────────────────────
            self.enemy_volley_timer = current_time

            # ── Filter to only normal enemies (special enemies never shoot) ────
            normal_enemies = [e for e in self.enemies if e['type'] == 'normal']
            if not normal_enemies:
                return  # Nothing to fire from

            # ── Select 2-3 random shooters from the pool ──────────────────────
            # If fewer than 2 normal enemies are alive, all of them fire.
            volley_count = random.randint(2, 3)
            shooters = random.sample(
                normal_enemies,
                min(volley_count, len(normal_enemies))
            )

            # ── Each selected enemy fires one bullet at the player ─────────────
            px, py, _ = self.player_spawn_position

            for enemy in shooters:
                ex_pos, ey_pos = enemy['x'], enemy['y']
                # Bullet spawns at body-centre height so it visually exits the gun
                bz = enemy['base_z']

                # Normalised 2-D direction vector: enemy → player
                shoot_dx = px - ex_pos
                shoot_dy = py - ey_pos
                shoot_dist = math.sqrt(shoot_dx ** 2 + shoot_dy ** 2)

                if shoot_dist > 0:  # Guard against division by zero
                    shoot_dx /= shoot_dist
                    shoot_dy /= shoot_dist
                    self.enemy_bullets.append({
                        'bullet_coord': [ex_pos, ey_pos, bz],
                        'bullet_direction': [shoot_dx, shoot_dy]
                    })

            print(f"[Volley] {len(shooters)} enemies fired. Active bullets: {len(self.enemy_bullets)}")

    def update_enemy_bullets(self):

        bullets_to_remove = []
        for i, bullet in enumerate(self.enemy_bullets):
            coord = bullet['bullet_coord']
            direction = bullet['bullet_direction']

            new_x = coord[0] + self.enemy_bullet_speed * direction[0]
            new_y = coord[1] + self.enemy_bullet_speed * direction[1]

            # Keep the bullet if it is still inside the arena
            if (-GRID_WIDTH // 2 < new_x < GRID_WIDTH // 2 and
                    -GRID_WIDTH // 2 < new_y < GRID_WIDTH // 2):
                bullet['bullet_coord'][0] = new_x
                bullet['bullet_coord'][1] = new_y
            else:
                bullets_to_remove.append(i)  # Out of bounds — queue for removal

        # Remove out-of-bounds bullets in reverse order to preserve indices
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.enemy_bullets):
                self.enemy_bullets.pop(i)

    def draw_enemy_bullets(self):

        for bullet in self.enemy_bullets:
            bx, by, bz = bullet['bullet_coord']
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glColor3f(1.0, 0.5, 0.0)   # Orange — distinct from player's yellow
            glutSolidCube(self.enemy_bullet_size)
            glPopMatrix()

    def enemy_bullet_player_collision(self):

        if self.game_level < 2:
            return  # Short-circuit: Level 1 has no enemy bullets

        bullets_to_remove = []
        px, py, _ = self.player_spawn_position

        for i, bullet in enumerate(self.enemy_bullets):
            bx, by, _ = bullet['bullet_coord']
            dist_2d = math.sqrt((bx - px) ** 2 + (by - py) ** 2)

            # Hit radius: player silhouette + half the bullet cube diagonal
            hit_radius = self.player_width + self.enemy_bullet_size / 2
            if dist_2d < hit_radius:
                bullets_to_remove.append(i)

                # --- Hit Tolerance Logic ---
                # Each confirmed bullet hit increments the tolerance counter.
                # Only after 5 accumulated hits does the player lose 1 HP.
                self.player_hit_tolerance += 1

                if self.player_hit_tolerance >= 5:
                    self.player_health = max(0, self.player_health - 1)
                    self.player_hit_tolerance = 0  # Reset after HP deduction
                    print(f"[EnemyBullet] 5 hits absorbed! HP reduced to {self.player_health}")

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.enemy_bullets):
                self.enemy_bullets.pop(i)

    def update_cannonballs(self):
        balls_to_remove = []
        for i, cb in enumerate(self.cannonballs):
            cb['coord'][0] += self.cannonball_speed * cb['direction'][0]
            cb['coord'][1] += self.cannonball_speed * cb['direction'][1]
            if not (-GRID_WIDTH // 2 < cb['coord'][0] < GRID_WIDTH // 2 and -GRID_WIDTH // 2 < cb['coord'][1] < GRID_WIDTH // 2):
                balls_to_remove.append(i)
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(self.cannonballs):
                self.cannonballs.pop(i)

    def draw_cannonballs(self):
        for cb in self.cannonballs:
            bx, by, bz = cb['coord']
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glColor3f(109/255.0, 242/255.0, 220/255.0) # Bright Cyan/Teal
            glutSolidSphere(self.cannonball_size, 16, 16)
            glPopMatrix()

    def cannonball_collisions(self):
        if self.game_level != 3: return
        balls_to_remove = []
        player_bullets_to_remove = []
        px, py, _ = self.player_spawn_position
        cx, cy, _ = self.capsule_position

        for i, cb in enumerate(self.cannonballs):
            if i in balls_to_remove: continue
            bx, by, _ = cb['coord']
            
            # Cannonball vs Capsule
            dist_capsule = math.sqrt((bx - cx)**2 + (by - cy)**2)
            if dist_capsule < (self.capsule_radius + self.cannonball_size):
                self.capsule_health = max(0, self.capsule_health - 3) # x3 damage
                balls_to_remove.append(i)
                print(f"[Cannonball] Hit capsule! Health: {self.capsule_health}")
                continue

            # Cannonball vs Player
            dist_player = math.sqrt((bx - px)**2 + (by - py)**2)
            if dist_player < (self.player_width + self.cannonball_size):
                self.player_health -= 2 # bypass hit tolerance
                balls_to_remove.append(i)
                print(f"[Cannonball] Hit player! Health: {self.player_health}")
                continue
                
            # Cannonball vs Player Bullets
            for j, pb in enumerate(self.all_bullets):
                if j in player_bullets_to_remove: continue
                pbx, pby, _ = pb['bullet_coord']
                dist_bullet = math.sqrt((bx - pbx)**2 + (by - pby)**2)
                if dist_bullet < (self.cannonball_size + self.bullet_size):
                    player_bullets_to_remove.append(j)
                    cb['health'] -= 1
                    if cb['health'] <= 0:
                        balls_to_remove.append(i)
                        
                        # --- Consecutive Health Reward Mechanic ---
                        self.consecutive_cannonballs_destroyed += 1
                        print(f"[Cannonball] Destroyed! Streak: {self.consecutive_cannonballs_destroyed}")
                        
                        if self.consecutive_cannonballs_destroyed == 2:
                            self.player_health += 2
                            self.consecutive_cannonballs_destroyed = 0
                            print(f"[Reward] 2 Cannonballs destroyed! Player health: {self.player_health}")
                    break

        for j in sorted(player_bullets_to_remove, reverse=True):
            if j < len(self.all_bullets):
                self.all_bullets.pop(j)
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(self.cannonballs):
                self.cannonballs.pop(i)

    # --- END ENEMY METHODS ---
    def draw_health_bar(self, x, y, width, height, current, maximum, fill_color):
        # Background bar (Grey) - always visible
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(x, y, 0)
        glVertex3f(x + width, y, 0)
        glVertex3f(x + width, y + height, 0)
        glVertex3f(x, y + height, 0)
        glEnd()
        
        # Fill (colored) showing remaining health
        if current > 0:
            fill_width = width * (min(current, maximum) / maximum)
            if current < 3:
                fill_color = (1.0, 0.2, 0.2)
                glColor3f(fill_color[0], fill_color[1], fill_color[2])
            elif current < 4:
                fill_color = (1.0, 0.6, 0.3)
                glColor3f(fill_color[0], fill_color[1], fill_color[2])
            else:
                glColor3f(fill_color[0], fill_color[1], fill_color[2])
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + fill_width, y, 0)
            glVertex3f(x + fill_width, y + height, 0)
            glVertex3f(x, y + height, 0)
            glEnd()

    def draw_hud(self):
        glDisable(GL_DEPTH_TEST)  # Disable depth test for 2D HUD
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        bar_w = 200
        bar_h = 25

        #player health bar text
        life_text = f"Player HP:"
        self.draw_text(30, window_height - 25, life_text, GLUT_BITMAP_HELVETICA_18)

        #capsule health bar text
        life_text = f"Capsule HP:"
        self.draw_text(30, 60, life_text, GLUT_BITMAP_HELVETICA_18)

        # Player bar — top-left, green
        self.draw_health_bar(
            x=30,
            y=window_height - 60,
            width=bar_w,
            height=bar_h,
            current= self.player_health,
            maximum=5,
            fill_color=(0.2, 0.9, 0.3)
        )

        # Capsule bar — bottom-left, cyan
        self.draw_health_bar(
            x= 30,
            y=25,
            width=bar_w,
            height=bar_h,
            current= self.capsule_health,
            maximum= 5,
            fill_color=(0.2, 0.8, 1.0)
        )
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST) # Re-enable depth test

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            # Set up an orthographic projection that matches window coordinates
            gluOrtho2D(0, window_width, 0, window_height)  # left, right, bottom, top

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glColor3f(1, 1, 1)
            # Draw text at (x, y) in screen coordinates
            glRasterPos2f(x, y)
            for ch in text:
                glutBitmapCharacter(font, ord(ch))
            
            # Restore original projection and modelview matrices
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

    def draw_elements(self):
        self.draw_lab()     
        self.weapon_upgrade()
        self.draw_capsule()
        self.draw_protagonist()
        self.draw_bullets()
        self.draw_enemies()
        # Draw enemy projectiles (no-op in Level 1 as the list stays empty)
        self.draw_enemy_bullets()
        if self.game_level == 3:
            self.draw_cannonballs()

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
        
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
                self.first_person_view = not self.first_person_view
                if self.first_person_view:
                    print("First-Person View: ON")
                else:
                    print("Third-Person View: ON")


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
        elif key == b"e":
            self.player_angle -= 5
        elif key == b"q":
            self.player_angle += 5
        elif key == b"a":
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            right_x = -dir_y
            right_y = dir_x
            move_x, move_y = x+right_x*self.player_speed, y+right_y*self.player_speed
            if (-GRID_LENGTH//2)+25<=move_x<=(GRID_LENGTH//2)-25 and (-GRID_WIDTH//2)+25<=move_y<=(GRID_WIDTH//2)-25:
                x = move_x
                y = move_y
                self.player_spawn_position = (x, y, z)             
        elif key == b"d":
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            right_x = -dir_y
            right_y = dir_x
            move_x, move_y = x-right_x*self.player_speed, y-right_y*self.player_speed
            if (-GRID_LENGTH//2)+25<=move_x<=(GRID_LENGTH//2)-25 and (-GRID_WIDTH//2)+25<=move_y<=(GRID_WIDTH//2)-25:
                x = move_x
                y = move_y
                self.player_spawn_position = (x, y, z)                       
        #  This part if for manually changing the level for checking the changes appearing
        # elif key == b"n":
        #     self.game_level_upgrader(False)
        # elif key == b"m":
        #     self.game_level_upgrader()

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
    def weapon_upgrade(self, level = 1):

        if self.level_1_limit_crossed and self.game_level == 2:
            self.level_weapon_head_color = (0/255, 200/255, 255/255)
            self.level_weapon_handle_color = (120/255, 255/255, 255/255)
            self.bullet_speed = 55
        elif self.level_2_limit_crossed   and self.game_level == 3:
            self.level_weapon_head_color = (255/255, 60/255, 120/255)
            self.level_weapon_handle_color = (255/255, 120/255, 180/255)  
            self.bullet_speed = 80
        else:
            self.level_weapon_head_color = (170/255, 120/255, 255/255)
            self.level_weapon_handle_color = (200/255, 180/255, 255/255)            


    def display_level(self):
            level_text = f"Level: {self.game_level}"
            self.draw_text(window_width - window_width//2, window_height - 30, level_text )   


    # level decider
    def game_level_upgrader(self, up = True):
        if up:
            self.game_level = self.game_level + 1 if self.game_level < 3 else self.game_level
            
            self.total_kills = 0

            # ── Bug Fix: Instant State Wipe on Level Up ──────────────────────
            # Prevent surviving entities from bleeding into the new level
            self.enemies.clear()
            self.enemy_bullets.clear()
            self.all_bullets.clear()
            
            if hasattr(self, 'cannonballs'):
                self.cannonballs.clear()

        # else:
            # self.game_level = self.game_level - 1 if self.game_level > 0 else self.game_level

        
        self.weapon_upgrade()
        # self.enemy_upgrade()
        glutPostRedisplay()

    def level_transitions(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()


        glDisable(GL_DEPTH_TEST)
        glColor3f(0,0.4,0)
        glBegin(GL_QUADS)
        glVertex2f(0, window_height//2 + 50)
        glVertex2f(window_width, window_height//2+ 50)
        glColor3f(0.2,1,0.2)        
        glVertex2f(window_width, window_height//2 - 50)
        glVertex2f(0, window_height//2-50)
        glEnd()

        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        # transition text
        if self.game_level < 3:
            transition_text =  f"Level {self.game_level} Cleared !!!!\n Next Level: {self.game_level + 1}"
        else:
            transition_text = f"End"
        self.draw_text(window_width//2 - 150 , window_height//2 - 10, transition_text,GLUT_BITMAP_TIMES_ROMAN_24)

    def animation(self):
        glutPostRedisplay()

    def setupCamera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(field_of_view, window_width/window_height, 0.1, 4500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if self.first_person_view:
            x, y, z = self.player_spawn_position
            dir_x = math.cos(math.radians(self.player_angle-90))
            dir_y = math.sin(math.radians(self.player_angle-90))
            eye_height = self.player_body_height * 3.2
            eye_forward_offset = self.player_head_radius + 12
            eye_x = x + dir_x * eye_forward_offset
            eye_y = y + dir_y * eye_forward_offset
            eye_z = z + eye_height
            look_dist = 100
            look_x = eye_x + look_dist * dir_x
            look_y = eye_y + look_dist * dir_y
            look_z = eye_z
            gluLookAt(eye_x, eye_y, eye_z,
                    look_x, look_y,look_z,
                    0, 0, 1)
        else:
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
        self.display_level()
        if self.game_level < 3:
            self.display_time()
        self.display_kill_count()
        self.draw_elements()
        self.draw_hud()

        if self.game_intro_ongoing:
            # self.intro_starting_time = time.time()
            # self.game_intro()
            if self.intro_starting_time is None:
                self.intro_starting_time = time.time()
            self.game_intro()
        else:

            if not self.transition_pause:
                if self.game_level < 3:
                    self.time_control()
                self.spawn_enemies()
                self.enemy_movement()
                self.bullet_enemy_collision()
                self.update_enemy_combat()
                self.update_enemy_bullets()
                self.enemy_bullet_player_collision()
                self.bullet_movement()

                if self.game_level == 3:
                    self.update_cannonballs()
                    self.cannonball_collisions()

            if self.transition_pause:
                self.level_transitions()
                if time.time() - self.transition_start >= 3:
                    self.transition_pause = False
                    self.game_level_upgrader()
                    self.start_time = time.time()
                    self.last_spawn_time = time.time()
                    self.enemy_volley_timer = time.time()
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