# Image Processing API
***
This Project is a FastAPI application that allows users to upload images,
apply transformations, and retrieve the processed images. It handles requests 
and image processing tasks asynchronously with async supported code.


## Features
*** 
* User registration and authentication
* Image upload and retrieval
* Asynchronous request handling
* User-specified image transformations
* Pagination and search functionality for images


## Technologies Used
***
* FastAPI
* SQLAlchemy
* PostgresSQL
* Aioboto3

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/TamaraDaye/ImageProcessingService.git 
   cd  ImageProcessingService
   ```

2. **Create a .env and export necessary variables with following content**
    ```bash
    REDIS_URL=redis_url_string
    DATABASE_URL=postgresql+asyncpg://$username:$password@localhost:5432/imageprocessing
    SECRET_KEY=secret_key_jwt_encoding
    ALGORITHM=HS256
    S3_BUCKET=your_s3_bucket
    ```

## Usage
***
### User Registration
POST /signup/
```json
{
    "username":"name",
    "plain_password":"your_password",
    "email": "your_email"
}
```

### JWT Token
POST /login/
```json
{
    "username": "useremail@example.com", #use email
    "password": "your_password"
}
```


