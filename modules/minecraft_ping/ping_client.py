import re
import socket
import struct
import time

import orjson


class PingClient:
    """
    改自 https://github.com/djkcyl/ABot-Graia/blob/MAH-V2/saya/MinecraftPing/

    可能会报如下错误：
    1. ConnectionRefusedError: [WinError 10061] 由于目标计算机积极拒绝，无法连接。
    2. socket.timeout: timed out
    3. socket.gaierror 无效的主机名
    """

    def __init__(self, host: str = 'localhost', port: int = 25565, timeout: int = 5):
        self._host = host
        self._port = port
        self._timeout = timeout

    @staticmethod
    def _unpack_varint(sock):
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)
            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7 * i

            if not byte & 0x80:
                break

        return data

    @staticmethod
    def _pack_varint(data):
        ordinal = b''

        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        if isinstance(data, str):
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif isinstance(data, int):
            return struct.pack('H', data)
        elif isinstance(data, float):
            return struct.pack('Q', int(data))
        else:
            return data

    def _send_data(self, sock, *args):
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        sock.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, sock, extra_varint=False) -> bytes:
        packet_length = self._unpack_varint(sock)
        packet_id = self._unpack_varint(sock)
        byte = b''

        if extra_varint:
            if packet_id > packet_length:
                self._unpack_varint(sock)

            extra_length = self._unpack_varint(sock)

            while len(byte) < extra_length:
                byte += sock.recv(extra_length)

        else:
            byte = sock.recv(packet_length)

        return byte

    @staticmethod
    def _format_desc(data: dict) -> str:  # type: ignore
        if 'extra' in data:
            return ''.join(part['text'] for part in data['extra'])
        elif 'text' in data:
            return re.sub(r'§[0-9a-gk-r]', '', data['text'])

    def get_ping(self, format_: bool = True) -> dict:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((self._host, self._port))
            self._send_data(sock, b'\x00\x00', self._host, self._port, b'\x01')
            self._send_data(sock, b'\x00')
            data = self._read_fully(sock, extra_varint=True)

            self._send_data(sock, b'\x01', time.time() * 1000)
            unix = self._read_fully(sock)

        status = orjson.loads(data.decode('utf8'))
        if format_:
            status['description'] = self._format_desc(status['description'])
        status['delay'] = time.time() * 1000 - struct.unpack('Q', unix)[0]
        return status


async def ping(host: str | None = None, port: int | None = None) -> dict:
    if host is None:
        raise ValueError('host can not be empty')
    client = PingClient(host=host, port=port or 25565)
    stats: dict = client.get_ping()

    player_list = stats['players'].get('sample') or []
    return {
        'version': stats['version']['name'],
        'protocol': str(stats['version']['protocol']),
        'motd': stats['description'],
        'delay': str(round(stats['delay'], 1)),
        'online_player': str(stats['players']['online']),
        'max_player': str(stats['players']['max']),
        'player_list': player_list,
    }
