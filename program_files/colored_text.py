import colored


def colored_text(text, color):
    """
    return text to be printed in the given color

    inputs:
    -------
        text - (str) - any string
        color - (str) - a hex-code as a color (including '#') i.e. "#0055cc"

    returns:
    --------
        (str) - given text formatted with the given color
    """
    use_color = colored.fg(color)
    return f"{use_color}{text}{colored.attr('reset')}"


def print_color_index(color_index):
    if color_index == 0:
        return colored_text('R', '#ff3333')
    if color_index == 1:
        return colored_text('Y', '#dddd00')
    if color_index == 2:
        return colored_text('G', '#22dd22')
    if color_index == 3:
        return colored_text('B', '#5588ff')
    if color_index == -1:
        return colored_text('no trump', '#dddddd')
