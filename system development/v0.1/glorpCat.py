from Functions.utilities import logger, t
from Functions import system
from ollama import chat

system.giveGPUstatus()

t.tic()
# Use the generate function for a one-off prompt
conversation = [
    {"role" : "user", "content" : "Hello, how are you?"}
]
reply = chat(model="llama2", messages=conversation)
print(reply.message.content)
t.toc("\nChat duration")