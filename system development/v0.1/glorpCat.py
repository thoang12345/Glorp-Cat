from Functions.utilities import logger, t
from Functions.agent import Agent
from Functions import system

system.giveGPUstatus()

t.tic()

agent = Agent()

while True:

    user = input("\n\nYou: ")

    if not user:
        break

    agent.chat(user)

t.toc("\nChat duration")