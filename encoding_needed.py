# True = has to be encoded (Text)
# False = shouldnt be encoded already binary (binary)
mimetype_encoding_needed = {
    # Textformate
    "text/plain": True,
    "text/html": True,
    "text/css": True,
    "application/javascript": True,
    "application/json": True,
    "application/xml": True,
    
    # Binary formats
    "image/png": False,
    "image/jpeg": False,
    "image/gif": False,
    "image/webp": False,
    "image/svg+xml": True,
    "application/pdf": False,
    "application/zip": False,
    "application/gzip": False,
    "audio/mpeg": False,
    "audio/wav": False,
    "video/mp4": False,
    "video/webm": False,
}
