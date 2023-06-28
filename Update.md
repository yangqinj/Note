
# torch\csrc\jit\python\script_init.cpp
void initJitScriptBindings(PyObject* module):
    py::class_<Module, Object>(m, "ScriptModule")
          .def(
          "_create_method_from_trace",
            ......
            std::shared_ptr<Graph> graph =
                std::get<0>(tracer::createGraphByTracing(
                    func,
                    typed_inputs,
                    var_name_lookup_fn,
                    strict,
                    force_outplace,
                    &self,
                    argument_names));
            ......
          )


-> 

# torch\csrc\jit\python\python_tracer.cpp
std::pair<std::shared_ptr<Graph>, Stack> createGraphByTracing(
    const py::function& func,
    Stack trace_inputs,
    const py::function& var_name_lookup_fn,
    bool strict,
    bool force_outplace,
    Module* self,
    const std::vector<std::string>& argument_names)


-> 

# torch\csrc\jit\frontend\tracer.cpp
std::pair<std::shared_ptr<TracingState>, Stack> trace(
    Stack inputs,
    const std::function<Stack(Stack)>& traced_fn,
    std::function<std::string(const Variable&)> var_name_lookup_fn,
    bool strict,
    bool force_outplace,
    Module* self,
    const std::vector<std::string>& argument_names)



TracingState

# 映射输入
IValue -> Value: addInput()

# 运行模型获取输出
auto out_stack = traced_fn(inputs);

# 出栈获取节点
size_t i = 0;
    for (auto& output : out_stack) {
      // NB: The stack is in "reverse" order, so when we pass the diagnostic
      // number we need to flip it based on size.
      state->graph->registerOutput(
          state->getOutput(output, out_stack.size() - i));
      i++;
    }

# inline pass优化
Inline(*graph);

# 
# NormalizeOps(graph);

--------------
# torch\csrc\jit\passes\inliner.cpp
Inline -> void inlineCalls(Block* block)  -> inlineCallTo


# torch\csrc\jit\ir\ir.cpp
inlineCallTo -> inlineCallStackOfNode 


# normalize_ops
NormalizeOps(graph)
