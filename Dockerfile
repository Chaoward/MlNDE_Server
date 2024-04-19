FROM python:3.9

WORKDIR /app

#additional depencencies for opencv
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev

COPY requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt

# # # Copy the flask_env directory and any other necessary directories
# # COPY ./flask_env /app/flask_env
# # COPY ./demo_script /app/demo_script
# # COPY ./old /app/old
# # COPY .gitignore /app/.gitignore

# Copy all of the application code into the container at /app
COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the app when the container launches
# CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
CMD ["python", "app.py"]