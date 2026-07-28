from Functions.tool import Tool

class GetCollections(Tool):
    def __init__(self):
        super().__init__(
            "get_collections",
            "returns the name and description of collections within chromaDB"
        )

    def schema(self):
        return {
            
        }