# official uv docs 
FROM ghcr.io/astral-sh/uv:debian-slim    

# Setting working directory 
WORKDIR /app

# this part to optimize performance
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# it controls where venv lives
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

# cache layering first copy and install dependencies. Not project neither dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# copy the rest of the code and install it
COPY . .
RUN uv sync --frozen --no-dev

# Adding the virtual environment to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Exposing the port
EXPOSE 8000

# Default command to start the FastAPI server
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]