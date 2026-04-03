import numpy as np
import yaml
from config import config

MAX_STORAGE: int = config["ds_amount_per"]
ROWS: int = config["ds_rows"]
COLS: int = config["ds_cols"]
X: float = config["ds_coords"]["x"]
Y: float = config["ds_coords"]["y"]
DX: float = config["ds_dx"]
DY: float = config["ds_dy"]

AMOUNT = config["cs_amount"]
CS_X = config["cs_coords"]["x"]
CS_Y = config["cs_coords"]["y"]

class DirtyShelf:
    __rows: int
    __cols: int
    __storage: list[list]

    # origin point, top left
    __x: float
    __y: float

    # spacing between columns and rows
    __dx: float
    __dy: float

    def __init__(self, rows: int, cols: int, x: float, y: float, dx: float, dy: float):
        self.__rows = rows
        self.__cols = cols
        self.__storage = [[0 for _ in range(cols)] for _ in range(rows)]
        self.__x = x
        self.__y = y
        self.__dx = dx
        self.__dy = dy

    def add_one(self, row, col) -> bool:
        if row > self.__rows-1 or col > self.__cols-1 or row < 0 or col < 0:
            print("Invalid position")
        
        if self.__storage[row][col] >= MAX_STORAGE:
            print("That position is full")
            return False
        
        self.__storage[row][col] += 1
        return True

    def detect_first_free(self) -> list:
        for i in range(self.__rows):
            for j in range(self.__cols):
                if (self.__storage[i][j] < MAX_STORAGE):
                    return [i, j]
            
        print("Free position not found")

        return [-1, -1]
    
    def remove_all(self):
        self.__storage = [[0 for _ in range(self.__cols)] for _ in range(self.__rows)]

    def get_storage(self) -> list:
        return self.__storage
    
    def get_origin(self) -> list:
        return [self.__x, self.__y]
    
    def coords_first_free(self) -> list:
        [ny, nx] = self.detect_first_free()
        x = self.__x + nx * self.__dx
        y = self.__y + ny * self.__dy

        return [x, y]
    
    def is_full(self):
        return self.detect_first_free() == [-1, -1]
        
class CleanDispenser:
    __amount: int
    __x: float
    __y: float

    def __init__(self, amount: int, x: float, y: float):
        self.__amount = amount
        self.__x = x
        self.__y = y

    def remove_one(self):
        if self.is_empty():
            print("Clean storage empty")
            return

        self.__amount -= 1

    def get_amount(self) -> int:
        return self.__amount
    
    def is_empty(self) -> bool:
        return self.__amount == 0
    
    def get_origin(self) -> list:
        return [self.__x, self.__y]
    
ds = DirtyShelf(ROWS, COLS, X, Y, DX, DY)
cs = CleanDispenser(AMOUNT, CS_X, CS_Y)

def main():
    ds.add_one(0, 0)
    ds.add_one(0, 0)
    ds.add_one(0, 0)
    ds.add_one(0, 0)
    ds.add_one(1, 1)
    ds.add_one(1, 1)
    ds.add_one(1, 1)
    ds.add_one(1, 1)

    print(ds.get_storage())
    print(ds.detect_first_free())
    print(ds.get_storage())

    ds.remove_all()

    print(ds.get_storage())

if __name__ == "__main__":
    main()
