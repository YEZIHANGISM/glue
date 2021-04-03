## 参数转换中间件

将使用驼峰命名的参数转换为蛇形命名
> 该中间件是非必要模块，如果在使用后希望弃用，需要修改参数的命名方式，请谨慎选择

### 加入该中间件

```python
# settings.py
MIDDLEWARE = [
    ...,
    'glue.middleware.ArgumentNamingRuleMiddleware'
]
```

### 请求方法与其支持的参数传递方式
|               | GET | POST | PUT | DELETE |
| :------------ | :-: | :-: | :-: | :-: |
| request.GET   |  Y  |  Y  |  Y  |  Y  |
| request.POST  |  N  |  Y  |  N  |  N  |
| request.body  |  Y  |  Y  |  Y  |  Y  |
| request.FILES |  N  |  Y  |  N  |  N  |

### 支持的参数格式
| type | support | example |
| :--- | :-----: | :-----: |
| string | Y | 'stringTest' |
| integer | Y | 12 |
| float | Y | 12.2 |
| list[any] | Y | [1, 'b', 3.9, [...], {...}] |
| dict{any} | Y | {'a': 1, 'b': '2', 'c': 3.0} |
| json | Y | '[{\"ll1T\": 1}, {\"ll2T\": \"2323\"}]' |

> 不鼓励非常复杂的入参，如果存在，考虑是否是业务逻辑理解有误。

### 修改JSON类型的内嵌参数
参数转换原则上秉承最小惊讶原则——只改变参数的命名方式，不对参数类型做改动。
对于复杂结构的入参，例如列表嵌套字典的结构，通常使用`json`传递，在序列化时使用`serializer.CharField`接收。
可以指定中间件是否修改内嵌JSON参数的类型

```python
# settings.py
MICRO_PARAM_LOADS = True
```

如此，在序列化层就可以依据该参数原本的类型使用相应的序列化器。上面的例子就可以直接使用
```python
class NestedSerializer:
    nest = serializer.ListField(child=serializers.DictField()
```

或者内嵌序列化类
```python
class NestedChildSerializer:
    ...
class NestedSerializer:
    nest = NestedChildSerializer(many=True)
```