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
   ```

   ```bash
   cd BlogpostProject
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   ```

   ```bash
   venv\Scripts\activate
   ```

   In linux

   ```bash
   python3 -m venv venv
   ```

   ```bash
   source venv/bin/activate
   ```

3. **Install the dependencies**:

   ```bash
   pip install -r app\requirements.txt
   ```

   ```bash
   pipx install -r app/requirements.txt
   ```

4. **Set up the database**:

   - Ensure that you have the necessary database set up (SQLite, PostgreSQL, etc.)
   - Adjust the database URL in the `app/.env` file to define the database connection.

5. **Run the application**:

   ```bash
   uvicorn app.main:app --reload
   ```

   This will run the FastAPI application with hot-reloading enabled.

## Project Structure

```
BlogpostProject/
│
├── app/
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
│   ├── drafts/
│   │   ├── __init__.py
│   │   ├── models.py        # Database models
│   │   ├── router.py        # FastAPI endpoints for handling draft Blog related API requests
│   │   └── schemas.py       # Pydantic schemas for request/response validation
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

### **User Registration**

#### POST `/api/user/register/`

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

### **User Confirmation**

#### GET `/api/user/confirm/{token}`

- **Description**:Confirm the email. By clicking on the link you get in email.

- **Response**:
  ```
  Success
  ```

---

### **User Login**

#### POST `/api/user/login/`

- **Description**: Authenticates the user and returns pair of JWT tokens.
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
    "token_type": "Bearer",
    "access_token": "jwt_token",
    "refresh_token": "jwt_token"
  }
  ```

---

### **User Token Refresh**

#### POST `/api/user/refresh-token/`

- **Description**: refresh token for user and returns a access token.
- **Request Body**:

  ```json
  {
    "refresh_token": "string"
  }
  ```

- **Response**:
  ```json
  {
    "token_type": "Bearer",
    "access_token": "<jwt_token>"
  }
  ```

---

### **User Password forgot email**

#### GET `/api/user/password-forgot-email/`

- **Description**: endpoint to let user request for password forgot email.

- **Response**:
  ```json
  {
    "message": "Email to reset password sent"
  }
  ```

---

### **User Password reset**

#### GET `/api/user/password-reset/`

- **Description**: endpoint to let user request for password forgot email.
- **Request Body**:

  ```json
  {
    "password": "<string>",
    "reset_token": "string"
  }
  ```

- **Response**:
  ```json
  {
    "user": {
      "id": 0,
      "full_name": "string",
      "email": "user@example.com",
      "username": "string",
      "is_active": true,
      "created_at": "2025-01-04T12:38:52.423Z"
    },
    "message": "Password reset done"
  }
  ```

---

### **Create Blog Post**

#### POST `/api/blog/`

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
    "created_at": "2025-01-04T12:44:50.504Z"
  }
  ```

---

### **List All Blog Posts**

#### GET `/api/blog/`

- **Description**: Get a list of all blog posts.
- **Response**:
  ```json
  [
    {
      "title": "Blog Post Title",
      "body": "This is the content of the blog post",
      "slug": "blog-post-title",
      "created_at": "2025-01-01T12:00:00"
    },
    {
      "title": "Another Blog Post",
      "body": "This is another blog post content",
      "slug": "another-blog-post",
      "created_at": "2025-01-02T14:00:00"
    }
  ]
  ```

---

### **List All Blog Posts for Author**

#### GET `/api/blog/posts/`

- **Description**: Get a list of all blog posts posted by author.

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
  ```json
  [
    {
      "id": 1,
      "title": "Blog Post Title",
      "body": "This is the content of the blog post",
      "slug": "blog-post-title",
      "created_at": "2025-01-01T12:00:00"
    },
    {
      "id": 2,
      "title": "Another Blog Post",
      "body": "This is another blog post content",
      "slug": "another-blog-post",
      "created_at": "2025-01-02T14:00:00"
    }
  ]
  ```

---

### **Get a Single Blog Post**

#### GET `/api/blog/{blog_slug}/`

- **Description**: Get details of a single blog post by slug.
- **Response**:
  ```json
  {
    "title": "Blog Post Title",
    "body": "This is the content of the blog post",
    "author_id": {
      "full_name": "string"
    },
    "created_at": "2025-01-01T12:00:00"
  }
  ```

---

### **Update Blog Post**

#### PATCH `/api/blog/{blog_id}/`

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
    "slug": "another-blog-post",
    "created_at": "2025-01-01T12:00:00"
  }
  ```

---

### **Delete Blog Post**

#### DELETE `/api/blog/{blog_id}/`

- **Description**: Delete a blog post (authentication required, and the post must be owned by the user).

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:

  - `204 No Content`

---

### **Create Draft Blog**

#### POST `/api/draft/`

- **Description**: Create a new draft blog (authentication required).
- **Request Body**:

  ```json
  {
    "title": "Draft Blog Title",
    "body": "This is the content of the draft blog"
  }
  ```

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
  ```json
  {
    "id": 0,
    "title": "Draft Blog Title",
    "body": "This is the content of the draft blog",
    "created_at": "2025-01-04T12:44:50.504Z"
  }
  ```

---

### **List All Draft Blogs**

#### GET `/api/draft/`

- **Description**: Get list of all draft blogs owned by the user(authentication required).

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
  ```json
  [
    {
      "id": 1,
      "title": "Draft Blog Title",
      "body": "This is the content of the draft blog",
      "created_at": "2025-01-01T12:00:00"
    },
    {
      "id": 2,
      "title": "Another Draft Blog",
      "body": "This is another draft blog content",
      "created_at": "2025-01-02T14:00:00"
    }
  ]
  ```

---

### **Get a Single Draft Blog**

#### GET `/api/draft/{draft_id}`

- **Description**: Get details of a single draft blog by id(authentication required, and user must be draft blog owner).

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:
  ```json
  {
    "title": "Blog Post Title",
    "body": "This is the content of the blog post",
    "author_id": {
      "full_name": "string"
    },
    "created_at": "2025-01-01T12:00:00"
  }
  ```

---

### **Update draft Blog**

#### PATCH `/api/draft/{draft_id}`

- **Description**: Update an existing draft blog by id(authentication required, and user must be draft blog owner).

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
    "created_at": "2025-01-01T12:00:00"
  }
  ```

---

### **Delete Draft Blog Post**

#### DELETE `/api/draft/{draft_id}/`

- **Description**: Delete a draft post (authentication required, and the post must be owned by the user).

- **Headers**:

  - `Authorization: Bearer {JWT_TOKEN}`

- **Response**:

  - `204 No Content`

---

### Authentication & JWT Token

- To authenticate, send the JWT token in the `Authorization` header as a Bearer token.
- Example:
  ```
  Authorization: Bearer <your_jwt_token>
  ```

### JWT Token Generation

- **POST /auth/login/** generates a JWT token when the user successfully logs in.
- The token should be included in the Authorization header for protected routes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
