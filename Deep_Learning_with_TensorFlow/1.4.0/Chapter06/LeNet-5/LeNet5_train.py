import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import LeNet5_infernece
import os
import numpy as np

# #### 1. 定义神经网络相关的参数

BATCH_SIZE = 100  # 批处理数量大小
LEARNING_RATE_BASE = 0.01  # 基础学习率
LEARNING_RATE_DECAY = 0.99  # 学习率衰减速率
REGULARIZATION_RATE = 0.0001  # 正则化参数
TRAINING_STEPS = 6000  # 训练周期数
MOVING_AVERAGE_DECAY = 0.99  # 平均滑动步长


# #### 2. 定义训练过程

def train(mnist):
    # 定义输出为4维矩阵的placeholder
    x = tf.placeholder(tf.float32, [
        BATCH_SIZE,
        LeNet5_infernece.IMAGE_SIZE,
        LeNet5_infernece.IMAGE_SIZE,
        LeNet5_infernece.NUM_CHANNELS],
                       name='x-input')
    # y_表示正确的标签
    y_ = tf.placeholder(tf.float32, [None, LeNet5_infernece.OUTPUT_NODE], name='y-input')

    # 定义L2正则化
    regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)
    y = LeNet5_infernece.inference(x, False, regularizer)  # 表示不使用dropout,但是使用正则化
    global_step = tf.Variable(0, trainable=False)

    # 定义损失函数、学习率、滑动平均操作以及训练过程。
    variable_averages = tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY, global_step)
    # 使用平均滑动模型
    variables_averages_op = variable_averages.apply(tf.trainable_variables())
    # 定义交叉熵函数
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=y, labels=tf.argmax(y_, 1))
    cross_entropy_mean = tf.reduce_mean(cross_entropy)
    # 将权重的L2正则化部分加到损失函数定义中
    loss = cross_entropy_mean + tf.add_n(tf.get_collection('losses'))
    # 定义递减的学习率
    learning_rate = tf.train.exponential_decay(
        LEARNING_RATE_BASE,
        global_step,
        mnist.train.num_examples/BATCH_SIZE, LEARNING_RATE_DECAY,
        staircase=True)

    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss, global_step=global_step)
    # with tf.control_dependencies([train_step, variables_averages_op]):
    #     train_op = tf.no_op(name='train')
    # 在反向传播梯度下降的过程中更新变量的滑动平均值
    train_op = tf.group(train_step, variables_averages_op)
    # 初始化TensorFlow持久化类。
    saver = tf.train.Saver()
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        for i in range(TRAINING_STEPS):
            xs, ys = mnist.train.next_batch(BATCH_SIZE)

            reshaped_xs = np.reshape(xs, (
                BATCH_SIZE,
                LeNet5_infernece.IMAGE_SIZE,
                LeNet5_infernece.IMAGE_SIZE,
                LeNet5_infernece.NUM_CHANNELS))
            _, loss_value, step = sess.run([train_op, loss, global_step], feed_dict={x: reshaped_xs, y_: ys})

            if i%1000 == 0:
                print("After %d training step(s), loss on training batch is %g."%(step, loss_value))


# #### 3. 主程序入口

def main(argv=None):
    mnist = input_data.read_data_sets("../../../datasets/MNIST_data", one_hot=True)
    train(mnist)


if __name__ == '__main__':
    main()
