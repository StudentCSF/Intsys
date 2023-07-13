import asyncio
import datetime
from random import uniform

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8867

READ_BYTES_COUNT = 100

MIN_SLEEP_SECONDS = 0.3
MAX_SLEEP_SECONDS = 3

request_number = 0


def write_log(date, requesting_time, request, response_time, response):
    with open('cl2.log', 'a') as f:
        f.write(f'{date};{requesting_time};{request};{response_time};{response}\n')


def get_date_and_time():
    actual_datetime = datetime.datetime.now()
    date = actual_datetime.date()
    time = actual_datetime.time().strftime('%H:%M:%S.%f')[:-3]
    return date, time


async def talk_with_server(reader, writer):
    global request_number

    while True:
        message = f'[{request_number}] PING'

        writer.write(message.encode())

        date, requesting_time = get_date_and_time()
        request = message
        response_time = response = ''

        try:
            data = await asyncio.wait_for(reader.read(READ_BYTES_COUNT), 1)
            response = data.decode()
            split_response = response.split()
            if len(split_response) == 2 and split_response[1] == 'keepalive':
                requesting_time = request = ''
            _, response_time = get_date_and_time()
        except asyncio.TimeoutError:
            _, response_time = get_date_and_time()
            response = '(таймаут)'
        finally:
            write_log(date=date, requesting_time=requesting_time, request=request,
                      response_time=response_time, response=response)

        request_number += 1
        await asyncio.sleep(uniform(MIN_SLEEP_SECONDS, MAX_SLEEP_SECONDS))


async def run_client():
    reader, writer = await asyncio.open_connection(
        host=SERVER_HOST,
        port=SERVER_PORT
    )

    await talk_with_server(reader, writer)

    writer.close()
    await writer.wait_closed()


asyncio.run(run_client())
