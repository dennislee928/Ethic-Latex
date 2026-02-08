---
paths: "**/*.py", "**/*mcp*.py"
---

# FastMCP Corrections

This project uses **fastmcp>=2.14.2** (PyPI - Python package).

## Module-Level Server Export Required

```python
# ❌ Server inside function (Cloud can't find it)
def create_server():
    mcp = FastMCP("my-server")
    return mcp

# ✅ Module-level export
mcp = FastMCP("my-server")

@mcp.tool()
def my_tool():
    pass
```

## Resource URI: Include Scheme

```python
# ❌ Missing scheme
@mcp.resource("users")
def get_users():
    pass

# ✅ Include scheme prefix
@mcp.resource("data://users")
def get_users():
    pass

@mcp.resource("user://{user_id}")
def get_user(user_id: str):
    pass
```

## Resource Params Must Match Template

```python
# ❌ Parameter name mismatch
@mcp.resource("user://{user_id}")
def get_user(id: str):  # Wrong param name!
    pass

# ✅ Names must match exactly
@mcp.resource("user://{user_id}")
def get_user(user_id: str):  # Matches template
    pass
```

## v2.13.0: Lifespan Is Per-Server-Instance

```python
# ⚠️ Breaking change in v2.13.0
# Lifespan now runs once per server instance, not per session

# ✅ Use for server-wide initialization
@mcp.lifespan
async def lifespan(context):
    db = await init_database()
    yield {"db": db}
    await db.close()
```

## FastAPI: Pass Lifespan

```python
# ❌ Database never initializes
app = FastAPI()

# ✅ Pass MCP lifespan to FastAPI
app = FastAPI(lifespan=mcp.lifespan)
```

## Production Storage Backend

```python
# ❌ Memory storage (data lost on restart)
# Default behavior

# ✅ Use persistent storage in production
from fastmcp.storage import DiskStore
from fastmcp.security import FernetEncryptionWrapper

storage = FernetEncryptionWrapper(
    DiskStore("/data/mcp"),
    key=os.getenv("ENCRYPTION_KEY")
)
```

## OAuth: Enable Consent Screen

```python
# ❌ Security vulnerability (confused deputy attack)
auth = OAuthProxy(...)

# ✅ Enable consent screen
auth = OAuthProxy(
    ...,
    enable_consent_screen=True  # Required for security!
)
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Server inside function | Module-level `mcp = FastMCP()` |
| `@mcp.resource("users")` | `@mcp.resource("data://users")` |
| Mismatched param names | Match function params to URI template |
| Per-session lifespan | Per-server lifespan (v2.13.0+) |
| Missing FastAPI lifespan | `FastAPI(lifespan=mcp.lifespan)` |
| Memory storage in prod | DiskStore or RedisStore |
| No consent screen | `enable_consent_screen=True` |
