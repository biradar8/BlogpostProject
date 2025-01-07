# Blogpost Project

## Overview

**Blogpost Project** is a FastAPI-based application that allows users to manage blog posts with JWT token authentication. It provides the ability to create, list, update and delete blog posts. JWT authentication ensures that only authenticated users can perform certain actions such as creating, modifying and deleting blog posts.

## Features

- **JWT Authentication**: Secure user login using JWT tokens.
- **Create Blog Posts**: Authenticated users can create blog posts.
- **List Blog Posts**: View all the blog posts created by users.
- **FastAPI**: Fast and modern web framework for building APIs.
- **Pydantic**: Data validation and settings management.

## Requirements

- Python 3.8+
- FastAPI
- Pydantic
- Uvicorn
- SQLAlchemy
- JWT (JSON Web Token) authentication
- SQLite, PostgreSQL, (Based on your choice, set in .env file)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/biradar8/BlogpostProject.git
   cd BlogpostProject
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv

   venv\Scripts\activate  # On Linux source venv/bin/activate
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r blogpost\requirements.txt
   ```

4. **Set up the database**:
   - Ensure that you have the necessary database set up (SQLite, PostgreSQL, etc.)
   - Adjust the database URL in the `blogpost/.env` file to define the database connection.

5. **Run the application**:

   ```bash
   uvicorn blogpost.main:app --reload
   ```

   This will run the FastAPI application with hot-reloading enabled.

## Project Structure

```
BlogpostProject/
│
├── blogpost/
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py        # Database models
│   │   ├── router.py        # FastAPI endpoints for handling User related API requests
│   │   ├── schemas.py       # Pydantic schemas for request/response validation
│   │   └── utils.py         # Utility file for storing JWT logic
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── db.py            # Database configuration
│   │   ├── log.py           # Logging configuration for project
│   │   └── settings.py      # Settings configuration for storing and accessing sensitive information with .env file
│   │
│   ├── posts/
│   │   ├── __init__.py
│   │   ├── models.py        # Database models
│   │   ├── router.py        # FastAPI endpoints for handling Blog related API requests
│   │   └── schemas.py       # Pydantic schemas for request/response validation
│   │
│   ├── .env                 # Environment file storing sensitive information(ignored by git)
│   ├── .env.example         # Environment file example storing sensitive information keywords used
│   ├── api.log              # Log file for storing all the logs in file(ignored by git)
│   ├── main.py              # FastAPI app instance and routers inclusion
│   └── requirements.txt     # List of Python dependencies
│
├── .gitignore               # File specifying list of files to be ignored while tracking code change
├── LICENSE                  # License for use of source code
└── README.md                # This file
```

## API Endpoints

### 1. **User Registration**

#### POST `/auth/register/`

- **Description**: Registers a new user. Passwords will be hashed before storing them.
- **Request Body**: 
    ```json
    {
        "full_name": "string",
        "email": "user@example.com",
        "username": "string",
        "password": "string"
    }
    ```

- **Response**:
    ```json
    {
        "id": 0,
        "full_name": "string",
        "email": "user@example.com",
        "username": "string",
        "is_active": true,
        "created_at": "2025-01-04T12:38:52.423Z"
    }
    ```

---

### 2. **User Login**

#### POST `/auth/login/`

- **Description**: Authenticates the user and returns a JWT token.
- **Request Body**:
    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```

- **Response**:
    ```json
    {
        "access_token": "jwt_token",
        "token_type": "Bearer"
    }
    ```

---

### 3. **Create Blog Post**

#### POST `/blog/`

- **Description**: Create a new blog post (authentication required).
- **Request Body**:
    ```json
    {
        "title": "Blog Post Title",
        "body": "This is the content of the blog post"
    }
    ```

- **Headers**: 
    - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
    ```json
    {
        "id": 0,
        "title": "string",
        "body": "string",
        "author": {
            "full_name": "string"
        },
        "created_at": "2025-01-04T12:44:50.504Z"
    }
    ```

---

### 4. **List All Blog Posts**

#### GET `/blog/`

- **Description**: Get a list of all blog posts.
- **Response**:
    ```json
    [
        {
            "id": 1,
            "title": "Blog Post Title",
            "body": "This is the content of the blog post",
            "created_at": "2025-01-01T12:00:00"
        },
        {
            "id": 2,
            "title": "Another Blog Post",
            "body": "This is another blog post content",
            "created_at": "2025-01-02T14:00:00"
        }
    ]
    ```

---

### 5. **Get a Single Blog Post**

#### GET `/blog/{blog_id}/`

- **Description**: Get details of a single blog post by ID.
- **Response**:
    ```json
    {
        "id": 1,
        "title": "Blog Post Title",
        "body": "This is the content of the blog post",
        "author_id": {
            "full_name": "string"
        },
        "created_at": "2025-01-01T12:00:00"
    }
    ```

---

### 6. **Update Blog Post**

#### PATCH `/blog/{blog_id}/`

- **Description**: Update an existing blog post (authentication required, and the post must be owned by the user).

- **Request Body**:
    ```json
    {
        "title": "Updated Title",
        "body": "Updated content of the blog post"
    }
    ```

- **Headers**: 
    - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
    ```json
    {
        "id": 1,
        "title": "Blog Post Title",
        "body": "This is the content of the blog post",
        "author_id": {
            "full_name": "string"
        },
        "created_at": "2025-01-01T12:00:00",
        "updated_at": "2025-01-04T12:53:46.448Z"
    }
    ```
---

### 7. **Delete Blog Post**

#### DELETE `/blog/{blog_id}/`

- **Description**: Delete a blog post (authentication required, and the post must be owned by the user).

- **Headers**: 
    - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:

    - `204 No Content`
---

## Authentication & JWT Token

- To authenticate, send the JWT token in the `Authorization` header as a Bearer token.
- Example:
    ```
    Authorization: Bearer <your_jwt_token>
    ```

## JWT Token Generation

- **POST /auth/login/** generates a JWT token when the user successfully logs in.
- The token should be included in the Authorization header for protected routes.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
