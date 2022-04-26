"""
Main driver file.
Handling user input.
Displaying current GameStatus object.
"""
'''hello maleeka here'''
'''hi maleeka'''
import pygame as p
import ChessEngine
import ChessAI
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15

#dictionary of images of pieces so that they can be later used
images={'wP': p.transform.scale(p.image.load("images/" + 'wp' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'wR': p.transform.scale(p.image.load("images/" + 'wR' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'wN': p.transform.scale(p.image.load("images/" + 'wN' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'wB': p.transform.scale(p.image.load("images/" + 'wB' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'wK': p.transform.scale(p.image.load("images/" + 'wK' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'wQ': p.transform.scale(p.image.load("images/" + 'wQ' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bP': p.transform.scale(p.image.load("images/" + 'bp' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bR': p.transform.scale(p.image.load("images/" + 'bR' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bN': p.transform.scale(p.image.load("images/" + 'bN' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bB': p.transform.scale(p.image.load("images/" + 'bB' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bK': p.transform.scale(p.image.load("images/" + 'bK' + ".png"), (SQUARE_SIZE, SQUARE_SIZE)),
        'bQ': p.transform.scale(p.image.load("images/" + 'bQ' + ".png"), (SQUARE_SIZE, SQUARE_SIZE))}
#this is for a two player game with AI hints
def mainAI():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.state()
    valid_moves = game_state.ValidMoves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    running = True
    square_selected = ()  # no square is selected initially, this will keep track of the last click of the user (tuple(row,col))
    player_clicks = []  # this will keep track of player clicks (two tuples)
    game_over = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # user clicked the same square twice
                        square_selected = ()  # deselect
                        player_clicks = []  # clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # append for both 1st and 2nd click
                    if len(player_clicks) == 2:  # after 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    move_undone = True
                if e.key == p.K_r:  # reset the game when 'r' is pressed
                    game_state = ChessEngine.state()
                    valid_moves = game_state.ValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    move_undone = True
                if e.key == p.K_h: # give hint when h is pressed
                    if not game_over:
                        return_queue = Queue()  # used to pass data between threads
                        move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                        move_finder_process.start()
                        move_finder_process.join()
                        if not move_finder_process.is_alive():
                            ai_move = return_queue.get()
                            if ai_move is None:
                                ai_move = ChessAI.findRandomMove(valid_moves)
                            game_state.makeMove(ai_move)
                            move_made = True
                            animate = True

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.ValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawBoard(screen)
        highlightSquares(screen, game_state, valid_moves, square_selected)
        drawPieces(screen, game_state.board)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

#for a game against AI
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.state()
    valid_moves = game_state.ValidMoves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    running = True
    square_selected = ()  # no square is selected initially, this will keep track of the last click of the user (tuple(row,col))
    player_clicks = []  # this will keep track of player clicks (two tuples)
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    player_one = True  # if a human is playing white, then this will be True, else False
    player_two = False  # if a hyman is playing white, then this will be True, else False

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # user clicked the same square twice
                        square_selected = ()  # deselect
                        player_clicks = []  # clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # append for both 1st and 2nd click
                    if len(player_clicks) == 2 and human_turn:  # after 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:  # reset the game when 'r' is pressed
                    game_state = ChessEngine.state()
                    valid_moves = game_state.ValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=ChessAI.findBestMove,
                                              args=(game_state, valid_moves, return_queue))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.ValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawBoard(screen)
        highlightSquares(screen, game_state, valid_moves, square_selected)
        drawPieces(screen, game_state.board)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

# draw squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

#show the possible moves with the highlight
def highlightSquares(screen, game_state, valid_moves, square_selected):
    """
    Highlight square selected and moves for piece selected.
    """
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_C * SQUARE_SIZE, last_move.end_R * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_R == row and move.start_C == col:
                    screen.blit(s, (move.end_C * SQUARE_SIZE, move.end_R * SQUARE_SIZE))

# draw pieces on top of those squares
def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(images[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log.

    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.end_R - move.start_R
    d_col = move.end_C - move.start_C
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_R + d_row * frame / frame_count, move.start_C + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_R + move.end_C) % 2]
        end_square = p.Rect(move.end_C * SQUARE_SIZE, move.end_R * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_R + 1 if move.piece_captured[0] == 'b' else move.end_R - 1
                end_square = p.Rect(move.end_C * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(images[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(images[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


mainClock = p.time.Clock()
from pygame.locals import *

p.init()
p.display.set_caption('Chess AI')
screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT), 0, 32)

font = p.font.SysFont(None, 20)


# text draws on screen
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


# loading images
AI_img = p.image.load('AI_img.png').convert_alpha()
PVP_img = p.image.load('PVP_img.png').convert_alpha()
title_img = p.image.load('title_pic.png').convert_alpha()
instruc_img = p.image.load('Instructions.png').convert_alpha()
click = False


class Title():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = p.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))


title = Title(33, 75, title_img, 0.8)
AI_button = Title(190, 250, AI_img, 0.7)
PVP_button = Title(465, 250, PVP_img, 0.7)
instruc = Title(245, 320, instruc_img, 0.6)


class Background(p.sprite.Sprite):
    def __init__(self, image_file, location):
        p.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = p.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


BackGround = Background('mi.png', [0, 0])


def main_menu():
    while True:

        screen.fill([169, 169, 169])
        screen.blit(BackGround.image, BackGround.rect)

        mx, my = p.mouse.get_pos()

        vsHuman = p.Rect(175, 275, 150, 25)
        vsAI = p.Rect(450, 275, 150, 25)

        if vsHuman.collidepoint((mx, my)):
            if click:
                main()
        if vsAI.collidepoint((mx, my)):
            if click:
                mainAI()

        p.draw.rect(screen, (255, 255, 255), vsHuman)
        p.draw.rect(screen, (255, 255, 255), vsAI)
        title.draw(screen)
        AI_button.draw(screen)
        PVP_button.draw(screen)
        instruc.draw(screen)

        click = False
        for event in p.event.get():
            if event.type == QUIT:
                p.quit()
                sys.exit()
            # if event.type == KEYDOWN:
            #     if event.key == K_ESCAPE:
            #         p.quit()
            #         sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        p.display.update()
        mainClock.tick(60)

if __name__ == "__main__":
    main_menu()