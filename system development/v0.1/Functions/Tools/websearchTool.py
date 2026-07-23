from Functions.tool import Tool
from ddgs import DDGS

class WebSearchTool(Tool):
    def __init__(self):
            super().__init__(
                "web_search",
                "Search the web for recent information and return. Relevant search results."
            )

    def schema(self):
          return {
                "type" : "function",
                "function" : {
                      "name" : self.name,
                      "description" : self.description,
                      "parameters" : {
                            "type" : "object",
                            "properties" : {
                                  "query" : {
                                        "type" : "string",
                                        "description" : "The search query to look up on the web."
                                  }
                            },
                            "required" : ["query"]
                      }
                }
          }

    def _search(self, query):
        try:
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        query,
                        max_results=5,
                        safesearch="off"
                    )
                )

            print(results)

            return {
                "query": query,
                "results": results
            }

        except Exception as e:
            print("DDGS ERROR:", repr(e))
            raise

    def execute(self, query):
        return self._search(query)




          