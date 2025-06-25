import chardet

# This function converts extracted files into utf8
def to_utf8(filepath: str):
    with open(filepath, "rb") as f:
        raw_data = f.read()
    # Guess file's encoding
    result = chardet.detect(raw_data) # Chardet mostly detects the encoding correctly, but sometimes doesn't
    encoding = result['encoding']

    # Try to decode the data
    content = None
    for i, enc in enumerate([ encoding ] + [ "ascii", "windows-1254", "windows-1252", "utf-8", "utf-16", "utf-32", "iso-8859-1", "iso-8859-9" ]):
        if enc is None: # Chardet can return encoding=None
            continue
        try:
            content = raw_data.decode(enc)
            if i > 0: # If chardet suggested encoding was wrong
                print(f"Info: Correct encoding for {filepath} found at {i + 1}th try: {enc}")
            break
        except UnicodeDecodeError:
            pass
    else:
        raise UnicodeDecodeError("multiple-encodings", raw_data, 0, len(raw_data), f"Could not decode the raw file after many attempts")

    # Encode and save as utf-8
    with open(filepath, "wb") as f:
        f.write(content.encode("utf-8"))
