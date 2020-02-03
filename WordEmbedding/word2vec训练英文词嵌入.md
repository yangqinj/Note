# word2vec训练英文词嵌入

## word2vec训练英文词向量
### 编译源码
下载好源码，解压之后，会看到目录下有一个src文件夹，源码就在这个文件夹中。进入这个文件夹，可以看到有一个makefile文件。在当前目录执行make命令进行编译。
  > $ make

然后在./bin文件夹中就会得到编译好的程序：
  ![编译好的程序](/Users/yangqj/Documents/Documents/知识就是力量/Note/WordEmbedding/32448330-97e6bdd2-c349-11e7-8bc3-016c2f95f869.png)

这里有很多个程序，但是我们暂时只关注基本的，即word2vec和distance。其中，word2vec是训练词向量的程序，distance是计算某个单词与其他词向量距离的程序。

### 训练词向量
在./scripts文件夹下有一个demo-word.sh脚本：
  ``` shell
  #!/bin/bash

DATA_DIR=../data
BIN_DIR=../bin
SRC_DIR=../src

TEXT_DATA=$DATA_DIR/text8
ZIPPED_TEXT_DATA="${TEXT_DATA}.zip"
VECTOR_DATA=$DATA_DIR/text8-vector.bin # 词向量输出文件

# pushd ${SRC_DIR} && make; popd # 每次训练之前都需要编译一次程序

if [ ! -e $VECTOR_DATA ]; then

if [ ! -e $TEXT_DATA ]; then
  if [ ! -e $ZIPPED_TEXT_DATA ]; then
    wget http://mattmahoney.net/dc/text8.zip -O $ZIPPED_TEXT_DATA
fi
  unzip $ZIPPED_TEXT_DATA
mv text8 $TEXT_DATA
fi
echo -----------------------------------------------------------------------------------------------------
echo -- Training vectors...
time $BIN_DIR/word2vec -train $TEXT_DATA -output $VECTOR_DATA -cbow 0 -size 200 -window 5 -negative 0 -hs 1 -sample 1e-3 -threads 12 -binary 1

fi

echo -----------------------------------------------------------------------------------------------------
echo -- distance...

$BIN_DIR/distance $DATA_DIR/$VECTOR_DATA # 训练完成后运行distance, 计算词向量的距离
  ```

如注释所示，这个脚本在每次训练词向量之前都会重新编译一次程序。运行这个脚本，会自动下载text8.zip压缩文件。解压后可以得到text8文件，这个文件大约96M，里面是纯英文的单词。

  > $ ./scripts/demo-word.sh
  >
  > $ more ./data/text8

  ```
    anarchism originated as a term of abuse first used against early working class radicals including the diggers of the english revolution and the sans culottes of the french revolution whilst the term is still used in a pejorative way to describe any act that used violent means to destroy the organization of society it has also been taken up as a positive label by self defined anarchists the word anarchism is derived from the greek without archons ruler chief king anarchism as a political philosophy is the belief that rulers are unnecessary and should be abolished although there are differing interpretations of what this means anarchism also refers to related social movements that advocate the elimination of authoritarian institutions particularly the state the word anarchy as most anarchists use it does not imply chaos nihilism or anomie but rather a harmonious anti authoritarian society in...
  ```

脚本中time那一行对应的就是传入word2vec程序的参数。time是linux系统上的一个命令，用于统计程序运行的时间。参数的解释如下：

| 参数      | 说明                                                         |
| --------- | ------------------------------------------------------------ |
| -train    | 训练文件的路径及文件名，脚本中使用的是../data/text8          |
| -output   | 输出文件的路径及文件名，脚本中使用的是../data//text8-vector.bin |
| -cbow     | 是否使用cbow训练。1表示使用cbow, 0表示使用skip-gram。        |
| -size     | 词向量的维度。                                               |
| -window   | 上下文窗口大小                                               |
| -negative | 是否使用负采样。0表示不使用负采样，大于1时表示负样本集的大小 |
| -hs       | 是否使用hierarchical softmax， 0表示不使用，1表示使用。      |
| -sample   | 处理高频词时使用的词频阈值                                   |
| -threads  | 线程个数                                                     |
| -binary   | 是否使用二进制的形式存储输出的词向量，0表示不使用，1表示使用。 |

