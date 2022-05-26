from pogram_files.colored_text import colored_text


class Wizard_Card:
  """
  Each Object of this class represents a card from the wizard game
  """
  def __init__(self, value):
    """initialize a wizard card object described by `value`.

    Args:
        value (int): integer in range [0,59].
            `value%15` describes the card's actual value (in range [0,14]),
            `value//15` specifies it's color (in range [0,3])
    """
    self.raw_value = value
    self.value = value % 15
    self.color = -1 if self.value in (0, 14) else value // 15
    self.colors = ["#ff3333", "#dddd00", "#22dd22", "#5588ff", "#dddddd"]


  def __str__(self):
    if self.value == 0:  # jester
      return colored_text("J", self.colors[self.color])
    if self.value == 14:  # wizard
      return colored_text("W", self.colors[self.color])
    return colored_text(str(self.value), self.colors[self.color])


  def __repr__(self):
    return str(self)


  def __hash__(self):
    return hash(self.raw_value)


  def __eq__(self, other: "Wizard_Card") -> bool:
    """
    compare two `Wizard_Card` obejects first by color, then by value.

    inputs:
    -------
        other (Wizard_Card): any wizard card object

    Returns:
        bool: whether or not `self` is considered to be less than `other`
    """
    if other is None:
      return False
    if self.color != other.color:
      return False
    if self.value != other.value:
      return False
    return True


  def __lt__(self, other: "Wizard_Card") -> bool:
    """
    compare two `Wizard_Card` obejects first by color, then by value.

    inputs:
    -------
        other (Wizard_Card): any wizard card object

    Returns:
        bool: whether or not `self` is considered to be `<` than `other`
    """
    if other is None:
      return False
    if -self.color > -other.color:
      return False
    if -self.color < -other.color:
      return True
    if self.value < other.value:  # color is equal
      return True
    return False


  def __gt__(self, other: "Wizard_Card") -> bool:
    """
    compare two `Wizard_Card` obejects first by color, then by value.

    inputs:
    -------
        other (Wizard_Card): any wizard card object

    Returns:
        bool: whether or not `self` is considered to be `>` than `other`
    """
    if other is None:
      return False
    if -self.color < -other.color:
      return False
    if -self.color > -other.color:
      return True
    if self.value > other.value:  # color is equal
      return True
    return False


  def __le__(self, other: "Wizard_Card") -> bool:
    """
    compare two `Wizard_Card` obejects first by color, then by value.

    inputs:
    -------
        other (Wizard_Card): any wizard card object

    Returns:
        bool: whether or not `self` is considered to be `<=` than `other`
    """
    if other is None:
      return False
    if -self.color > -other.color:
      return False
    if -self.color < -other.color:
      return True
    if self.value <= other.value:  # color is equal
      return True
    return False


  def __ge__(self, other: "Wizard_Card") -> bool:
    """
    compare two `Wizard_Card` obejects first by color, then by value.

    inputs:
    -------
        other (Wizard_Card): any wizard card object

    Returns:
        bool: whether or not `self` is considered to be `>=` than `other`
    """
    if other is None:
      return False
    if -self.color < -other.color:
      return False
    if -self.color > -other.color:
      return True
    if self.value >= other.value:  # color is equal
      return True
    return False
