# Foodgram 

The Foodgram project is implemented to share recipes.
Authorized users can publish their recipes, subscribe to the authors they like,
add recipes to favorites, make a shopping list and download it to themselves in txt format.


## Description of Workflow
### Workflow consists of four steps:
#### tests
- Checking the code for compliance with PEP8.
#### push Docker image to DockerHub
- Building and publishing the image on DockerHub.
#### deploy 
- Automatic deployment to the production server when pushing to the main branch.
#### send_massage
- Sending a notification to a telegram chat.

## Preparation and project launch

## To work with a remote server (on ubuntu):
* Log in to your remote server

* Install docker:
```
sudo apt install docker.io 
```
* Install docker-compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
* Edit the infra/nginx/nginx.conf file locally and enter your IP in the server_name line
* Copy the docker-compose.yml and nginx.conf files from the infra directory to the server:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx/nginx.conf <username>@<host>:/home/<username>/nginx/nginx.conf
```

* Create an .env file and write the following:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<postgres database name>
    POSTGRES_USER=<database user>
    POSTGRES_PASSWORD=<password>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<django project secret key>
    ```
* To work with Workflow, add environment variables to Secrets GitHub:
    ```
    DOCKER_PASSWORD=<DockerHub password>
    DOCKER_USERNAME=<username>
    
    SECRET_KEY=<django project secret key>

    USER=<username to connect to the server>
    HOST=<server IP>
    PASSPHRASE=<password for the server, if set>
    SSH_KEY=<your SSH key (to get: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<chat ID where the message will be sent>
    TELEGRAM_TOKEN=<your bot token>
    ```
  
* Build docker-compose on the server:
```
sudo docker-compose up -d --build
```
* After a successful build, run the commands (only after the first deployment):
    - Collect static files:
    ```
    sudo docker-compose exec backend python manage.py collectstatic --noinput
    ```
    - Apply migrations:
    ```
    sudo docker-compose exec backend python manage.py migrate --noinput
    ```
    - Upload the ingredients to the database:  
    ```
    sudo docker-compose exec backend python manage.py loaddata data/ingredients.json
    ```
    - Create superuser:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
    - The project will be available by your IP


#### Author
Karapetyan Zorik   
Russian Federation, St. Petersburg, Kupchino.