执行该脚本，训练完成后，可以看到训练的结果。其中，Alpha代表训练的步长，Progress代表训练的进度，Words/thread/sec代表线程运行的时间，real,user,sys给出了不同角度下程序的运行时间。另外，distance程序要求你从命令行输入一个单词，计算它跟其他词向量的距离，结果输出最近的前40个单词，并且按照从近到远排序。单词对应的数字是余弦相似度，取值在0到1之间，所以值越大代表越相似。
  ![运行结果](/Users/yangqj/Documents/Documents/知识就是力量/Note/WordEmbedding/32448966-4c656816-c34b-11e7-9b0f-0d7df37016cf.png)
  ![运行结果2](/Users/yangqj/Documents/Documents/知识就是力量/Note/WordEmbedding/32449018-7796c322-c34b-11e7-8a77-20897d640950.png)



## 实验及结果分析

为了比较两种模型和两种训练方法的不同，我一共进行了四个实验：CBOW/Skip-gram VS hierarchical softmax(hs)/negative sampling(neg)。特别的，[word2vec 中的数学原理详解](http://blog.csdn.net/itplus/article/details/37969519)中说明，neg的目的是提高训练速度并改善所得词向量的质量，实验验证这两点。实验中使用的参数设置如下表所示：

| -size | -window | -sample | -negative | -threads | -binary |
| ----- | ------- | ------- | --------- | -------- | ------- |
| 200   | 5       | 1e-3    | 5         | 12       | 1       |

### 训练时间

|           | hs        | neg       |
| --------- | --------- | --------- |
| CBOW      | 0m42.140s | 0m43.249s |
| Skip-gram | 2m11.658s | 1m47.121  |

从表中的结果，我们可以观察到：  

+ 从原理上来看，使用neg会比hs要快。在Skip-gram中，实验结果符合；但是在CBOW下，两者的训练时间却不符合。这是因为word2vec的实现不是完全按照hs和neg的方法：虽然window设置为5，但是word2vec中对于上下文的窗口大小是在1~5之间随机取的。  
+ 总体来看，CBOW的训练时间比Skip-gram少，这是因为：CBOW的目标是求 p(w|context(w)) , 即根据上下文预测当前词，而Skip-gram则是求p(context(w)|w), 即根据当前词预测上下文。因此，在训练的时候在 每个hs和neg外面多了一层对上下文的遍历。  

### 词向量质量

为了查看词向量的质量，我测试了"love"和"university"两个单词。为了方便比较，我只列出了前25个相似的词向量。

![love](/Users/yangqj/Documents/Documents/知识就是力量/Note/WordEmbedding/32449085-9d08ac42-c34b-11e7-9ee5-62d43226c684.png)
![university](/Users/yangqj/Documents/Documents/知识就是力量/Note/WordEmbedding/32449129-babda490-c34b-11e7-9c69-a3ff0d2a600b.png)

得到的相似词向量的结果显示：  

+ 对于单词"love"来说，使用neg得到的结果要比hs要好很多。使用hs得到的top5单词中，会出现"me","my"这种极不相关的单词；但是使用neg得到的top5单词，都与"love"非常相关。对于"university"来说，也是neg得到的结果比hs要好。  
+ 在使用hs训练方法条件下，"university"得到的结果要比"love"要好。由此可见，基础的word2vec模型比较适合非情感词。所以，后来又学者提出了许多引入情感信息的词向量模型。


## 总结
这篇博客讲解了使用word2vec训练英文词向量的步骤，并且分析了CBOW和Skip-gram模型在hierarchical softmax和negative sampling方法下的不同结果。实验结果验证了negative sampling确实可以达到提高训练速度和词向量质量的目的。