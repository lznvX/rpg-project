"""
Implémente des vecteurs spatiaux ainsi que leurs opérations

Projet OC Informatique Semestre 2
Alexandre, Kevin, Romain
"""

from typing import NamedTuple


class Vector2(NamedTuple):
    """Classe non-muable de vecteurs à deux dimensions opérables."""
    x: float
    y: float
    
    @property
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def __add__(self, other: "Vector2") -> "Vector2":
        return Vector2(
            self.x + other.x,
            self.y + other.y,
        )
    
    def __sub__(self, other: "Vector2") -> "Vector2":
        return Vector2(
            self.x - other.x,
            self.y - other.y,
        )
    
    def __mul__(self, other: float) -> "Vector2":
        return Vector2(
            self.x * other,
            self.y * other,
        )


class Vector3(NamedTuple):
    """Classe non-muable de vecteurs à trois dimensions opérables."""
    x: float
    y: float
    z: float
    
    @property
    def length(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def dot(self, other: "Vector3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: "Vector3") -> "Vector3":
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )
    
    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )
    
    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )
    
    def __mul__(self, other: float) -> "Vector3":
        return Vector3(
            self.x * other,
            self.y * other,
            self.z * other,
        )


def _tests_vector2() -> None:
    assert Vector2(3, 4).length == 5
    assert Vector2(1, 1) + Vector2(0, 2) == Vector2(1, 3)
    assert Vector2(1, 1) - Vector2(0, 2) == Vector2(1, -1)
    assert Vector2(2, 4) * 2 == Vector2(4, 8)
    print("Tests Vector2 OK")


def _tests_vector3() -> None:
    assert Vector3(0, 3, 4).length == 5
    assert Vector3(4, 2, 5).dot(Vector3(-3, 0, 7)) == 23
    assert Vector3(1, 2, 3).cross(Vector3(1, 5, 7)) == Vector3(-1, -4, 3)
    assert Vector3(1, 1, 1) + Vector3(0, 2, 3) == Vector3(1, 3, 4)
    assert Vector3(1, 1, 1) - Vector3(0, 2, 3) == Vector3(1, -1, -2)
    assert Vector3(2, 4, 16) * 2 == Vector3(4, 8, 32)
    print("Tests Vector3 OK")


if __name__ == "__main__":
    _tests_vector2()
    _tests_vector3()
