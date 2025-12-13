
# This function converts extracted files into utf8, enchanced by Gemini 3-Pro
def to_utf8(filepath: str):
    with open(filepath, "rb") as f:
        raw_data = f.read()

    # Optimized List: 
    # 1. 'utf_8_sig' handles BOM if present, otherwise acts like utf_8.
    # 2. 'utf_8' is strict and standard.
    # 3. 'ascii' is the strictest subset.
    # 4. Then try the permissive legacy encodings (cp1252, latin_1, etc.)
    
    # Note: "latin_1" and many "cp..." encodings accept ANY byte sequence. 
    # They MUST be at the end of the list, or they will produce false positives 
    # for files that are actually UTF-8.
    
    preferred_encodings = ["utf_8_sig", "utf_8", "ascii"]
    
    # The rest of your list (moved legacy encodings after the strict ones)
    legacy_encodings = [
        "cp1254", "cp1252", "utf_16", "utf_32", "latin_1", "iso8859_9",
        "big5", "big5hkscs", "cp037", "cp273", "cp424", "cp437", "cp500", "cp720", "cp737", "cp775", "cp850", "cp852", "cp855", "cp856", "cp857", "cp858", "cp860", "cp861", "cp862", "cp863", "cp864", "cp865", "cp866", "cp869", "cp874", "cp875", "cp932", "cp949", "cp950", "cp1006", "cp1026", "cp1125", "cp1140", "cp1250", "cp1251", "cp1253", "cp1255", "cp1256", "cp1257", "cp1258", "euc_jp", "euc_jis_2004", "euc_jisx0213", "euc_kr", "gb2312", "gbk", "gb18030", "hz", "iso2022_jp", "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_2004", "iso2022_jp_3", "iso2022_jp_ext", "iso2022_kr", "iso8859_2", "iso8859_3", "iso8859_4", "iso8859_5", "iso8859_6", "iso8859_7", "iso8859_8", "iso8859_10", "iso8859_11", "iso8859_13", "iso8859_14", "iso8859_15", "iso8859_16", "johab", "koi8_r", "koi8_t", "koi8_u", "kz1048", "mac_cyrillic", "mac_greek", "mac_iceland", "mac_latin2", "mac_roman", "mac_turkish", "ptcp154", "shift_jis", "shift_jis_2004", "shift_jisx0213", "utf_32_be", "utf_32_le", "utf_16_be", "utf_16_le", "utf_7"
    ]
    
    all_encodings = preferred_encodings + legacy_encodings

    content = None
    decoded_enc = None

    for enc in all_encodings:
        try:
            content = raw_data.decode(enc)
            decoded_enc = enc # Save which one worked for debugging if needed
            break # <--- CRITICAL FIX: Stop once we find a working encoding
        except Exception: 
            pass
    
    if content is None:
        raise UnicodeDecodeError("all-encodings", raw_data, 0, len(raw_data), "Could not decode the raw file with any encoding")
    
    # Encode and save as utf-8
    with open(filepath, "wb") as f:
        f.write(content.encode("utf-8"))
    
