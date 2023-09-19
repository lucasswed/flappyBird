# flappyBird
Flappy bird game developed in python with pygame. This game was developed to put an neural network to play and learn how to play. I used the neat python library to do the neural network.
The neat python is a library that uses a genetic algorithm, it basicly make a population of neural networks and put them to play the game with random weights and bias, then when the all population die, it takes the neural network that perform better with the fitness, points that we give to them during the game, and then clone that neural network for the new population and perform random mutations on the weights and bias. 

# Use of the program
1 - You need to install the dependencies, this project was developed with python 3.10, so i don't know if it works with older versions. You will need to install the pygame and the neat libs, to do so you can run "pip install pygame" and "pip install neat-python".

2 - After you install all dependencies, you can run the program with python3 flappyBird.py.
