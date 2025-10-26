import pygame
import random
import math
import sys
import os
import requests
import json
import threading
import time


from collections import deque


GROK_API_KEY = os.getenv('GROK_API_KEY')
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Whether to read quotes from text file or generate with API
USE_TEXT_QUOTES = True

pygame.init()

NEXT_QUOTES = {
    'appeared': [],
    'damaged': [],
    'dying': [],
    'nibble': []
}

# Constants - 1080p resolution
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (224, 224, 224)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
DARK_GREEN = (60, 179, 113)
ORANGE = (255, 127, 80)
GRAY = (169, 169, 169)
PURPLE = (186, 85, 211)
YELLOW = (255, 215, 0)
DARK_RED = (178, 34, 52)
EXPLOSION_COLOR = (255, 140, 0)
BLUE = (70, 130, 180)
CYAN = (72, 209, 204)

# Game settings scaled for 1080p
SCROLL_SPEED = 8
SNAKE_RADIUS = 40
GRID_SIZE = int(SNAKE_RADIUS * 3)
GRID_COLS = SCREEN_WIDTH // GRID_SIZE
GRID_ROWS = SCREEN_HEIGHT // GRID_SIZE
FOOD_RADIUS = 20
BOMB_RADIUS = 28
MOVE_SPEED = 24
EXPLOSION_RADIUS = 400
EXPLOSION_DURATION = 20

# Particles
FOOD_PARTICLE_COUNT = 10
BOMB_PARTICLE_COUNT = 20
BREAK_PARTICLE_COUNT = 15

# Growth
SEGMENTS_PER_FOOD = 3

# Snake constants
SNAKE_GROW_RATE = 0.1
SNAKE_SEG_SPEED_MULTIPLIER = 2
SNAKE_EYE_LERP_FACTOR = 0.15
SNAKE_IDLE_DIST_THRESHOLD = 2
SNAKE_FRICTION = 0.7
SNAKE_DRIFT_FORCE = 0.002
SNAKE_ACCEL = 0.2
SNAKE_BUFFER_MULTIPLIER = 5.0
REST_POSITION_THRESHOLD = 10

# Eye constants
EYE_RADIUS = 12
PUPIL_RADIUS = 6
EYE_OFFSET_FORWARD = 35
EYE_OFFSET_SIDE = 14
PUPIL_OFFSET_X_FACTOR = 0.05
PUPIL_OFFSET_X_AMPLITUDE = 3
PUPIL_OFFSET_Y_FACTOR = 0.05
PUPIL_OFFSET_Y_AMPLITUDE = 2

# Food constants
FOOD_SCALE_INCREMENT = 0.1

# Bomb constants
BOMB_SCALE_INCREMENT = 0.1
BOMB_PULSE_INCREMENT = 0.15
BOMB_SPEED = 20

# Obstacle constants
OBSTACLE_RECT_BORDER = 4
OBSTACLE_NUM_TILES_MIN = 1
OBSTACLE_NUM_TILES_MAX = 3

# Explosion constants
EXPLOSION_CORE_START_FACTOR = 0.3
EXPLOSION_CORE_END_FACTOR = 0.7
EXPLOSION_INNER_FADE_START = 0.6
EXPLOSION_INNER_RADIUS_FACTOR = 0.4
EXPLOSION_INNER_FACTOR_MULTIPLIER = 1.2
EXPLOSION_RING_COUNT = 6
EXPLOSION_RING_RADIUS_DECREMENT = 15
EXPLOSION_RING_PROGRESS_OFFSET = 0.1
EXPLOSION_RING_THICKNESS_BASE = 14
EXPLOSION_RING_THICKNESS_DECREMENT = 2

# Particle constants
PARTICLE_GLOW_BRIGHTNESS_MULTIPLIER = 0.5
PARTICLE_SIZE_GLOW_OFFSET = 2

# Game constants
FOOD_SPAWN_DISTANCE_MIN = 600
FOOD_SPAWN_DISTANCE_MAX = 1400
OBSTACLE_SPAWN_DISTANCE_MIN = 300
OBSTACLE_SPAWN_DISTANCE_MAX = 600
SPAWN_ATTEMPTS = 100
SPAWN_INTERVAL_MIN = 2
SPAWN_INTERVAL_MAX = 4
FOOD_REMOVE_OFFSET_MULTIPLIER = 2
BOMB_REMOVE_OFFSET_MULTIPLIER = 2
OBSTACLE_REMOVE_OFFSET = 3200

# Collision particles
FOOD_PARTICLE_VX_MIN = -10
FOOD_PARTICLE_VX_MAX = 10
FOOD_PARTICLE_VY_MIN = -10
FOOD_PARTICLE_VY_MAX = 10
FOOD_PARTICLE_LIFETIME = 30
FOOD_PARTICLE_SIZE = 4
BOMB_PARTICLE_VX_MIN = -15
BOMB_PARTICLE_VX_MAX = 15
BOMB_PARTICLE_VY_MIN = -15
BOMB_PARTICLE_VY_MAX = 15
BOMB_PARTICLE_LIFETIME = 40
BOMB_PARTICLE_SIZE = 6
BREAK_PARTICLE_VX_MIN = -15
BREAK_PARTICLE_VX_MAX = 15
BREAK_PARTICLE_VY_MIN = -15
BREAK_PARTICLE_VY_MAX = 15
BREAK_PARTICLE_LIFETIME = 40
BREAK_PARTICLE_SIZE = 6
SNAKE_SHRINK_PERCENTAGE = 0.2

# Bomb constants
BOMB_COLLISION_MARGIN = 20

# Bird constants
BIRD_SIZE = 240
BIRD_HEALTH = 5
BIRD_HOVER_AMPLITUDE = 100
BIRD_HOVER_SPEED = 0.02
BIRD_FONT_SIZE = 40
BIRD_DIALOGUE_Y = 950  # Bottom of screen for dialogue box
BIRD_DIALOGUE_HEIGHT = 90
BIRD_HEALTH_BAR_WIDTH = 100
BIRD_HEALTH_BAR_HEIGHT = 10

# UI constants
GAME_OVER_OVERLAY_ALPHA = 180
GAME_OVER_FONT_SIZE = 192
GAME_OVER_TEXT_Y_OFFSET = -130
RESTART_FONT_SIZE = 96
RESTART_TEXT_Y_OFFSET = 180

# Input constants

# Level generation
LEVEL_SPACING_MULTIPLIER = 3
GROK_TEMPERATURE = 0.3




# Movement zone settings
MOVEMENT_ZONE_END = int(SCREEN_WIDTH)
REST_POSITION = int(SCREEN_WIDTH * 0.35)

