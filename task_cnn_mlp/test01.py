import torch
from torch import nn
from torchvision import models


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, 3, 1),
            nn.MaxPool2d(2, stride=2),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.net(x)


if __name__ == '__main__':
    # net = Net()
    # demo = torch.randn(1, 3, 7, 7)
    # print(net.forward(demo).shape)
    # print(models.resnet34())
    demo = torch.randn(480)
    print(demo.shape)
    print((demo > 0.5).float())
    print((demo[:, None]).shape)
