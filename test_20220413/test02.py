import numpy as np

def iou(box,boxes,isMin = False):
    #计算面积：[x1,y1,x2,y2]
    box_area = (box[2]-box[0])*(box[3]-box[1])
    boxes_area = (boxes[:,2]-boxes[:,0])*(boxes[:,3]-boxes[:,1])

    #找交集
    xx1 = np.maximum(box[0],boxes[:,0])#横坐标，左上角的最大值
    yy1 = np.maximum(box[1],boxes[:,1])#纵坐标，左上角的最大值
    xx2 = np.minimum(box[2],boxes[:,2])#横坐标，右下角的最小值
    yy2 = np.minimum(box[3],boxes[:,3])#纵坐标，右下角的最小值

    #判断是否有交集
    w = np.maximum(0,xx2-xx1)
    h = np.maximum(0,yy2-yy1)

    #交集的面积
    inter = w*h
    if isMin:
        ovr = np.true_divide(inter,np.minimum(box_area,boxes_area))
    else:
        ovr = np.true_divide(inter, (box_area + boxes_area - inter))
    return ovr

def nms(boxes,thresh=0.3,isMin=False):
    if boxes.shape[0] == 0:
        return np.array([])
    #根据置信度排序：[x1,y1,x2,y2,c]
    _boxes = boxes[(-boxes[:, 4]).argsort()]
    #创建空列表，存放 保留的框
    r_boxes = []
    while _boxes.shape[0]>1:
        #取出第一个框
        a_box = _boxes[0]
        #取出剩余的框
        b_boxes = _boxes[1:]
        #将1st个框保留
        r_boxes.append(a_box)

        #比较IOU，保留IOU小于阈值的框
        index = np.where(iou(a_box,b_boxes,isMin)<thresh)
        _boxes = b_boxes[index]
    #保留最后一个框
    if _boxes.shape[0] >0:
        r_boxes.append(_boxes[0])
    return np.stack(r_boxes)

if __name__ == '__main__':
    # a = np.array([1,1,11,11])
    # b = np.array([[1,1,10,10],[10,10,20,20],[12,12,34,34]])
    # print(iou(a,b))
    bs = np.array([[1, 1, 10, 10, 40], [1, 1, 9, 9, 10], [9, 8, 13, 20, 15], [6, 1, 18, 17, 13]])
    print(nms(bs,thresh=0.01))