"""Unit tests for the zero-dependency Protobuf codec using unittest."""

import unittest
from antigravity_restore.protobuf_codec import (
    decode_varint,
    encode_length_delimited,
    encode_string_field,
    encode_timestamp_field,
    encode_varint,
    iter_length_delimited_fields,
)


class TestProtobufCodec(unittest.TestCase):
    def test_varint_roundtrip(self):
        values = [0, 1, 127, 128, 300, 16384, 2097151, 1727891234]
        for v in values:
            enc = encode_varint(v)
            dec, next_pos = decode_varint(enc, 0)
            self.assertEqual(dec, v)
            self.assertEqual(next_pos, len(enc))

    def test_string_field_encoding(self):
        encoded = encode_string_field(1, "test-title")
        self.assertIn(b"test-title", encoded)

    def test_timestamp_field(self):
        encoded = encode_timestamp_field(3, 1700000000)
        self.assertTrue(len(encoded) > 0)

    def test_iter_length_delimited(self):
        p1 = encode_string_field(1, "hello")
        p2 = encode_string_field(1, "world")
        combined = p1 + p2
        items = list(iter_length_delimited_fields(combined, 1))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0], b"hello")
        self.assertEqual(items[1], b"world")


if __name__ == "__main__":
    unittest.main()
