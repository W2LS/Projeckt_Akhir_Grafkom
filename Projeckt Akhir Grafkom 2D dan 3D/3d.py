from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
from numpy import cross, array
from numpy.linalg import norm

angle_x, angle_y = 0, 0
mouse_down = False
last_pos = (0, 0)
zoom = 5.0

translate_x, translate_y, translate_z = 0.0, 0.0, 0.0

def init():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)

    ambient = [0.2, 0.2, 0.2, 1.0]
    diffuse = [0.7, 0.7, 0.7, 1.0]
    specular = [1.0, 1.0, 1.0, 1.0]
    position = [2.0, 2.0, 2.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
    glLightfv(GL_LIGHT0, GL_POSITION, position)

    glMaterialfv(GL_FRONT, GL_SPECULAR, [1, 1, 1, 1])
    glMateriali(GL_FRONT, GL_SHININESS, 50)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_cube():
    vertices = [
        [-1, -1, -1],
        [ 1, -1, -1],
        [ 1,  1, -1],
        [-1,  1, -1],
        [-1, -1,  1],
        [ 1, -1,  1],
        [ 1,  1,  1],
        [-1,  1,  1]
    ]

    faces = [
        [0, 1, 2, 3],
        [3, 2, 6, 7],
        [7, 6, 5, 4],
        [4, 5, 1, 0],
        [1, 5, 6, 2],
        [4, 0, 3, 7]
    ]

    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    # Gambar permukaan kubus
    glBegin(GL_QUADS)
    for face in faces:
        glColor3fv((0.8, 0.5, 0.2))
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

    # Gambar garis tepi
    glColor3fv((0, 0, 0))  # warna hitam untuk outline
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    global angle_x, angle_y, mouse_down, last_pos, zoom
    global translate_x, translate_y, translate_z

    init()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_down = True
                    last_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Scroll up
                    zoom -= 0.5
                    if zoom < 2: zoom = 2
                elif event.button == 5:  # Scroll down
                    zoom += 0.5
                    if zoom > 20: zoom = 20

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

            elif event.type == MOUSEMOTION and mouse_down:
                x, y = pygame.mouse.get_pos()
                dx = x - last_pos[0]
                dy = y - last_pos[1]
                angle_y += dx * 0.5
                angle_x += dy * 0.5
                last_pos = (x, y)

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_a:  # Left
                    translate_x -= 0.2
                elif event.key == K_d:  # Right
                    translate_x += 0.2
                elif event.key == K_w:  # Forward (z-)
                    translate_z -= 0.2
                elif event.key == K_s:  # Backward (z+)
                    translate_z += 0.2
                elif event.key == K_q:  # Up
                    translate_y += 0.2
                elif event.key == K_e:  # Down
                    translate_y -= 0.2

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(zoom, zoom, zoom, 0, 0, 0, 0, 1, 0)

        glPushMatrix()
        glTranslatef(translate_x, translate_y, translate_z)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)
        draw_cube()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
