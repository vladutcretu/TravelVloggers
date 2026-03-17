# Development Notes
This document provides a more in-depth view of the application, which was designed from the beginning to support versioning.


## Table of Contents
1. [Versioning](#versioning)
    - [Version 1.0.0](#version-100)
        - Database design
        - Endpoints design
        - Wireframe design
    
2. [Tasks](#tasks)


## Versioning

### Version 1.0.0
All vlogger profiles and their videos are added manually by an administrator. There is no sign-up flow for regular users.

Administrators can: 
- Log in using email + password and access private endpoints using JWT auth.
- Manage (CRUD) vloggers profiles.
- Create vlog entries using YouTube video ID by fetching <b>YouTube Data API</b> with id=YOUTUBE_VIDEO_ID and extracts the title, thumbnail, and publish date and saves them in the database.
- Update or delete vlog entries.

Visitors can:
- View the most recently added vloggers and a single vlogger's profile, where they can filter the vlogs by the country they were filmed in.
- View the most recenlty added vlogs, a single vlog details, and filter all vlogs by the country they were filmed in.
- View all available countries so users know which locations can be used for filtering.

#### Database design
![Database design](https://i.imgur.com/xY66ELD.png)

```SQL 
Table users {
  id id [primary key]
  email email [unique, not null]
  password_hash str [not null]
  is_admin bool [not null]
  is_superuser bool [not null]
  created_at datetime [not null]
}

Table vloggers {
  id id [primary key]
  youtube_channel_id varchar(255) [unique, not null]
  youtube_channel_name varchar(255) [unique, not null]
  youtube_channel_link varchar(255) [unique, not null]
  avatar_url varchar(255) [not null]
  created_at datetime [not null]
}

Table countries {
  id id [primary key]
  name varchar(255) [not null]
  iso_code varchar(3) [not null]
}

Table vlogs {
  id id [primary key]
  vlogger_id varchar(255) [ref: > vloggers.id, not null]
  youtube_video_id varchar(255) [unique, not null]
  title varchar(255) [not null]
  thumbnail_url varchar(255) [not null]
  published_at varchar(255) [not null]
  youtube_video_link varchar(255) [not null]
  country_id varchar(255) [ref: > countries.id, not null]
  created_at datetime [not null]
}
```

### API Endpoints
<b>Authentication</b>

- `POST /api/v1/auth/register`
    - Body: 
        ```json
        { 
            "email": "string", 
            "password": "string"
        }
        ```
    - Rules: 
        - email must be unique
        - password minimum length: 6
        - if email == SUPERUSER_EMAIL from .env then set is_superuser = True
    - Response: 201 Created
        ```json
        {
            "id": int,
            "email": "EmailStr",
            "is_superuser": true if is_superuser else None
        }
        ```

- `POST /api/v1/auth/login`
    - Body: 
        ```json
        { 
            "email": "string", 
            "password": "string"
        }
        ```
    - Behavior: 
        - verify credentials
        - return JWT access token
    - Response: 200 OK
        ```json
        {
            "access_token": ...,
            "token_type": bearer
        }

<b>User Management - Private endpoints</b>

- `GET /api/v1/users`
    - Response: 200 OK
        ```json
        {
            "users": [
                {
                    "id": int,
                    "email": "EmailStr",
                    "is_admin": bool,
                    "is_superuser": bool,
                    "created_at": datetime
                },
            ]
        }

- `PATCH /api/v1/users/{user_id}` 
    - Body: 
        ```json
        { 
            "is_admin": bool
        }
        ```
    - Rules: only user.is_superuser == True can update other users
    - Response: 200 OK
        ```json
        {
            "id": int,
            "email": "EmailStr",
            "is_admin": bool,
            "is_superuser": bool,
            "created_at": datetime
        }
        ```

- `DELETE /api/v1/users/{user_id}`
    - Rules: only user.is_superuser == True can delete other users
    - Response: 204 No content

<b>Vlogger Management - Private endpoints</b>

- `POST /api/v1/vloggers`
    - Body: 
        ```json
        { 
            "youtube_channel_id": "string", 
            "youtube_channel_name": "string",
            "avatar_url": "string"
        }
        ```
    - Rules: 
        - only user.is_admin == True can create vlogger entry
        - youtube_channel_id and youtube_channel_name must be unique
    - Response: 201 Created
        ```json
        {
            "id": int,
            "youtube_channel_id": "string", 
            "youtube_channel_name": "string",
            "avatar_url": "string"
            "created_at": datetime
        }
        ```

- `PATCH /api/v1/vloggers/{vlogger_id}`
    - Body: 
        ```json
        { 
            "youtube_channel_name": "string",
            "avatar_url": "string"
        }
        ```
    - Rules: only user.is_admin == True can update vlogger entry
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string", 
            "youtube_channel_name": "string",
            "avatar_url": "string"
            "created_at": datetime
        }
        ```

- `DELETE /api/v1/vloggers/{vlogger_id}`
    - Rules: only user.is_admin == True can delete vlogger entry
    - Response: 204 No content

<b>Vlogger - Public endpoints</b>

- `GET /api/v1/vloggers` (query params for pagination, sorting and filtering: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "vloggers": [
                {
                    "id": int,
                    "youtube_channel_id": "string", 
                    "youtube_channel_name": "string",
                    "avatar_url": "string",
                    "video_count": 87,
                    "countries_count": 52,
                    "created_at": datetime
                },
            ]
        }
        ```

- `GET /api/v1/vloggers/{vlogger_id}`
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string", 
            "youtube_channel_name": "string",
            "avatar_url": "string",
            "video_count": 87,
            "countries_count": 52,
            "created_at": datetime
        }
        ```

<b>Country - Public endpoints</b>

- `GET /api/v1/countries` (query params for pagination, sorting and filtering: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "countries": [
                {
                    "id": int,
                    "name": "string",
                    "iso_code": "string"
                },
            ]
        }
        ```

- `GET /api/v1/countries/{country_iso}/vlogs` (query params for pagination, sorting and filtering: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "vlogs": [
                {
                    "id": int,
                    "youtube_channel_name": "string",
                    "thumbnail_url": "string",
                    "title": "string",
                    "link": "string",
                    "country_name": "string",
                    "published_at": date,
                    "created_at": datetime
                },
            ]
        }
        ```

<b>Vlog Management - Private endpoints</b>

- `POST /api/v1/vlogs`
    - Body: 
        ```json
        { 
            "vlogger_id": int,
            "youtube_video_id": "string",
            "country_iso": "string"
        }
        ```
    - Rules: 
        - only user.is_admin == True can create vlog entry
        - youtube_video_id must be unique
    - Response: 201 Created
        ```json
        {
            "id": int,
            "vlogger_id": int,
            "youtube_video_id": "string",
            "title": "string",
            "thumbnail_url": "string",
            "youtube_video_link": "string",
            "published_at": date,
            "country_name": "string",
            "created_at": datetime
        }
        ```

- `PATCH /api/v1/vlogs/{vlog_id}`
    - Body: 
        ```json
        {
            "country_iso": "string"
        }
        ```
    - Rules: only user.is_admin == True can update vlog entry
    - Response: 200 OK
        ```json
        {
            "id": int,
            "vlogger_id": int,
            "youtube_video_id": "string",
            "title": "string",
            "thumbnail_url": "string",
            "youtube_video_link": "string",
            "published_at": date,
            "country_name": "string",
            "created_at": datetime
        }
        ```

- `DELETE /api/v1/vlogs/{vlog_id}`
    - Rules: only user.is_admin == True can delete vlog entry
    - Response: 204 No content

<b>Vlog - Public endpoints</b>

- `GET /api/v1/vlogs` (query params for pagination, sorting and filtering: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "vlogs": [
                {
                    "id": int,
                    "youtube_channel_name": "string",
                    "thumbnail_url": "string",
                    "title": "string",
                    "link": "string",
                    "country_name": "string",
                    "published_at": date,
                    "created_at": datetime
                },
            ]
        }
        ```

- `GET /api/v1/vlogs/{vlog_id}`
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_name": "string",
            "thumbnail_url": "string",
            "title": "string",
            "link": "string",
            "country_name": "string",
            "published_at": date,
            "created_at": datetime
        }
        ```

#### Wireframe Design
It serves as a conceptual showcase of how the API could be used by a frontend application.
![Wireframe Design](https://i.imgur.com/bSQ3zp8.png)


## Tasks
The project author creates and completes tasks to address the technical aspects and design decisions described in the [Versioning](#versioning) section. They can be found accessing [Trello](https://trello.com/b/GufG4LeA/travelvloggers).