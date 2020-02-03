# word2vec原理和代码细节

## word2vec基本原理
关于word2vec的基本原理，我认为看这篇博客就可以了[word2vec 中的数学原理详解](http://blog.csdn.net/itplus/article/details/37969519)，作者在里面详细介绍了跟词向量和word2vec的基础知识。

## word2vec源码
word2vec的源码原本是可以在[http://word2vec.googlecode.com/svn/trunk/](http://word2vec.googlecode.com/svn/trunk/)下载的，但是由于种种原因，现在不仅上不去网站，而且源码也不在这个网址里了。不过幸好我们可以在github找到，有以下两个资源。我下载的是第一个（下文的实验都假设从github上下载）。  
  - C源码: [https://github.com/dav/word2vec](https://github.com/dav/word2vec)  
  - python接口: [https://github.com/dani
    lfrg/word2vec](https://github.com/danielfrg/word2vec)

关于word2vec的源码解析，网上也有非常多的资料。上面提及的[word2vec 中的数学原理详解](http://blog.csdn.net/itplus/article/details/37969519) 中作者在最后一章就讲解了[若干源码细节](http://blog.csdn.net/itplus/article/details/37999613)。另外，[这里博客](http://blog.csdn.net/lingerlanlan/article/details/38232755)的作者直接在源码上做了中文注解。

## 代码

### 词汇表

**代码中定义了结构体`vocab_word`来存储每一个词的相关信息。**

```C++
struct vocab_word {
  long long cn; // 词对应的下标
  int *point; // 
  char *word, // 词语
       *code, // 词对应的huffman编码
       codelen; // 词对应的huffman编码的长度
};
```

**代码中采用哈希表的方式存储词汇**。代码中使用一个大小为3^e7的哈希表`vocab_hash`，并且初始化每一个元素为-1.
```C++
const int vocab_hash_size = 30000000;
int *vocab_hash = (int *)calloc(vocab_hash_size, sizeof(int));
for (a = 0; a < vocab_hash_size; a++) vocab_hash[a] = -1;
```

哈希表的映射关系为：$$vocab\_hash[hash]=word\_index$$
哈希值的计算公式为$$hash = \sum_i(hash * 257 + int(word[i])) % vocab_hash_size$$
当出现冲突的时候，则采用线性探测方法解决。
```C++
hash = GetWordHash(word);
while (vocab_hash[hash] != -1) hash = (hash + 1) % vocab_hash_size;
vocab_hash[hash] = vocab_size - 1;
```

**当词语的个数达到阈值时，会删除掉频次低于最小阈值的词语**。
```C++
if (vocab_size > vocab_hash_size * 0.7) ReduceVocab();
```

最小阈值初始设置为1，当进行了一次删除词语操作之后最低阈值会加一。这个操作时很合理的，因为进行了一次删除操作后，剩下的词语的频次都是大于最低阈值的，如果不提高阈值，那么将会有越来越多满足条件的词语，之后的每次删除操作可以删除的词语就越来越少。

### $\sigma(x)$的近似计算

$\sigma(x)$中包含了$e^x$指数计算，会花费大量的计算时间，所以代码中采用了查表的方式提高效率。观察sigmoid函数可以发现，在$(-\infty, -6]$和$[6, \infty)$区间sigmoid函数变化不大，前者趋向于0，后者趋向于1，因此代码中计算了在$[-6,6]$之间的函数值，并且将区间划分为1000份计算。

```C++
#define EXP_TABLE_SIZE 1000
#define MAX_EXP 6

expTable = (real *)malloc((EXP_TABLE_SIZE + 1) * sizeof(real));
  if (expTable == NULL) {
    fprintf(stderr, "out of memory\n");
    exit(1);
  }
  for (i = 0; i <= EXP_TABLE_SIZE; i++) {
    expTable[i] = exp((i / (real)EXP_TABLE_SIZE * 2 - 1) * MAX_EXP); // 计算-6到6区间的exp()值
    expTable[i] = expTable[i] / (expTable[i] + 1); // 计算sigmoid函数，1/(1 + e^-x) = (e^x)/(1+e^x)
  }
```

### 多线程

为了加快训练速度，代码采用了多线程的方式训练。

```C++
void TrainModel() {
    pthread_t *pt = (pthread_t *)malloc(num_threads * sizeof(pthread_t));
    for (a = 0; a < num_threads; a++) pthread_create(&pt[a], NULL, TrainModelThread, (void *)a);
    for (a = 0; a < num_threads; a++) pthread_join(pt[a], NULL);
}
```

TrainModelThread负责单个线程的训练。对于每一个线程，先根据线程id获取到对应的起始位置，当完成了`目标`数量的词语后就停止训练。
```C++
// 寻找到对应的起始位置
fseek(fi, file_size / (long long)num_threads * (long long)id, SEEK_SET);
```

`file_size`为训练语料文件大小，通过`ftell`函数获得
```C++
file_size = ftell(fin);
```

当读取到文件末尾，或者训练词语数量达到目标后则停止。
```C++
// 到达文件末尾
if (feof(fi)) break;
// 达到目标数量。train_words为总的词语个数，在第一次遍历文件获取词汇表的时候统计得到
if (word_count > train_words / num_threads) break;
```

### CBOW+hs

```C++
// in -> hidden
  for (a = b; a < window * 2 + 1 - b; a++) if (a != window) {
    // ...
    // X_w: 上下文词语的词嵌入和
    for (c = 0; c < layer1_size; c++) {
        neu1[c] += syn0[c + last_word * layer1_size];
  }

// hs
if (hs) for (d = 0; d < vocab[word].codelen; d++) {
    f = 0;
    l2 = vocab[word].point[d] * layer1_size;
    // Propagate hidden -> output
    // neu1: X_w
    // syn1: theta_{j-1}^w
    // X_w^T * theta_{j-1}^w
    for (c = 0; c < layer1_size; c++) f += neu1[c] * syn1[c + l2];
    if (f <= -MAX_EXP) continue;
    else if (f >= MAX_EXP) continue;
    // q = \sigma (X_w^T * \theta_{j-1}^w)
    else f = expTable[(int)((f + MAX_EXP) * (EXP_TABLE_SIZE / MAX_EXP / 2))];
    // 'g' is the gradient multiplied by the learning rate
    // g = \eta * (1- d_j^w - q)
    g = (1 - vocab[word].code[d] - f) * alpha;
    // Propagate errors output -> hidden
    // e = e + g * \theta_{j-1}^w
    for (c = 0; c < layer1_size; c++) neu1e[c] += g * syn1[c + l2];
    // Learn weights hidden -> output
    // \theta_{j-1}^w = \theta_{j-1}^w + g * X_w
    for (c = 0; c < layer1_size; c++) syn1[c + l2] += g * neu1[c];
  }

// hidden -> in
  for (a = b; a < window * 2 + 1 - b; a++) if (a != window) {
    // ...
    // v(nu) = v(nu) + e
    for (c = 0; c < layer1_size; c++) syn0[c + last_word * layer1_size] += neu1e[c];
  }
```
