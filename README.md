# Binario Solver

a solver for the popular puzzle game [Binario](https://de.puzzle-binairo.com).
This solver utilizes the z3 SAT-solver

## Usage

```bash
./main.py levels/prod_6x6.csv
```

Output:

```
White stones at:  (2/0)(1/3)(1/4)(2/6)(5/1)(5/6)(7/6)
Black stones at:  (0/1)(0/6)(2/1)(2/7)(5/0)(5/7)(6/3)(6/4)(7/1)
(=)-Connections between: (2/3)=(3/3) 
(X)-Connections between: (0/2)X(1/2) (0/4)X(0/5) (2/2)X(2/3) (3/1)X(3/2) (3/6)X(3/7) (7/3)X(7/4) 
X O X O X O O X 
O X O X X O O X 
X O X O O X X O 
O X O O X X O X 
X O X X O O X O 
O X O X X O X O 
O X X O O X O X 
X O O X O X X O 
```
