import numpy as np
import yaml

with open("ref_files/config.yaml", "r") as file:
    config = yaml.safe_load(file)

    MAX_STORAGE = config["ds_amount_per"]
    ROWS = config["ds_rows"]
    COLS = config["ds_cols"]

class DirtyShelf:
    __rows: int
    __cols: int
    __storage: list[list]

    def __init__(self, rows: int, cols: int):
        self.__rows = rows
        self.__cols = cols
        self.__storage = [[0 for _ in range(cols)] for _ in range(rows)]

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
        
class CleanDispenser:
    __amount: int

    def remove_one(self):
        if self.is_empty():
            print("Clean storage empty")
            return

        self.__amount -= 1

    def get_amount(self) -> int:
        return 
    
    def is_empty(self) -> bool:
        return self.__amount == 0

def main():

    ds = DirtyShelf(ROWS, COLS)
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
