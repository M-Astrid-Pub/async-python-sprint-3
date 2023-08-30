import logging
import sys
import asyncio
from asyncio.streams import StreamReader, StreamWriter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Server:
    def __init__(self):
        self.clients = []
        self.messages = []


    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        self.clients.append(writer)

        address = writer.get_extra_info('peername')
        logger.info('Client connected: %s', address)

        username = await reader.read(1024)
        writer.write(f"Welcome to the messenger, {username.decode().strip()}! \n".encode())
        await writer.drain()

        while True:
            data = await reader.read(1024)
            if data == 'quit':
                self.clients.remove(writer)
                writer.write("Disconnected from the chat.\n".encode())
                await writer.drain()
                break
            await self.broadcast(data)

        logger.info('Stop serving %s', address)
        writer.close()

    async def broadcast(self, msg):
        for writer in self.clients:
            writer.write(msg)
            await writer.drain()


    async def run(self, host: str, port: int):
        srv = await asyncio.start_server(
            self.client_connected, host, port)

        async with srv:
            await srv.serve_forever()


if __name__ == '__main__':
    server = Server()
    asyncio.run(server.run('127.0.0.1', 8000))