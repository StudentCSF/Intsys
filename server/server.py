import asyncio
import datetime
import re
from random import randint, uniform

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8867

MESSAGE_PONG = 'PONG'
MESSAGE_KEEPALIVE = 'keepalive'
MESSAGE_IGNORED = '(проигнорировано)'

READ_BYTES_COUNT = 100

MIN_SLEEP_SECONDS = 0.1
MAX_SLEEP_SECONDS = 1

response_number = 0

clients = dict()


def write_log(date, receiving_time='', received_message='', sending_time=None, send_message=MESSAGE_IGNORED):
    if sending_time:
        suffix_log = f'{sending_time};{send_message}'
    else:
        suffix_log = send_message
    with open('server.log', 'a') as f:
        f.write(f'{date};{receiving_time};{received_message};{suffix_log}\n')


def is_need_response():
    return bool(randint(0, 9))


def get_date_and_time():
    actual_datetime = datetime.datetime.now()
    date = actual_datetime.date()
    time = actual_datetime.time().strftime('%H:%M:%S.%f')[:-3]
    return date, time


async def send_keepalive():
    global response_number, clients

    while True:
        await asyncio.sleep(5)
        for writer, _ in clients.items():
            message = f'[{response_number}] {MESSAGE_KEEPALIVE}'
            response_number += 1
            writer.write(message.encode())
            await writer.drain()

            date, sending_time = get_date_and_time()
            write_log(date=date, send_message=message, sending_time=sending_time)


async def handle_client(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
):
    global response_number, clients

    clients[writer] = len(clients) + 1

    while True:
        data = await reader.read(READ_BYTES_COUNT)

        receiving_date, receiving_time = get_date_and_time()

        message = data.decode()
        split_message = message.split(' ')
        request_number = re.findall(r'\d+', split_message[0])[0]

        sending_time = None
        send_message = MESSAGE_IGNORED

        if is_need_response():
            await asyncio.sleep(uniform(MIN_SLEEP_SECONDS, MAX_SLEEP_SECONDS))

            send_message = f'[{response_number}/{request_number}] {MESSAGE_PONG} ({clients[writer]})'
            writer.write(send_message.encode())
            await writer.drain()

            _, sending_time = get_date_and_time()

        write_log(date=receiving_date, receiving_time=receiving_time, received_message=message,
                  sending_time=sending_time, send_message=send_message)

        response_number += 1

    writer.close()
    await writer.wait_closed()


async def init_server():
    server = await asyncio.start_server(
        client_connected_cb=handle_client,
        host=SERVER_HOST,
        port=SERVER_PORT
    )

    asyncio.create_task(send_keepalive())

    async with server:
        await server.serve_forever()


asyncio.run(init_server())
