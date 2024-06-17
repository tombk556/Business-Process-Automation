import base64


def encode_to_base64(original_string: str):
    """
    Encodes a given string into its Base64 representation.

    This function takes a string, encodes it to bytes using UTF-8 encoding, then converts those bytes into
    a Base64 encoded string. Base64 is commonly used when there is a need to encode binary data, especially
    when that data needs to be stored and transferred over media that are designed to deal with textual data.

    Args:
        original_string (str): The original string to be encoded into Base64.

    Returns:
        str: A Base64 encoded string of the original string.

    Example:
        encoded_string = encode_to_base64("Hello, World!")
        print(encoded_string)  # Outputs: SGVsbG8sIFdvcmxkIQ==
    """
    string_bytes = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string
