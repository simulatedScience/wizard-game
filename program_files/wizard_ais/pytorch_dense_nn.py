import torch
import torch.nn as nn

class Dense_NN(nn.Module):
  """
  create a dense neural network using pytorch. The neural network is a feed forward network with the given number of neurons in each layer.
  """
  def __init__(self,
        input_size: int,
        output_size: int,
        hidden_sizes: list[int],
        last_activation: nn.Module = nn.Linear()):
    super().__init__()
    self.input = nn.Linear(input_size, hidden_sizes[0])
    self.hidden = nn.ModuleList([nn.Linear(hidden_sizes[i], hidden_sizes[i+1]) for i in range(len(hidden_sizes)-1)])
    self.output = last_activation(hidden_sizes[-1], output_size)

  def forward(self, x: torch.Tensor) -> torch.Tensor:
    """
    evaluate the neural network for the given input x

    inputs:
    -------
        x (torch.Tensor): input tensor

    returns:
    --------
        torch.Tensor: output tensor
    """
    x: torch.Tensor = nn.functional.relu(self.input(x))
    for layer in self.hidden:
        x = nn.functional.relu(layer(x))
    x = self.output(x)
    return x
  
  def get_weights(self) -> list[torch.Tensor]:
    """
    get the weights of the neural network

    returns:
    --------
        list[torch.Tensor]: list of weights for each layer
    """
    return [layer.weight for layer in self.layers]

  def set_weights(self, weights: list[torch.Tensor]) -> None:
    """
    set the weights of the neural network

    parameters:
    -----------
        weights (list[torch.Tensor]): list of new weights for each layer
    """
    for i, param in enumerate(self.parameters()):
        param.data = weights[i] #.clone()