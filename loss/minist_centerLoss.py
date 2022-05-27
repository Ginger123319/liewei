import torch
import torchvision
from torch import nn
from torch.nn.functional import one_hot
from torchvision import transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from FocalLoss import FocalCE
from CenterLoss import CenterLoss

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# 加载数据集
# transforms.ToTensor()转Tensor，换轴（HWC->CHW），归一化
train_data = torchvision.datasets.MNIST(root=r"G:\liewei\source\MNIST_DATA", download=False, train=True,
                                        transform=transforms.ToTensor())
train_loader = DataLoader(dataset=train_data, batch_size=512, shuffle=True)


# 特征可视化函数
# 此处feature是N，2；tag是N
def visualize(feature, tag, epoch):
    plt.ion()
    # 定义十种颜色，16进制表示RGB
    c = ["#f0e000", "#ffd000", "#fffe00", "#fffba0", "#ffb400",
         "#908000", "#990000", "#993900", "#994990", "#888888"]
    # 绘画之前，清屏
    plt.clf()
    for i in range(10):
        # 从特征中取出对应标签的所有x，y值进行绘画
        # 此处是重点需要仔细研究
        # print((tag == i).shape)
        plt.plot(feature[tag == i, 0], feature[tag == i, 1], ".", c=c[i])
    # 图例
    plt.legend(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], loc="upper right")
    plt.title(epoch)
    plt.savefig("images/epoch=%d.jpg" % epoch)
    # draw()功能和show类似
    # plt.draw()
    plt.show()
    plt.pause(0.01)


# 手写数字识别以及输出特征的网络
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.loss = CenterLoss(10, 10)
        self.cnn_layer = nn.Sequential(
            nn.Conv2d(1, 16, 3, 1, padding=1),
            # nn.Conv2d(1, 16, 3, 1),
            nn.MaxPool2d(2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Conv2d(16, 32, 3, 1, padding=1),
            nn.MaxPool2d(2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, 1, padding=1),
            nn.MaxPool2d(2),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, 1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 256, 3, 1),
            nn.BatchNorm2d(256),
            nn.ReLU()

        )
        self.fc1 = nn.Sequential(
            # 特征输出，形状为N，2
            # 便于画在二维平面上
            nn.Linear(256 * 1 * 1, 2)
        )
        self.fc2 = nn.Sequential(
            # 十分类输出
            nn.Linear(2, 10),
            nn.Softmax(dim=-1)
        )

    def get_loss_fun(self):
        return self.loss

    def forward(self, x):
        cnn_out = self.cnn_layer(x).reshape(-1, 256 * 1 * 1)
        # print(cnn_out.shape)
        out1 = self.fc1(cnn_out)
        out2 = self.fc2(out1)
        return out1, out2


if __name__ == '__main__':
    net = Net().to(device)
    # loss_func = net.get_loss_fun()
    loss_func = FocalCE(1, 2)
    # loss_func = nn.MSELoss()
    # loss_func = nn.CrossEntropyLoss()
    # 增大步长lr
    # 增加动量momentum（加快调整的速度，减少运行时长）
    # opt = torch.optim.SGD(net.parameters(), lr=0.01, momentum=0.5)
    opt = torch.optim.Adam(net.parameters())
    epoch = 0
    while True:
        feat_list = []
        tag_list = []
        train_acc_sum = 0.
        for i, (x, y) in enumerate(train_loader):
            x = x.to(device)
            y = y.to(device)
            target = one_hot(y, 10).float().to(device)
            feature, out = net(x)
            loss = loss_func(out, target)
            # loss = loss_func(out, y)

            opt.zero_grad()
            loss.backward()
            opt.step()

            feat_list.append(feature)
            tag_list.append(y)
            if i % 10 == 0:
                print(loss.item())
            # 计算精度
            out = torch.argmax(out, dim=-1)
            # print(out.shape)
            y = y
            # print(torch.mean((out == y).float()))
            train_acc = torch.mean((out == y).float())
            train_acc_sum += train_acc.item()
        print("开始画图{}".format(epoch))
        print("{}epoch acc:{}".format(epoch, train_acc_sum / len(train_loader)))
        # print(feat_list[0].shape)
        # print(tag_list[0].shape)
        # 因为有很多个批次512，所以需要进行cat操作
        # torch.cat将list中的张量合并后转为Tensor
        feat = torch.cat(feat_list, 0)
        label = torch.cat(tag_list, 0)
        # print(feat.shape)
        # print(label.shape)
        # 解绑转np便于画图
        visualize(feat.detach().cpu().numpy(), label.detach().cpu().numpy(), epoch)
        epoch += 1