def grid_to_pixel(grid_x, grid_y):
    return (grid_x * GRID_SIZE + GRID_SIZE // 2, grid_y * GRID_SIZE + GRID_SIZE // 2)

def pixel_to_grid(px, py):
    return (px // GRID_SIZE, py // GRID_SIZE)

class Snake:
    def __init__(self, x, y):
        self.segments = deque([{'x': x, 'y': y, 'scale': 1.0, 'vx': 0, 'vy': 0}])
        self.radius = SNAKE_RADIUS
        self.length = 1
        self.last_direction = None
        self.facing_angle = 0
        self.vx = 0
        self.vy = 0
        self.grow_rate = SNAKE_GROW_RATE  # animation rate
        self.min_seg_dist = SCROLL_SPEED
        self.seg_speed = MOVE_SPEED * SNAKE_SEG_SPEED_MULTIPLIER
        self.eye_time = 0  # for pupil animation
        self.target_facing_angle = 0
        self.current_facing_angle = 0
        self.eye_lerp_factor = SNAKE_EYE_LERP_FACTOR  # smooth eye movement
        self.red_tint_timer = 0
        self.dying = False
        self.eye_fall_speed = 5
        self.eye_x = 0
        self.eye_y = 0
        self.dying_timer = 0
        # Start with 5 segments
        for i in range(4):
            self.grow()

    def move(self, dx, dy):
        head_seg = self.segments[0]
        head_x, head_y = head_seg['x'], head_seg['y']
        # Reset last_direction if movement is idle/slow
        if len(self.segments) > 1:
            prev_seg = self.segments[1]
            prev_x, prev_y = prev_seg['x'], prev_seg['y']
            dist_last = math.hypot(head_x - prev_x, head_y - prev_y)
            if dist_last < SNAKE_IDLE_DIST_THRESHOLD:
                self.last_direction = None
        
        input_dx, input_dy = dx, dy
        effective_dx, effective_dy = dx, dy
        update_direction = True
        

        
        # Compute target velocity
        norm = math.sqrt(effective_dx**2 + effective_dy**2)
        if norm > 0:
            target_vx = (effective_dx / norm) * MOVE_SPEED
            target_vy = (effective_dy / norm) * MOVE_SPEED
        else:
            target_vx = 0.0
            target_vy = 0.0
    
        if input_dx == 0 and input_dy == 0:
            # Idle: apply friction and drift force
            friction = SNAKE_FRICTION
            self.vx *= friction
            self.vy *= friction
            if abs(head_x - REST_POSITION) > REST_POSITION_THRESHOLD:
                drift_force_x = (REST_POSITION - head_x) * SNAKE_DRIFT_FORCE
                self.vx += drift_force_x
        else:
            # Accelerate towards target velocity
            accel = SNAKE_ACCEL
            self.vx += (target_vx - self.vx) * accel
            self.vy += (target_vy - self.vy) * accel
        
        move_x = SCROLL_SPEED + self.vx
        move_y = self.vy
        
        target_x = head_x + move_x
        target_y = head_y + move_y
        
        buffer = self.radius * SNAKE_BUFFER_MULTIPLIER
        
        # Left edge slowdown
        left_limit = self.radius
        dist_to_left = head_x - left_limit
        if move_x < 0 and dist_to_left < buffer:
            proximity = max(0, dist_to_left) / buffer
            slowdown = proximity ** 2
            move_x *= slowdown
        
        # Right edge slowdown
        right_limit = MOVEMENT_ZONE_END - self.radius
        dist_to_right = right_limit - head_x
        if move_x > 0 and dist_to_right < buffer:
            proximity = max(0, dist_to_right) / buffer
            slowdown = proximity ** 2
            move_x *= slowdown
        
        # Top edge slowdown
        top_limit = self.radius
        dist_to_top = head_y - top_limit
        if move_y < 0 and dist_to_top < buffer:
            proximity = max(0, dist_to_top) / buffer
            slowdown = proximity ** 2
            move_y *= slowdown
        
        # Bottom edge slowdown
        bottom_limit = SCREEN_HEIGHT - self.radius
        dist_to_bottom = bottom_limit - head_y
        if move_y > 0 and dist_to_bottom < buffer:
            proximity = max(0, dist_to_bottom) / buffer
            slowdown = proximity ** 2
            move_y *= slowdown
        
        new_x = head_x + move_x
        new_y = head_y + move_y
        new_x = max(self.radius, min(right_limit, new_x))
        new_y = max(self.radius, min(bottom_limit, new_y))
        
        actual_dx = new_x - head_x
        actual_dy = new_y - head_y
        if actual_dx != 0 or actual_dy != 0:
            self.facing_angle = math.atan2(actual_dy, actual_dx)
            self.target_facing_angle = self.facing_angle
        
        # Smooth eye positioning
        self.current_facing_angle += (self.target_facing_angle - self.current_facing_angle) * self.eye_lerp_factor
        
        self.segments[0] = {'x': new_x, 'y': new_y, 'scale': self.segments[0]['scale']}

        # Move segments towards the one in front
        for i in range(1, len(self.segments)):
            target_x, target_y = self.segments[i-1]['x'], self.segments[i-1]['y']
            curr_x, curr_y = self.segments[i]['x'], self.segments[i]['y']
            dx = target_x - curr_x
            dy = target_y - curr_y
            dist = math.hypot(dx, dy)
            if dist > self.min_seg_dist:
                move_dist = min(self.seg_speed, dist - self.min_seg_dist)
                curr_x += (dx / dist) * move_dist
                curr_y += (dy / dist) * move_dist
                self.segments[i]['x'] = curr_x
                self.segments[i]['y'] = curr_y

        if update_direction and (input_dx != 0 or input_dy != 0):
            self.last_direction = (input_dx, input_dy)
        self.eye_time += 1  # increment for pupil animation

    def shift_world_scroll(self, amount):
        for seg in self.segments:
            seg['x'] -= amount

    def grow(self):
        tail = self.segments[-1]
        self.segments.append({'x': tail['x'], 'y': tail['y'], 'scale': 0.0, 'vx': 0, 'vy': 0})
        self.length += 1

    def shrink(self, percentage):
        reduction = max(1, int(self.length * percentage))
        self.length = max(1, self.length - reduction)
        self.segments = deque(list(self.segments)[:self.length])

    def start_dying(self):
        self.dying = True
        for seg in self.segments:
            seg['vx'] = random.uniform(-10, 10)
            seg['vy'] = random.uniform(-10, 10)
        self.eye_x = self.segments[0]['x']
        self.eye_y = self.segments[0]['y']
        self.dying_timer = 0

    def draw(self, surf):
        segments_list = list(self.segments)

        for i, seg in enumerate(segments_list):
            scale = seg['scale']
            radius = int(self.radius * scale)
            if radius > 0:
                color = RED if self.red_tint_timer > 0 else (DARK_GREEN if i == 0 or i == len(segments_list) - 1 else GREEN)
                if self.dying:
                    alpha = max(0, 255 - self.dying_timer * 3)
                    if alpha > 0:
                        temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(temp_surf, (*color, alpha), (radius, radius), radius)
                        surf.blit(temp_surf, (int(seg['x'] - radius), int(seg['y'] - radius)))
                else:
                    pygame.draw.circle(surf, color, (int(seg['x']), int(seg['y'])), radius)

        # Draw eyes on top, always visible
        if len(segments_list) > 0:
            head_seg = segments_list[0]
            head_x, head_y = head_seg['x'], head_seg['y']
            eye_radius = EYE_RADIUS  # slightly smaller eyes
            pupil_radius = PUPIL_RADIUS
            eye_offset_forward = EYE_OFFSET_FORWARD  # reduced offset to slightly overlap head
            eye_offset_side = EYE_OFFSET_SIDE

            if self.dying:
                # Eyes fall straight down from initial position, no fading
                pygame.draw.circle(surf, WHITE, (int(self.eye_x - 10), int(self.eye_y)), eye_radius)
                pygame.draw.circle(surf, WHITE, (int(self.eye_x + 10), int(self.eye_y)), eye_radius)
                pygame.draw.circle(surf, BLACK, (int(self.eye_x - 10), int(self.eye_y)), pupil_radius)
                pygame.draw.circle(surf, BLACK, (int(self.eye_x + 10), int(self.eye_y)), pupil_radius)
            else:
                left_eye_x = head_x + math.cos(self.current_facing_angle) * eye_offset_forward - math.sin(self.current_facing_angle) * eye_offset_side
                left_eye_y = head_y + math.sin(self.current_facing_angle) * eye_offset_forward + math.cos(self.current_facing_angle) * eye_offset_side

                right_eye_x = head_x + math.cos(self.current_facing_angle) * eye_offset_forward + math.sin(self.current_facing_angle) * eye_offset_side
                right_eye_y = head_y + math.sin(self.current_facing_angle) * eye_offset_forward - math.cos(self.current_facing_angle) * eye_offset_side

                pygame.draw.circle(surf, WHITE, (int(left_eye_x), int(left_eye_y)), eye_radius)
                pygame.draw.circle(surf, WHITE, (int(right_eye_x), int(right_eye_y)), eye_radius)
                # Moving pupils
                pupil_offset_x = math.sin(self.eye_time * PUPIL_OFFSET_X_FACTOR) * PUPIL_OFFSET_X_AMPLITUDE
                pupil_offset_y = math.cos(self.eye_time * PUPIL_OFFSET_Y_FACTOR) * PUPIL_OFFSET_Y_AMPLITUDE
                pygame.draw.circle(surf, BLACK, (int(left_eye_x + pupil_offset_x), int(left_eye_y + pupil_offset_y)), pupil_radius)
                pygame.draw.circle(surf, BLACK, (int(right_eye_x + pupil_offset_x), int(right_eye_y + pupil_offset_y)), pupil_radius)

class Food:
    def __init__(self, grid_x, grid_y, pixel_x_offset):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x_offset = pixel_x_offset
        px, py = grid_to_pixel(grid_x, grid_y)
        self.x = px + pixel_x_offset
        self.y = py
        self.scale = 0.0
        self.radius = FOOD_RADIUS

    def shift_left(self, amt):
        self.pixel_x_offset -= amt
        self.x = grid_to_pixel(self.grid_x, self.grid_y)[0] + self.pixel_x_offset
    
    def update(self):
        if self.scale < 1.0:
            self.scale = min(1.0, self.scale + FOOD_SCALE_INCREMENT)

    def draw(self, surf, image):
        scaled_image = pygame.transform.scale(image, (int(image.get_width() * self.scale), int(image.get_height() * self.scale)))
        rect = scaled_image.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(scaled_image, rect)

    def check_collision(self, snake):
        head = snake.segments[0]
        head_x, head_y = head['x'], head['y']
        dist = math.hypot(head_x - self.x, head_y - self.y)
        return dist < self.radius * self.scale + snake.radius + BOMB_COLLISION_MARGIN

class BombApple:
    def __init__(self, grid_x, grid_y, pixel_x_offset):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x_offset = pixel_x_offset
        px, py = grid_to_pixel(grid_x, grid_y)
        self.x = px + pixel_x_offset
        self.y = py
        self.scale = 0.0
        self.radius = BOMB_RADIUS
        self.pulse = 0

    def shift_left(self, amt):
        self.pixel_x_offset -= amt
        self.x = grid_to_pixel(self.grid_x, self.grid_y)[0] + self.pixel_x_offset
    
    def update(self):
        if self.scale < 1.0:
            self.scale = min(1.0, self.scale + BOMB_SCALE_INCREMENT)
        self.pulse += BOMB_PULSE_INCREMENT

    def draw(self, surf, image):
        scaled_image = pygame.transform.scale(image, (int(image.get_width() * self.scale), int(image.get_height() * self.scale)))
        rect = scaled_image.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(scaled_image, rect)
        self.pulse += BOMB_PULSE_INCREMENT

    def check_collision(self, snake):
        head = snake.segments[0]
        head_x, head_y = head['x'], head['y']
        dist = math.hypot(head_x - self.x, head_y - self.y)
        return dist < self.radius * self.scale + snake.radius

class Bomb:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.timer = 0
        self.max_timer = 3 * FPS
        self.active = True
        self.radius = BOMB_RADIUS

    def shift_left(self, amt):
        self.x -= amt

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.timer += 1
        if self.timer >= self.max_timer:
            self.active = False

    def check_explode(self, obstacles):
        for obs in obstacles:
            positions = obs.get_pixel_positions()
            for px, py in positions:
                if (px - GRID_SIZE//2 - BOMB_COLLISION_MARGIN <= self.x <= px + GRID_SIZE//2 + BOMB_COLLISION_MARGIN and
                    py - GRID_SIZE//2 - BOMB_COLLISION_MARGIN <= self.y <= py + GRID_SIZE//2 + BOMB_COLLISION_MARGIN):
                    return True
        return False

    def draw(self, surf, image):
        rect = image.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(image, rect)

class GridObstacle:
    def __init__(self, grid_positions, pixel_x_offset):
        self.grid_positions = grid_positions
        self.pixel_x_offset = pixel_x_offset
        self.color = random.choice([GRAY, ORANGE, PURPLE])
        
    def shift_left(self, amt):
        self.pixel_x_offset -= amt
        
    def update(self):
        pass
        
    def get_pixel_positions(self):
        positions = []
        for gx, gy in self.grid_positions:
            px, py = grid_to_pixel(gx, gy)
            positions.append((px + self.pixel_x_offset, py))
        return positions
        
    def draw(self, surf):
        positions = self.get_pixel_positions()
        for px, py in positions:
            rect = pygame.Rect(px - GRID_SIZE//2, py - GRID_SIZE//2, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surf, self.color, rect)
            pygame.draw.rect(surf, WHITE, rect, OBSTACLE_RECT_BORDER)
            
    def check_collision(self, snake):
        head = snake.segments[0]
        head_x, head_y = head['x'], head['y']
        positions = self.get_pixel_positions()

        for px, py in positions:
            if (px - GRID_SIZE//2 <= head_x <= px + GRID_SIZE//2 and
                py - GRID_SIZE//2 <= head_y <= py + GRID_SIZE//2):
                return True
        return False
    
    def get_center(self):
        positions = self.get_pixel_positions()
        if not positions:
            return (0, 0)
        avg_x = sum(p[0] for p in positions) / len(positions)
        avg_y = sum(p[1] for p in positions) / len(positions)
        return (avg_x, avg_y)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = EXPLOSION_RADIUS
        self.duration = EXPLOSION_DURATION
        self.timer = 0

    def shift_left(self, amt):
        self.x -= amt

    def update(self):
        self.timer += 1
        return self.timer < self.duration

    def draw(self, surf):
        progress = self.timer / self.duration
        current_radius = int(self.radius * (EXPLOSION_CORE_START_FACTOR + progress * EXPLOSION_CORE_END_FACTOR))

        # Inner bright core that fades quickly
        if progress < EXPLOSION_INNER_FADE_START:
            inner_r = int(current_radius * EXPLOSION_INNER_RADIUS_FACTOR)
            inner_factor = 1 - progress / EXPLOSION_INNER_FADE_START
            inner_color = (min(255, int(EXPLOSION_COLOR[0] * inner_factor * EXPLOSION_INNER_FACTOR_MULTIPLIER + 255 * (1 - inner_factor))),
                          min(255, int(EXPLOSION_COLOR[1] * inner_factor * EXPLOSION_INNER_FACTOR_MULTIPLIER + 255 * (1 - inner_factor))),
                          min(255, int(EXPLOSION_COLOR[2] * inner_factor * EXPLOSION_INNER_FACTOR_MULTIPLIER + 0 * (1 - inner_factor))))
            pygame.draw.circle(surf, inner_color, (int(self.x), int(self.y)), inner_r)

        # Gradient-like rings with varying thickness and color
        for i in range(EXPLOSION_RING_COUNT):
            r = current_radius - i * EXPLOSION_RING_RADIUS_DECREMENT
            if r > 0:
                # Staggered color fading for gradient effect
                ring_progress = progress + i * EXPLOSION_RING_PROGRESS_OFFSET
                if ring_progress > 1: ring_progress = 1
                factor = 1 - ring_progress
                faded_color = (int(EXPLOSION_COLOR[0] * factor + 255 * (1 - factor)),
                              int(EXPLOSION_COLOR[1] * factor + 255 * (1 - factor)),
                              int(EXPLOSION_COLOR[2] * factor + 0 * (1 - factor)))
                thickness = max(1, EXPLOSION_RING_THICKNESS_BASE - i * EXPLOSION_RING_THICKNESS_DECREMENT)  # Thinner outer rings
                pygame.draw.circle(surf, faded_color, (int(self.x), int(self.y)), r, thickness)

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=5, shape='circle'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.timer = 0
        self.size = size
        self.shape = shape
        self.original_color = color

    def shift_left(self, amt):
        self.x -= amt

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.timer += 1
        return self.timer < self.lifetime

    def draw(self, surf):
        if self.timer < self.lifetime:
            brightness = max(0, 1 - self.timer / self.lifetime)
            r, g, b = self.original_color
            faded_color = (int(r * brightness + 255 * (1 - brightness)), int(g * brightness + 255 * (1 - brightness)), int(b * brightness + 255 * (1 - brightness)))
            size = self.size
            if self.shape == 'circle':
                pygame.draw.circle(surf, faded_color, (int(self.x), int(self.y)), size)
            elif self.shape == 'square':
                pygame.draw.rect(surf, faded_color, (int(self.x - size), int(self.y - size), size * 2, size * 2))
            elif self.shape == 'triangle':
                # Draw a triangle pointing up
                points = [
                    (int(self.x), int(self.y - size)),
                    (int(self.x - size), int(self.y + size)),
                    (int(self.x + size), int(self.y + size))
                ]
                pygame.draw.polygon(surf, faded_color, points)

class Bird:
    def __init__(self, x, y, images):
        self.target_x = x
        self.x = x + 200  # Start off-screen to the right
        self.initial_y = y
        self.y = y
        self.size = BIRD_SIZE
        self.health = BIRD_HEALTH
        self.active = True
        self.timer = 0
        self.text = ""
        self.images = images
        self.frame = 0
        self.show_health_timer = 0
        self.shake_timer = 0
        self.shake_offset = (0, 0)
        self.falling = False
        self.fall_speed = 3
        self.appearing = True
        self.immunity_timer = 0
        self.state = 'appearing'
        self.charge_speed = 15
        self.charge_timer = 120
        self.play_hit_sound = False
        self.play_screech_sound = False
        self.play_dead_sound = False
        self.play_nibble_quote = False
        self.play_damaged_quote = False

    def update(self, snake):
        self.timer += 1
        if self.state == 'appearing':
            self.x -= 15  # Fly in speed
            if self.x <= self.target_x:
                self.x = self.target_x
                self.state = 'hovering'
                self.charge_timer = 120
        elif self.state == 'hovering':
            self.y = self.initial_y + math.sin(self.timer * BIRD_HOVER_SPEED) * BIRD_HOVER_AMPLITUDE
            self.charge_timer -= 1
            if self.charge_timer <= 0:
                self.state = 'charging'
                self.play_screech_sound = True
        elif self.state == 'charging':
            head_x = snake.segments[0]['x']
            head_y = snake.segments[0]['y']
            dx = head_x - self.x
            dy = head_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.charge_speed
                self.y += (dy / dist) * self.charge_speed
            if dist < self.size / 2 + snake.radius:
                # Eat half of the segments
                half = len(snake.segments) // 2
                snake.segments = deque(list(snake.segments)[:half])
                snake.length = half
                snake.red_tint_timer = 15
                self.play_hit_sound = True
                self.play_nibble_quote = True
                self.falling = True
                self.state = 'falling'
        elif self.state == 'knockback':
            dx = self.target_x - self.x
            dy = self.initial_y - self.y
            self.x += dx * 0.1
            self.y += dy * 0.1
            if abs(dx) < 1 and abs(dy) < 1:
                self.x = self.target_x
                self.y = self.initial_y
                self.state = 'hovering'
                self.charge_timer = 120

        elif self.state == 'falling':
            self.y += self.fall_speed
        self.frame = (self.timer // 10) % len(self.images)
        if self.show_health_timer > 0:
            self.show_health_timer -= 1
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
        else:
            self.shake_offset = (0, 0)
        if self.immunity_timer > 0:
            self.immunity_timer -= 1

    def draw(self, surf):
        scaled_image = pygame.transform.scale(self.images[self.frame], (self.size, self.size))
        surf.blit(scaled_image, (int(self.x - self.size // 2 + self.shake_offset[0]), int(self.y - self.size // 2 + self.shake_offset[1])))
        if self.show_health_timer > 0:
            bar_x = self.x - BIRD_HEALTH_BAR_WIDTH // 2
            bar_y = self.y - self.size // 2 - 30
            # Background
            pygame.draw.rect(surf, BLACK, (bar_x, bar_y, BIRD_HEALTH_BAR_WIDTH, BIRD_HEALTH_BAR_HEIGHT), border_radius=5)
            # Health fill
            health_width = max(0, (self.health / BIRD_HEALTH) * BIRD_HEALTH_BAR_WIDTH)
            pygame.draw.rect(surf, GREEN, (bar_x, bar_y, health_width, BIRD_HEALTH_BAR_HEIGHT), border_radius=5)
        # Dialogue box at bottom
        dialogue_rect = pygame.Rect(0, BIRD_DIALOGUE_Y, SCREEN_WIDTH, BIRD_DIALOGUE_HEIGHT)
        pygame.draw.rect(surf, (0, 0, 0), dialogue_rect, border_radius=15)  # Black background
        pygame.draw.rect(surf, WHITE, dialogue_rect, 2, border_radius=15)  # White border
        font = pygame.font.Font('assets/font.ttf', BIRD_FONT_SIZE)
        # Wrap text to fit within dialogue box
        max_width = SCREEN_WIDTH - 100  # Padding
        words = self.text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        # Render each line
        line_height = font.get_height()
        line_spacing = line_height + 7  # Increase spacing
        total_height = len(lines) * line_spacing - 3  # Adjust total height
        start_y = BIRD_DIALOGUE_Y + (BIRD_DIALOGUE_HEIGHT - total_height) // 2
        for i, line in enumerate(lines):
            text_surf = font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * line_spacing + line_height // 2))
            surf.blit(text_surf, text_rect)

    def set_text(self, new_text):
        self.text = new_text

    def take_damage(self):
        self.health -= 1
        self.shake_timer = 10  # Shake for 10 frames
        self.immunity_timer = 60  # 1 second immunity
        if self.health <= 0:
            self.falling = True
            self.state = 'falling'

    def stun(self):
        self.health -= 2
        self.shake_timer = 10
        self.red_tint_timer = 15  # Red tint for 0.25 seconds
        self.show_health_timer = FPS
        self.play_damaged_quote = True
        if self.health <= 0:
            self.falling = True
            self.state = 'falling'
            self.play_dead_sound = True
        else:
            self.state = 'knockback'

    def check_collision(self, bomb):
        if self.immunity_timer > 0:
            return False
        dist = math.hypot(bomb.x - self.x, bomb.y - self.y)
        return dist < (self.size / 2 + bomb.radius + BOMB_COLLISION_MARGIN)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("snAIke")
        self.clock = pygame.time.Clock()
        self.menu_timer = 0
        self.distance_traveled = 0

        # Load and tile background image
        self.bg_image = pygame.image.load('assets/background.png').convert()
        self.bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_w = self.bg_image.get_width()
        bg_h = self.bg_image.get_height()
        x = -(bg_w - SCREEN_WIDTH) / 2
        y = -(bg_h - SCREEN_HEIGHT) / 2
        self.bg_surface.blit(self.bg_image, (x, y))

        # Load food and bomb images
        self.food_image = pygame.image.load('assets/apple.png').convert_alpha()
        self.bomb_image = pygame.image.load('assets/bomb.png').convert_alpha()
        self.bird_image = pygame.image.load('assets/bird.png').convert_alpha()
        self.bird_image2 = pygame.image.load('assets/bird2.png').convert_alpha()
        # Load sounds
        self.bomb_sound = pygame.mixer.Sound('assets/bomb.wav')
        self.deadbird_sound = pygame.mixer.Sound('assets/deadbird.wav')
        self.eat_sound = pygame.mixer.Sound('assets/eat.mp3')
        self.hit_sound = pygame.mixer.Sound('assets/hit.wav')
        self.screech_sound = pygame.mixer.Sound('assets/screech.wav')
        self.click_sound = pygame.mixer.Sound('assets/click.wav')
        self.bombs = []
        self.bird = None
        self.last_bird_time = 0
        self.bird_quote = ""
        self.previous_quotes = []
        self.event_cycle = ['appeared', 'damaged', 'damaged', 'dying']
        self.event_index = 0

        self.state = 'menu'

        # Score tracking
        self.apples_collected = 0
        self.bombs_shot = 0
        self.birds_killed = 0
        self.bomb_cooldown = 60  # 1 second delay before bombs can be shot

        self.load_quotes()



    def reset_game(self):
        self.snake = Snake(REST_POSITION, SCREEN_HEIGHT // 2)
        self.foods = []
        self.bomb_apples = []
        self.bombs = []
        self.bird = None
        self.obstacles = []
        self.explosions = []
        self.particles = []
        self.obstacle_queue = []
        self.distance_traveled = 0
        self.next_food_spawn = random.randint(FOOD_SPAWN_DISTANCE_MIN, FOOD_SPAWN_DISTANCE_MAX)
        self.next_obstacle_spawn = random.randint(OBSTACLE_SPAWN_DISTANCE_MIN, OBSTACLE_SPAWN_DISTANCE_MAX)
        self.last_bird_time = pygame.time.get_ticks()
        self.game_over = False

        # Reset score tracking
        self.apples_collected = 0
        self.bombs_shot = 0
        self.birds_killed = 0

        self.previous_quotes = []
        self.load_quotes()

    def spawn_food(self):
        pixel_x_offset = SCREEN_WIDTH + GRID_SIZE
        forbidden_positions = set((gx, gy) for obs in self.obstacles for gx, gy in obs.grid_positions)
        grid_x, grid_y = None, None
        for _ in range(SPAWN_ATTEMPTS):
            candidate_x = random.randint(0, GRID_COLS - 1)
            candidate_y = random.randint(1, GRID_ROWS - 2)
            if (candidate_x, candidate_y) not in forbidden_positions:
                grid_x, grid_y = candidate_x, candidate_y
                break
        if grid_x is None:
            grid_x = random.randint(0, GRID_COLS - 1)
            grid_y = random.randint(1, GRID_ROWS - 2)
        self.foods.append(Food(grid_x, grid_y, pixel_x_offset))

    def spawn_bomb_apple(self):
        pixel_x_offset = SCREEN_WIDTH + GRID_SIZE
        forbidden_positions = set((gx, gy) for obs in self.obstacles for gx, gy in obs.grid_positions)
        grid_x, grid_y = None, None
        for _ in range(SPAWN_ATTEMPTS):
            candidate_x = random.randint(0, GRID_COLS - 1)
            candidate_y = random.randint(0, GRID_ROWS - 1)
            if (candidate_x, candidate_y) not in forbidden_positions:
                grid_x, grid_y = candidate_x, candidate_y
                break
        if grid_x is None:
            grid_x = random.randint(0, GRID_COLS - 1)
            grid_y = random.randint(0, GRID_ROWS - 1)
        self.bomb_apples.append(BombApple(grid_x, grid_y, pixel_x_offset))

    def spawn_obstacle(self):
        forbidden_y = set(gy for obs in self.obstacles for gx, gy in obs.grid_positions if gx == 0)
        num_tiles = random.randint(OBSTACLE_NUM_TILES_MIN, OBSTACLE_NUM_TILES_MAX)
        start_grid_y = random.randint(0, GRID_ROWS - num_tiles)
        attempts = 0
        while any(start_grid_y + i in forbidden_y for i in range(num_tiles)) and attempts < SPAWN_ATTEMPTS:
            start_grid_y = random.randint(0, GRID_ROWS - num_tiles)
            attempts += 1
        grid_positions = [(0, start_grid_y + i) for i in range(num_tiles)]
        
        new_obstacle = GridObstacle(grid_positions, pixel_x_offset=SCREEN_WIDTH + GRID_SIZE)
        self.obstacles.append(new_obstacle)


    def handle_input(self):
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1





        self.snake.move(dx, dy)

    def update(self):
        # Update dying animation first
        if self.snake.dying:
            for seg in self.snake.segments:
                seg['x'] += seg['vx']
                seg['y'] += seg['vy']
                seg['vx'] *= 0.98
                seg['vy'] *= 0.98
            self.snake.eye_y += self.snake.eye_fall_speed
            self.snake.dying_timer += 1

        if self.game_over:
            return
        
        self.snake.shift_world_scroll(SCROLL_SPEED)
        self.snake.red_tint_timer = max(0, self.snake.red_tint_timer - 1)
        self.bomb_cooldown = max(0, self.bomb_cooldown - 1)
        
        # Update snake segment scales
        for seg in self.snake.segments:
            if seg['scale'] < 1.0:
                seg['scale'] = min(1.0, seg['scale'] + self.snake.grow_rate)
        
        for food in self.foods:
            food.shift_left(SCROLL_SPEED)
            food.update()
        for bomb in self.bomb_apples:
            bomb.shift_left(SCROLL_SPEED)
            bomb.update()
        for bomb in self.bombs:
            bomb.shift_left(SCROLL_SPEED)
            bomb.update()
        for obstacle in self.obstacles:
            obstacle.shift_left(SCROLL_SPEED)
        for explosion in self.explosions:
            explosion.shift_left(SCROLL_SPEED)
        for particle in self.particles:
            particle.shift_left(SCROLL_SPEED)


        
        self.distance_traveled += SCROLL_SPEED
        self.handle_input()
        self.explosions = [e for e in self.explosions if e.update()]
        self.particles = [p for p in self.particles if p.update()]
        if self.bird:
            self.bird.update(self.snake)
            if self.bird.play_hit_sound:
                self.hit_sound.play()
                self.bird.play_hit_sound = False
            if self.bird.play_screech_sound:
                self.screech_sound.play()
                self.bird.play_screech_sound = False
            if self.bird.play_dead_sound:
                self.deadbird_sound.play()
                self.bird.play_dead_sound = False
            if self.bird.play_nibble_quote:
                self.get_quote_by_event('nibble')
                self.bird.play_nibble_quote = False
            if self.bird.play_damaged_quote:
                self.get_quote_by_event('damaged')
                self.bird.play_damaged_quote = False
        
        if self.distance_traveled >= self.next_food_spawn:
            self.spawn_food()
            self.next_food_spawn += random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX) * GRID_SIZE
        
        if self.distance_traveled >= self.next_obstacle_spawn:
            if self.obstacle_queue:
                obs_def = self.obstacle_queue.pop(0)
                new_obstacle = GridObstacle(obs_def['grid_positions'], pixel_x_offset=SCREEN_WIDTH + GRID_SIZE)
                self.obstacles.append(new_obstacle)
                self.next_obstacle_spawn += obs_def['spacing']
            else:
                self.spawn_obstacle()
                self.next_obstacle_spawn += random.randint(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX) * GRID_SIZE

        if pygame.time.get_ticks() - self.last_bird_time >= 10000 and self.bird is None:
            y = SCREEN_HEIGHT // 2
            self.bird = Bird(SCREEN_WIDTH - 100, y, [self.bird_image, self.bird_image2])
            self.get_quote_by_event('appeared')
            self.last_bird_time = pygame.time.get_ticks()
            # Screech when bird appears/attacks, but since appears first, perhaps on charge

        
        self.foods = [f for f in self.foods if f.x > -FOOD_RADIUS * FOOD_REMOVE_OFFSET_MULTIPLIER]
        self.bomb_apples = [b for b in self.bomb_apples if b.x > -BOMB_RADIUS * BOMB_REMOVE_OFFSET_MULTIPLIER]
        self.bombs = [b for b in self.bombs if b.active]
        self.obstacles = [o for o in self.obstacles if o.pixel_x_offset > -OBSTACLE_REMOVE_OFFSET]

        
        for food in self.foods[:]:
            if food.check_collision(self.snake):
                for _ in range(SEGMENTS_PER_FOOD):
                    self.snake.grow()
                # spawn particles for eating apple
                for _ in range(FOOD_PARTICLE_COUNT):
                    vx = random.uniform(FOOD_PARTICLE_VX_MIN, FOOD_PARTICLE_VX_MAX)
                    vy = random.uniform(FOOD_PARTICLE_VY_MIN, FOOD_PARTICLE_VY_MAX)
                    self.particles.append(Particle(food.x, food.y, vx, vy, GREEN, FOOD_PARTICLE_LIFETIME, FOOD_PARTICLE_SIZE, 'circle'))
                self.eat_sound.play()
                self.foods.remove(food)
                self.apples_collected += 1
        

        
        for bomb in self.bomb_apples[:]:
            if bomb.check_collision(self.snake):
                bomb_x, bomb_y = bomb.x, bomb.y
                self.explosions.append(Explosion(bomb_x, bomb_y))
                self.bomb_sound.play()
                # spawn particles for explosion
                for _ in range(BOMB_PARTICLE_COUNT):
                    vx = random.uniform(BOMB_PARTICLE_VX_MIN, BOMB_PARTICLE_VX_MAX)
                    vy = random.uniform(BOMB_PARTICLE_VY_MIN, BOMB_PARTICLE_VY_MAX)
                    self.particles.append(Particle(bomb_x, bomb_y, vx, vy, EXPLOSION_COLOR, BOMB_PARTICLE_LIFETIME, BOMB_PARTICLE_SIZE, 'square'))
                obstacles_to_remove = []
                for obstacle in self.obstacles:
                    ox, oy = obstacle.get_center()
                    dist = math.hypot(bomb_x - ox, bomb_y - oy)
                    if dist < EXPLOSION_RADIUS:
                        obstacles_to_remove.append(obstacle)
                for obs in obstacles_to_remove:
                    # spawn destruction particles for each grid in the obstacle
                    for grid_pos in obs.grid_positions:
                        gx, gy = grid_pos
                        px, py = grid_to_pixel(gx, gy)
                        actual_px = px + obs.pixel_x_offset
                        actual_py = py
                        for _ in range(BREAK_PARTICLE_COUNT):
                            vx = random.uniform(BREAK_PARTICLE_VX_MIN, BREAK_PARTICLE_VX_MAX)
                            vy = random.uniform(BREAK_PARTICLE_VY_MIN, BREAK_PARTICLE_VY_MAX)
                            self.particles.append(Particle(actual_px, actual_py, vx, vy, obs.color, BREAK_PARTICLE_LIFETIME, BREAK_PARTICLE_SIZE, 'triangle'))
                    self.obstacles.remove(obs)
                self.snake.shrink(SNAKE_SHRINK_PERCENTAGE)
                self.last_bomb_distance = self.distance_traveled
                self.bomb_apples.remove(bomb)
        
        for bomb in self.bombs[:]:
            if bomb.check_explode(self.obstacles) or bomb.timer >= bomb.max_timer:
                bomb_x, bomb_y = bomb.x, bomb.y
                self.explosions.append(Explosion(bomb_x, bomb_y))
                self.bomb_sound.play()
                # spawn particles for explosion
                for _ in range(BOMB_PARTICLE_COUNT):
                    vx = random.uniform(BOMB_PARTICLE_VX_MIN, BOMB_PARTICLE_VX_MAX)
                    vy = random.uniform(BOMB_PARTICLE_VY_MIN, BOMB_PARTICLE_VY_MAX)
                    self.particles.append(Particle(bomb_x, bomb_y, vx, vy, EXPLOSION_COLOR, BOMB_PARTICLE_LIFETIME, BOMB_PARTICLE_SIZE, 'square'))
                obstacles_to_remove = []
                for obstacle in self.obstacles:
                    ox, oy = obstacle.get_center()
                    dist = math.hypot(bomb_x - ox, bomb_y - oy)
                    if dist < EXPLOSION_RADIUS:
                        obstacles_to_remove.append(obstacle)
                for obs in obstacles_to_remove:
                    # spawn destruction particles for each grid in the obstacle
                    for grid_pos in obs.grid_positions:
                        gx, gy = grid_pos
                        px, py = grid_to_pixel(gx, gy)
                        actual_px = px + obs.pixel_x_offset
                        actual_py = py
                        for _ in range(BREAK_PARTICLE_COUNT):
                            vx = random.uniform(BREAK_PARTICLE_VX_MIN, BREAK_PARTICLE_VX_MAX)
                            vy = random.uniform(BREAK_PARTICLE_VY_MIN, BREAK_PARTICLE_VY_MAX)
                            self.particles.append(Particle(actual_px, actual_py, vx, vy, obs.color, BREAK_PARTICLE_LIFETIME, BREAK_PARTICLE_SIZE, 'triangle'))
                    self.obstacles.remove(obs)
                self.bombs.remove(bomb)
        
        if self.bird:
            for bomb in self.bombs[:]:
                if self.bird.check_collision(bomb):
                    bomb_x, bomb_y = bomb.x, bomb.y
                    self.explosions.append(Explosion(bomb_x, bomb_y))
                    self.bomb_sound.play()
                    # spawn particles for explosion
                    for _ in range(BOMB_PARTICLE_COUNT):
                        vx = random.uniform(BOMB_PARTICLE_VX_MIN, BOMB_PARTICLE_VX_MAX)
                        vy = random.uniform(BOMB_PARTICLE_VY_MIN, BOMB_PARTICLE_VY_MAX)
                        self.particles.append(Particle(bomb_x, bomb_y, vx, vy, EXPLOSION_COLOR, BOMB_PARTICLE_LIFETIME, BOMB_PARTICLE_SIZE, 'square'))
                    if self.bird.state == 'charging':
                        self.bird.stun()
                    else:
                        self.bird.take_damage()
                        self.bird.show_health_timer = FPS
                        if self.bird.health <= 0:
                            self.get_quote_by_event('dying')
                        else:
                            self.get_quote_by_event('damaged')
                        if self.bird.health <= 0:
                            self.deadbird_sound.play()
                            self.bird.active = False
                            self.birds_killed += 1
                            # Don't set to None yet, let it fall
                    self.bombs.remove(bomb)
                    break
                
        all_obstacles = self.obstacles[:]
        for obstacle in all_obstacles:
            if obstacle.check_collision(self.snake):
                self.game_over = True
                self.deadbird_sound.play()
                if not self.snake.dying:
                    self.snake.start_dying()
                return

        # Self collision check after length > 25
        if len(self.snake.segments) > 25:
            head = self.snake.segments[0]
            segments = list(self.snake.segments)
            for i in range(25, len(segments), 5):
                seg = segments[i]
                dist = math.hypot(head['x'] - seg['x'], head['y'] - seg['y'])
                if dist < self.snake.radius * 2:
                    self.game_over = True
                    self.deadbird_sound.play()
                    if not self.snake.dying:
                        self.snake.start_dying()
                    return

        # Remove bird if it has fallen off screen
        if self.bird and self.bird.state == 'falling' and self.bird.y > SCREEN_HEIGHT + self.bird.size:
            self.bird = None
            self.last_bird_time = pygame.time.get_ticks()

    def draw(self):
        self.screen.blit(self.bg_surface, (0, 0))

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for food in self.foods:
            food.draw(self.screen, self.food_image)
        for bomb in self.bomb_apples:
            bomb.draw(self.screen, self.bomb_image)
        for bomb in self.bombs:
            bomb.draw(self.screen, self.bomb_image)
        if self.bird:
            self.bird.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        # Draw particles main
        for particle in self.particles:
            particle.draw(self.screen)
        # Draw particle glow effects
        for particle in self.particles:
            if particle.timer < particle.lifetime:
                glow_brightness = max(0, 1 - particle.timer / particle.lifetime) * PARTICLE_GLOW_BRIGHTNESS_MULTIPLIER  # brighter glow
                r, g, b = particle.original_color
                glow_color = (int(r * glow_brightness + 255 * (1 - glow_brightness)), int(g * glow_brightness + 255 * (1 - glow_brightness)), int(b * glow_brightness + 255 * (1 - glow_brightness)))
                if particle.shape == 'circle':
                    pygame.draw.circle(self.screen, glow_color, (int(particle.x), int(particle.y)), particle.size + PARTICLE_SIZE_GLOW_OFFSET)
                elif particle.shape == 'square':
                    size = particle.size + PARTICLE_SIZE_GLOW_OFFSET
                    pygame.draw.rect(self.screen, glow_color, (int(particle.x - size/2), int(particle.y - size/2), size, size))
        self.snake.draw(self.screen)

        # Draw score
        score = self.apples_collected - self.bombs_shot + (10 * self.birds_killed)
        font = pygame.font.Font('assets/font.ttf', 48)
        score_text = font.render(f"score: {score}", True, BLACK)
        text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(score_text, text_rect)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(GAME_OVER_OVERLAY_ALPHA)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.Font('assets/font.ttf', GAME_OVER_FONT_SIZE)
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + GAME_OVER_TEXT_Y_OFFSET))
            self.screen.blit(game_over_text, text_rect)
            small_font = pygame.font.Font('assets/font.ttf', RESTART_FONT_SIZE)
            restart_text = small_font.render("restart", True, WHITE)
            quit_text = small_font.render("quit to menu", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_TEXT_Y_OFFSET - 50))
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + RESTART_TEXT_Y_OFFSET + 140))
            self.restart_button_rect = pygame.Rect(restart_rect.left - 50, restart_rect.top - 25, restart_rect.width + 100, restart_rect.height + 50)
            self.quit_to_menu_button_rect = pygame.Rect(quit_rect.left - 50, quit_rect.top - 25, quit_rect.width + 100, quit_rect.height + 50)
            mouse_pos = pygame.mouse.get_pos()
            restart_hover = self.restart_button_rect.collidepoint(mouse_pos)
            quit_hover = self.quit_to_menu_button_rect.collidepoint(mouse_pos)
            restart_color = (0, 200, 0) if restart_hover else (0, 150, 0)
            quit_color = (200, 0, 0) if quit_hover else (150, 0, 0)
            pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, border_radius=15)
            pygame.draw.rect(self.screen, quit_color, self.quit_to_menu_button_rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, self.restart_button_rect, 4, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, self.quit_to_menu_button_rect, 4, border_radius=15)
            self.screen.blit(restart_text, restart_rect)
            self.screen.blit(quit_text, quit_rect)
        
        pygame.display.flip()

    def draw_menu(self):
        self.menu_timer += 1
        self.screen.blit(self.bg_surface, (0, 0))
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font('assets/font.ttf', 192)
        font_button = pygame.font.Font('assets/font.ttf', 96)
        title_text = font_large.render("sn[AI]ke", True, (255, 255, 255))
        start_text = font_button.render("start", True, (255, 255, 255))
        quit_text = font_button.render("quit", True, (255, 255, 255))
        title_y = 300 + math.sin(self.menu_timer * 0.05) * 10
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 750))

        # Title shadow
        title_shadow = font_large.render("sn[AI]ke", True, (0, 0, 0))
        self.screen.blit(title_shadow, (title_rect.x + 5, title_rect.y + 5))

        # Draw button backgrounds with colors and borders
        self.start_button_rect = pygame.Rect(start_rect.left - 50, start_rect.top - 25, start_rect.width + 100, start_rect.height + 50)
        self.quit_button_rect = pygame.Rect(quit_rect.left - 50, quit_rect.top - 25, quit_rect.width + 100, quit_rect.height + 50)
        mouse_pos = pygame.mouse.get_pos()
        start_hover = self.start_button_rect.collidepoint(mouse_pos)
        quit_hover = self.quit_button_rect.collidepoint(mouse_pos)
        start_color = (0, 200, 0) if start_hover else (0, 150, 0)
        quit_color = (200, 0, 0) if quit_hover else (150, 0, 0)
        pygame.draw.rect(self.screen, start_color, self.start_button_rect, border_radius=15)
        pygame.draw.rect(self.screen, quit_color, self.quit_button_rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), self.start_button_rect, 4, border_radius=15)
        pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button_rect, 4, border_radius=15)

        self.screen.blit(title_text, title_rect)
        self.screen.blit(start_text, start_rect)
        self.screen.blit(quit_text, quit_rect)
        pygame.display.flip()

    def get_player_stats(self):
        length = self.snake.length if hasattr(self, 'snake') and self.snake else 0
        time_alive = (self.distance_traveled / SCROLL_SPEED) / FPS if hasattr(self, 'snake') and self.snake else 0
        return {
            'length': length,
            'time_alive': time_alive,
        }

    def load_quotes(self):
        if USE_TEXT_QUOTES:
            try:
                with open('quotes.json', 'r') as f:
                    data = json.load(f)
                    for event, quotes in data.items():
                        NEXT_QUOTES[event] = quotes
            except FileNotFoundError:
                pass
        else:
            for event in ['appeared', 'damaged', 'dying', 'nibble']:
                if not NEXT_QUOTES[event]:
                    threading.Thread(target=self._generate_quote, args=(event,)).start()

    def save_quote(self, event, quote):
        try:
            with open('quotes.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {'appeared': [], 'damaged': [], 'dying': [], 'nibble': []}
        if event not in data:
            data[event] = []
        data[event].append(quote)
        with open('quotes.json', 'w') as f:
            json.dump(data, f, indent=4)

    def get_quote_by_event(self, event='regular'):
        if NEXT_QUOTES[event] and not USE_TEXT_QUOTES:
            self.bird_quote = NEXT_QUOTES[event].pop(0)
            self.previous_quotes.append(self.bird_quote)
        elif NEXT_QUOTES[event] and USE_TEXT_QUOTES:
            self.bird_quote = random.choice(NEXT_QUOTES[event])
            self.previous_quotes.append(self.bird_quote)
        else:
            fallback = "You're just a slimy worm!"
            self.bird_quote = fallback
            self.previous_quotes.append(fallback)
        self.previous_quotes = self.previous_quotes[-5:]
        if self.bird:
            self.bird.set_text(self.bird_quote)
        if not USE_TEXT_QUOTES:
            threading.Thread(target=self._generate_quote, args=(event,)).start()

    def _generate_quote(self, event):
        should_save = True
        print(f"Generating bird quote with Grok API for event: {event}...")
        if not GROK_API_KEY:
            print("GROK_API_KEY environment variable not set.")
        else:
            stats = self.get_player_stats()
            previous_context = "\n".join(self.previous_quotes[-3:]) if self.previous_quotes else "None"
            system_prompt = """
            You are a witty bird that taunts a worm (the snake player) in an infinite runner Snake game.

            Generate ONLY a short, funny quote that the bird can say to taunt the worm.

            Make it humorous, clever, and related to the game, like the worm being slow, slimy, etc.

            Do not include any numbers, times, or specific lengths in the quote.

            If the event is 'dying', hint that the bird will be back soon.
            
            If the event is 'nibble', hint that the worm tastes good.
            
            If the event is 'appeared', hint that the bird is ready for action.
            
            If the event is 'damaged', hint that the bird is hurt.
            
            Output ONLY the quote text. No extra text or formatting.
            """

            # User prompt with dynamic adaptation
            prompt = f"""

            Event: {event}

            Previous quotes: {previous_context}

            Generate a taunting quote based on these stats and the event. The bird is alive and actively taunting. Make it varied from previous quotes.
            """

            # API call with improvements
            headers = {
                'Authorization': f'Bearer {GROK_API_KEY}',
                'Content-Type': 'application/json'
            }
            data = {
                'model': 'grok-4-fast-non-reasoning',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'stream': False,
                'temperature': GROK_TEMPERATURE  # Slight randomness for variety, but low for consistency
            }
            try:
                response = requests.post(GROK_API_URL, headers=headers, json=data)
                response.raise_for_status()
                print("Grok API response received with data: ", response.text)
                result = response.json()
                level_data = result['choices'][0]['message']['content']
                quote = level_data.strip()
            except Exception as e:
                print(f"Error calling Grok API: {e}. Using fallback quote.")
                quote = "You're just a slimy worm!"
                should_save = False
        if should_save:
            self.save_quote(event, quote)
        NEXT_QUOTES[event].append(quote)

        print("Generated bird quote with Grok API.")



    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == 'playing':
                        if self.game_over:
                            if event.key == pygame.K_r:
                                self.click_sound.play()
                                self.reset_game()
                            elif event.key == pygame.K_q:
                                self.state = 'menu'
                    elif self.state == 'menu':
                        if event.key == pygame.K_SPACE:
                            self.click_sound.play()
                            self.state = 'playing'
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            self.click_sound.play()
                            running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'menu':
                        mouse_pos = pygame.mouse.get_pos()
                        if self.start_button_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            self.state = 'playing'
                            self.reset_game()
                        elif self.quit_button_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            running = False
                    elif self.state == 'playing' and self.game_over:
                        mouse_pos = pygame.mouse.get_pos()
                        if self.restart_button_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            self.reset_game()
                        elif self.quit_to_menu_button_rect.collidepoint(mouse_pos):
                            self.click_sound.play()
                            self.state = 'menu'
                elif event.type == pygame.KEYUP:
                    if self.state == 'playing' and not self.game_over and event.key == pygame.K_SPACE and self.snake.length > 2 and self.bomb_cooldown == 0:
                        head = self.snake.segments[0]
                        x = head['x']
                        y = head['y']
                        angle = self.snake.facing_angle
                        vx = math.cos(angle) * BOMB_SPEED
                        vy = math.sin(angle) * BOMB_SPEED
                        self.bombs.append(Bomb(x, y, vx, vy))
                        # Cost 2 segments
                        self.snake.length -= 2
                        self.snake.segments = deque(list(self.snake.segments)[:self.snake.length])
                        self.bombs_shot += 1
            

            
            if self.state == 'menu':
                self.draw_menu()
            else:
                self.update()
                self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
