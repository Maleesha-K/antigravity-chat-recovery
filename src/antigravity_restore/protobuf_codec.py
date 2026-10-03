"""Zero-dependency Protocol Buffers wire-format encoder/decoder.

Antigravity IDE stores `trajectorySummaries` as a serialized Protobuf payload.
This module provides low-level varint, length-delimited and record manipulation
using only Python's standard library.
"""


def encode_varint(value: int) -> bytes:
    """Encode an integer into protobuf varint wire format (wire type 0)."""
    result = bytearray()
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result) or b"\x00"


def decode_varint(data: bytes, pos: int = 0) -> tuple[int, int]:
    """Decode a varint from data starting at position `pos`.

    Returns (value, next_pos).
    """
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if (b & 0x80) == 0:
            return result, pos
        shift += 7
    return result, pos


def skip_protobuf_field(data: bytes, pos: int, wire_type: int) -> int:
    """Skip over a field value based on its wire type. Returns new position."""
    if wire_type == 0:  # varint
        _, pos = decode_varint(data, pos)
    elif wire_type == 1:  # 64-bit fixed
        pos += 8
    elif wire_type == 2:  # length-delimited
        length, pos = decode_varint(data, pos)
        pos += length
    elif wire_type == 5:  # 32-bit fixed
        pos += 4
    return pos


def encode_length_delimited(field_number: int, data: bytes) -> bytes:
    """Encode a length-delimited field (wire type 2)."""
    tag = (field_number << 3) | 2
    return encode_varint(tag) + encode_varint(len(data)) + data


def encode_string_field(field_number: int, string_val: str) -> bytes:
    """Encode a UTF-8 string field (wire type 2)."""
    return encode_length_delimited(field_number, string_val.encode("utf-8"))


def encode_timestamp_field(field_number: int, epoch_seconds: int) -> bytes:
    """Encode a google.protobuf.Timestamp field (sub-field 1 is seconds as varint)."""
    seconds_bytes = encode_varint(1 << 3) + encode_varint(epoch_seconds)
    return encode_length_delimited(field_number, seconds_bytes)


def iter_length_delimited_fields(data: bytes, target_field_number: int):
    """Yield all payload byte blocks corresponding to target_field_number."""
    pos = 0
    while pos < len(data):
        try:
            tag, pos = decode_varint(data, pos)
            field_num = tag >> 3
            wire_type = tag & 7
            if wire_type == 2:
                length, pos = decode_varint(data, pos)
                end = pos + length
                if end > len(data):
                    break
                if field_num == target_field_number:
                    yield data[pos:end]
                pos = end
            else:
                next_pos = skip_protobuf_field(data, pos, wire_type)
                if next_pos <= pos:
                    break
                pos = next_pos
        except Exception:
            break
