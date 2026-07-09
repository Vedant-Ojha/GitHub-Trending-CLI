# ── Stage 1: Build ──────────────────────────────────────────
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install build tools
RUN pip install --no-cache-dir build

# Copy only what's needed for the build
COPY pyproject.toml .
COPY src/ src/

# Build the wheel package
RUN python -m build --wheel --outdir dist/


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /home/appuser

# Copy the built wheel from builder stage
COPY --from=builder /app/dist/*.whl .

# Install the package
RUN pip install --no-cache-dir *.whl && rm -f *.whl

# Switch to non-root user
USER appuser

# Default entrypoint
ENTRYPOINT ["trending-repos"]

# Default arguments
CMD ["--duration", "week", "--limit", "10"]