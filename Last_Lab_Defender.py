from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import time

# Global variables
camera_pos = (1000, 1000, 800)
camera_look_at = (327, 77, 75)
axis_decision = (0, 0, 1)
window_height, window_width = 630, 1270
field_of_view = 90
GRID_LENGTH, GRID_WIDTH = 2250, 2250


class Last_Lab_Defender:
    def __init__(self):
        self.floor_right_max = -GRID_LENGTH // 2
        self.floor_left_max = GRID_LENGTH // 2
        self.floor_behind_max = -GRID_WIDTH // 2
        self.floor_front_max = GRID_WIDTH // 2
        self.initiate_all()

    def initiate_all(self):

        # game intro (multi-stage from Doc 2)
        self.intro_starting_time = None
        self.game_started = False
        self.ongoing_game_restarted = False
        self.game_intro_ongoing = True
        self.into_skipped = False
        self.intro_stage = 1

        # time related
        self.level_1_time_limit = 40  # seconds
        self.level_2_time_limit = 60
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

        # capsule
        self.capsule_height = GRID_LENGTH // 10
        self.capsule_radius = GRID_WIDTH // 32
        self.capsule_position = [self.floor_left_max - 260, self.floor_front_max - 260, 10]
        self.capsule_base_position = [self.floor_left_max - 260, self.floor_front_max - 260, 0]
        self.capsule_base_height = 10
        self.capsule_health = 10

        # protagonist
        self.player_angle = 0
        self.player_spawn_position = (self.floor_left_max - 260, self.floor_front_max - 600, 0)
        self.player_body_height = 40
        self.player_head_radius = 20
        self.shoe_radius = 5
        self.player_leg_height = self.player_body_height
        self.player_leg_max_radius = 10
        self.player_width = 25
        self.gun_height = 45
        self.gun_facing = [0, 0, 0]
        self.player_speed = 10

        # bullets
        self.bullet_size = 6
        self.bullet_speed = 16
        self.all_bullets = []

        # --- ENEMY & PLAYER STATE ---
        self.player_health = 5
        self.normal_enemies_killed = 0
        self.normal_enemy_kills_for_special = 0

        self.enemies = []

        #nerfed speed for dense swarms
        self.enemy_speed = 0.85
        self.enemy_body_radius = 35
        self.enemy_head_radius = 25
        self.enemy_base_z = self.enemy_body_radius

        # spawn timer
        self.last_spawn_time = time.time()

        # enemy projectiles (Level 2+)
        self.enemy_bullets = []
        self.enemy_bullet_speed = 3.5
        self.enemy_bullet_size = 8

        # volley coordinator (Level 2+)
        self.enemy_volley_timer = time.time()
        self.volley_interval = 2.0

        # player hit tolerance
        self.player_hit_tolerance = 0

        # Level 3 boss state
        self.boss_spawned = False
        self.cannonballs = []
        self.cannonball_speed = 7
        self.cannonball_size = 45
        self.consecutive_cannonballs_destroyed = 0

        # player view
        self.first_person_view = False

        # pause + game over
        self.paused = False
        self.pause_start_time = None
        self.game_over = False
        self.game_won = False

        # Cheat mode
        self.cheat_mode_active = False

        #magazine
        self.mag_size = 20
        self.ammo_mag = self.mag_size

    # GAME INTRO 
    def game_intro_1(self):
        global camera_pos, camera_look_at
        camera_pos = (900, 700, 650)
        camera_look_at = (300, 200, 150)
        x = window_width // 2 - 620
        top = window_height // 2
        bottom = 30
        y_center = (top + bottom) // 2
        self.draw_text(x, y_center + 60,
                       "Our protagonist is the last of the guardians assigned for shielding a capsule containing a secret bio substance. ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center,
                       "Some aliens have already made it all the way to this realm in search of this. ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center - 60,
                       "They have obliterated all sorts of defenses and terminated all the guardians except the protagonist ",
                       GLUT_BITMAP_HELVETICA_18)

    def game_intro_2(self):
        global camera_pos, camera_look_at
        camera_pos = (-200, 650, 250)
        camera_look_at = (300, 200, 120)
        x = window_width // 2 - 620
        top = window_height // 2
        bottom = 30
        y_center = (top + bottom) // 2
        self.draw_text(x, y_center + 60,
                       "Aliens  have already made it all the way to this realm in search of the capsule ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center,
                       "They have obliterated all sorts of defenses  in their  path and terminated all the guardians. ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center - 60,
                       "Only the protagonist survives, who is now stuck with the capsule inside the room",
                       GLUT_BITMAP_HELVETICA_18)

    def game_intro_3(self):
        global camera_pos, camera_look_at
        camera_pos = (320, 80, 170)
        camera_look_at = (300, 200, 140)
        x = window_width // 2 - 620
        top = window_height // 2
        bottom = 30
        y_center = (top + bottom) // 2
        self.draw_text(x, y_center + 60,
                       "Now our protagonist has to defend the capsule at any cost using a gunlike weapon to neutralize the enemies. ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center,
                       "Our guardian's suit can automatically extract lifeline regenerating substances by killing some special aliens colored in red. ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center - 60,
                       "Furthermore, after a certain number of kills, his weapon can automatically upgrade to a better version with more efficiency.",
                       GLUT_BITMAP_HELVETICA_18)

    def game_intro_4(self):
        global camera_pos, camera_look_at
        camera_pos = (350, 250, 180)
        camera_look_at = (300, 200, 120)
        x = window_width // 2 - 620
        top = window_height // 2
        bottom = 30
        y_center = (top + bottom) // 2
        self.draw_text(x, y_center + 60,
                       "Aliens  sending the weak unarmed aliens initially to test the power of the threat ",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center,
                       "Within a timeframe if the protagonist proves to be resilient enough, they will send a more potent armed regiment.",
                       GLUT_BITMAP_HELVETICA_18)
        self.draw_text(x, y_center - 60,
                       " If the guardian remains unweavered, then the final boss of the aliens will take matters into its own hands.",
                       GLUT_BITMAP_HELVETICA_18)

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

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, window_width, 0, window_height, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glColor3f(0.0, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(0, window_height // 2)
        glVertex2f(window_width, window_height // 2)
        glColor3f(0.1, 0.4, 0.1)
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
        elif self.intro_stage == 2:
            self.game_intro_2()
        elif self.intro_stage == 3:
            self.game_intro_3()
        elif self.intro_stage == 4:
            self.game_intro_4()

    def time_control(self):
        self.time_passed = time.time() - self.start_time
        current_limit = self.level_1_time_limit if self.game_level == 1 else self.level_2_time_limit
        self.remaining_time = max(0, current_limit - self.time_passed)
        if self.remaining_time <= 0 and not self.transition_pause:
            self.transition_pause = True
            self.transition_start = time.time()
            self.enemies.clear()
            self.enemy_bullets.clear()
            self.all_bullets.clear()
            self.cannonballs.clear()

    def display_time(self):
        if self.remaining_time > 59:
            time_text = "Remaining Time: 01:00"
        else:
            time_text = f"Remaining Time: 00:{int(self.remaining_time)}"
        self.draw_text(window_width - 250, window_height - 30, time_text)

    def draw_protagonist(self):
        p_x, p_y, p_z = self.player_spawn_position
        glPushMatrix()
        glTranslatef(p_x, p_y, p_z)
        glRotatef(self.player_angle, 0, 0, 1)

        # body
        glPushMatrix()
        glColor3f(225 / 255, 225 / 255, 230 / 255)
        glTranslatef(0, 0, (2 * self.player_body_height))
        glRotatef(5, 1, 0, 0)
        glScalef(1.2, 0.6, 1.5)
        glutSolidCube(self.player_body_height)
        glPopMatrix()

        # shoes
        glPushMatrix()
        glColor3f(0, 0, 0)
        glTranslatef(-10, -5, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(), self.shoe_radius, 80, 80)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0, 0)
        glTranslatef(-12, 0, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(), self.shoe_radius, 80, 80)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0, 0)
        glTranslatef(+12, 0, 5)
        glScalef(1.5, 2.5, 1.5)
        gluSphere(gluNewQuadric(), self.shoe_radius, 80, 80)
        glPopMatrix()

        # legs
        glPushMatrix()
        glColor3f(60 / 255, 70 / 255, 80 / 255)
        glTranslatef(-12, 0, +10)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius * 0.5, self.player_leg_max_radius,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(60 / 255, 70 / 255, 80 / 255)
        glTranslatef(12, 0, +10)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius * 0.5, self.player_leg_max_radius,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        # head
        glPushMatrix()
        glColor3f(240 / 255, 204 / 255, 173 / 255)
        glTranslatef(0, -12, self.player_body_height * 3.2)
        gluSphere(gluNewQuadric(), self.player_head_radius, 80, 80)
        glPopMatrix()

        # hat
        glPushMatrix()
        glColor3f(51 / 255, 51 / 255, 51 / 255)
        glTranslatef(0, -12, self.player_body_height * 3.5)
        glRotatef(-200, 1, 0, 0)
        glScalef(1.05, 1.08, 0.6)
        gluSphere(gluNewQuadric(), self.player_head_radius, 80, 80)
        glPopMatrix()

        # arms
        glPushMatrix()
        glColor3f(196 / 255, 196 / 255, 196 / 255)
        glTranslatef(-30, 0, self.player_body_height * 2 + self.player_leg_height - self.player_head_radius)
        gluSphere(gluNewQuadric(), self.player_head_radius // 2, 80, 80)
        glPopMatrix()

        glPushMatrix()
        glColor3f(196 / 255, 196 / 255, 196 / 255)
        glTranslatef(-30, 0, self.player_body_height * 2 + self.player_leg_height - self.player_head_radius)
        glRotatef(90, 1, 0, 0)
        glRotate(45, 1, 0, 0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius * 0.7,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(240 / 255, 204 / 255, 173 / 255)
        glTranslatef(-30, -self.player_leg_height + 18, self.player_body_height * 2 - 6)
        glRotatef(90, 1, 0, 0)
        glRotate(-25, 1, 0, 0)
        glRotatef(45, 0, 1, 0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius - 2, self.player_leg_max_radius * 0.5,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(196 / 255, 196 / 255, 196 / 255)
        glTranslatef(30, 0, self.player_body_height * 2 + self.player_leg_height - self.player_head_radius)
        gluSphere(gluNewQuadric(), self.player_head_radius // 2, 80, 80)
        glPopMatrix()

        glPushMatrix()
        glColor3f(196 / 255, 196 / 255, 196 / 255)
        glTranslatef(30, 0, self.player_body_height * 2 + self.player_leg_height - self.player_head_radius)
        glRotatef(90, 1, 0, 0)
        glRotate(45, 1, 0, 0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius, self.player_leg_max_radius * 0.5,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(240 / 255, 204 / 255, 173 / 255)
        glTranslatef(30, -self.player_leg_height + 18, self.player_body_height * 2 - 3)
        glRotatef(90, 1, 0, 0)
        glRotate(-15, 1, 0, 0)
        glRotatef(-45, 0, 1, 0)
        gluCylinder(gluNewQuadric(), self.player_leg_max_radius - 2, self.player_leg_max_radius * 0.5,
                    self.player_leg_height, 50, 20)
        glPopMatrix()

        # weapon wrist
        glPushMatrix()
        glColor3f(240 / 255, 204 / 255, 173 / 255)
        glTranslatef(0, -50, self.player_leg_height + self.player_body_height * 1.5 - 14)
        gluSphere(gluNewQuadric(), self.player_head_radius // 2, 80, 20)
        glPopMatrix()

        # weapon back
        glPushMatrix()
        glColor3f(self.level_weapon_head_color[0], self.level_weapon_head_color[1], self.level_weapon_head_color[2])
        glTranslatef(0, -35, self.player_leg_height + self.player_body_height * 1.5)
        gluSphere(gluNewQuadric(), self.player_head_radius // 2.5, 80, 20)
        glPopMatrix()

        # weapon barrel
        glPushMatrix()
        glColor3f(self.level_weapon_head_color[0], self.level_weapon_head_color[1], self.level_weapon_head_color[2])
        glTranslatef(0, -35, self.player_leg_height + self.player_body_height * 1.5)
        dir_x = math.cos(math.radians(self.player_angle - 90))
        dir_y = math.sin(math.radians(self.player_angle - 90))
        self.gun_facing = [
            p_x + dir_x * (self.gun_height + 20),
            p_y + dir_y * (self.gun_height + 20),
            p_z + self.player_leg_height + self.player_body_height * 1.5
        ]
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), self.shoe_radius * 1.5, self.shoe_radius, self.player_leg_height * 2, 50, 80)
        glPopMatrix()

        # weapon handle
        glPushMatrix()
        glColor3f(self.level_weapon_handle_color[0], self.level_weapon_handle_color[1],
                  self.level_weapon_handle_color[2])
        glTranslatef(0, -45, self.player_leg_height + self.player_body_height - 5)
        glRotatef(15, 1, 0, 0)
        gluCylinder(gluNewQuadric(), self.shoe_radius * 1.5, self.shoe_radius, self.player_leg_height - 10, 50, 80)
        glPopMatrix()

        glPopMatrix()

    def bullet_movement(self):
        for i in self.all_bullets:
            bullet_coord = i["bullet_coord"]
            bullet_direction = i["bullet_direction"]
            x_move = bullet_coord[0] + self.bullet_speed * bullet_direction[0]
            y_move = bullet_coord[1] + self.bullet_speed * bullet_direction[1]
            if (-GRID_WIDTH // 2 < x_move < GRID_WIDTH // 2 and -GRID_WIDTH // 2 < y_move < GRID_WIDTH // 2):
                bullet_coord[0] = x_move
                bullet_coord[1] = y_move
                i["bullet_coord"] = bullet_coord
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
        glColor3f(90 / 255, 95 / 255, 100 / 255)
        gluCylinder(gluNewQuadric(), self.capsule_radius * 1.5, self.capsule_radius, self.capsule_base_height, 50, 20)
        glPopMatrix()

        cap_x, cap_y, cap_z = self.capsule_position
        glPushMatrix()
        glTranslatef(cap_x, cap_y, cap_z)
        glColor3f(120 / 255, 255 / 255, 200 / 255)
        gluCylinder(gluNewQuadric(), self.capsule_radius, self.capsule_radius, self.capsule_height, 50, 20)
        glPopMatrix()

    def draw_walls(self, axis_close):
        length = GRID_LENGTH // 7
        grid_wall_height = length

        if axis_close == "+x":
            glBegin(GL_QUADS)
            glColor3f(4 / 255, 5 / 255, 5 / 255)
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31 / 255, 33 / 255, 34 / 255)
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)
            glEnd()
        elif axis_close == "+y":
            glBegin(GL_QUADS)
            glColor3f(34 / 255, 36 / 255, 37 / 255)
            glVertex3f(self.floor_left_max, self.floor_front_max, 0)
            glVertex3f(self.floor_right_max, self.floor_front_max, 0)
            glColor3f(78 / 255, 82 / 255, 86 / 255)
            glVertex3f(self.floor_right_max, self.floor_front_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_front_max, grid_wall_height)
            glEnd()
        elif axis_close == "-y":
            glBegin(GL_QUADS)
            glColor3f(4 / 255, 5 / 255, 5 / 255)
            glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
            glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
            glColor3f(31 / 255, 33 / 255, 34 / 255)
            glVertex3f(self.floor_right_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_behind_max, grid_wall_height)
            glEnd()
        elif axis_close == "-x":
            glBegin(GL_QUADS)
            glColor3f(34 / 255, 36 / 255, 37 / 255)
            glVertex3f(self.floor_left_max, self.floor_front_max, 0)
            glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
            glColor3f(78 / 255, 82 / 255, 86 / 255)
            glVertex3f(self.floor_left_max, self.floor_behind_max, grid_wall_height)
            glVertex3f(self.floor_left_max, self.floor_front_max, grid_wall_height)
            glEnd()

    def draw_lab(self):
        # floor
        glBegin(GL_QUADS)
        glColor3f(135 / 255, 175 / 255, 145 / 255)
        glVertex3f(self.floor_left_max, self.floor_front_max, 0)
        glColor3f(61 / 255, 66 / 255, 70 / 255)
        glVertex3f(self.floor_right_max, self.floor_front_max, 0)
        glColor3f(2 / 255, 2 / 255, 9 / 255)
        glVertex3f(self.floor_right_max, self.floor_behind_max, 0)
        glColor3f(61 / 255, 66 / 255, 70 / 255)
        glVertex3f(self.floor_left_max, self.floor_behind_max, 0)
        glEnd()
        # grid
        for i in range(self.floor_left_max - 2, self.floor_right_max + 2, -GRID_LENGTH // 15):
            glLineWidth(3)
            glBegin(GL_LINES)
            glColor3f(110 / 255, 118 / 255, 125 / 255)
            glVertex3f(i, self.floor_front_max - 1, 0)
            glColor3f(12 / 255, 12 / 255, 9 / 255)
            glVertex3f(i, self.floor_behind_max + 1, 0)
            glEnd()
        for i in range(self.floor_front_max - 2, self.floor_behind_max + 2, -GRID_WIDTH // 15):
            glBegin(GL_LINES)
            glColor3f(110 / 255, 118 / 255, 125 / 255)
            glVertex3f(self.floor_left_max - 1, i, 0)
            glColor3f(12 / 255, 12 / 255, 9 / 255)
            glVertex3f(self.floor_right_max + 1, i, 0)
            glEnd()
        # walls
        x, y, z = camera_pos
        wall_distance_from_camera = {
            "+x": math.sqrt(((x + GRID_WIDTH // 2) ** 2) + ((y - 0) ** 2) + ((z - 0) ** 2)),
            "+y": math.sqrt(((x - 0) ** 2) + ((y - GRID_LENGTH // 2) ** 2) + ((z - 0) ** 2)),
            "-y": math.sqrt(((x - 0) ** 2) + ((y + GRID_LENGTH // 2) ** 2) + ((z - 0) ** 2)),
            "-x": math.sqrt(((x - GRID_WIDTH // 2) ** 2) + ((y - 0) ** 2) + ((z - 0) ** 2)),
        }
        wall_distance_from_camera = dict(
            sorted(wall_distance_from_camera.items(), key=lambda item: item[1], reverse=True))
        for key, value in wall_distance_from_camera.items():
            self.draw_walls(key)

    # ENEMY SYSTEM 
    def get_random_spawn_coordinates(self):
        cap_x, cap_y, _ = self.capsule_position
        px, py, _ = self.player_spawn_position

        exclusion_radius = 500                                  
        min_enemy_separation = self.enemy_body_radius * 2.5     
        min_safe_dist = 200.0                                   
        max_attempts = 50
        margin = int(self.enemy_body_radius)

        # Full arena bounds 
        x_min = self.floor_right_max + margin
        x_max = self.floor_left_max  - margin
        y_min = self.floor_behind_max + margin
        y_max = self.floor_front_max  - margin

        # LEVELS 1 & 2 
        if self.game_level in (1, 2):
            spawn_padding = 50.0    # how far inside the boundary the enemy first appears

            if cap_x >= 0:
                opposite_x_wall = self.floor_right_max + spawn_padding   
            else:
                opposite_x_wall = self.floor_left_max  - spawn_padding   

            if cap_y >= 0:
                opposite_y_wall = self.floor_behind_max + spawn_padding  
            else:
                opposite_y_wall = self.floor_front_max  - spawn_padding  

            corner_margin = spawn_padding * 2
            free_x_min = self.floor_right_max  + corner_margin
            free_x_max = self.floor_left_max   - corner_margin
            free_y_min = self.floor_behind_max + corner_margin
            free_y_max = self.floor_front_max  - corner_margin

            for attempt in range(max_attempts):        
                wall_choice = random.choice(['x_wall', 'y_wall'])

                depth_jitter = random.uniform(0.0, 80.0)

                if wall_choice == 'x_wall':
                    if cap_x >= 0:
                        ex = opposite_x_wall + depth_jitter      # inward = +X
                    else:
                        ex = opposite_x_wall - depth_jitter      # inward = -X
                    ey = random.uniform(free_y_min, free_y_max)

                else:  
                    if cap_y >= 0:
                        ey = opposite_y_wall + depth_jitter      # inward = +Y
                    else:
                        ey = opposite_y_wall - depth_jitter      # inward = -Y
                    ex = random.uniform(free_x_min, free_x_max)

                dist_to_capsule = math.dist((ex, ey), (cap_x, cap_y))
                dist_to_player  = math.dist((ex, ey), (px, py))
                if dist_to_capsule < min_safe_dist or dist_to_player < min_safe_dist:
                    continue   # too close — reroll

                #enemy-vs-enemy spacing check 
                too_close = False
                for existing in self.enemies:
                    if math.dist((ex, ey), (existing['x'], existing['y'])) < min_enemy_separation:
                        too_close = True
                        break
                if too_close:
                    continue

                return ex, ey

            fallback_x = random.uniform(free_x_min, free_x_max)
            fallback_y = (self.floor_behind_max + spawn_padding
                          if cap_y >= 0
                          else self.floor_front_max - spawn_padding)
            return fallback_x, fallback_y


        # LEVEL 3 
        ex, ey = x_min, y_min
        for attempt in range(max_attempts):
            ex = random.uniform(x_min, x_max)
            ey = random.uniform(y_min, y_max)

            dist_to_capsule = math.dist((ex, ey), (cap_x, cap_y))
            if dist_to_capsule < exclusion_radius:
                continue

            too_close_to_enemy = False
            for existing_enemy in self.enemies:
                if math.dist((ex, ey), (existing_enemy['x'], existing_enemy['y'])) < min_enemy_separation:
                    too_close_to_enemy = True
                    break

            if too_close_to_enemy:
                continue

            return int(ex), int(ey)

        print(f"[SpawnWarning] Could not find a non-overlapping spawn after {max_attempts} attempts.")
        return int(ex), int(ey)

    def spawn_enemies(self):
        if self.game_level == 1:
            # Population threshold: overlapping waves
            if len(self.enemies) <= 6:
                num_to_spawn = random.randint(8, 10)
                for _ in range(num_to_spawn):
                    ex, ey = self.get_random_spawn_coordinates()
                    self.enemies.append({
                        'x': ex, 'y': ey,
                        'z': self.enemy_base_z,
                        'base_z': self.enemy_base_z,
                        'run_cycle': random.uniform(0.0, 5.0),
                        'type': 'normal',
                        'body_r': self.enemy_body_radius,
                        'head_r': self.enemy_head_radius,
                        'color': (0.0, 125 / 255.0, 140 / 255.0)
                    })
                self.last_spawn_time = time.time()
                print(f"[L1 Wave] Population threshold hit (<=6). Spawned {num_to_spawn} new enemies. Total: {len(self.enemies)}")

            # High-density continuous: 5 every 5s
            current_time = time.time()
            if current_time - self.last_spawn_time >= 5.0:
                for _ in range(5):
                    ex, ey = self.get_random_spawn_coordinates()
                    self.enemies.append({
                        'x': ex, 'y': ey,
                        'z': self.enemy_base_z,
                        'base_z': self.enemy_base_z,
                        'run_cycle': random.uniform(0.0, 5.0),
                        'type': 'normal',
                        'body_r': self.enemy_body_radius,
                        'head_r': self.enemy_head_radius,
                        'color': (0.0, 125 / 255.0, 140 / 255.0)
                    })
                self.last_spawn_time = current_time
                print(f"[L1 Spawn] Group of 5 enemies spawned from wall. Active: {len(self.enemies)}")

            # Special enemy: every 20 normal kills
            if self.normal_enemy_kills_for_special >= 20:
                self.normal_enemy_kills_for_special -= 20
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
                print(f"[L1 Spawn] Special enemy spawned after 20 kills! Active: {len(self.enemies)}")

        elif self.game_level == 2:
            L2_NORMAL_COLOR = (27 / 255.0, 196 / 255.0, 118 / 255.0)

            if len(self.enemies) <= 12:
                num_to_spawn = random.randint(10, 15)
                for _ in range(num_to_spawn):
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
                    })
                self.last_spawn_time = time.time()
                print(f"[L2 Wave] Population threshold hit (<=12). Spawned {num_to_spawn} new enemies. Total: {len(self.enemies)}")

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
                })
                self.last_spawn_time = current_time
                print(f"[L2 Spawn] Timed enemy spawned. Active: {len(self.enemies)}")

            if self.normal_enemy_kills_for_special >= 10:
                self.normal_enemy_kills_for_special -= 10
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
                print(f"[L2 Spawn] Special enemy spawned after 10 kills! Active: {len(self.enemies)}")

        elif self.game_level == 3:
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
                    'color': (94 / 255.0, 4 / 255.0, 135 / 255.0),
                    'health': 50,
                    'max_health': 50
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
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < (self.capsule_radius + enemy['body_r']):
                enemies_to_remove.append(e_idx)
                self.capsule_health = max(0, self.capsule_health - 1)
                print(f"Capsule hit! Remaining health: {self.capsule_health}")
                continue

            dx_p = player_x - enemy['x']
            dy_p = player_y - enemy['y']
            distance_p = math.sqrt(dx_p ** 2 + dy_p ** 2)
            if distance_p < (self.player_width + enemy['body_r']):
                enemies_to_remove.append(e_idx)
                if not self.cheat_mode_active:
                    self.player_health = max(0, self.player_health - 1)
                    print(f"Player hit! Remaining health: {self.player_health}")
                continue

            if enemy['type'] == 'boss':
                margin = int(enemy['body_r'])
                x_min = self.floor_right_max + margin
                x_max = self.floor_left_max - margin
                base_y = self.floor_behind_max + margin + 100

                if 'boss_direction_x' not in enemy:
                    enemy['boss_direction_x'] = 1
                    enemy['y'] = base_y

                base_sweep_speed = self.enemy_speed * 1.5
                enemy['run_cycle'] += 0.05
                speed_wobble = math.cos(enemy['run_cycle'] * 1.5) * base_sweep_speed * 1.2
                new_x = enemy['x'] + (enemy['boss_direction_x'] * base_sweep_speed) + speed_wobble

                if new_x > x_max:
                    new_x = x_max
                    enemy['boss_direction_x'] = -1
                elif new_x < x_min:
                    new_x = x_min
                    enemy['boss_direction_x'] = 1

                enemy['x'] = new_x

                depth_wobble = math.sin(enemy['run_cycle'] * 2.0) * 20.0
                enemy['y'] = base_y + depth_wobble
                enemy['z'] = enemy['base_z'] + abs(math.sin(enemy['run_cycle'] * 2)) * 20
            else:
                if distance > 0:
                    enemy['x'] += (dx / distance) * self.enemy_speed
                    enemy['y'] += (dy / distance) * self.enemy_speed
                    enemy['run_cycle'] += 0.08
                    bounce_height = abs(math.sin(enemy['run_cycle'])) * 15
                    enemy['z'] = enemy['base_z'] + bounce_height

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

                dist_2d = math.sqrt((bx - enemy['x']) ** 2 + (by - enemy['y']) ** 2)

                if dist_2d < (enemy['body_r'] + self.bullet_size):
                    bullets_to_remove.append(b_idx)

                    # Boss: take damage instead of dying instantly
                    if enemy['type'] == 'boss':
                        enemy['health'] -= 1
                        print(f"[Boss] Hit! Health: {enemy['health']}/{enemy['max_health']}")
                        if enemy['health'] <= 0:
                            enemies_to_remove.append(e_idx)
                            self.total_kills += 1
                            self.game_won = True
                            self.game_over = True
                            print("[Boss] DEFEATED! YOU WIN!")
                        break

                    # Normal/special enemies: die in one shot
                    enemies_to_remove.append(e_idx)

                    if enemy['type'] == 'special':
                        if self.player_health < 5:
                            self.player_health += 1
                            print(f"Special Enemy Killed! Health increased to {self.player_health}")
                    else:
                        self.normal_enemies_killed += 1
                        #counter for special spawns
                        self.normal_enemy_kills_for_special += 1

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

    # ENEMY DRAWING 
    def draw_enemies(self):
        for enemy in self.enemies:
            ex, ey, ez = enemy['x'], enemy['y'], enemy['z']
            cr, cg, cb = enemy['color']

            # Doc 1: Boss scale adjustment
            if enemy['type'] == 'boss':
                br = enemy['body_r'] * 1.18
                hr = enemy['head_r'] * 1.18
            else:
                br = enemy['body_r']
                hr = enemy['head_r']

            glPushMatrix()
            glTranslatef(ex, ey, ez)

            #Yaw orientation
            if enemy['type'] == 'boss':
                px, py, _ = self.player_spawn_position
                dx = px - ex
                dz = py - ey
            else:
                cap_x, cap_y, _ = self.capsule_position
                dx = cap_x - ex
                dz = cap_y - ey

            raw_yaw = math.degrees(math.atan2(dz, dx))
            yaw_deg = raw_yaw + 90.0
            glRotatef(yaw_deg, 0, 0, 1)

            # Body
            glColor3f(cr, cg, cb)
            gluSphere(gluNewQuadric(), br, 30, 30)

            # Head
            glPushMatrix()
            glTranslatef(0, 0, br + hr - 5)
            glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)
            gluSphere(gluNewQuadric(), hr, 30, 30)

            # Horns
            if enemy['type'] == 'boss':
                h_base_r = hr * 0.4
                h_top_r = hr * 0.1
                h_height = hr * 1.5
            else:
                h_base_r = hr * 0.22
                h_top_r = 0.01
                h_height = hr * 0.8

            glPushMatrix()
            glTranslatef(-hr * 0.5, 0, hr * 0.6)
            glRotatef(-40, 0, 1, 0)
            glRotatef(-10, 1, 0, 0)
            gluCylinder(gluNewQuadric(), h_base_r, h_top_r, h_height, 15, 5)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(hr * 0.5, 0, hr * 0.6)
            glRotatef(40, 0, 1, 0)
            glRotatef(-10, 1, 0, 0)
            gluCylinder(gluNewQuadric(), h_base_r, h_top_r, h_height, 15, 5)
            glPopMatrix()

            glPopMatrix()

            # Limb parameters
            shoulder_offset = br * 1.1
            shoulder_z = br * 0.4
            upper_arm_len = br * 1.1
            arm_r_top = br * 0.22
            arm_r_bot = br * 0.15
            forearm_r_top = br * 0.18
            forearm_r_bot = br * 0.11
            hand_r = hr * 0.35
            elbow_z = -upper_arm_len * 0.65
            elbow_y = -upper_arm_len * 0.75

            if self.game_level == 3:
                # Boss: full articulated arms
                glPushMatrix()
                glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
                glTranslatef(-shoulder_offset, 0, shoulder_z)
                gluSphere(gluNewQuadric(), arm_r_top * 1.2, 20, 20)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
                glTranslatef(-shoulder_offset, 0, shoulder_z)
                glRotatef(90, 1, 0, 0)
                glRotatef(45, 1, 0, 0)
                gluCylinder(gluNewQuadric(), arm_r_top, arm_r_bot, upper_arm_len, 20, 5)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.85, cg * 0.85, cb * 0.85)
                glTranslatef(-shoulder_offset, elbow_y, elbow_z)
                glRotatef(90, 1, 0, 0)
                glRotatef(-25, 1, 0, 0)
                glRotatef(45, 0, 1, 0)
                gluCylinder(gluNewQuadric(), forearm_r_top, forearm_r_bot, upper_arm_len, 20, 5)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)
                glTranslatef(-shoulder_offset, elbow_y - upper_arm_len * 0.7, elbow_z - upper_arm_len * 0.5)
                gluSphere(gluNewQuadric(), hand_r, 20, 20)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
                glTranslatef(shoulder_offset, 0, shoulder_z)
                gluSphere(gluNewQuadric(), arm_r_top * 1.2, 20, 20)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
                glTranslatef(shoulder_offset, 0, shoulder_z)
                glRotatef(90, 1, 0, 0)
                glRotatef(45, 1, 0, 0)
                gluCylinder(gluNewQuadric(), arm_r_top, arm_r_bot, upper_arm_len, 20, 5)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.85, cg * 0.85, cb * 0.85)
                glTranslatef(shoulder_offset, elbow_y, elbow_z)
                glRotatef(90, 1, 0, 0)
                glRotatef(-15, 1, 0, 0)
                glRotatef(-45, 0, 1, 0)
                gluCylinder(gluNewQuadric(), forearm_r_top, forearm_r_bot, upper_arm_len, 20, 5)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.8, cg * 0.8, cb * 0.8)
                glTranslatef(shoulder_offset, elbow_y - upper_arm_len * 0.7, elbow_z - upper_arm_len * 0.5)
                gluSphere(gluNewQuadric(), hand_r, 20, 20)
                glPopMatrix()

                # Boss legs (Doc 1: pillar appearance)
                leg_len = br * 2.2
                leg_r = br * 0.45

                glPushMatrix()
                glColor3f(cr * 0.7, cg * 0.7, cb * 0.7)
                glTranslatef(-br * 0.8, 0, -br * 0.5)
                glRotatef(180, 1, 0, 0)
                gluCylinder(gluNewQuadric(), leg_r, leg_r * 0.8, leg_len, 20, 5)
                glPopMatrix()

                glPushMatrix()
                glColor3f(cr * 0.7, cg * 0.7, cb * 0.7)
                glTranslatef(br * 0.8, 0, -br * 0.5)
                glRotatef(180, 1, 0, 0)
                gluCylinder(gluNewQuadric(), leg_r, leg_r * 0.8, leg_len, 20, 5)
                glPopMatrix()

                # Massive cannon
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

            elif self.game_level in (1, 2):
                #Symmetrical cylinder hands with weapons
                for side in [-1, 1]:
                    glPushMatrix()
                    glColor3f(cr * 0.9, cg * 0.9, cb * 0.9)
                    glTranslatef(side * shoulder_offset, 0, shoulder_z)

                    gluSphere(gluNewQuadric(), arm_r_top * 1.2, 16, 16)

                    glRotatef(90, 1, 0, 0)
                    glRotatef(30, 1, 0, 0)
                    gluCylinder(gluNewQuadric(), arm_r_top, arm_r_bot, upper_arm_len * 0.8, 16, 5)

                    if side == 1 and enemy['type'] != 'special':
                        glTranslatef(0, 0, upper_arm_len * 0.8)

                        if self.game_level == 1:
                            glColor3f(5 / 255.0, 255 / 255.0, 243 / 255.0)
                            glRotatef(-15, 1, 0, 0)
                            gluCylinder(gluNewQuadric(), arm_r_bot, arm_r_bot * 0.4, br * 1.2, 16, 5)
                            glTranslatef(0, 0, br * 1.2)
                            gluSphere(gluNewQuadric(), arm_r_bot * 0.5, 16, 16)

                        elif self.game_level == 2:
                            e_shoe_r = br * 0.14
                            e_leg_h = br * 1.1
                            GUN_R, GUN_G, GUN_B = 1.0, 165 / 255.0, 0.0

                            glPushMatrix()
                            glColor3f(GUN_R, GUN_G, GUN_B)
                            glRotatef(60, 1, 0, 0)
                            gluCylinder(gluNewQuadric(), e_shoe_r * 1.5, e_shoe_r, e_leg_h * 2, 32, 32)
                            glPopMatrix()

                            glPushMatrix()
                            glColor3f(GUN_R * 0.85, GUN_G * 0.85, 0.0)
                            glRotatef(150, 1, 0, 0)
                            gluCylinder(gluNewQuadric(), e_shoe_r * 1.5, e_shoe_r, e_leg_h * 0.8, 32, 32)
                            glPopMatrix()

                    glPopMatrix()

            glPopMatrix()

    def update_enemy_combat(self):
        if self.game_level >= 2:
            if self.game_level == 3:
                current_time = time.time()
                # Boss fires slower (every ~5s instead of ~3s)
                if current_time - self.enemy_volley_timer < self.volley_interval * 2.5:
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

            #Attack token system (max 3 active shooters)
            active_tokens = len(self.enemy_bullets)
            max_tokens = 3
            available_tokens = max_tokens - active_tokens

            if available_tokens <= 0:
                return

            current_time = time.time()
            if current_time - self.enemy_volley_timer < self.volley_interval:
                return

            self.enemy_volley_timer = current_time

            normal_enemies = [e for e in self.enemies if e['type'] == 'normal']
            if not normal_enemies:
                return

            volley_target = random.randint(2, 3)
            num_to_fire = min(volley_target, available_tokens, len(normal_enemies))

            if num_to_fire <= 0:
                return

            shooters = random.sample(normal_enemies, num_to_fire)

            px, py, _ = self.player_spawn_position

            for enemy in shooters:
                ex_pos, ey_pos = enemy['x'], enemy['y']
                bz = enemy['base_z']

                shoot_dx = px - ex_pos
                shoot_dy = py - ey_pos
                shoot_dist = math.sqrt(shoot_dx ** 2 + shoot_dy ** 2)

                if shoot_dist > 0:
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

            if (-GRID_WIDTH // 2 < new_x < GRID_WIDTH // 2 and
                    -GRID_WIDTH // 2 < new_y < GRID_WIDTH // 2):
                bullet['bullet_coord'][0] = new_x
                bullet['bullet_coord'][1] = new_y
            else:
                bullets_to_remove.append(i)

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.enemy_bullets):
                self.enemy_bullets.pop(i)

    def draw_enemy_bullets(self):
        for bullet in self.enemy_bullets:
            bx, by, bz = bullet['bullet_coord']
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glColor3f(1.0, 0.5, 0.0)
            glutSolidCube(self.enemy_bullet_size)
            glPopMatrix()

    def enemy_bullet_player_collision(self):
        if self.game_level < 2:
            return

        bullets_to_remove = []
        px, py, _ = self.player_spawn_position

        for i, bullet in enumerate(self.enemy_bullets):
            bx, by, _ = bullet['bullet_coord']
            dist_2d = math.sqrt((bx - px) ** 2 + (by - py) ** 2)

            hit_radius = self.player_width + self.enemy_bullet_size / 2
            if dist_2d < hit_radius:
                bullets_to_remove.append(i)
                self.player_hit_tolerance += 1

                if self.player_hit_tolerance >= 5:
                    if not self.cheat_mode_active:
                        self.player_health = max(0, self.player_health - 1)
                        print(f"[EnemyBullet] 5 hits absorbed! HP reduced to {self.player_health}")
                    self.player_hit_tolerance = 0

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.enemy_bullets):
                self.enemy_bullets.pop(i)

    def update_cannonballs(self):
        balls_to_remove = []
        for i, cb in enumerate(self.cannonballs):
            cb['coord'][0] += self.cannonball_speed * cb['direction'][0]
            cb['coord'][1] += self.cannonball_speed * cb['direction'][1]
            if not (-GRID_WIDTH // 2 < cb['coord'][0] < GRID_WIDTH // 2 and
                    -GRID_WIDTH // 2 < cb['coord'][1] < GRID_WIDTH // 2):
                balls_to_remove.append(i)
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(self.cannonballs):
                self.cannonballs.pop(i)

    def draw_cannonballs(self):
        for cb in self.cannonballs:
            bx, by, bz = cb['coord']
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glColor3f(109 / 255.0, 242 / 255.0, 220 / 255.0)
            gluSphere(gluNewQuadric(), self.cannonball_size, 80, 80)
            glPopMatrix()

    def cannonball_collisions(self):
        if self.game_level != 3:
            return
        balls_to_remove = []
        player_bullets_to_remove = []
        px, py, _ = self.player_spawn_position
        cx, cy, _ = self.capsule_position

        for i, cb in enumerate(self.cannonballs):
            if i in balls_to_remove:
                continue
            bx, by, _ = cb['coord']

            dist_capsule = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
            if dist_capsule < (self.capsule_radius + self.cannonball_size):
                self.capsule_health = max(0, self.capsule_health - 3)
                balls_to_remove.append(i)
                print(f"[Cannonball] Hit capsule! Health: {self.capsule_health}")
                continue

            dist_player = math.sqrt((bx - px) ** 2 + (by - py) ** 2)
            if dist_player < (self.player_width + self.cannonball_size):
                if not self.cheat_mode_active:
                    self.player_health = max(0, self.player_health - 2)
                    print(f"[Cannonball] Hit player! Health: {self.player_health}")
                balls_to_remove.append(i)
                continue

            for j, pb in enumerate(self.all_bullets):
                if j in player_bullets_to_remove:
                    continue
                pbx, pby, _ = pb['bullet_coord']
                dist_bullet = math.sqrt((bx - pbx) ** 2 + (by - pby) ** 2)
                if dist_bullet < (self.cannonball_size + self.bullet_size):
                    player_bullets_to_remove.append(j)
                    cb['health'] -= 1
                    if cb['health'] <= 0:
                        balls_to_remove.append(i)

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


    # HUD 
    def draw_health_bar(self, x, y, width, height, current, maximum, fill_color):
        # Background
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(x, y, 0)
        glVertex3f(x + width, y, 0)
        glVertex3f(x + width, y + height, 0)
        glVertex3f(x, y + height, 0)
        glEnd()

        # Fill — ratio-based color tiers 
        if current > 0:
            fill_width = width * (min(current, maximum) / maximum)
            ratio = current / maximum
            if ratio < 0.4:
                glColor3f(1.0, 0.2, 0.2)
            elif ratio < 0.7:
                glColor3f(1.0, 0.6, 0.3)
            else:
                glColor3f(fill_color[0], fill_color[1], fill_color[2])
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + fill_width, y, 0)
            glVertex3f(x + fill_width, y + height, 0)
            glVertex3f(x, y + height, 0)
            glEnd()

    def draw_hud(self):
        glDisable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        self.draw_text(30, window_height - 25, "Player HP:", GLUT_BITMAP_HELVETICA_18)
        self.draw_text(30, 60, "Capsule HP:", GLUT_BITMAP_HELVETICA_18)

        # Player bar  5
        self.draw_health_bar(
            x=30,
            y=window_height - 60,
            width=170,
            height=25,
            current=self.player_health,
            maximum=5,
            fill_color=(0.2, 0.9, 0.3)
        )

        # Capsule bar
        self.draw_health_bar(
            x=30,
            y=25,
            width=280,
            height=25,
            current=self.capsule_health,
            maximum=10,
            fill_color=(0.2, 0.8, 1.0)
        )

        # Boss bar 
        if self.game_level == 3:
            bosses = [e for e in self.enemies if e['type'] == 'boss']
            if bosses:
                boss = bosses[0]
                boss_bar_w = 350
                boss_bar_x = window_width - boss_bar_w - 30
                self.draw_text(boss_bar_x, window_height - 25,
                               "Boss HP:", GLUT_BITMAP_HELVETICA_18)
                self.draw_health_bar(
                    x=boss_bar_x,
                    y=window_height - 60,
                    width=boss_bar_w,
                    height=25,
                    current=boss['health'],
                    maximum=boss['max_health'],
                    fill_color=(0.7, 0.2, 0.9)
                )

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

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
        self.draw_enemy_bullets()
        if self.game_level == 3:
            self.draw_cannonballs()

    # CONTROLS 
    def MouseListener(self, button, state, x, y):
        if self.paused or self.game_over or self.transition_pause:
            return
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if self.ammo_mag <= 0 and not self.cheat_mode_active:
                print("Out of ammo! Press 'R' to reload")
                return
            x, y, z = self.gun_facing
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            self.all_bullets.append({
                'bullet_coord': [x, y, z],
                'bullet_direction': [dir_x, dir_y]
            })
            if not self.cheat_mode_active:
                self.ammo_mag -= 1
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            self.first_person_view = not self.first_person_view
            if self.first_person_view:
                print("First-Person View: ON")
            else:
                print("Third-Person View: ON")

    def KeyboardListener(self, key, x, y):
        global field_of_view
        x, y, z = self.player_spawn_position

        # Cheat Mode toggle
        if key == b"c" or key == b"C":
            self.cheat_mode_active = not self.cheat_mode_active
            if self.cheat_mode_active:
                print("Cheat Mode: ON")
            else:
                print("Cheat Mode: OFF")
            self.weapon_upgrade()

        # Restart (always available)
        elif key == b"f" or key == b"F":
            self.reset_game()
            print("Game Restarted")

        # Pause toggle (always available)
        elif key == b"p" or key == b"P":
            if not self.paused:
                self.paused = True
                self.pause_start_time = time.time()
                print("Game Paused")
            else:
                pause_duration = time.time() - self.pause_start_time
                self.start_time += pause_duration
                self.last_spawn_time += pause_duration
                self.enemy_volley_timer += pause_duration
                if self.transition_start is not None:
                    self.transition_start += pause_duration
                if self.intro_starting_time is not None:
                    self.intro_starting_time += pause_duration
                self.paused = False
                print("Game Resumed")

        # Block all other input during pause / game over
        elif self.paused or self.game_over:
            return

        elif key == b"z":
            field_of_view -= 2
        elif key == b"x":
            field_of_view += 2
        elif key == b"w":
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            move_x, move_y = x + dir_x * self.player_speed, y + dir_y * self.player_speed
            self.gun_facing[0] += dir_x * self.player_speed
            self.gun_facing[1] += dir_y * self.player_speed
            if (-GRID_WIDTH // 2 < self.gun_facing[0] + self.gun_height < GRID_WIDTH // 2 and
                    -GRID_WIDTH // 2 < self.gun_facing[1] + self.gun_height < GRID_WIDTH // 2) and \
                    (-GRID_WIDTH // 2 < move_x < GRID_WIDTH // 2 and -GRID_WIDTH // 2 < move_y < GRID_WIDTH // 2):
                x = move_x
                y = move_y
            self.player_spawn_position = (x, y, z)
        elif key == b"s":
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            move_x, move_y = x - dir_x * self.player_speed, y - dir_y * self.player_speed
            self.gun_facing[0] -= dir_x * self.player_speed
            self.gun_facing[1] -= dir_y * self.player_speed
            if (-GRID_WIDTH // 2 < self.gun_facing[0] + self.gun_height < GRID_WIDTH // 2 and
                    -GRID_WIDTH // 2 < self.gun_facing[1] + self.gun_height < GRID_WIDTH // 2) and \
                    (-GRID_WIDTH // 2 < move_x < GRID_WIDTH // 2 and -GRID_WIDTH // 2 < move_y < GRID_WIDTH // 2):
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
            move_x, move_y = x + right_x * self.player_speed, y + right_y * self.player_speed
            if (-GRID_LENGTH // 2) + 25 <= move_x <= (GRID_LENGTH // 2) - 25 and \
                    (-GRID_WIDTH // 2) + 25 <= move_y <= (GRID_WIDTH // 2) - 25:
                x = move_x
                y = move_y
                self.player_spawn_position = (x, y, z)
        elif key == b"d":
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
            right_x = -dir_y
            right_y = dir_x
            move_x, move_y = x - right_x * self.player_speed, y - right_y * self.player_speed
            if (-GRID_LENGTH // 2) + 25 <= move_x <= (GRID_LENGTH // 2) - 25 and \
                    (-GRID_WIDTH // 2) + 25 <= move_y <= (GRID_WIDTH // 2) - 25:
                x = move_x
                y = move_y
                self.player_spawn_position = (x, y, z)

        # Magazine reload
        elif key == b"r" or key == b"R":
            self.ammo_mag = self.mag_size
            print("Reloaded!")

        glutPostRedisplay()

    def specialKeyListener(self, key, x, y):
        global camera_pos, field_of_view
        x, y, z = camera_pos
        if key == GLUT_KEY_LEFT:
            angle_of_rotation = math.radians(1)
            old_x = x
            old_y = y
            x = old_x * math.cos(angle_of_rotation) - old_y * math.sin(angle_of_rotation)
            y = old_x * math.sin(angle_of_rotation) + old_y * math.cos(angle_of_rotation)
        elif key == GLUT_KEY_RIGHT:
            angle_of_rotation = math.radians(-1)
            old_x = x
            old_y = y
            x = old_x * math.cos(angle_of_rotation) - old_y * math.sin(angle_of_rotation)
            y = old_x * math.sin(angle_of_rotation) + old_y * math.cos(angle_of_rotation)
        elif key == GLUT_KEY_UP:
            z += 5
        elif key == GLUT_KEY_DOWN:
            z -= 5
        camera_pos = (x, y, z)
        glutPostRedisplay()

    def weapon_upgrade(self, level=1):
        if self.cheat_mode_active:
            self.level_weapon_head_color = (255 / 255, 60 / 255, 120 / 255)
            self.level_weapon_handle_color = (255 / 255, 120 / 255, 180 / 255)
            self.bullet_speed = 80
        elif self.level_1_limit_crossed and self.game_level == 2:
            self.level_weapon_head_color = (0 / 255, 200 / 255, 255 / 255)
            self.level_weapon_handle_color = (120 / 255, 255 / 255, 255 / 255)
            self.bullet_speed = 55
        elif self.level_2_limit_crossed and self.game_level == 3:
            if self.level_1_limit_crossed:
                self.level_weapon_head_color = (255 / 255, 60 / 255, 120 / 255)
                self.level_weapon_handle_color = (255 / 255, 120 / 255, 180 / 255)
                self.bullet_speed = 80
            else:
                self.level_weapon_head_color = (0 / 255, 200 / 255, 255 / 255)
                self.level_weapon_handle_color = (120 / 255, 255 / 255, 255 / 255)
                self.bullet_speed = 55
        else:
            self.level_weapon_head_color = (170 / 255, 120 / 255, 255 / 255)
            self.level_weapon_handle_color = (200 / 255, 180 / 255, 255 / 255)
            self.bullet_speed = 16

    def display_level(self):
        level_text = f"Level: {self.game_level}"
        self.draw_text(window_width - window_width // 2, window_height - 30, level_text)

    def display_magazine(self):
        if self.cheat_mode_active:
            mag_text = "Ammo: Infinite"
        else:
            if self.ammo_mag == 0:
                mag_text = "Ammo: Empty! Press 'R' to reload"
            else:
                mag_text = f"Ammo: {self.ammo_mag}/{self.mag_size}"
        self.draw_text(25, window_height - 90, mag_text)

    def reset_game(self):
        self.initiate_all()

    def game_level_upgrader(self, up=True):
        if up:
            self.game_level = self.game_level + 1 if self.game_level < 3 else self.game_level

            # Restore enemy speed for boss phase
            if self.game_level == 3:
                self.enemy_speed = 0.75

            self.total_kills = 0
            self.enemies.clear()
            self.enemy_bullets.clear()
            self.all_bullets.clear()

            if hasattr(self, 'cannonballs'):
                self.cannonballs.clear()

        self.weapon_upgrade()
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
        glColor3f(0, 0.4, 0)
        glBegin(GL_QUADS)
        glVertex2f(0, window_height // 2 + 50)
        glVertex2f(window_width, window_height // 2 + 50)
        glColor3f(0.2, 1, 0.2)
        glVertex2f(window_width, window_height // 2 - 50)
        glVertex2f(0, window_height // 2 - 50)
        glEnd()
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        if self.game_level < 3:
            transition_text = f"Level {self.game_level} Cleared !!!!\n Next Level: {self.game_level + 1}"
        else:
            transition_text = "End"
        self.draw_text(window_width // 2 - 150, window_height // 2 - 10, transition_text)

    def animation(self):
        glutPostRedisplay()

    def setupCamera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(field_of_view, window_width / window_height, 0.1, 4500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if self.first_person_view:
            x, y, z = self.player_spawn_position
            dir_x = math.cos(math.radians(self.player_angle - 90))
            dir_y = math.sin(math.radians(self.player_angle - 90))
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
                      look_x, look_y, look_z,
                      0, 0, 1)
        else:
            x, y, z = camera_pos
            look_x, look_y, look_z = camera_look_at
            respect_to_x, respect_to_y, respect_to_z = axis_decision
            gluLookAt(x, y, z,
                      look_x, look_y, look_z,
                      respect_to_x, respect_to_y, respect_to_z)

    # MAIN LOOP 
    def showScreen(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, window_width, window_height)
        self.setupCamera()

        # Auto game over detection
        if not self.game_over and not self.game_intro_ongoing:
            if self.player_health <= 0 or self.capsule_health <= 0:
                self.game_over = True
                print("GAME OVER! Press 'F' to restart.")

        self.display_level()
        if self.game_level < 3:
            self.display_time()
        self.display_kill_count()
        self.draw_elements()
        self.draw_hud()
        self.display_magazine()

        if self.game_intro_ongoing:
            if self.intro_starting_time is None:
                self.intro_starting_time = time.time()
            self.game_intro()

        elif not self.paused and not self.game_over:
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

        # Overlays drawn last       
        elif self.paused:
            self.draw_text(window_width // 2 - 20, window_height // 2 + 20,
                           "PAUSED")
            self.draw_text(window_width // 2 - 60, window_height // 2 - 10,
                           "Press P to resume")
        elif self.game_won:
            self.draw_text(window_width // 2 - 60, window_height // 2 + 40,
                           "YOU WIN!", GLUT_BITMAP_HELVETICA_18, color=(0.2, 1.0, 0.4))
            self.draw_text(window_width // 2 - 70, window_height // 2,
                           "Final Boss Defeated!", color=(0.2, 1.0, 0.4))
            self.draw_text(window_width // 2 - 60, window_height // 2 - 60,
                           "Press F to restart", color=(0.2, 1.0, 0.4))
        elif self.game_over:
            self.draw_text(window_width // 2 - 60, window_height // 2 + 40,
                           "GAME OVER", GLUT_BITMAP_HELVETICA_18, color=(1.0, 0.2, 0.2))
            self.draw_text(window_width // 2 - 60, window_height // 2 - 30,
                           "Press F to restart", color=(1.0, 0.2, 0.2))

        glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
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
