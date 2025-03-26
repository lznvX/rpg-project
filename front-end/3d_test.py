"""
Work In Progress
"""

from bresenham import bresenham, bresenham_depth
import curses
import ctypes
import random
import time
from typing import NamedTuple
from vectormath import Vector2, Vector3

DISPLAY_CHAR = "█" # █ ─
RENDER_DISTANCE = 250
ASPECT_RATIO = 16 / 9
CUBE_EDGE_INDICES = (
        (0, 1), (1, 3), (3, 2), (2, 0),  # Front face edges
        (4, 5), (5, 7), (7, 6), (6, 4),  # Back face edges
        (0, 4), (1, 5), (2, 6), (3, 7),  # Connecting edges
)

class Edge(NamedTuple):
    a: Vector3
    b: Vector3


class Camera(NamedTuple):
    position: Vector3
    screen_size: Vector2 # Taille de l'écran de caractères ASCII
    x_correction: float # Facteur de correction car les charactères ne sont pas carrés
    
    def translate(self, translation: Vector3) -> "Camera":
        return Camera(self.position + translation, self.screen_size, self.x_correction)


def distance_to_curses_color(distance: float) -> int:
    """
    Convertit la distance d'un point à une couleur entre noir et blanc en
    format curses.
    """
    brightness = 1 - min((distance / RENDER_DISTANCE) ** 0.5, 1)
    return curses.color_pair(233 + round(brightness * 22))


def world_to_screen(camera: Camera, world_pos: Vector3) -> Vector2:
    """Retourne la projection d'une position 3D sur l'écran."""
    relative_pos = world_pos - camera.position
    
    if relative_pos.z >= 0: return None
    
    proj_x = relative_pos.x / -relative_pos.z
    proj_y = relative_pos.y / -relative_pos.z
    
    screen_x = round((0.5 + proj_x * camera.x_correction) * camera.screen_size.x)
    screen_y = round((0.5 - proj_y) * camera.screen_size.y)
    
    return Vector2(screen_x, screen_y)


def world_to_screen_shaded(camera: Camera, world_pos: Vector3) -> Vector3:
    """Retourne la projection d'une position 3D sur l'écran, avec sa distance"""
    relative_pos = world_pos - camera.position
    
    if relative_pos.z >= 0: return None
    
    proj_x = relative_pos.x / -relative_pos.z
    proj_y = relative_pos.y / -relative_pos.z
    
    screen_x = round((0.5 + proj_x * camera.x_correction) * camera.screen_size.x)
    screen_y = round((0.5 - proj_y) * camera.screen_size.y)
    
    return Vector3(screen_x, screen_y, -relative_pos.z)


def edges_to_points(camera: Camera, screen_size: Vector2, edges: tuple) -> dict:
    points = []
    
    for edge in edges:
        for screen_pos in bresenham(world_to_screen(camera, edge.a), world_to_screen(camera, edge.b)):
            if (screen_pos is not None
            and 0 <= screen_pos.x < screen_size.x
            and 0 <= screen_pos.y < screen_size.y
            and (screen_pos.x < screen_size.x - 1 or screen_pos.y < screen_size.y - 1)):
                point = (int(screen_pos.y), int(screen_pos.x))
                if not point in points:
                    points.append(point)
    
    return points


def edges_to_points_shaded(camera: Camera, screen_size: Vector2, edges: tuple) -> dict:
    point_depths = {}
    
    for edge in edges:
        for screen_pos in bresenham_depth(world_to_screen_shaded(camera, edge.a), world_to_screen_shaded(camera, edge.b)):
            if (screen_pos is not None
            and 0 <= screen_pos.x < screen_size.x
            and 0 <= screen_pos.y < screen_size.y
            and (screen_pos.x < screen_size.x - 1 or screen_pos.y < screen_size.y - 1)):
                point = (int(screen_pos.y), int(screen_pos.x))
                if (not point in point_depths) or point_depths[point] > screen_pos.z:
                    point_depths[point] = screen_pos.z
    
    return point_depths


def display_points(stdscr, points: tuple, char: str) -> None:
    """Batch rendering without shading for improved performance."""
    screen_buffer = {}

    # Collect characters for each row
    for (y, x) in points:
        if y not in screen_buffer:
            screen_buffer[y] = []
        screen_buffer[y].append(x)

    # Render rows in batch without colors
    for y, x_positions in screen_buffer.items():
        x_positions.sort()  # Ensure correct order
        prev_x = None
        row_str = ""

        stdscr.move(y, x_positions[0])  # Move cursor once per row

        for x in x_positions:
            if prev_x is not None and x > prev_x + 1:
                row_str += " " * (x - prev_x - 1)  # Fill gaps with spaces
            row_str += char
            prev_x = x

        stdscr.addstr(row_str)  # Render entire row in one call


def display_points_shaded(stdscr, point_depths: dict, char: str) -> None:
    for point, depth in point_depths.items():
        stdscr.addch(point[0], point[1], char, distance_to_curses_color(depth))


def cube(center: Vector3, side: float) -> tuple:
    half = side / 2
    
    vertices = tuple(center + Vector3(
        (-1) ** int(i / 4) * half,
        (-1) ** int(i / 2) * half,
        (-1) ** i * half,
    ) for i in range(8))

    edges = tuple(Edge(
        vertices[edge_indices[0]],
        vertices[edge_indices[1]],
    ) for edge_indices in CUBE_EDGE_INDICES)

    return edges


def fullscreen():
    """Simule la pression de la touche f11."""
    user32 = ctypes.windll.user32
    user32.keybd_event(0x7A, 0, 0, 0)
    user32.keybd_event(0x7A, 0, 0x0002, 0)


def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLOR_PAIRS - 1):
        curses.init_pair(i + 1, i, -1)
    
    curses.curs_set(0) # Cache le curseur
    stdscr.nodelay(1) # Pas de blocage d'entrées
    stdscr.timeout(0) # Taux de rafraichissement
    
    screen_size = stdscr.getmaxyx()
    screen_size = Vector2(screen_size[1], screen_size[0])
    
    x_correction = ASPECT_RATIO / (screen_size.x / screen_size.y)
    camera = Camera(Vector3(0, 0, 10), screen_size, x_correction)
    
    edges = ()
    for i in range(16):
        edges += cube(Vector3(
            random.randint(-100, 100),
            random.randint(-100, 100),
            random.randint(-100, 100)
        ), random.randint(5, 50))
    
    while True:
        key = stdscr.getch()
        if key == ord("a"):
            camera = camera.translate(Vector3(-1, 0, 0))
        elif key == ord("d"):
            camera = camera.translate(Vector3(1, 0, 0))
        elif key == ord("w"):
            camera = camera.translate(Vector3(0, 0, -1))
        elif key == ord("s"):
            camera = camera.translate(Vector3(0, 0, 1))
        elif key == ord(" "):
            camera = camera.translate(Vector3(0, 1, 0))
        elif key == ord("c"):
            camera = camera.translate(Vector3(0, -1, 0))
        elif key == ord("q"):
            break
        
        stdscr.clear()
        
        #point_depths = edges_to_points_shaded(camera, screen_size, edges)
        #display_points_shaded(stdscr, point_depths, DISPLAY_CHAR)
        
        points = edges_to_points(camera, screen_size, edges)
        display_points(stdscr, points, DISPLAY_CHAR)
        
        stdscr.refresh()


time.sleep(0.5)
fullscreen()
time.sleep(0.5)
curses.wrapper(main)
