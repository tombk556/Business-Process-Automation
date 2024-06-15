import base64


def encode_to_base64(original_string: str):
    string_bytes = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string
