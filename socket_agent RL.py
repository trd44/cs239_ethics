# Author: Gyan Tatiya
# Email: Gyan.Tatiya@tufts.edu

import json
import random
import socket

import gymnasium as gym
from env import SupermarketEnv
from utils import recv_socket_data


if __name__ == "__main__":

    # Make the env
    # env_id = 'Supermarket-v0'
    # env = gym.make(env_id)

    action_commands = ['NOP', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'TOGGLE_CART', 'INTERACT', 'RESET']

    print("action_commands: ", action_commands)

    # Connect to Supermarket
    HOST = '127.0.0.1'
    PORT = 9000
    sock_game = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_game.connect((HOST, PORT))
    training_time = 100
    for i in range(training_time):

        sock_game.send(str.encode("0 RESET"))  # reset the game
        obs = recv_socket_data(sock_game)
        while True:
            # implement your RL learning loop here

            # assume this is the only agent in the game
            action = "0 " + random.choice(action_commands)

            print("Sending action: ", action)
            sock_game.send(str.encode(action))  # send action to env

            obs = recv_socket_data(sock_game)  # get observation from env
            obs = json.loads(obs)
            print("JSON: ", type(obs))
            