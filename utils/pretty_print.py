def pretty_print(data, indent=1, indent_size=2):
    out = ""
    indent_text = (" " * indent_size) * indent

    if type(data) is dict:
        out += "{\n"
        for key, value in data.items():
            out += indent_text + f"{key}: {pretty_print(value, indent + 1)}\n"
        out += ("  " * (indent - 1)) + "}"
    elif type(data) is list:
        out += "[\n"
        for i in range(len(data)):
            out += indent_text + f"{pretty_print(data[i], indent + 1)}\n"
        out += ("  " * (indent - 1)) + "]"
    else:
        return data

    return out
