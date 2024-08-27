def scrub_str_(v, replace, lowercase):
    """
    Removes unwanted string chars from value
    Args:
        value ([type]): [string]
    Returns:
        [type]: [clean string]
    """
    bad_chars = [
        ";",
        ":",
        "!",
        "*",
        "/",
        ",",
        "'",
        ".",
        '"',
        "|",
        "(",
        ")",
        "+",
        "\r",
        "\n",
    ]
    value = ""
    try:
        value = str(v)
        for i in bad_chars:
            value = value.replace(i, "")

        if replace:
            value = value.replace(" ", replace)

        if lowercase:
            value = value.lower()
    except Exception:
        value = ""

    return value.strip()


def slice_str(string: str, limit: int):
    new_ = string
    if string != "":
        new_ = string[:limit]

    return new_
