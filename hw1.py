"""
Timothy Duggan
Homework 1
CS AI Ethics
January 21, 2025 

This is a simple agent that will pick up a cart, pick up 2 items, and then head to the exit.
"""

import json
import socket
import sys

from utils import recv_socket_data


def move_towards_goal(my_pos, goal_pos, no_progress=False):
    action = None
    delta_pos = (goal_pos[0] - my_pos[0], goal_pos[1] - my_pos[1])

    if delta_pos[0] > delta_pos[1]:
        if delta_pos[0] > 0:
            action = "0 " + "EAST"
        else:
            action = "0 " + "WEST"

    else:
        if delta_pos[1] > 0:
            action = "0 " + "SOUTH"
        else:
            action = "0 " + "NORTH"

    return action


if __name__ == "__main__":

    action_commands = ['NOP', 'NORTH', 'SOUTH',
                       'EAST', 'WEST', 'TOGGLE_CART', 'INTERACT']

    print("action_commands: ", action_commands)

    # Connect to Supermarket
    HOST = '127.0.0.1'
    PORT = 9000
    sock_game = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_game.connect((HOST, PORT))

    action = action_commands[0]  # NOP action to get first obs
    sock_game.send(str.encode(action))  # send action to env

    my_pos = None

    while True:

        output = recv_socket_data(sock_game)  # get observation from env
        output = json.loads(output)

        prev_pos = my_pos
        my_pos = output["observation"]["players"][0]["position"]

        # Pick up cart
        if output["observation"]["players"][0]["curr_cart"] == -1:

            cart_pos = output["observation"]["cartReturns"][0]["position"]

            action = move_towards_goal(my_pos, cart_pos)

            delta_pos = (cart_pos[0] - my_pos[0], cart_pos[1] - my_pos[1])
            dist = delta_pos[0] ** 2 + delta_pos[1] ** 2
            if (dist < 0.5):
                action = "0 " + "INTERACT"

            print("Sending action: ", action)
            sock_game.send(str.encode(action))  # send action to env
            output = recv_socket_data(sock_game)
            print("Sending action: ", action)
            # send interact twice to get rid of message
            sock_game.send(str.encode(action))

        # Get 2 items
        elif output["observation"]["carts"][0]["contents_quant"] == [] or output["observation"]["carts"][0]["contents_quant"][0] < 2:

            goal_pos = (output["observation"]["shelves"][15]["position"][0] + 1,
                        output["observation"]["shelves"][15]["position"][1]+1.25)

            delta_pos = (goal_pos[0] - my_pos[0], goal_pos[1] - my_pos[1])

            dist = delta_pos[0] ** 2 + delta_pos[1] ** 2
            if (dist > 0.5):
                if delta_pos[1] < 0:
                    action = "0 NORTH"
                elif delta_pos[0] > 0:
                    action = "0 EAST"
                print("Sending action: ", action)
                sock_game.send(str.encode(action))
            else:
                action = "0 TOGGLE_CART"
                print("Sending action: ", action)
                sock_game.send(str.encode(action))
                output = recv_socket_data(sock_game)

                for i in range(2):
                    action = "0 NORTH"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)

                    action = "0 INTERACT"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)
                    action = "0 INTERACT"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)

                    action = "0 EAST"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)

                    action = "0 INTERACT"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)
                    action = "0 INTERACT"
                    print("Sending action: ", action)
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)

                action = "0 TOGGLE_CART"
                print("Sending action: ", action)
                sock_game.send(str.encode(action))

        # Head to exit
        elif output["observation"]["carts"][0]["contents_quant"][0] == 2:
            # pre_exit_pos = [1.2, 15.6]
            x_aisle = 4
            y_exit = 3

            while my_pos[0] > x_aisle:
                action = "0 WEST"
                print("Sending action: ", action)
                sock_game.send(str.encode(action))
                output = recv_socket_data(sock_game)
                output = json.loads(output)
                my_pos = output["observation"]["players"][0]["position"]

            while my_pos[1] > y_exit:
                action = "0 NORTH"
                print("Sending action: ", action)
                sock_game.send(str.encode(action))
                output = recv_socket_data(sock_game)
                output = json.loads(output)
                my_pos = output["observation"]["players"][0]["position"]

            while True:
                action = "0 WEST"
                print("Sending action: ", action)
                try:
                    sock_game.send(str.encode(action))
                    output = recv_socket_data(sock_game)
                except ConnectionResetError as e:
                    print("Exited")
                    sys.exit()

        else:
            action = action_commands[0]
            sock_game.send(str.encode(action))
            print("Agent is outside of the script and were sending the NOP action")
