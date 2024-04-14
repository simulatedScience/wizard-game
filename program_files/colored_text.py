import colored
import matplotlib.colors as mplcolors


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
    if color.startswith('#'):
        color = color[1:]  # Remove the '#' if present
    # rgb_color = mplcolors.hex2color(color)
    rgb_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    use_color = colored.Fore.rgb(*rgb_color)
    return colored.stylize(text, use_color)
    # return f"{use_color}{text}{colored.Style.reset}"
    # return f'\x1b[38;2;{rgb_color[0]};{rgb_color[1]};{rgb_color[2]}m{text}\x1b[0m'


def print_color_index(color_index):
    if color_index == 0:
        return colored_text('R', '#dd3333')
    if color_index == 1:
        return colored_text('Y', '#cccc00')
    if color_index == 2:
        return colored_text('G', '#22cc22')
    if color_index == 3:
        return colored_text('B', '#5588ff')
    if color_index == -1:
        return colored_text('no trump', '#dddddd')
    

if __name__ == '__main__':
    # Print the output of the print_color_index function
    print(print_color_index(0))
    print(print_color_index(1))
    print(print_color_index(2))
    print(print_color_index(3))
    print(print_color_index(-1))