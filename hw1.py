"""
Timothy Duggan
Homework 1
CS 239: Ethics in AI
January 21, 2025 

Agent:
    - Picks up a cart
    - Picks up 2 items
    - Heads to the exit
"""

import json
import socket
import sys
from math import sqrt

from utils import recv_socket_data

###################################################
# HELPER FUNCTIONS
###################################################


def send_action_and_receive_response(sock, action, verbose=True):
    """
    Send an action to the environment and receive the response
    Returns the parsed JSON observation
    """
    if verbose:
        print("Sending action: ", action)
    sock.send(str.encode(action))
    response = recv_socket_data(sock)
    return json.loads(response)


def distance(pos1, pos2):
    """ Returns the Euclidean distance between two positions """
    return sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def move_towards_goal(my_pos, goal_pos):
    """
    Returns a single step acttion that moves the agent towards the goal position
    """
    # Direction deltas
    dx = goal_pos[0] - my_pos[0]
    dy = goal_pos[1] - my_pos[1]

    # Move in the direction with the largest delta
    if abs(dx) > abs(dy):
        return "0 EAST" if dx > 0 else "0 WEST"
    else:
        return "0 SOUTH" if dy > 0 else "0 NORTH"

###################################################
# PHASED LOGIC
###################################################


def pick_up_cart(sock, response):
    """
    Move to the first cart return and interact to pick up a cart
    Returns updated observation after cart is picked up
    """
    cart_pos = response["observation"]["cartReturns"][0]["position"]
    my_pos = response["observation"]["players"][0]["position"]

    # Move until close enough to interact
    while distance(my_pos, cart_pos) > 0.5:
        action = move_towards_goal(my_pos, cart_pos)
        response = send_action_and_receive_response(sock, action)
        my_pos = response["observation"]["players"][0]["position"]

    # Interact to pick up the cart
    response = send_action_and_receive_response(sock, "0 INTERACT")
    # Interact again to dismiss message
    response = send_action_and_receive_response(sock, "0 INTERACT")
    return response


def pick_up_items(sock, response, shelf_index=15, n_items=2):
    """
    Moves to shelf[shelf_index], picks up `n_items` from that shelf,
    and returns the updated observation.
    """
    # Our goal position is offset to be infront of the shelf
    shelf_pos = response["observation"]["shelves"][shelf_index]["position"]
    goal_pos = (shelf_pos[0] + 1, shelf_pos[1] + 1.25)

    my_pos = response["observation"]["players"][0]["position"]
    contents_quant = response["observation"]["carts"][0]["contents_quant"]
    num_items_in_cart = 0 if contents_quant == [] else contents_quant[0]

    # Move to the shelf
    while distance(my_pos, goal_pos) > 0.5:
        delta_pos = (goal_pos[0] - my_pos[0], goal_pos[1] - my_pos[1])
        action = "0 NORTH" if delta_pos[1] < 0 else "0 EAST"
        response = send_action_and_receive_response(sock, action)
        my_pos = response["observation"]["players"][0]["position"]

    # Release the cart to pick up items
    response = send_action_and_receive_response(sock, "0 TOGGLE_CART")

    # Pick up items one by one
    while num_items_in_cart < n_items:
        response = send_action_and_receive_response(sock, "0 NORTH")  # Face shelf
        response = send_action_and_receive_response(sock, "0 INTERACT")  # Pick up item
        response = send_action_and_receive_response(sock, "0 INTERACT")  # Dismiss message

        response = send_action_and_receive_response(sock, "0 EAST")  # Face cart
        response = send_action_and_receive_response(sock, "0 INTERACT")  # Place item in cart
        response = send_action_and_receive_response(sock, "0 INTERACT")  # Dismiss message

        num_items_in_cart = response["observation"]["carts"][0]["contents_quant"][0]

    # Re-attach the cart
    response = send_action_and_receive_response(sock, "0 TOGGLE_CART")
    return response

def go_to_exit(sock, response):
    """
    Moves to the exit and exits the store
    """
    # Exit position
    my_pos = response["observation"]["players"][0]["position"]
    exit_column_path_coord = 4
    exit_row_path_coord = 3

    # Move to the exit column
    while my_pos[0] > exit_column_path_coord:
        response = send_action_and_receive_response(sock, "0 WEST")
        my_pos = response["observation"]["players"][0]["position"]

    # Move to the exit row
    while my_pos[1] > exit_row_path_coord:
        response = send_action_and_receive_response(sock, "0 NORTH")
        my_pos = response["observation"]["players"][0]["position"]

    # Continue WEST until you exit the store
    while True:
        try:
            response = send_action_and_receive_response(sock, "0 WEST")
            my_pos = response["observation"]["players"][0]["position"]
        except (ConnectionResetError, BrokenPipeError):
            print("Exited")
            sys.exit()


###################################################
# MAIN
###################################################


if __name__ == "__main__":
    # List of possible actions
    action_commands = ['NOP', 'NORTH', 'SOUTH',
                       'EAST', 'WEST', 'TOGGLE_CART', 'INTERACT']

    print("action_commands: ", action_commands)

    # Connect to Supermarket environment
    HOST = '127.0.0.1'
    PORT = 9000
    sock_game = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_game.connect((HOST, PORT))

    # Start by sending a NOP action to get the first observation
    response = send_action_and_receive_response(sock_game, "0 NOP")

    while True:
        # Update current information
        my_pos = response["observation"]["players"][0]["position"]
        curr_cart = response["observation"]["players"][0]["curr_cart"]
        num_items_in_cart = 0
        carts = response["observation"].get("carts", [])
        if len(carts) > 0:
            cart_contents = carts[0].get("contents_quant", [0])
            num_items_in_cart = cart_contents[0] if cart_contents else 0

        # If we don't have a cart, pick one up
        if curr_cart == -1:
            response = pick_up_cart(sock_game, response)

        # If we have fewer than 2 items in the cart, pick up items
        elif num_items_in_cart < 2:
            response = pick_up_items(sock_game, response)

        # Head to exit if we have 2 items in the cart
        elif num_items_in_cart == 2:
            go_to_exit(sock_game, response)

        # If the conditions are not recognized, send a NOP action
        else:
            response = send_action_and_receive_response(sock_game, "0 NOP")
            print("Agent is outside of the script and were sending the NOP action")
