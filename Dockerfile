FROM python:3.12

WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "-m", "src.main"]
