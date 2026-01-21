FROM debian:13.3-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    npm python3 python3-pip graphviz \
    && rm -rf /var/lib/apt/lists/*

# Install LikeC4 CLI
RUN npm install -g likec4

RUN pip3 install --break-system-packages mkdocs mkdocs-material mkdocs-doubleslash-theme

# Copy plugin source and install
COPY . /tmp/mkdocs-likec4/
RUN pip3 install --break-system-packages /tmp/mkdocs-likec4/ && rm -rf /tmp/mkdocs-likec4

WORKDIR /docs
EXPOSE 8000
CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000", "--livereload"]
