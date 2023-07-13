import subprocess as sp
import time


DURATION_SECONDS = 300


def main():
    server = sp.Popen(['python', '.\\server\\server.py'])
    client1 = sp.Popen(['python', '.\\client\\cl1.py'])
    client2 = sp.Popen(['python', '.\\client\\cl2.py'])
    time.sleep(DURATION_SECONDS)
    client1.terminate()
    client2.terminate()
    server.terminate()


if __name__ == '__main__':
    main()
