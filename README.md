# Social Media API

A Django-based GraphQL API for a social media platform with user authentication, posts, comments, and interactions (likes/shares).

## Features

- **User Management**: Registration, authentication with email/username
- **Posts**: Create and manage social media posts
- **Comments**: Add comments to posts
- **Interactions**: Like and share posts
- **GraphQL API**: Modern API with relay-style pagination
- **JWT Authentication**: Secure token-based authentication
- **Admin Interface**: Django admin for content management

## Tech Stack

- **Backend**: Django 5.1
- **API**: GraphQL (Graphene-Django)
- **Authentication**: JWT with HTTP-only cookies
- **Database**: SQLite (development)
- **Admin**: Django Admin Interface

## Project Structure

```
social_media_api/
├── users/                 # User management app
│   ├── models.py         # Custom user model
│   ├── schema.py         # GraphQL schema for users
│   ├── backends.py       # Email/username authentication
│   └── admin.py          # User admin configuration
├── posts/                # Posts management app
│   ├── models.py         # Post, Comment, Interaction models
│   ├── schema.py         # GraphQL schema for posts
│   └── admin.py          # Posts admin configuration
└── social_media_api/     # Main project settings
    ├── settings.py       # Django settings
    ├── urls.py          # URL configuration
    └── schema.py        # Main GraphQL schema
```

## Models

### User Model
- UUID primary key
- Email and username authentication
- Profile fields: full_name, bio, profile_image, date_of_birth
- Custom user manager for email/username login

### Post Model
- UUID primary key
- Author (ForeignKey to User)
- Content (TextField)
- Timestamps (created_at, updated_at)
- Denormalized counters (likes_count, comments_count, shares_count)

### Comment Model
- UUID primary key
- Post and Author references
- Content and timestamp

### Interaction Model
- Like and Share interactions
- Unique constraint to prevent duplicate interactions
- UUID primary key

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd social_media_api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install django
pip install graphene-django
pip install django-graphql-jwt
pip install django-filter
pip install Pillow  # For image handling
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

## API Endpoints

- **GraphQL Playground**: `http://localhost:8000/graphql/`
- **Django Admin**: `http://localhost:8000/admin/`

## GraphQL Operations

### Authentication

#### Register User
```graphql
mutation {
  registerUser(email: "user@example.com", username: "username", password: "password123") {
    user {
      id
      email
      username
    }
  }
}
```

#### Login
```graphql
mutation {
  loginUser(email: "user@example.com", password: "password123") {
    success
    token
    user {
      id
      username
      email
    }
  }
}
```

#### Get Current User
```graphql
query {
  me {
    id
    username
    email
    fullName
    bio
  }
}
```

### Posts

#### Create Post
```graphql
mutation {
  createPost(content: "This is my first post!") {
    post {
      id
      content
      author {
        username
      }
      createdAt
      likesCount
      commentsCount
    }
  }
}
```

#### Get Posts
```graphql
query {
  posts(first: 10) {
    edges {
      node {
        id
        content
        author {
          username
        }
        createdAt
        likesCount
        commentsCount
        sharesCount
      }
    }
  }
}
```

#### Add Comment
```graphql
mutation {
  addComment(postId: "UG9zdE5vZGU6...", content: "Great post!") {
    comment {
      id
      content
      author {
        username
      }
      createdAt
    }
  }
}
```

#### Like/Share Post
```graphql
mutation {
  interactWithPost(postId: "UG9zdE5vZGU6...", type: "like") {
    interaction {
      id
      type
      user {
        username
      }
      createdAt
    }
  }
}
```

### Queries with Filters

#### Filter Posts by Content
```graphql
query {
  posts(content_Icontains: "django") {
    edges {
      node {
        id
        content
        author {
          username
        }
      }
    }
  }
}
```

#### Get Comments for a Post
```graphql
query {
  comments(post_Id: "POST_UUID_HERE") {
    edges {
      node {
        id
        content
        author {
          username
        }
        createdAt
      }
    }
  }
}
```

## Authentication Headers

For authenticated requests, include the JWT token in headers:

```
Authorization: JWT <your-token-here>
```

Or use HTTP-only cookies (configured in settings).

## Configuration

### JWT Settings (settings.py)
```python
GRAPHQL_JWT = {
    'JWT_EXPIRATION_DELTA': timedelta(minutes=30),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_COOKIE_SECURE': False,  # Set to True in production
    'JWT_COOKIE_HTTP_ONLY': False,
    'JWT_ALLOW_ARGUMENT': True,
}
```

### Database
Currently configured for SQLite. For production, update `DATABASES` setting in `settings.py`.

## Development Features

- **Debug Mode**: Enabled by default
- **GraphiQL Interface**: Interactive GraphQL explorer
- **Admin Interface**: Full CRUD operations for all models
- **Logging**: Configured for development debugging

## Production Considerations

1. **Security Settings**:
   - Set `DEBUG = False`
   - Update `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Set `JWT_COOKIE_SECURE = True`

2. **Database**: 
   - Switch to PostgreSQL or MySQL
   - Configure database credentials

3. **Media Files**:
   - Configure proper media file handling
   - Set up cloud storage for profile images

4. **CORS**:
   - Add django-cors-headers for frontend integration

## API Features

- **Relay-style Pagination**: Efficient cursor-based pagination
- **Node Interface**: Global object identification
- **Optimized Queries**: Prefetch related data to avoid N+1 queries
- **Input Validation**: Proper error handling and validation
- **Denormalized Counters**: Fast access to like/comment counts

