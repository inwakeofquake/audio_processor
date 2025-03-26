import torch
print(torch.cuda.is_available())  # Should be True
print(torch.version.cuda)  # Should show version