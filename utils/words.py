def get_python_var_syntax(name: str):
    new_letter = ""

    for letter in name:
        if letter.isupper():
            new_letter += letter.lower()
        elif letter == " ":
            new_letter += "_"
        elif not letter.isalpha():
            continue
        else:
            new_letter += letter

    return new_letter
