import socket
from gameboard import BoardClass

print("Setting up server..")
a = True
while a:
    try:
        address = input("Enter the address: ")
        port = int(input("Enter a port: "))

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((address, port))

        a = False

        print("Setup successfully!")
        print("Waiting for connection")

    except Exception as msg_error:
        try_again = input("failed. try again? (y/n): ")
        if try_again == "y":
            pass
        else:
            a = False

if a is False:
    WLT_check = False
    player_move = "o"

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind((address, port))

    server_socket.listen(2)

    connection = True

    while connection:
        try:
            client_soc, client_add = server_socket.accept()
            print(f"Connected: {client_add}")
        except Exception as msg_error:
            print("Failed to accept connection")
            connection = False
            print("Disconnected")
            server_socket.close()

        # going forward means things are connected
        client_soc.send("Username: ".encode())
        username_1 = client_soc.recv(16).decode()
        print("Player 1:", username_1)

        # sending username "player2" to player1
        username_2 = "player2"
        client_soc.send(username_2.encode())

        # creates BoardClass obj
        the_game = BoardClass(username_2, username_1)

        # board = the_game.print_board()
        client_soc.send(the_game.print_board().encode())

        p1_board = eval(client_soc.recv(1024).decode())
        the_game.updateGameBoard(p1_board)
        print(the_game.print_board())

        play = True

        while play:
            # p2 will make move
            # also checks if p2 move is taken
            dup2 = True
            if the_game.boardIsFull() is False:
                while dup2:
                    print("Enter a number between (1-9)")
                    p2_move = input(f"{username_2}: ")

                    the_game.name = username_2
                    the_game.last_plyr = username_1

                    try:
                        if 1 <= int(p2_move) <= 9:
                            if the_game.board[int(p2_move) - 1] == " ":
                                dup2 = False
                                the_game.board[int(p2_move) - 1] = "o"
                            else:
                                print("taken! choose another")
                    except IndexError:
                        pass
                    except ValueError:
                        pass

                # show player 2 the results of their move
                print(the_game.print_board())

                # Checks if player 2 has won
                try:
                    if the_game.isWinner()[0]:
                        if the_game.isWinner()[1] == "o":
                            client_soc.send("done".encode())
                            the_game.wins += 1
                            print(f"You Won!")
                            WLT_check = True
                        play = False
                except TypeError:
                    print(f"waiting for {username_1} to play")
                    # sends the board
                    client_soc.send(str(the_game.cur_board()).encode())

                    try:
                        p1_board = eval(client_soc.recv(1024).decode())
                        the_game.updateGameBoard(p1_board)
                        print(the_game.print_board())

                        the_game.name = username_1
                        the_game.last_plyr = username_2
                    except NameError:
                        the_game.loss += 1
                        print("you lost..")
                        play = False
                        WLT_check = True

                # someone won
                if WLT_check:
                    # so that it doesn't awlwats check
                    WLT_check = False
                    print(f"waiting if {username_1} wants to play again")
                    play_again = client_soc.recv(1024).decode()
                    if play_again == "y":
                        play = True
                        print(f"{username_1} wants to play again..")
                        the_game.resetGameBoard()

                        # since player 1 plays first
                        # client_soc.recv(1024).decode()
                        p1_board = eval(client_soc.recv(1024).decode())
                        the_game.updateGameBoard(p1_board)
                        print(the_game.print_board())
                    else:
                        pass

            else:
                # board is full
                print("Tie..")
                the_game.ties += 1
                play = False

                WLT_check = False

                print(f"waiting if {username_1} wants to play again")
                play_again = client_soc.recv(1024).decode()
                if play_again == "y":
                    play = True
                    print(f"{username_1} wants to play again..")
                    the_game.resetGameBoard()

                    # since player 1 plays first
                    # client_soc.recv(1024).decode()
                    p1_board = eval(client_soc.recv(1024).decode())
                    the_game.updateGameBoard(p1_board)
                    print(the_game.print_board())

        connection = False

    if connection is False:
        print(f"{username_1} does not want to play again")
        print()
        print("Statistics")
        the_game.printStats()

        print("Thank you for playing! ^_^")
        print("Disconnected")
        server_socket.close()