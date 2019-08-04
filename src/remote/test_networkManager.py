from unittest import TestCase
from remote.network import NetworkManager, pack, unpack


def split_into_packets(bts: bytes, packet_size: int = 1024):
    packets = []
    while bts:
        if len(bts) < packet_size:
            packets.append(bts)
            bts = b''
        else:
            packets.append(bts[:packet_size])
            bts = bts[packet_size:]
    return packets


class TestNetworkManager(TestCase):
    def setUp(self):
        self.nm = NetworkManager()
        self.sid = self.nm.new_session(None, None)

    def test_pack_unpack(self):
        xs = range(1000)
        self.assertEqual(xs, unpack(pack(xs)))
        self.assertEqual(range, unpack(pack(range)))
        self.assertEqual(xs, unpack(pack(range))(1000))

    def test_handle_message_to_session(self):
        sid = self.sid
        nm = self.nm
        s = nm.get_session(sid)
        d = {i: str(i) for i in range(20)}
        packed_d = pack(d)
        nm.handle_message_to_session(sid, packed_d)
        self.assertEqual(1, len(s.recv))
        self.assertEqual(d, s.recv[-1])

        e = {i: str(i + 1) for i in range(100)}
        packed_e = pack(e)
        for pck in split_into_packets(packed_e, packet_size=32):
            self.assertEqual(1, len(s.recv))
            nm.handle_message_to_session(sid, pck)
        self.assertEqual(2, len(s.recv))
        self.assertEqual(e, s.recv[-1])
        self.assertEqual(d, s.recv[-2])

        packed_2 = packed_e + packed_d

        for p in split_into_packets(packed_2, packet_size=100):
            nm.handle_message_to_session(sid, p)
        self.assertEqual(4, len(s.recv))
        self.assertEqual(d, s.recv[-1])
        self.assertEqual(e, s.recv[-2])
        s.close()

    def test_close_session(self):
        sid = self.sid
        s = self.nm.get_session(sid)
        name = s.user_name
        self.assertFalse(self.nm.namegen.name_is_available(name))
        s.close()
        self.assertTrue(self.nm.namegen.name_is_available(name))
