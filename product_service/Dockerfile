# ── Stage: Production Image ────────────────────────────────────────
# We use python:3.11-slim to keep the image small (~150MB vs ~900MB
# for the full image). "slim" removes build tools we don't need.
FROM python:3.11-slim

# Set the working directory *inside* the container.
# All subsequent commands run relative to this path.
WORKDIR /app

# Copy requirements first (Docker caching optimization).
# If requirements.txt hasn't changed, Docker skips the pip install
# step on rebuilds — saving minutes of build time.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code.
COPY . .

# Document which port this container listens on.
# (This is informational — you still need -p to publish it.)
EXPOSE 5001

# The command that runs when the container starts.
CMD ["python", "app.py"]
