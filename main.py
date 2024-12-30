#!/usr/bin/python3

from z3 import *
import argparse
import csv

def read_level(filename):
    # Open the file
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            data = []
            for row_id, row in enumerate(reader):
                if row_id == 0:
                    size = int(row[0])
                elif row_id == 1 or row_id == 2:
                    coordinates_row = [(int(item.split(" ")[0]), int(item.split(" ")[1])) for item in row]  # Convert each item in the row to an integer
                    data.append(coordinates_row)
                else:
                    coordinates_row = [(
                        (int(item.split(" ")[0]), 
                         int(item.split(" ")[1])),
                        (int(item.split(" ")[2]), 
                         int(item.split(" ")[3]))
                        ) for item in row]  # Convert each item in the row to an integer
                    data.append(coordinates_row)
            return (size, data)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        exit(-1)

def handle_args():
    parser = argparse.ArgumentParser(description="Solve the mosaik puzzle using Z3 solver.")
    parser.add_argument("file", type=str, help="Path to the input file")

    # Parse command-line arguments
    return parser.parse_args()

def get_horizontal_neighbors(matrix, row, col):
    # List of relative positions of the 8 neighbors
    neighbors = [
        ( 0, -1), ( 0, 0), ( 0, 1)   # Left, Self, Right
    ]
    
    # List to store valid neighbors
    valid_neighbors = []
    
    # Iterate over each relative position
    for dr, dc in neighbors:
        new_row, new_col = row + dr, col + dc
        
        # Check if the new position is within bounds of the matrix
        if 0 <= new_row < len(matrix) and 0 <= new_col < len(matrix[0]):
            valid_neighbors.append(matrix[new_row][new_col])
    
    return valid_neighbors

def get_vertical_neighbors(matrix, row, col):
    # List of relative positions of the 8 neighbors
    neighbors = [
            ( -1, 0),   # Top
            (  0, 0),   # Self
            ( 1, 0)     # Bottom
    ]
    
    # List to store valid neighbors
    valid_neighbors = []
    
    # Iterate over each relative position
    for dr, dc in neighbors:
        new_row, new_col = row + dr, col + dc
        
        # Check if the new position is within bounds of the matrix
        if 0 <= new_row < len(matrix) and 0 <= new_col < len(matrix[0]):
            valid_neighbors.append(matrix[new_row][new_col])
    
    return valid_neighbors

def add_line_different_constraint(solver, row_A, row_B, size):
    or_list = []
    for i in range(size):
        or_list.append(Xor(row_A[i], row_B[i]))
    solver.add(Or(or_list))

def solve_level(size, level):
    solver = Solver()
    vars = [[Bool(f"var_{i}_{o}") for i in range(size)] for o in range(size)]
    
    # add constant constraints
    # white stones
    for coord in level[0]:
        solver.add(vars[coord[0]][coord[1]])

    # black stones
    for coord in level[1]:
        solver.add(Not(vars[coord[0]][coord[1]]))

    for row_index, row in enumerate(vars):
        for column_index, var in enumerate(row):
            horizontal_neighbors = get_horizontal_neighbors(vars, row_index, column_index)
            vertical_neighbors = get_vertical_neighbors(vars, row_index, column_index)
            if(len(horizontal_neighbors) == 3):
                all_white = And(horizontal_neighbors)
                all_black = Not(Or(horizontal_neighbors))
                solver.add(Not(Or(all_white, all_black)))
            if(len(vertical_neighbors) == 3):
                all_white = And(vertical_neighbors)
                all_black = Not(Or(vertical_neighbors))
                solver.add(Not(Or(all_white, all_black)))
            
    # all rows and columns have the same amount of blac and white stones
    for row in vars:
        solver.add(Sum([If(var, 1, 0) for var in row]) == size / 2)

    for column_index in range(size):
        column = [row[column_index] for row in vars]
        solver.add(Sum([If(var, 1, 0) for var in column]) == size / 2)
    
    # all rows have to be unique
    for row_A_index, row_A in enumerate(vars):
        for row_B_index, row_B in enumerate(vars):
            if (row_A_index is row_B_index):
                continue
            add_line_different_constraint(solver, row_A, row_B, size)
    
    # all columns have to be unique
    for column_A_index, column_A in enumerate(vars):
        for column_B_index, column_B in enumerate(vars):
            if (column_A_index is column_B_index):
                continue
            add_line_different_constraint(solver, column_A, column_B, size)

    # add equals constraints
    if len(level) > 2:
        for connection in level[2]:
            start = connection[0]
            end = connection[1]
            solver.add(Not(Xor(vars[start[0]][start[1]], vars[end[0]][end[1]])))
    # add different constraints
    if len(level) > 3:
        for connection in level[3]:
            start = connection[0]
            end = connection[1]
            solver.add(Xor(vars[start[0]][start[1]], vars[end[0]][end[1]]))

    # for assertion in solver.assertions():
    #     print(assertion)

    # Check satisfiability
    if solver.check() == sat:
        model = solver.model()
        return [[model[square] for square in row] for row in vars]  # Return the values of the variables
    else:
        print("No solution exists")
        exit(-1)

def main():
    args = handle_args()

    size, level = read_level(args.file)
    print("White stones at:  ", end="")
    for white_stones in level[0]:
        print("(" + str(white_stones[0]) + "/" + str(white_stones[1]) + ")", end="")
    print()
    print("Black stones at:  ", end="")
    for black_stones in level[1]:
        print("(" + str(black_stones[0]) + "/" + str(black_stones[1]) + ")", end="")
    print()
    if len(level) > 2:
        print("(=)-Connections between: ", end="")
        for connection in level[2]:
            start = connection[0]
            end = connection[1]
            print("(" + str(start[0]) + "/" + str(start[1]) + ")=", end="")
            print("(" + str(end[0]) + "/" + str(end[1]) + ") ", end="")
        print()
    if len(level) > 3:
        print("(X)-Connections between: ", end="")
        for connection in level[3]:
            start = connection[0]
            end = connection[1]
            print("(" + str(start[0]) + "/" + str(start[1]) + ")X", end="")
            print("(" + str(end[0]) + "/" + str(end[1]) + ") ", end="")
        print()

    solution = solve_level(size, level)
    for row in solution:
        for square in row:
            print("X" if square else "O", end=" ")
        print()

if __name__ == "__main__":
    main()