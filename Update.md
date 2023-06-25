=============== torch目录结构官方说明
# https://github.com/pytorch/pytorch/blob/v1.13.1/CONTRIBUTING.md#codebase-structure
+ torch: 我们平常使用的python接口和相关函数
+ torch/csrc: 使用pybind11绑定python接口和c++接口，而绑定的代码并不是手动一个一个写的，而是通过函数自动生成的，这里就需要结合tools目录下的脚本来实现，比较重要的有这几个：`tools\autograd\templates\python_torch_functions.cpp, ./torch/csrc/autograd/python_torch_functions_manual.cpp， ./tools/autograd/templates/python_variable_methods.cpp， ./tools/autograd/templates/python_nn_functions.cpp`
 - jit：对应TorchScript，是pytorch提供的静态图实现方式
 - autograd: 自动求导相关功能，用于模型训练时loss的反向求导
 - api: C++提供的接口
 - distributed: 分布式训练
+ aten/src/ATen: A Tesor Library, C++实现的张量计算库，我们在torch前端用到的很多计算函数或者说算子，其实绝大部分在底层都是用aten实现的。
+ tools: 代码自动生成的相关脚本，包括生成pybind11绑定代码、*.pyi存根文件编译.so动态库和编译libtorch.so等
  - autograd: 
  - jit
  - setup_helpers
  - build_pytorch_libs.py
  - build_libtorch.py
+ test: 测试代码
+ caffe2: Caffe2工具库的相关代码
+ c10: torch完整的集成了caffe框架的后端，用于实现基本的Tensor操作，在ATen中会看到大量使用了C10中的功能。
