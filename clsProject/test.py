import os
import shutil

import torch
from torch.nn import BCELoss

# from dataset import MyData
from dataset_changed import MyData
# from net import Net
from net2 import Net
from torch.utils.data import DataLoader

param_path = r"./param_pt"

test_loader = DataLoader(MyData(False), batch_size=50, shuffle=False)
net = Net()
loss_fun = BCELoss()
# 加载参数
if os.path.exists(param_path):
    try:
        net.load_state_dict(torch.load(param_path))
        print("Loaded!")
    except RuntimeError:
        os.remove(param_path)
        print("参数异常，重新开始训练")
else:
    print("No Param!")
sum_test_loss = 0.
sum_score = 0.
for epoch in range(1):
    for i, (test_data, test_tag) in enumerate(test_loader):
        net.eval()
        # 新加的
        test_data = test_data.permute(0, 3, 1, 2)
        out = net(test_data)[0]
        out1 = net(test_data)[1]
        loss = loss_fun(out.reshape(-1), test_tag.float())

        # 精度计算
        score = torch.mean((torch.eq((out.reshape(-1) > 0.5).float(), test_tag.float())).float())
        print("out:{}\ntag:{}".format((out.reshape(-1)).float(), test_tag.float()))

        # print(torch.mean((torch.eq((out.squeeze() > 0.5).float(), test_tag.float())).float()))
        # print(test_tag.float())
        # exit()
    print("epoch {} score {} ".format(epoch, score))
    sum_test_loss += loss.item()
    sum_score += score.item()
    print((out1.permute(0, 2, 3, 1) > 0.5).float())
# 测试
test_avg_loss = sum_test_loss / (epoch + 1)
test_avg_score = sum_score / (epoch + 1)
print("{} epochs: test_avg_loss is {}".format((epoch + 1), test_avg_loss))
print("{} epochs: test_avg_score is {}".format((epoch + 1), test_avg_score))
# 计算召回率
