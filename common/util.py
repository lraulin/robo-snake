"""Gets text from a file."""


def get_text_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()
