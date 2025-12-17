# Python Client

## ERHLocalClient

Use `ERHLocalClient` for in-process simulations.

```python
from erh.client import ERHLocalClient
client = ERHLocalClient()
```

## ERHRemoteClient

Use `ERHRemoteClient` to connect to a running API.

```python
from erh.client import ERHRemoteClient
client = ERHRemoteClient("http://localhost:8000")
```
