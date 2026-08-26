import asyncio

from Functions.Media.inspector import MediaInspector


IMAGE_PATH = (
    "/home/thienan/Documents/GitHub/Glorp-Cat/"
    "system development/v0.1/Data/media/17/"
    "17_24_01a03643-2cb0-7350-9af5-e5b82f5e09ab_Scope1.png"
)

async def main():
    inspector = MediaInspector()

    result = await inspector.inspect_image(
        IMAGE_PATH,
        "What kind of graph is this?"
    )

    print(result)


asyncio.run(main())