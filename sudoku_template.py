import os
import numpy as np
import copy

def load_sudoku(puzzle_path):
    ''' Load the sudoku from the given path; it returns the sudoku as a list of lists
        input: puzzle_path: path to the puzzle
        output: ret: the sudoku as a list of lists where -1 represents an empty cell
        and 0-8 represents the value in the cell corresponding to the numbers 1-9'''
    ret = []
    with open(puzzle_path, 'r') as sudoku_f: 
        for line in sudoku_f:
            line = line.rstrip()
            cur = line.split(" ")
            cur = [ord(x) - ord('1') if x.isdigit() else -1 for x in cur]
            ret.append(cur)
    return ret


def isSolved(sudoku, **kwargs):
    '''' Check if the sudoku is solved
        input: sudoku: the sudoku to be solved
               kwargs: other keyword arguments
        output: True if solved, False otherwise
    '''
    for i in sudoku:
        if -1 in i:
            return False
    return True 
    # pass

def undo_changes_for_position(sudoku, x, y, val, **kwargs):
    ''' Undo the changes made for the given position
        input: sudoku: the sudoku to be solved
               x: row number
               y: column number
               val: value to be checked
               kwargs: other keyword arguments
        output: None
    '''
    sudoku[x][y] = -1
    # pass


def update_changes_for_position(sudoku, x, y, val, **kwargs):
    ''' Update the changes for the given position
        input: sudoku: the sudoku to be solved
               x: row number
               y: column number
               val: value to be checked
               kwargs: other keyword arguments
        output: None
    '''
    sudoku[x][y] = val
    # pass


