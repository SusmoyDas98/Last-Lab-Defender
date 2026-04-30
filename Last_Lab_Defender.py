from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import time

# Global variables 
camera_pos = (800, 800, 700)
camera_look_at = (327,77,75)
axis_decision = (0, 0, 1)
window_height, window_width = 600, 1250
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

        # time related 
        self.level_1_time_limit = 60 #  60 seconds
        self.level_2_time_limit = 60 #  60 seconds
        self.start_time = time.time()

        # game level 
        self.game_level = 1

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
        self.bullet_size = 8
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

        #player-view
        self.first_person_view = False     


    def time_control(self):
        self.time_passed  = time.time() - self.start_time
        self.remaining_time = max(0, self.level_1_time_limit - self.time_passed)
        if self.remaining_time <= 0:
            self.game_level_upgrader()
            self.start_time = time.time()

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
        # The cylinder is at the Top-Left corner (Left Max, Front Max).
        # We will spawn enemies in the other three corners of the arena.
        corners = [
            # 1. Top-Right Corner
            (self.floor_right_max + 50, self.floor_right_max + 350, 
             self.floor_front_max - 350, self.floor_front_max - 50),
            
            # 2. Bottom-Left Corner
            (self.floor_left_max - 350, self.floor_left_max - 50, 
             self.floor_behind_max + 50, self.floor_behind_max + 350),
             
            # 3. Bottom-Right Corner (Opposite)
            (self.floor_right_max + 50, self.floor_right_max + 350, 
             self.floor_behind_max + 50, self.floor_behind_max + 350)
        ]
        
        # Pick one of the 3 valid corners randomly
        chosen_corner = random.choice(corners)
        
        # Generate random x and y within that specific corner
        ex = random.randint(chosen_corner[0], chosen_corner[1])
        ey = random.randint(chosen_corner[2], chosen_corner[3])
        
        return ex, ey

    def spawn_enemies(self):
        if self.game_level == 1:
            if len(self.enemies) == 0:
                num_enemies = random.randint(6, 8)
                for _ in range(num_enemies):
                    ex, ey = self.get_random_spawn_coordinates()
                    
                    self.enemies.append({
                        'x': ex, 'y': ey, 
                        'z': self.enemy_base_z, 
                        'base_z': self.enemy_base_z, # Floor level
                        'run_cycle': random.uniform(0.0, 5.0), # Randomize animation start
                        'type': 'normal',
                        'body_r': self.enemy_body_radius,
                        'head_r': self.enemy_head_radius,
                        # Teal/Ocean Blue: hex #007D8C → normalized floats
                        'color': (0.0, 125/255.0, 140/255.0)
                    })
                    
            if self.normal_enemies_killed >= 20:
                self.normal_enemies_killed -= 20 
                
                # Special enemies also spawn in one of the 3 valid corners
                ex, ey = self.get_random_spawn_coordinates()
                
                self.enemies.append({
                    'x': ex, 'y': ey, 
                    'z': self.enemy_base_z * 1.5, 
                    'base_z': self.enemy_base_z * 1.5,
                    'run_cycle': random.uniform(0.0, 5.0),
                    'type': 'special',
                    'body_r': self.enemy_body_radius * 1.5, 
                    'head_r': self.enemy_head_radius * 1.5,
                    'color': (1.0, 0.0, 0.0)
                })

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
            if distance > 0:
                enemy['x'] += (dx / distance) * self.enemy_speed
                enemy['y'] += (dy / distance) * self.enemy_speed
                
                # Slower Bobbing Animation scaled for larger bodies
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

            glPopMatrix()  # base enemy transform

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
        elif key == b"d":
            self.player_angle -= 5
        elif key == b"a":
            self.player_angle += 5
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

        # else:
            # self.game_level = self.game_level - 1 if self.game_level > 0 else self.game_level

        
        self.weapon_upgrade()
        # self.enemy_upgrade()
        glutPostRedisplay()

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
        
        # show levels
        self.display_level()

        # time functions 
        if self.game_level < 3:
            self.time_control()
            self.display_time()

        # kill count 
        self.display_kill_count()


        # Enemy calls
        self.spawn_enemies()
        self.enemy_movement()
        self.bullet_enemy_collision()
        
        # call the functions 
        self.draw_elements()
        self.bullet_movement()

        self.draw_hud()
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
