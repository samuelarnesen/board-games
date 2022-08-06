from models import LinearBlock, TransformerBlock

import torch

tb = TransformerBlock(number_of_heads=4)

input_tensor = torch.rand([5, 16])
tb(input_tensor)