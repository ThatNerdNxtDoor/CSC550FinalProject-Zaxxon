# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:58:30 2023

@author: Isaiah Thompson
"""

import pygame
from pygame import mixer
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GLU import *
import time
import random
from math import *

pygame.init()
glutInit()
mixer.init()
gameDisplay = pygame.display.set_mode((800,600), DOUBLEBUF|OPENGL)
pygame.display.set_caption("Zaxxon")
clock = pygame.time.Clock()

#Definiing Colors and Textures
#-----------------------------------------------------------------------------#
ship = pygame.image.load('player_ship.png')
ship_data = pygame.image.tostring(ship, 'RGBA')
shipTexID = glGenTextures(1)

wall = pygame.image.load('wall.png')
wall_data = pygame.image.tostring(wall, 'RGBA')
wallTexID = glGenTextures(1)

space = pygame.image.load('space.png')
space_data = pygame.image.tostring(space, 'RGBA')
spaceTexID = glGenTextures(1)

#Defining Colors
black = (0, 0, 0)
orange = (255, 165, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
dark_green = (21, 71, 52)
#-----------------------------------------------------------------------------#

#Defining Sound Effects
#-----------------------------------------------------------------------------#
#Sound effect made by myself using https://www.beepbox.co
flying = pygame.mixer.Sound("ship_ambience.wav")
flying.set_volume(0.15)

#Sounds effects from https://opengameart.org/content/space-sound-effects
shoot = pygame.mixer.Sound("laser3.ogg")
shoot.set_volume(0.05)

gun_shoot = pygame.mixer.Sound("explosion4.ogg")
gun_shoot.set_volume(0.1)

explosion = pygame.mixer.Sound("explosion5.ogg")
explosion.set_volume(0.15)

wall_explosion = pygame.mixer.Sound("explosion2.ogg")
wall_explosion.set_volume(0.05)

boost_sfx = pygame.mixer.Sound("warpout.ogg")
boost_sfx.set_volume(0.05)
#-----------------------------------------------------------------------------#

#Defining Vertices
#-----------------------------------Ground------------------------------------#
ground_vertices = (( 10, -1,  10), #v0
                   (-10, -1,  10), #v1
                   (-10, -1, -10), #v2
                   ( 10, -1, -10)) #v3

ground_edges = ((0, 1),
                (1, 2),
                (2, 3),
                (3, 0))

ground_face = ((0, 1, 2, 3))

#-----------------------------------------------------------------------------#

#----------------------------------Sky Box------------------------------------#
space_verticies = (
    (1, -1, -1), # 0
    (1, 1, -1), # 1
    (-1, 1, -1), # 2
    (-1, -1, -1), # 3
    (1, -1, 1), # 4
    (1, 1, 1), # 5
    (-1, -1, 1), # 6
    (-1, 1, 1) # 7
    )

space_edges = (
    (0,1), # e0
    (0,3), # e1
    (0,4), # e2
    (2,1), # e3
    (2,3), # e4
    (2,7), # e5
    (6,3), # e6
    (6,4), # e7
    (6,7), # e8
    (5,1), # e9
    (5,4), # e10
    (5,7) # e11
    )

space_surfaces = (
    (0,1,2,3), # f0
    (3,2,7,6), # f1
    (6,7,5,4), # f2
    (4,5,1,0), # f3
    (1,5,7,2), # f4
    (4,0,3,6) # f5
    )

space_texture_coords = ((0,1),(0,0),(1,0),(1,1))

space_texture_normals = [
( 0,  0, -1),  # surface 0
(-1,  0,  0),  # surface 1
( 0,  0,  1),  # surface 2
( 1,  0,  0),  # surface 3
( 0,  1,  0),  # surface 4
( 0, -1,  0)   # surface 5
]

#-----------------------------------------------------------------------------#

#-----------------------------------Player------------------------------------#
player_verticies = (
    (1, -1, -1), # 0
    (1, 1, -1), # 1
    (-1, 1, -1), # 2
    (-1, -1, -1), # 3
    (1, -1, 1), # 4
    (1, 1, 1), # 5
    (-1, -1, 1), # 6
    (-1, 1, 1) # 7
    )

player_edges = (
    (0,1), # e0
    (0,3), # e1
    (0,4), # e2
    (2,1), # e3
    (2,3), # e4
    (2,7), # e5
    (6,3), # e6
    (6,4), # e7
    (6,7), # e8
    (5,1), # e9
    (5,4), # e10
    (5,7) # e11
    )

player_surfaces = (
    (0,1,2,3), # f0
    (3,2,7,6), # f1
    (6,7,5,4), # f2
    (4,5,1,0), # f3
    (1,5,7,2), # f4
    (4,0,3,6) # f5
    )

#-----------------------------------------------------------------------------#

#----------------------------Object Parent Class------------------------------#
class Obj():
    def __init__(self, model, xpos, ypos, zpos, change_x, change_y, change_z, scale_x, scale_y, scale_z):
        self.model_ID = model #ID will also be used to identify the objects when colliding
        self.x = xpos
        self.y = ypos
        self.z = zpos
        
        self.x_change = change_x
        self.y_change = change_y
        self.z_change = change_z
        
        self.x_scale = scale_x
        self.y_scale = scale_y
        self.z_scale = scale_z
        
        self.world_matrix = 0 
        
        self.gun_fired = False
        self.gun_range = random.randint(20, 30)
        
#-----------------------------------------------------------------------------#

#------------------------------Ship Child Class-------------------------------#
class Ship(Obj): #is a child of the Obj class
    def __init__(self, x, y, z, scx, scy, scz):
        Obj.__init__(self, 1, x, y, z, 0, 0, 0, scx, scy, scz)
        self.cooldown = 1

#-----------------------------------------------------------------------------#

#------------------------Object Rendering Function----------------------------#
def draw_object(obj):
    if(obj.z > 40 or obj.z < -10): #Don't render if outside of view
        pass
    else:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glFrontFace(GL_CCW)
        
        glPushMatrix()
        glTranslate(obj.x, obj.y, obj.z)
        glScale(obj.x_scale, obj.y_scale, obj.z_scale)
        match (obj.model_ID):
            case 1: #player
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, shipTexID)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ship.get_width(), ship.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, ship_data)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                
                glBegin(GL_QUADS)
                glColor3fv((1, 1, 1))
                # for surface in player_surfaces:
                #     for vertex in surface:
                #         glColor3fv((.5, 0, 0))
                #         glVertex3fv(player_verticies[vertex])
                for i_surface, surface in enumerate(player_surfaces):
                    glNormal3fv(space_texture_normals[i_surface])
                    for i_vertex, vertex in enumerate(surface):
                        glTexCoord2fv(space_texture_coords[i_vertex])
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                
                glDisable(GL_TEXTURE_2D)
                
                glColor3fv((1,1,1))
                glBegin(GL_LINES)
                for edge in player_edges:
                    for vertex in edge:
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                pass
            case 2: #player laser
                glColor3fv((0, 1, 0))
                sphere = gluNewQuadric()
                gluSphere(sphere, 1.0, 32, 16)
                pass
            case 3: #wall
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, wallTexID)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, wall.get_width(), wall.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, wall_data)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                
                glBegin(GL_QUADS)
                glColor3fv((1, 1, 1))
                # for surface in player_surfaces:
                #     for vertex in surface:
                #         glColor3fv((50, 50, 50))
                #         glVertex3fv(player_verticies[vertex])
                for i_surface, surface in enumerate(player_surfaces):
                    glNormal3fv(space_texture_normals[i_surface])
                    for i_vertex, vertex in enumerate(surface):
                        glTexCoord2fv(space_texture_coords[i_vertex])
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                
                glDisable(GL_TEXTURE_2D)
                
                glColor3fv((0,0,0))
                glBegin(GL_LINES)
                for edge in player_edges:
                    for vertex in edge:
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                pass
            case 4: #gun
                glBegin(GL_QUADS)
                for surface in player_surfaces:
                    for vertex in surface:
                        glColor3fv(black)
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                
                glColor3fv(white)
                glBegin(GL_LINES)
                for edge in player_edges:
                    for vertex in edge:
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                pass
            case 5: #enemy laser
                glColor3fv((1, 0, 0))
                sphere = gluNewQuadric()
                gluSphere(sphere, 1.0, 32, 16)
                pass
            case 6: #tanker
                glBegin(GL_QUADS)
                for surface in player_surfaces:
                    for vertex in surface:
                        glColor3fv(red)
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                
                glColor3fv(orange)
                glBegin(GL_LINES)
                for edge in player_edges:
                    for vertex in edge:
                        glVertex3fv(player_verticies[vertex])
                glEnd()
                pass
            case _: #none
                pass
        glPopMatrix()
    
#-----------------------------------------------------------------------------#

#------------------------Ground Rendering Function----------------------------#
def draw_ground(ground_x, ground_y, ground_z):
    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)
    glFrontFace(GL_CCW)
    
    glPushMatrix()
    glTranslatef(ground_x, ground_y, ground_z)
    glScalef(1, 1, 10)
    
    glBegin(GL_QUADS)
    glColor3fv((0, 0, 1))
    for face in ground_face:
        for i,vertex in enumerate(ground_face):
            #glTexCoord2fv(ground_texture_coords[i])
            glVertex3fv(ground_vertices[vertex])
    glEnd()
    
    glColor3fv((1,1,1))
    glBegin(GL_LINES)
    for edge in ground_edges:
        for vertex in edge:
            glVertex3fv(ground_vertices[vertex])
    glEnd()
    
    glPopMatrix()
    
#-----------------------------------------------------------------------------#

#-----------------------Sky Box Rendering Function----------------------------#
def draw_sky():
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    glPushMatrix()

    glScalef(40, 40, 40)
    glTranslatef(0, 0, 0)
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, spaceTexID)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, space.get_width(), space.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, space_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    
    glBegin(GL_QUADS)
    glColor3fv((1, 1, 1))
    for i_surface, surface in enumerate(space_surfaces):
        glNormal3fv(space_texture_normals[i_surface])
        for i_vertex, vertex in enumerate(surface):
            glTexCoord2fv(space_texture_coords[i_vertex])
            glVertex3fv(space_verticies[vertex])
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    
    glColor3fv((1,0,0))
    glBegin(GL_LINES)
    for edge in space_edges:
        for vertex in edge:
            glVertex3fv(space_verticies[vertex])
    glEnd()
    
    glPopMatrix()
    
#-----------------------------------------------------------------------------#

#------------------------Text Rendering Function------------------------------#
def draw_message(message, font, x, y):
    glPushMatrix()
    glColor3fv(orange)
    glWindowPos2f(x, y)
    glutBitmapString(GLUT_BITMAP_TIMES_ROMAN_24, message.encode("ascii"))
    glPopMatrix()
    pass
    
#-----------------------------------------------------------------------------#

#------------------------Main Rendering Function------------------------------#
def update_display(pre_game, gameEnd, win, timer, time_bonus, score, objects, ground_x, ground_y, ground_z):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    
    glPushMatrix()
    gluLookAt(-20.0, 15.0, -10.0, 5.0, 0.0, 10.0, 0.0, 1.0, 0.0)
    glPopMatrix()
    
    if (pre_game):
        draw_message("--Zaxxon--", GLUT_BITMAP_TIMES_ROMAN_24, 329, 400)
        draw_message("Controls: \n LEFT/RIGHT/UP/DOWN - Move left/right/up/down \n SPACE - Fire laser \n B - Boost", GLUT_BITMAP_TIMES_ROMAN_24, 175, 325)
        draw_message("Starting in: " + str(timer//1000), GLUT_BITMAP_TIMES_ROMAN_24, 310, 150)
        print("pregame")
    elif (not gameEnd):
        draw_sky()        
        draw_ground(ground_x, ground_y, ground_z)
        
        glPushMatrix()
        #draw all of the objects
        for obj in objects:
            draw_object(obj)
            #print("obj_drawn")
            
        draw_message("Score: " + str(score), GLUT_BITMAP_TIMES_ROMAN_24, 50, 550)
        draw_message("Time: " + str(timer//1000), GLUT_BITMAP_TIMES_ROMAN_24, 600, 560)
        glPopMatrix()
    else:
        if (win):
            draw_message("--You Won!--", GLUT_BITMAP_TIMES_ROMAN_24, 329, 400)
            draw_message("Time Bonus: " + str(time_bonus//1000) + " x 50 = " + str((time_bonus//1000) * 50), GLUT_BITMAP_TIMES_ROMAN_24, 310, 325)
            draw_message("Score: " + str(score + ((time_bonus//1000) * 50)), GLUT_BITMAP_TIMES_ROMAN_24, 300, 250)
        else:
            draw_message("--You Died!--", GLUT_BITMAP_TIMES_ROMAN_24, 329, 400)
            draw_message("Score: " + str(score), GLUT_BITMAP_TIMES_ROMAN_24, 310, 300)
        print("You Lost")
        
    pygame.display.flip()
    pygame.time.wait(60)
    
#-----------------------------------------------------------------------------#

#--------------------------Collision Check Function---------------------------#
def check_collision(obj1, obj2) -> bool:
    #Collisions using each vertex
    if ((obj2.x - obj2.x_scale <= obj1.x + obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y - obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z - obj1.z_scale <= obj2.z + obj2.z_scale)): #v0
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x + obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y + obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z - obj1.z_scale <= obj2.z + obj2.z_scale)): #v1
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x - obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y + obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z - obj1.z_scale <= obj2.z + obj2.z_scale)): #v2
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x - obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y - obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z - obj1.z_scale <= obj2.z + obj2.z_scale)): #v3
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x + obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y - obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z + obj1.z_scale <= obj2.z + obj2.z_scale)): #v4
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x + obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y + obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z + obj1.z_scale <= obj2.z + obj2.z_scale)): #v5
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x - obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y - obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z + obj1.z_scale <= obj2.z + obj2.z_scale)): #v6
        return True
    elif ((obj2.x - obj2.x_scale <= obj1.x - obj1.x_scale <= obj2.x + obj2.x_scale) 
    and (obj2.y - obj2.y_scale <= obj1.y + obj1.y_scale <= obj2.y + obj2.y_scale) 
    and (obj2.z - obj2.z_scale <= obj1.z + obj1.z_scale <= obj2.z + obj2.z_scale)): #v7
        return True
    else:
        return False
#-----------------------------------------------------------------------------#

#-----------------------------Main Loop Function------------------------------#
def game_loop():    
    pre_game = True
    gameEnd = False
    flying_playing = False
    win = False
    gameExit = False
    timer = 11000.0 #10 seconds
    time_bonus = 0
    
    display = (800,600)
    #pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
    gluPerspective(45, (display[0]/display[1]), 0.01, 100.0)
    
    gluLookAt(-20.0, 15.0, -10.0, 5.0, 0.0, 10.0, 0.0, 1.0, 0.0)

    print("Inside game_loop")
    
    player = Ship(0, 0, -5, .75, .75, .75)
    boost = 1
    score = 0
    
    ground_x = 0
    ground_y = 0
    ground_z = 135
    
    objects = []
    
    #Add Player
    objects.append(player)
    
    #Add Objects
    #-------------------------------Walls-------------------------------------#
    #First major wall
    objects.insert(0, Obj(3, -6.6,  .5, 40, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0,  .5, 40, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6,  .5, 40, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3, -6.6, 4.5, 40, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0, 4.5, 40, 0, 0, -0.3, 3.3, 2, 1))
    
    #Intermediary walls
    objects.insert(0, Obj(3,  6.6,  .5, 60, 0, 0, -0.3, 3.3, 2, 1))
    
    objects.insert(0, Obj(3,    0,  .5, 120, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0, 4.5, 120, 0, 0, -0.3, 3.3, 2, 1))
    
    objects.insert(0, Obj(3,    0,  .5, 150, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3, -6.6,  .5, 150, 0, 0, -0.3, 3.3, 2, 1))
    
    objects.insert(0, Obj(3,    0,  .5, 170, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3, -6.6,  .5, 170, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3, -6.6, 4.5, 170, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6,  .5, 170, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6, 4.5, 170, 0, 0, -0.3, 3.3, 2, 1))
    
    objects.insert(0, Obj(3,    0,  .5, 200, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0, 4.5, 200, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6, 4.5, 200, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3, -6.6, 4.5, 200, 0, 0, -0.3, 3.3, 2, 1))
    
    #Second major wall
    objects.insert(0, Obj(3, -6.6,  .5, 230, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0,  .5, 230, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6,  .5, 230, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,    0, 4.5, 230, 0, 0, -0.3, 3.3, 2, 1))
    objects.insert(0, Obj(3,  6.6, 4.5, 230, 0, 0, -0.3, 3.3, 2, 1))
    
    #------------------------------Tankers------------------------------------#
    objects.insert(0, Obj(6, 0,   0, 80, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6,  6,  0, 120, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6, -6,  0, 140, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6,  6,  0, 150, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6,  0,  4, 170, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6, -6,  0, 200, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6, 6,  0, 215, 0, 0, -0.3, 2, 1, 2))
    objects.insert(0, Obj(6, 0,  0, 225, 0, 0, -0.3, 2, 1, 2))
    
    #-------------------------------Guns--------------------------------------#
    objects.insert(0, Obj(4,    5, 0,  90, 0, 0, -0.3, .75, .75, 1.5))
    
    objects.insert(0, Obj(4,    0, 0, 100, 0, 0, -0.3, .75, .75, 1.5))
    
    objects.insert(0, Obj(4,   -5, 0, 120, 0, 0, -0.3, .75, .75, 1.5))
    objects.insert(0, Obj(4,   -7, 0, 120, 0, 0, -0.3, .75, .75, 1.5))
    
    objects.insert(0, Obj(4, -3.3, 2, 149, 0, 0, -0.3, .75, .75, 1.5))
    
    objects.insert(0, Obj(4, -3.3, 2, 169, 0, 0, -0.3, .75, .75, 1.5))
    objects.insert(0, Obj(4,  3.3, 2, 169, 0, 0, -0.3, .75, .75, 1.5))
    
    objects.insert(0, Obj(4, -3.3, 2, 199, 0, 0, -0.3, .75, .75, 1.5))
    objects.insert(0, Obj(4,  3.3, 2, 199, 0, 0, -0.3, .75, .75, 1.5))
    
    #------------------------------Game Loop----------------------------------#
    while not gameExit:     
        #---------------------------Handle Movement---------------------------#
        if(pre_game):
            timer -= clock.tick(60)
            print(str(timer))
            if (timer <= 0):
                timer = 60000.0 #60 seconds
                pre_game = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
        else:
            if (not gameEnd):
                if (not flying_playing):
                    flying.play(4)
                    flying_playing = True
                    
                timer -= clock.tick(60)
                print(str(timer))
                if (timer <= 0):
                    print("Time_Up")
                    #gameEnd = True
                
                #-----------------------Take Player Input---------------------#
                player.cooldown -= 0.1
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameExit = True
                    if event.type == pygame.KEYDOWN:
                       if event.key == pygame.K_UP:
                           player.y_change = 0.2
                       elif event.key == pygame.K_DOWN:
                           player.y_change = -0.2
                       elif event.key == pygame.K_LEFT:
                           player.x_change = 0.2
                       elif event.key == pygame.K_RIGHT:
                           player.x_change = -0.2
                       elif event.key == pygame.K_SPACE:
                           if (player.cooldown <= 0):
                               objects.insert(0, Obj(2, player.x, player.y, player.z + .5, 0, 0, .45, .5, .5, .5))
                               shoot.play()
                               player.cooldown = 1
                               print("fire")
                       elif event.key == pygame.K_b:
                           boost = 2
                           boost_sfx.play()
                    elif event.type == pygame.KEYUP:
                       if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                           player.y_change = 0
                       elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                           player.x_change = 0
                       elif event.key == pygame.K_b:
                           boost = 1
                
                #--------------------Handle Player Movement-------------------#
                if (player.x + player.x_change > 10):
                    player.x = 10
                elif (player.x + player.x_change < -10):
                    player.x = -10
                else:
                    player.x += player.x_change 
                
                if (player.y + player.y_change > 6):
                    player.y = 6
                elif (player.y + player.y_change < 0):
                    player.y = 0
                else:
                    player.y += player.y_change
                
                #-------------------------------------------------------------#
                
                #--------------------Handle Object Movement-------------------#
                for obj in objects:
                    if obj == player:
                        pass
                    else:
                        if not (obj.model_ID == 2):
                            obj.x += obj.x_change * boost
                            obj.y += obj.y_change * boost
                            obj.z += obj.z_change * boost
                        else:
                            obj.x += obj.x_change
                            obj.y += obj.y_change
                            obj.z += obj.z_change
                #-------------------------------------------------------------#
                
                #----------------Handle Environment Movement------------------#
                ground_z += -0.3 * boost
                #-------------------------------------------------------------#
            else:
                timer -= clock.tick(60)
                print(str(timer))
                if (timer <= 0):
                    if (gameEnd):
                        gameExit = True
                    else:
                        gameEnd = True
                        win = False
                pass
        #---------------------------------------------------------------------#
        
        #--------------------------Update Rendering---------------------------#
        update_display(pre_game, gameEnd, win, timer, time_bonus, score, objects, ground_x, ground_y, ground_z)
        #---------------------------------------------------------------------#
        
        #--------------------------Check Collisions---------------------------#
        for obj1 in objects:
            for obj2 in objects:
                if obj1 == obj2 or obj1.model_ID == obj2.model_ID: #check to see if two objects are the same object or are the same 'type' of object
                    pass
                else:
                    if (obj2.model_ID == 2 or obj2.model_ID == 5) and (abs(obj2.z) > 30): #remove bullets when they do not need to be rendered to free up memory
                        objects.remove(obj2)
                        pass
                    
                    #If Player is within range of a gun, the gun will fire
                    if (obj1.model_ID == 1 and obj2.model_ID == 4) and (pygame.math.Vector3(obj1.x, obj1.y, obj1.z).distance_to(pygame.math.Vector3(obj2.x, obj2.y, obj2.z)) <= obj2.gun_range):
                        if (not obj2.gun_fired):
                            gun_shoot.play()
                            objects.append(Obj(5, obj2.x, obj2.y, obj2.z - .5, 0, 0, -.6, .5, .5, .5))
                            obj2.gun_fired = True
                    elif (obj1.model_ID == 4 and obj2.model_ID == 1) and (pygame.math.Vector3(obj1.x, obj1.y, obj1.z).distance_to(pygame.math.Vector3(obj2.x, obj2.y, obj2.z)) <= obj1.gun_range):
                        if (not obj1.gun_fired):
                            gun_shoot.play()
                            objects.append(Obj(5, obj1.x, obj1.y, obj1.z - .5, 0, 0, -.6, .5, .5, .5))
                            obj1.gun_fired = True
                         
                    if (check_collision(obj1, obj2)):
                        if (obj1.model_ID == 1 or obj2.model_ID == 1) and (obj1.model_ID != 2 and obj2.model_ID != 2): #If object collides w/ player and its not a player laser
                            print("collision")
                            if (not gameEnd):
                                explosion.play()
                                timer = 6600.0 #6 seconds
                            gameEnd = True
                            pass
                        elif (obj1.model_ID == 2 or obj2.model_ID == 2) and (obj1.model_ID != 2 or obj2.model_ID != 2) and (obj1.model_ID != 1 and obj2.model_ID != 1): #If laser collides w/ object and its not player or another player laser
                            print("collision " + str(obj2.model_ID))
                            if (obj1.model_ID == 2):
                                if (obj2.model_ID == 4 or obj2.model_ID == 6):
                                    score += 100 * obj2.model_ID
                                    objects.remove(obj2)
                                    explosion.play()
                                else:
                                    wall_explosion.play()
                                objects.remove(obj1)
                                break
                            elif (obj2.model_ID == 2):
                                if (obj1.model_ID == 4 or obj1.model_ID == 6):
                                    score += 100 * obj1.model_ID
                                    objects.remove(obj1)
                                    explosion.play()
                                else:
                                    wall_explosion.play()
                                objects.remove(obj2)
                                pass
                            
        #---------------------------------------------------------------------#
        #Check for if the player has reached the end
        if (ground_z <= -115 and (not gameEnd)):
            print("End game")
            gameEnd = True
            win = True
            if (time_bonus == 0):
                time_bonus = timer
                timer = 11000.0 #10 Seconds
        else:
            print(ground_z)
        #Move to next frame
    #-------------------------------------------------------------------------#
        
#-----------------------------------------------------------------------------#
game_loop()
pygame.quit()