def isPossible(sudoku, x, y, val, **kwargs):
    ''' Check if the value(val) is possible at the given position (x, y)
        input: sudoku: the sudoku to be solved
               x: row number
               y: column number
               val: value to be checked
               kwargs: other keyword arguments
        output: True if possible, False otherwise
    '''
    
    domains = kwargs['domains']
    if val not in domains[(x,y)]:
        return False
    
    #check row
    if val in sudoku[x]:
        return False

    # check column
    if val in [sudoku[i][y] for i in range(0, 9)]:
        return False

    # check 3x3 box
    box_row = (x // 3) * 3
    box_col = (y // 3) * 3
    if val in [sudoku[i][j] for i in range(box_row, box_row + 3) for j in range(box_col, box_col + 3)]:
        return False

    # if the value is valid for the cell, return True
    return True
    # pass


def get_mrv_position(sudoku, **kwargs):
    ''' Get the position with minimum remaining values
        input: sudoku: the sudoku to be solved
               kwargs: other keyword arguments'
        output: x: row number
                y: column number'''
    mrv_cell = (-1, -1)
    min_remaining_values = 9
    remaining_values= 0
    for row in range(0, 9):
        for col in range(0, 9):
            if sudoku[row][col] == -1:
                for i in range(9):
                    if isPossible(sudoku, row, col, i, **kwargs):
                        remaining_values += 1
                if remaining_values < min_remaining_values:
                    mrv_cell = (row, col)
                    min_remaining_values = remaining_values
                remaining_values = 0
    return mrv_cell
    # pass



def undo_waterfall_changes(sudoku, changes, **kwargs):
    ''' Undo the changes made by the waterfalls
        input: sudoku: the sudoku to be solved
               changes: list of changes made by the waterfalls previously
               kwargs: other keyword arguments
        output: None

    '''
    domains = kwargs['domains']
    for lst in changes:
        var_removed = lst[0]
        val_removed = lst[1]
        domains[var_removed].add(val_removed) 
    kwargs['domains'] = domains
    # pass

def apply_waterfall_methods(sudoku, list_of_waterfalls, **kwargs):
    ''' Apply the waterfall methods to the sudoku
        input: sudoku: the sudoku to be solved
               list_of_waterfalls: list of waterfall methods
               kwargs: other keyword arguments
        output: isPoss: True if the sudoku is solved, False otherwise
                all_changes: list of changes made by the waterfalls'''
    all_changes = []
    #Keep applying the waterfalls until no change is made
    while True:
        #Flag to check if any change is made by the waterfalls
        any_chage = False
        for waterfall in list_of_waterfalls:
            isPoss, changes = waterfall(sudoku, **kwargs)
            all_changes += changes
            # If any change is made, then set the flag to True
            if len(changes) > 0:
                any_chage = True
            # If the sudoku is not possible fill up, then return False and the changes made to be undone
            if not isPoss:
                return False, all_changes
        # If no change is made by the waterfalls at current iteration, then break
        if not any_chage:
            break
    return True, all_changes


def get_next_position_to_fill(sudoku, x, y, mrv_on, **kwargs):
    ''' Get the next position to fill during the backtracking
        input: sudoku: the sudoku to be solved
               x: row number
               y: column number
               mrv_on: True if mrv is on, False otherwise
               kwargs: other keyword arguments
        output: nx: next row number
                ny: next column number'''
    if mrv_on:
        return get_mrv_position(sudoku, **kwargs)
    else:
        for row in range(0, 9):
            for col in range(0, 9):
                if sudoku[row][col] == -1:
                    return (row, col)
        return -1, -1
    # pass

def solve_sudoku(sudoku, x, y, mrv_on, list_of_waterfalls, **kwargs):
    '''' Solve the sudoku using the given waterfall methods with/without mrv
        input: sudoku: the sudoku to be solved
               x: row number of the current position
               y: column number the current position
               mrv_on: True if mrv is on, False otherwise
               list_of_waterfalls: list of waterfalls to be applied
               kwargs: other keyword arguments
               output:  True if solved, False otherwise
                        sudoku: the solved sudoku
                        guess: number of guesses made'''
    
    #Feel free to change the function as you need, for example, you can change the keyword arguments in the function calls below
    #First you need to check whether the sudoku is solved or not
    if isSolved(sudoku):
        return True, sudoku, 0
    #Apply the waterfalls; change the kwargs with your own
    isPoss, changes = apply_waterfall_methods(sudoku, list_of_waterfalls, **kwargs)
    
    # If the sudoku is not possible, undo the changes and return False
    if not isPoss:
        undo_waterfall_changes(sudoku, changes, **kwargs)
        return False, sudoku, 0
    #After waterfalls are applied, now you need to check if the current position is already filled or not; if it is filled, 
    #then you need to get the next position to fill

    if sudoku[x][y] != -1:

        nx, ny = get_next_position_to_fill(sudoku, x, y, mrv_on, **kwargs)

        solved, sudoku, guess = solve_sudoku(sudoku, nx, ny, mrv_on, list_of_waterfalls, **kwargs)

        if solved:
            return True, sudoku, guess
        else:
            #Undo the changes made by the already applied waterfalls
            undo_waterfall_changes(sudoku, changes, **kwargs)
            return False, sudoku, guess
    


    no_cur_guess = 0
    #Check how many guesses are possible for the current position
    for i in range(9):
        if isPossible(sudoku, x, y, i, **kwargs):
            no_cur_guess += 1
        
    if no_cur_guess == 0:
        return False, sudoku, 0

    for i in range(9):
        #Check if the value is possible at the current position
        if isPossible(sudoku, x, y, i, **kwargs):
            #If the value is possible, then update the changes for the current position
            update_changes_for_position(sudoku, x, y, i, **kwargs)
            #Get the next position to fill
            nx, ny = get_next_position_to_fill(sudoku, x, y, mrv_on, **kwargs)
            #Solve the sudoku for the next position
            solved, sudoku, guesses = solve_sudoku(sudoku, nx, ny, mrv_on, list_of_waterfalls, **kwargs)
            no_cur_guess += guesses

            #If the sudoku is solved, then return True, else undo the changes for the current position
            if solved:
                return True, sudoku, no_cur_guess -1
            else:
                undo_changes_for_position(sudoku, x, y, i, **kwargs)
    
    #If the sudoku cannot solved at current partially filled state, then undo the changes made by the waterfalls and return False
    undo_waterfall_changes(sudoku, changes, **kwargs)
    return False, sudoku, no_cur_guess - 1


def ac3_waterfall(sudoku, **kwargs):
    '''The ac3 waterfall method to apply
    input:  sudoku: the sudoku to apply AC-3 method on'
            kwargs: the kwargs to be passed to the isPossible function
    output: isPoss: whether the sudoku is still possible to solve (i.e. not inconsistent))
            changes: the changes made to the sudoku'''
    changes = []
    domains = kwargs['domains']
    arcs = set()
    for i in range(9):
            for j in range(9):
                neighbors = get_neighbors(sudoku,(i, j))
                for neighbor in neighbors:
                    arcs.add(((i, j), neighbor))
    queue = []
    for arc in arcs:
        queue.append(arc)

    while queue:
        (xi, xj) = queue.pop(0)
        revise_bool, changes = revise(domains, xi, xj, changes)
        if revise_bool:
            if len(domains[xi]) == 0:
                return False, changes
            for xk in get_neighbors(sudoku,xi) - {xj}:
                queue.append((xk, xi))
    
    kwargs['domains'] = domains
    return True, changes

def revise(domains, xi, xj, changes):
    revised = False
    to_remove=[]
    for x in domains[xi]:
        if not any(y!=x for y in domains[xj]):
            to_remove.append(x)
            changes.append([xi,x])
            revised = True
    for x in to_remove:
        domains[xi].remove(x)
    return revised, changes

def get_neighbors(sudoku, cell):
        neighbors = set()
        row, col = cell
        n = len(sudoku)

        #Adding all elemets in same row and same column
        for i in range(n):
            neighbors.add((row, i))
            neighbors.add((i, col))

        #Adding elements in the block
        sqrt_n = int(np.sqrt(n))
        row_start = (row // sqrt_n) * sqrt_n
        col_start = (col // sqrt_n) * sqrt_n

        for i in range(row_start, row_start+sqrt_n):
            for j in range(col_start, col_start+sqrt_n):
                neighbors.add((i, j))

        neighbors.remove(cell)
        return neighbors


def waterfall1(sudoku, **kwargs):
    '''The first waterfall method to apply
    input:  sudoku: the sudoku to apply the waterfall method on
            kwargs: the kwargs to be passed to the isPossible function
    output: isPoss: whether the sudoku is still possible to solve (i.e. not inconsistent))
            changes: the changes made to the sudoku'''
    changes = []
    '''
    We are implementing Hidden Pair Inference, this is the case, where we have a pair of 2 values in the domains of exactly 2
    positions, but it is not very obvious. Hence the hidden. There will be a pair of values present in the domain of 2 different postions
    that can only be assigned to these specific positons (and all the other domain values can be removed from the domain). For example, 
    in a row there is 2, 9, 5, and 7 already placed. Remaining values are 1,3,4,6 and 8. Now assume considering all the other constraints 
    that are derived from the row, column and the box. We have 2 values in the unit such that they have values [1,4] in the domain and no
    other position has these domains. From this we can infer that 1 and 4 are to be placed in these 2 boxes and we can safely remove other
    domain values from these positons.
    '''
    #Write your code here

    #Creating sets of all elements in each row, column and a box
    rows, cols, boxes = [], [], []
    for i in range(9):
        rows.append(set([(i, j) for j in range(9)]))
        cols.append(set([(j, i) for j in range(9)]))
        boxes.append(set([(i // 3 * 3 + j // 3, i % 3 * 3 + j % 3) for j in range(9)]))

    domains = kwargs['domains']
    # Check for hidden pairs in each row, column, and 3x3 box

    for group in [rows, cols, boxes]:
        for cells in group:
            pairs = {}
            for cell in cells:
                if sudoku[cell[0]][cell[1]] == -1:
                    for value in domains[(cell[0], cell[1])]:
                        key = frozenset(digit for digit in domains[cell] if digit != value)
                        if key not in pairs:
                            pairs[key] = []

            for key, cells_pair in pairs.items():
                if len(cells_pair) == 2 and len(key) == 2:
                    # If there is a hidden pair, remove all other occurrences of those values from the group
                    for cell in cells:
                        for other_cell in cells_pair:
                            if cell==other_cell:
                                to_be_removed = []
                                for digit in domains[cell]:
                                    if digit not in key:
                                        changes.append([(cell[0], cell[1]), digit])
                                        to_be_removed.append(digit)
                                for x in to_be_removed:
                                        domains[(cell[0],cell[1])].remove(x)
                                if len(domains[(cell[0],cell[1])]) == 0:
                                    kwargs['domains'] = domains
                                    return False, changes

    kwargs['domains'] = domains
    return True, changes

def waterfall2(sudoku, **kwargs):
    '''The second waterfall method to apply
    input:  sudoku: the sudoku to apply the waterfall method on
            kwargs: the kwargs to be passed to the isPossible function
    output: isPoss: whether the sudoku is still possible to solve (i.e. not inconsistent))
            changes: the changes made to the sudoku'''

    '''
    Waterfall2 is Naked Pair Inference, and this is not implicitly implemented while performing the AC3 with MRV
    Naked Pairs is the case when there are 2 unassigned positions in the unit, where both of them have exactly same 2 possible values
    Therefore we remove those 2 domain values from all the remaining unassigned positions of that unit 
    Implementation given as follows:.
    '''
    domains = kwargs['domains']
    changes = []
    
    # Creating sets of all elements in each row, column and a box
    rows, cols, boxes = [], [], []
    for i in range(9):
        rows.append(set([(i, j) for j in range(9)]))
        cols.append(set([(j, i) for j in range(9)]))
        boxes.append(set([(i // 3 * 3 + j // 3, i % 3 * 3 + j % 3) for j in range(9)]))
    
    # Check for naked pairs in each row, column, and 3x3 box
    for group in [rows, cols, boxes]:
        for cells in group:
            pairs = {}
            for cell in cells:
                if sudoku[cell[0]][cell[1]] == -1:
                    value = domains[(cell[0], cell[1])]
                    key = frozenset(value)
                    if key not in pairs:
                        pairs[key] = []
                    pairs[key].append(cell)
            
            for key, cells_pair in pairs.items():
                if len(cells) == 2 and len(key) == 2:
                    # If there is a naked pair, remove all other occurrences of those values from the group
                    for cell in cells:
                        for other_cell in cells_pair:
                            if cell != other_cell:
                                to_be_removed = []
                                for digit in key:
                                    if digit in domains[(cell[0], cell[1])]:
                                        changes.append([(cell[0], cell[1]), digit])
                                        to_be_removed.append(digit)
                                for x in to_be_removed:
                                        domains[(cell[0],cell[1])].remove(x)
                                if len(domains[(cell[0],cell[1])]) == 0:
                                    kwargs['domains'] = domains
                                    return False, changes

    kwargs['domains'] = domains
    return True, changes
                            
 
def get_all_waterfall_methods():
    '''Get all the waterfall methods as list.'''
    pass


def get_initial_kwargs(sudoku, mrv_on, **kwargs):
    '''Get the initial kwargs for the solve_sudoku function.
    input:  sudoku: the sudoku to solve
            mrv_on: whether to use the mrv heuristic
            kwargs: other keyword arguments
    output: kwargs: the kwargs to be passed to the solve_sudoku function
    '''
    domains = {}
    for i in range(9):
        for j in range(9):
            if sudoku[i][j] == -1:
                domains[(i, j)] = set(range(9))
            else:
                domains[(i, j)] = set([sudoku[i][j]])
    kwargs['domains'] = domains
    return kwargs



def solve_plain_backtracking(original_sudoku):
    '''Solve the sudoku using plain backtracking.'''
    sudoku = copy.deepcopy(original_sudoku)
    kwargs = get_initial_kwargs(sudoku, False)
    ini_x, ini_y = 0, 0
    return solve_sudoku(sudoku, ini_x, ini_y, False, [], **kwargs)

def solve_with_mrv(original_sudoku):
    '''Solve the sudoku using mrv heuristic.'''
    sudoku = copy.deepcopy(original_sudoku)
    kwargs = get_initial_kwargs(sudoku, True)
    ini_x, ini_y = get_next_position_to_fill(sudoku, -1, -1, True, **kwargs)
    return solve_sudoku(sudoku, ini_x, ini_y, True, [], **kwargs)

def solve_with_ac3(original_sudoku):
    '''Solve the sudoku using mrv heuristic and ac3 waterfall method.'''
    sudoku = copy.deepcopy(original_sudoku)
    all_waterfalls = [ac3_waterfall]
    kwargs = get_initial_kwargs(sudoku, True)
    ini_x, ini_y = get_next_position_to_fill(sudoku, -1, -1, True, **kwargs)
    return solve_sudoku(sudoku, ini_x, ini_y, True, all_waterfalls, **kwargs)

def solve_with_addition_of_waterfall1(original_sudoku):
    '''Solve the sudoku using mrv heuristic and waterfall1 waterfall method besides ac3.'''
    sudoku = copy.deepcopy(original_sudoku)
    all_waterfalls = [ac3_waterfall, waterfall1]
    kwargs = get_initial_kwargs(sudoku, True)
    ini_x, ini_y = get_next_position_to_fill(sudoku, -1, -1, True, **kwargs)
    return solve_sudoku(sudoku, ini_x, ini_y, True, all_waterfalls, **kwargs)

def solve_with_addition_of_waterfall2(original_sudoku):
    '''Solve the sudoku using mrv heuristic and waterfall2 waterfall method besides ac3 and waterfall1.'''
    sudoku = copy.deepcopy(original_sudoku)
    all_waterfalls = [ac3_waterfall, waterfall1, waterfall2]
    kwargs = get_initial_kwargs(sudoku, True)
    ini_x, ini_y = get_next_position_to_fill(sudoku, -1, -1, True, **kwargs)
    return solve_sudoku(sudoku, ini_x, ini_y, True, all_waterfalls, **kwargs)



def solve_one_puzzle(puzzle_path):

    sudoku = load_sudoku(puzzle_path)
    # print(sudoku)

    solved, solved_sudoku_bt, backtracking_guesses = solve_plain_backtracking(sudoku)
    assert solved
    solved, solved_sudoku_mrv, mrv_guesses = solve_with_mrv(sudoku)
    assert solved
    solved, solved_sudoku_ac, ac3_guesses = solve_with_ac3(sudoku)
    assert solved
    solved, solved_sudoku, waterfall1_guesses = solve_with_addition_of_waterfall1(sudoku)
    assert solved
    solved, solved_sudoku, waterfall2_guesses = solve_with_addition_of_waterfall2(sudoku)
    assert solved
    #Add more waterfall methods here if you want need to and return the number of guesses for each method
    return (backtracking_guesses, mrv_guesses, ac3_guesses, waterfall1_guesses, waterfall2_guesses)

def solve_all_sudoku():
    puzzles_folder = "D:\Programming Assignments Files-20230402\Assignment 3\puzzles"
    puzzles = os.listdir(puzzles_folder)
    puzzles.sort()

    for puzzle_file in puzzles:
        puzzle_path = os.path.join(puzzles_folder, puzzle_file)

        backtracking_guesses, mrv_guesses, ac3_guesses, waterfall1_guesses, waterfall2_guesses = solve_one_puzzle(puzzle_path)
        print("Puzzle: ", puzzle_file)
        print("backtracking guesses: ", backtracking_guesses)
        print("mrv guesses: ", mrv_guesses)
        print( "ac3 guesses: ", ac3_guesses)
        print("with waterfall1 guesses: ", waterfall1_guesses)
        print("with waterfall2 guesses: ", waterfall2_guesses)

if __name__ == '__main__':
    solve_all_sudoku()