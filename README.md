# Vanish-Point-Detect
#### 阳希明 Yang Ximing
#### Fudan University
## 项目介绍
计算机视觉期中课程项目  
消失点检测是一些平面检测，道路检测算法中重要的一步。三维物体投影在二维时（比如被照下来），在三维中平行的线段集合于二维中不再平行，其交点即为消失点。这个项目实现了一个，从单个图片检测消失点（在图片上）位置的算法。

## 算法介绍
该项目采用了一种投票方法求出消失点，并解决了一些细节问题。具体算法步骤如下：
1. 使用双边滤波器对图像降噪。
2. 使用canny边缘检测检测出图片边缘。
3. 使用概率霍夫变换检测出直线片段。
4. 对直线片段尽可能扩展到最长的线段。
5. 将非常接近的线段合并为一条线段。
6. 将所有线段按照极坐标排序之后，与相邻一定角度的线段求所在直线的交点做候选点。
7. 所有线段对所有候选点投票，投票方法为计算线段中点到指定点的直线和原线段的夹角theta，投票值为 | l | * e ^ (theta / (2 * u ^ 2)),l为线段长度，u为一个鲁棒性参数，具体设置为0.1。
8. 对投票之后的待选点做层次聚类，聚类结束条件为最小距离大于50像素点（可设置）。
9. 对于每个聚类计算票数加权重心，作为新的待选点。票数为聚类中所有待选点的票数之和。
10. 选择票数最高的聚类，作为第一个输出点，并将所有中点待选点连线与自身夹角小与10度的线段剔除。再跳转第6步。
11. 若没有剩下的线段，或已找到三个消失点，或没有待选点。则结束算法。

## 部分效果展示
13份测试数据在data文件夹中，输出结果在data/result/中
部分输出结果如下
不同颜色标记的线段表示其属于某个颜色的消失点，部分消失点在图片外没有显示，以文本方式输出于data/result中
<div align='center'\>
　　<img src='https://github.com/SymenYang/Vanish-Point-Detect/blob/master/data/result/1_final.jpg' />
</div>
<div align='center'\>
　　<img src='https://github.com/SymenYang/Vanish-Point-Detect/blob/master/data/result/9_final.jpg'  />
</div>
<div align='center'\>
　　<img src='https://github.com/SymenYang/Vanish-Point-Detect/blob/master/data/result/8_final.jpg'  />
</div>

--------
## Project introduction
Vanish point detect is an important step of some plane/road detection algorithm.When a 3D object project into 2D space(such as been drawn), the lines which are parallel in 3D may not be parallel in 2D space,and they may intersect in one point which is the vanish point. This project realized an algorithm which can detect vanish points from single image.

## Algorithm introduction
This algorithm first caculate some candidate points, and then each line votes for the points. This project also solved some corner work. As follow is the full algorithm:
1. Use bilateral filters for noise reducion.
2. Use Canny edge-detection algorithm to detect edges.
3. Use Probabilistic Hough Transform to detect line's segments.
4. Extend the segments as long as we can and get the final line segments.
5. Merge close segments into one segment(use Hierarchical clustering).
6. Sort all segments by slope and get candidate points by caculate the intersect point of lines which are close in slope.
7. Each line votes for each candidate point. Votes value is | l | * e ^ (theta / (2 * u ^ 2)),where l is line segment's length;$theta$ is the angle of line segment and line through line segment's midpoint and candidate point;;u is a parameter which is set to 0.1.
8. Get clusters from candidate points use Hierarchical clustering algorithm.The end condition is the min_distance is bigger than 50px.
9. Get the gravity center for each cluster, and use the gravity center as a new candidate point whose value is the sum of this cluster's value.
10. Choose the most voted point as the first vanish point, and remove line segments that belong to this vanish point. Jump to step 6.
11. If there is no line segments, or no candidate points, or algorithm already found three vanish point: halt and output.

## testdata & result
Test data is under 'data/'. The result for each image is under 'data/result/'.
