# Development Notes
This document provides a more in-depth view of the application, which was designed from the beginning to support versioning.


## Table of Contents
1. [Versioning](#versioning)
    - [Version 1.0.0](#version-100)
        - Database design
        - Endpoints design
        - Wireframe design
    - [Version 2.0.0](#version-200)
        - Overview
        - Wireframe design
        - Endpoints design
        - Database design
2. [Tasks](#tasks)


## Versioning

### Version 1.0.0
All vlogger profiles and their videos are added manually by an administrator. There is no sign-up flow for regular users.

Administrators can: 
- Log in using email + password and access private endpoints using JWT auth.
- Manage (CRUD) vloggers profiles.
- Create vlog entries using YouTube video ID by fetching YouTube Data API with id=YOUTUBE_VIDEO_ID and extracts the title, thumbnail, and publish date and saves them in the database.
- Update or delete vlog entries.

Visitors can:
- View the most recently added vloggers and a single vlogger's profile, where they can see its vlogs.
- View the most recently added vlogs, a single vlog details, and filter all vlogs by the country they were filmed in.
- View all available countries so users know which locations can be used for filtering.

#### Database design
![Database design](https://i.imgur.com/HrRvz1T.png)

```SQL 
Table users {
  id int [primary key]
  email email [unique, not null]
  password_hash str [not null]
  is_admin bool [not null]
  is_superuser bool [not null]
  created_at datetime [not null]
}

Table vloggers {
  id int [primary key]
  youtube_channel_id varchar(255) [unique, not null]
  youtube_channel_name varchar(255) [unique, not null]
  youtube_channel_link varchar(255) [unique, not null]
  youtube_avatar_url varchar(255) [not null]
  created_at datetime [not null]
}

Table countries {
  id int [primary key]
  name varchar(255) [unique, not null]
  iso_code varchar(2) [unique, not null]
}

Table vlogs {
  id int [primary key]
  vlogger_id int [ref: > vloggers.id, not null]
  country_id int [ref: > countries.id, not null]
  youtube_video_id varchar(255) [unique, not null]
  published_at varchar(255) [not null]
  title varchar(255) [not null]
  thumbnail_url varchar(255) [not null]
  language varchar(2) [null]
  created_at datetime [not null]
}
```

#### Endpoints design
Authentication

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
            "email": "EmailStr", 
            "password": "string"
        }
        ```
    - Behavior: 
        - verify credentials
        - return JWT access token
    - Response: 200 OK
        ```json
        {
            "access_token": "string",
            "token_type": "bearer"
        }

- `GET /api/v1/auth/me`
    - Behavior: does not request a body but requires a valid Bearer token in the Authorization header
    - Response: 200 OK
        ```json
            {
            "id": int,
            "email": "EmailStr",
            "is_admin": bool,
            "is_superuser": bool
            }
        ```
User Management - Private endpoints

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

Vlogger Management - Private endpoints

- `POST /api/v1/vloggers`
    - Body: 
        ```json
        { 
            "youtube_channel_id": "string",
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string"
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
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string",
            "created_at": datetime
        }
        ```

- `PATCH /api/v1/vloggers/{vlogger_id}`
    - Body: 
        ```json
        { 
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string"
        }
        ```
    - Rules: only user.is_admin == True can update vlogger entry
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string",
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string",
            "created_at": datetime
        }
        ```

- `DELETE /api/v1/vloggers/{vlogger_id}`
    - Rules: only user.is_admin == True can delete vlogger entry
    - Response: 204 No content

Vlogger - Public endpoints

- `GET /api/v1/vloggers` (query params for pagination and sorting: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "vloggers": [
                {
                    "id": int,
                    "youtube_channel_id": "string",
                    "youtube_channel_name": "string",
                    "youtube_channel_url": "string",
                    "youtube_avatar_url": "string",
                    "created_at": datetime,
                },
            ],
            "skip": int,
            "limit": int,
            "has_more": bool
        }
        ```

- `GET /api/v1/vloggers/{vlogger_id}`
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string",
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string",
            "created_at": datetime,
        }
        ```

- `GET /api/v1/vloggers/{vlogger_id}/vlogs` (query params for pagination and sorting: ?skip=&limit=&order=asc/desc by created_at)
    - Behavior: return all vlogs that have vlog.vlogger_id == vlogger_id
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string",
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string",
            "created_at": datetime,
            "vlogs": [
                {
                    "id": int,
                    "vlogger_id": int,
                    "country_id": int,
                    "youtube_video_id": "string",
                    "youtube_video_url": "string",
                    "published_at": datetime,
                    "title": "string",
                    "thumbnail_url": "string",
                    "language": "string",
                    "created_at": datetime
                },
            ]
        }
        ```

Country - Public endpoints

- `GET /api/v1/countries` (query params for pagination and sorting: ?skip=&limit=&order=asc/desc by created_at)
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

- `GET /api/v1/countries/{country_iso}/vlogs` (query params for pagination and sorting: ?skip=&limit=&order=asc/desc by created_at)
    - Behavior: return all vlogs that have vlog.vlogger_id == vlogger_id
    - Response: 200 OK
        ```json
        {
            "id": int,
            "name": "string",
            "iso_code": "string",
            "vlogs": [
                {
                    "id": int,
                    "vlogger_id": int,
                    "country_id": int,
                    "youtube_video_id": "string",
                    "youtube_video_url": "string",
                    "published_at": datetime,
                    "title": "string",
                    "thumbnail_url": "string",
                    "language": "string",
                    "created_at": datetime
                },
            ]
        }
        ```

Vlog Management - Private endpoints

- `POST /api/v1/vlogs`
    - Body: 
        ```json
        { 
            "vlogger_id": int,
            "country_id": int,
            "youtube_video_id": "string"
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
            "country_id": int,
            "youtube_video_id": "string",
            "youtube_video_url": "string",
            "published_at": datetime,
            "title": "string",
            "thumbnail_url": "string",
            "language": "string",
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
            "country_id": int,
            "youtube_video_id": "string",
            "youtube_video_url": "string",
            "published_at": datetime,
            "title": "string",
            "thumbnail_url": "string",
            "language": "string",
            "created_at": datetime
        }
        ```

- `DELETE /api/v1/vlogs/{vlog_id}`
    - Rules: only user.is_admin == True can delete vlog entry
    - Response: 204 No content

Vlog - Public endpoints

- `GET /api/v1/vlogs` (query params for pagination and sorting: ?skip=&limit=&order=asc/desc by created_at)
    - Response: 200 OK
        ```json
        {
            "vlogs": [
                {
                    "id": int,
                    "vlogger_id": int,
                    "country_id": int,
                    "youtube_video_id": "string",
                    "youtube_video_url": "string",
                    "published_at": datetime,
                    "title": "string",
                    "thumbnail_url": "string",
                    "language": "string",
                    "created_at": datetime
                },
            ],
            "skip": int,
            "limit": int,
            "has_more": bool
        }
        ```

- `GET /api/v1/vlogs/{vlog_id}`
    - Response: 200 OK
        ```json
        {
            "id": int,
            "vlogger_id": int,
            "country_id": int,
            "youtube_video_id": "string",
            "youtube_video_url": "string",
            "published_at": datetime,
            "title": "string",
            "thumbnail_url": "string",
            "language": "string",
            "created_at": datetime
        }
        ```

#### Wireframe Design
It serves as a conceptual showcase of how the API could be used by a frontend application.
![Wireframe Design](https://i.imgur.com/bSQ3zp8.png)

### Version 2.0.0
The previous version was developed by first describing an idea, then modeling the database and API endpoints as needed. After that, a wireframe was created to illustrate the implementation of the idea, the usage of the endpoints, and the model fields.

For this version, we will start with a Figma wireframe, a short description of what is new compared to v1, user roles and flows, and a set of business rules. Based on these, we will then develop all the technical aspects necessary for an MVP implementation:
- Design preliminary database models and API endpoints
- Write tasks and a backlog to follow a structured work plan

#### Overview
The original idea of the project has been improved to enhance user experience, automation, and monetization. In v2, the application evolves from an admin-managed content platform into a creator-driven ecosystem.

The main features and flows for Administrators and Visitors remain the same. However, critical endpoints that return vlog data will include filtering options by language and published_at in this version.

Registered Users can:
- Sign up using a Google account with YouTube scopes, which provides access to the associated YouTube account and the necessary data to automatically create a Vlogger instance for each new User.
- Purchase a membership subscription to unlock premium features.
- List their own YouTube videos: the last 10 for non-members, and unlimited (paginated) for members.
- Sync their YouTube videos on demand to retrieve the latest uploads: once per week for non-members, and once per day for members.
- Create Vlog entries by aggregating their own YouTube videos: once per week for non-members, and unlimited for members.

#### Wireframe design
Represents the client's vision of the final product and serves as a reference for the developer, outlining what backend components need to be built to achieve the desired functionality.
![Wireframe design](https://i.imgur.com/PcHglMO.jpeg)

#### Endpoints design
Authentication

- Public endpoint `POST /api/v2/auth/with-google` handles registration (creates User and Vlogger entries) & login via Google OAuth
    - Include YouTube Data API integration by calling `GET https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true` to retrieve channel data in order to create / update (when login) Vlogger record
        - Response: 200 OK
        ```json
            {
                "items": [
                    {
                        "id": "channel_id",
                        "snippet": {
                            "title": "channel_name",
                            "thumbnails": {
                            "default": { "url": "avatar_url" }
                            }
                        },
                        "statistics": {
                            "subscriberCount": "0"
                        }
                    }
                ]
            }
        ```
        - Map returned data with Vlogger model fields as: id -> youtube_channel_id, snippet.title -> youtube_channel_name, snippet.thumbnails.default.url -> youtube_avatar_url, statistics.subscriberCount -> youtube_subscribers_count
    - Also includes more YouTube Data API integration by fetching `GET https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true` to get Uploads playlist ID (contentDetails.uploads)
        - Response: 200 OK
        ```json
            {
                "items": [
                    {
                    "contentDetails": {
                        "relatedPlaylists": {
                        "uploads": "UPLOADS_ID"
                        }
                    }
                    }
                ]
            }
        ```
        - Map returned data with Vlogger model field as: contentDetails.uploads -> youtube_uploads_id

- Private endpoint `GET /api/v2/auth/me` returns data for the authenticated user
    - Response: 200 OK
        ```json
            {
                "id": int,
                "has_membership": bool,
                "membership_expiration": datetime
            }
        ```

Discover vlogs page

- Public endpoint `GET /api/v2/vlogs/countries` returns data used to highlight countries on the world map (e.g., coloring countries that have at least one aggregated vlog)
    - Response: 200 OK
        ```json
        {
            "countries": [
                {
                    "id": int,
                    "name": "string",
                    "iso_code": "string",
                    "has_vlog": bool
                },
            ]
        }
        ```
    - Behavior: has_vlog is True when Country.vlogs > 0

- Public endpoint `GET /api/v2/vlogs/countries/{country_id}` returns paginated vlogs for a specific country
    - Filters: ?skip=&limit=&order=&language=&publish_year=
    - Response: 200 OK
        ```json
        {
            "vlogs": [
                {
                    "id": int,
                    "vlogger_id": int,
                    "country_id": int,
                    "youtube_video_id": "string",
                    "youtube_video_url": "string",
                    "published_at": datetime,
                    "title": "string",
                    "thumbnail_url": "string",
                    "language": "string",
                    "created_at": datetime
                },
            ],
            "skip": int,
            "limit": int,
            "has_more": bool
        }
        ```

Discover vlogger page

- Public endpoint `GET /api/v2/vloggers/{vlogger_id}` returns data for a specific vlogger
    - Response: 200 OK
        ```json
        {
            "id": int,
            "youtube_channel_id": "string",
            "youtube_channel_name": "string",
            "youtube_channel_url": "string",
            "youtube_avatar_url": "string",
            "youtube_subscribers_count": int,
            "vlogs_count": int,
            "countries_count": int,
            "created_at": datetime
        }
    - Behavior: vlogs_count and countries_count are calculated at request and are not stored in the database

- Public endpoint `GET /api/v2/vloggers/{vlogger_id}/countries` returns country data for map highlighting
    - Response: 200 OK
        ```json
        {
            "countries": [
                {
                    "id": int,
                    "name": "string",
                    "iso_code": "string",
                    "has_vlog": bool
                },
            ]
        }
        ```
    - Behavior: has_vlog is True when a vlog exists for the given vlogger_id and country_id

- Public endpoint `GET /api/v2/vloggers/{vlogger_id}/country/{country_id}` returns paginated vlogs for a specific vlogger and country
    - Filters: ?skip=&limit=&order=&language=&publish_year=
    - Response: 200 OK
        ```json
        {
            "vlogs": [
                {
                    "id": int,
                    "vlogger_id": int,
                    "country_id": int,
                    "youtube_video_id": "string",
                    "youtube_video_url": "string",
                    "published_at": datetime,
                    "title": "string",
                    "thumbnail_url": "string",
                    "language": "string",
                    "created_at": datetime
                },
            ],
            "skip": int,
            "limit": int,
            "has_more": bool
        }
        ```

Dashboard page

- Private endpoint `GET /api/v2/youtube/videos` returns videos from the vlogger’s uploads playlist with pagination
    - Behavior: returns cached videos if available; otherwise (on first request) fetches from the YouTube API and stores the result in cache
    - Include YouTube Data API integration by fetching `GET https://www.googleapis.com/youtube/v3/playlistItems?part=snippet,contentDetails&playlistId=UPLOADS_ID&maxResults=10&pageToken=NEXT_PAGE_TOKEN` to retrieve videos from Uploads playlist
        - Response: 200 OK
        ```json
            {
                "nextPageToken": "token",
                "items": [
                    {
                        "snippet": {
                            "title": "Video title",
                            "thumbnails": {
                                "high": { "url": "thumbnail" }
                            }
                        },
                        "contentDetails": {
                            "videoId": "video_id",
                            "videoPublishedAt": "date"
                        }
                    }
                ]
            }
        ```
    - Rules: applies membership limits (non-membership: max 10 videos, membership unlimited - paginated)
    - Cache: stored per user (key: youtube_videos:{user_id}), includes pagination tokens (nextPageToken) and overwritten only via POST endpoint

- Private endpoint `POST /api/v2/youtube/videos` refreshes cached videos from YouTube
    - Behavior: fetches latest videos and updates Redis cache
    - Rules: applies membership limits (non-membership have max 1 request / 7 days, membership have max 1 request / 1 day)

- Private endpoint `POST /api/v2/vlogs` creates a Vlog record by Vlogger
    - Body: 
        ```json
        { 
            "vlogger_id": int,
            "country_id": int,
            "youtube_video_id": "string"
        }
        ```
    - Rules: 
        - youtube_video_id must be unique
    - Response: 201 Created
        ```json
        {
            "id": int,
            "vlogger_id": int,
            "country_id": int,
            "youtube_video_id": "string",
            "youtube_video_url": "string",
            "published_at": datetime,
            "title": "string",
            "thumbnail_url": "string",
            "language": "string",
            "created_at": datetime
        }
        ```

Membership page

- Private endpoint `POST /api/v2/users/membership-subscribe` initiates a Stripe checkout for a monthly subscription

#### Database design
![Database design](https://i.imgur.com/chW30DK.png)

Update tables from v1, with the following additional fields:
```SQL 
Table users {
  has_membership boolean [not null, default=false]
  membership_expiration timestamp [null]
  stripe_customer_id varchar(255) [not null]
  stripe_subscription_id varchar(255) [not null]
}

Table vloggers {
  user_id int [ref: > users.id, not null]
  youtube_subscribers_count int [not null]
  youtube_uploads_id varchar(255) [not null]
}
```

## Tasks
The project author creates and completes tasks to address the technical aspects and design decisions described in the [Versioning](#versioning) section. They can be found accessing [Trello](https://trello.com/b/GufG4LeA/travelvloggers).
