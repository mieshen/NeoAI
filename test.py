import ast
def estimate_timeout(code):
    """
    根据代码复杂度动态计算超时时间，优化简单语句和重复语句的权重
    """
    try:
        # 解析代码为 AST（抽象语法树）
        tree = ast.parse(code)
        
        # 基础时间和权重
        base_timeout = 5  # 基础超时时间
        statement_weight = 0.5  # 默认语句权重
        simple_call_weight = 0.1  # 简单函数调用权重
        loop_weight = 2  # 循环结构权重
        total_complexity = base_timeout

        # 定义常见简单函数集合
        simple_functions = {"print", "len", "input", "range", "str", "int", "float", "bool", "list", "dict", "set", "tuple"}

        # 遍历 AST，计算复杂度
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                total_complexity += loop_weight
            elif isinstance(node, (ast.If, ast.FunctionDef)):
                total_complexity += statement_weight
            elif isinstance(node, ast.Call):
                # 如果是简单的调用（如 print），降低权重
                if isinstance(node.func, ast.Name) and node.func.id in simple_functions:
                    total_complexity += simple_call_weight
                else:
                    total_complexity += statement_weight
            elif isinstance(node, ast.Assign):
                total_complexity += statement_weight
        
        # 返回计算的超时时间，确保至少为 5 秒
        return max(5, total_complexity)
    except Exception as e:
        # 如果代码解析失败，返回默认超时时间
        return 10



code  = """
def test():
    for i in range(100):
        print(i)
    return 0
test()


"""
print(estimate_timeout(code))
