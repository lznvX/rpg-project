"""
Version modifiée du module bresenham d'encukou

https://github.com/encukou/bresenham
"""

from vectormath import Vector2, Vector3

def bresenham(a: Vector2, b: Vector2):
    """Retourne les points entiers approximant le mieux la ligne de a à b"""
    if a == None or b == None: return None
    
    dx = b.x - a.x
    dy = b.y - a.y

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2 * dy - dx
    y = 0

    for x in range(dx + 1):
        yield Vector2(
            a.x + x * xx + y * yx,
            a.y + x * xy + y*  yy,
        )
        if D >= 0:
            y += 1
            D -= 2 * dx
        D += 2 * dy


def bresenham_depth(a: Vector3, b: Vector3):
    """
    Retourne les points entiers approximant le mieux la ligne de a à b et la
    profondeur de chaque point interpolée entre a et b
    """
    if a == None or b == None: return None
    if a == b: return (a,)
    
    dx = b.x - a.x
    dy = b.y - a.y

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2 * dy - dx
    y = 0

    for x in range(dx + 1):
        yield Vector3(
            a.x + x * xx + y * yx,
            a.y + x * xy + y * yy,
            a.z + (b.z - a.z) * x / (dx + 1),
        )
        if D >= 0:
            y += 1
            D -= 2 * dx
        D += 2 * dy