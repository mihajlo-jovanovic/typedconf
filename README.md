# typedconf

Minimalistic configuration management for your Python application. 

## Features

- **Typed & validated**: Pydantic v2 models as your schema.
- type checking and validation (via Pydantic)
- uses Toml files to store configuration definition
- well defined order of precendence files → secrets → env vars → argv (last-wins).
- support for profiles (local, dev, prod)


