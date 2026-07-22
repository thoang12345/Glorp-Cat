import logging
from pytictoc import TicToc

logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s',
                     datefmt='%Y-%m-%d %I:%M:%S %p')
logger = logging.getLogger(__name__)

t = TicToc()

def getResponseFromUser(question : str, correctResponse : str = "correct") -> str:
        quit = True
        while quit:
                questionResponse = input(question)

                if questionResponse in ["q", "n"]:
                        quit = False
                        return "quit"
                
                if questionResponse not in correctResponse and questionResponse == "":
                        logger.info("Empty response, please type something.")
                        continue

                if correctResponse == "correct" or questionResponse in correctResponse:
                        return questionResponse
                
                if questionResponse not in correctResponse:
                        logger.info(f"Invalid answer. Try typing something like: {', '.join(correctResponse)}")
                        continue
                
