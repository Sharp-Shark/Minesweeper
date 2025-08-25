import msvcrt, os, random, math

'''
    by Sharp-Shark (18th of July, 2025)
    
    color docs: https://learn.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
    msvcrt docs: https://docs.python.org/3/library/msvcrt.html#msvcrt.kbhit
'''

os.system('color')

x1b_reset = '\x1b[0m'
x1b_bg_blue = '\x1b[44m'
x1b_bg_red = '\x1b[41m'
x1b_fg_red = '\x1b[31m'
x1b_underline = '\x1b[4m'

def x1b_bg_rbg (red, green, blue) :
    return f'\x1b[48;2;{red};{green};{blue}m'

def x1b_fg_rbg (red, green, blue) :
    return f'\x1b[38;2;{red};{green};{blue}m'

tile_graphic = {
    '0': ' ' + x1b_reset,
    '1': x1b_fg_rbg(85, 85, 255) + '1' + x1b_reset,
    '2': x1b_fg_rbg(55, 185, 55) + '2' + x1b_reset,
    '3': x1b_fg_rbg(255, 55, 55) + '3' + x1b_reset,
    '4': x1b_fg_rbg(55, 55, 155) + '4' + x1b_reset,
    '5': x1b_fg_rbg(155, 55, 55) + '5' + x1b_reset,
    '6': x1b_fg_rbg(55, 155, 155) + '6' + x1b_reset,
    '7': x1b_fg_rbg(155, 55, 155) + '7' + x1b_reset,
    '8': x1b_fg_rbg(115, 115, 115) + '8' + x1b_reset,
    '*': x1b_bg_red + '@' + x1b_reset,
    'h': '#' + x1b_reset,
    'f': x1b_fg_red + '@' + x1b_reset,
}

neighbours = (
    # cardinal
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
    # diagonal
    (-1, 1),
    (1, 1),
    (1, -1),
    (-1, -1),
)    

def is_pos_bounded (x, y, width, height) :
    if x < 0 : return False
    if x > width - 1 : return False
    if y < 0 : return False
    if y > height - 1 : return False
    return True

def generate_board (width, height, bombs, nobomb_coords) :
    valid_bomb_coords = []
    board = []
    for y in range(height) :
        board.append([])
        for x in range(width) :
            board[y].append('0')
            if (x, y) not in nobomb_coords : valid_bomb_coords.append((x, y))

    def bump (x, y) :
        if not is_pos_bounded(x, y, width, height) : return
        if board[y][x] in '012345678' :
            board[y][x] = str(int(board[y][x]) + 1)
    
    bomb_coords = set()
    for i in range(bombs) :
        index = random.randint(0, len(valid_bomb_coords) - 1)
        x, y = valid_bomb_coords.pop(index)
        board[y][x] = '*'
        bomb_coords.add((x, y))
        for neighbour in neighbours :
            bump(x + neighbour[0], y + neighbour[1])

    return (board, bomb_coords)

def render_board (board, mask, cursor) :
    print_buffer = ''
    y = 0
    for row in mask :
        x = 0
        for tile in row :
            if (x, y) == cursor :
                print_buffer += x1b_underline
            if tile == 1 :
                print_buffer += tile_graphic[board[y][x]]
            elif tile == -1 :
                print_buffer += tile_graphic['f']
            else :
                print_buffer += tile_graphic['h']
            print_buffer += ' '
            x += 1
        print_buffer = print_buffer[:len(print_buffer) - 1] + '\n'
        y += 1
    return print_buffer
    
def game () :
    try :
        width = max(4, int(input('width ')))
    except :
        width = 9
    try :
        height = max(4, int(input('height ')))
    except :
        height = 9
    try :
        bombs = max(0, min(width * height - 9, int(input('bombs '))))
    except :
        bombs = 9
    
    mask = [[0 for x in range(width)] for y in range(height)] # 1 is revealed, 0 is hidden, -1 is flagged
    board, bomb_coords = [], set()
    board_generated = False
    cursor = ((math.floor(width / 2), math.floor(height / 2)))
    flags = bombs # amount of flags left
    remaining = width * height - bombs # amount of safe tiles remaining before victory
    queue = [] # dig queue
    kaboom = False # lose
    victory = False
    print_needed = True
    
    while not (victory or kaboom) :
        if msvcrt.kbhit() :
            key = msvcrt.getch()
            x, y = cursor
            if key == b'w' :
                x, y = cursor[0], cursor[1] - 1
                if is_pos_bounded(x, y, width, height) :
                    cursor = (x, y)
                    print_needed = True
            elif key == b's' :
                x, y = cursor[0], cursor[1] + 1
                if is_pos_bounded(x, y, width, height) :
                    cursor = (x, y)
                    print_needed = True
            elif key == b'd' :
                x, y = cursor[0] + 1, cursor[1]
                if is_pos_bounded(x, y, width, height) :
                    cursor = (x, y)
                    print_needed = True
            elif key == b'a' :
                x, y = cursor[0] - 1, cursor[1]
                if is_pos_bounded(x, y, width, height) :
                    cursor = (x, y)
                    print_needed = True
            elif key == b' ' :
                if mask[y][x] == 0 :
                    queue.append(cursor)
                    print_needed = True
                if not board_generated :
                    board_generated = True
                    nobomb_coords = set()
                    nobomb_coords.add(cursor)
                    for neighbour in neighbours :
                        nobomb_coords.add((x + neighbour[0], y + neighbour[1]))
                    board, bomb_coords = generate_board(width, height, bombs, nobomb_coords)
            elif key == b'f' :
                if mask[y][x] == 0 and flags > 0 :
                    mask[y][x] = -1
                    flags -= 1
                    print_needed = True
                elif mask[y][x] == -1 :
                    mask[y][x] = 0
                    flags += 1
                    print_needed = True
        
        while len(queue) > 0 :
            x, y = queue.pop()
            if mask[y][x] == 1 : continue
            if mask[y][x] == -1 : flags += 1
            mask[y][x] = 1
            if board[y][x] == '*' :
                kaboom = True
                break
            if board[y][x] == '0' :
                for neighbour in neighbours :
                    if is_pos_bounded(x + neighbour[0], y + neighbour[1], width, height) : queue.append((x + neighbour[0], y + neighbour[1]))
            remaining -= 1
            if remaining <= 0 :
                victory = True
                break
                
        # reveal all tiles when game ends
        if victory or kaboom :
            for y in range(height) :
                for x in range(width) :
                    if mask[y][x] != 1 :
                        if board[y][x] == '*' : mask[y][x] = -1
                        else : mask[y][x] = 1
        
        if print_needed :
            print_needed = False
            print_buffer = ''
            print_buffer += render_board(board, mask, cursor)
            if kaboom :
                print_buffer += '\n' + x1b_bg_red + 'KABOOM!' + x1b_reset
            elif victory :
                print_buffer += '\n' + x1b_bg_blue + 'CLEAR!' + x1b_reset
            else :
                print_buffer += '\n' + str(flags) + '/' + str(bombs) + ' flags left'
                print_buffer += '\n\nwasd moves\nspace digs\nf flags'
            print_buffer += '\n'
            os.system('cls')
            print(print_buffer)

while True : game()