# Videoflix - API Documentation

Base URL: `http://127.0.0.1:8000/api/`
Authentication: Cookie-based (`access_token` / `refresh_token` as HttpOnly cookies, set automatically on login)

---

## Table of Contents

- [Authentication](#authentication)
  - [POST /register/](#post-register)
  - [GET /activate/{uidb64}/{token}/](#get-activateuidb64token)
  - [POST /login/](#post-login)
  - [POST /token/refresh/](#post-tokenrefresh)
  - [POST /logout/](#post-logout)
  - [POST /password_reset/](#post-password_reset)
  - [POST /password_confirm/{uidb64}/{token}/](#post-password_confirmuidb64token)
- [Video Library](#video-library)
  - [GET /video/](#get-video)
  - [GET /video/{movie_id}/{resolution}/index.m3u8](#get-videomovie_idresolutionindexm3u8)
  - [GET /video/{movie_id}/{resolution}/{segment}/](#get-videomovie_idresolutionsegment)

---

## Authentication

### POST /register/

Registers a new, initially inactive user and triggers an activation email.

**Auth required:** No

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
}
```

**Success Response `201`**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 201  | User was created successfully. |
| 400  | Invalid request data (e.g. passwords do not match, email already in use). |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Permissions:** No permissions required
**Extra Information:** The account remains inactive until confirmed via the activation link sent by email.

---

### GET /activate/{uidb64}/{token}/

Activates a user account based on the `uidb64`/`token` pair from the activation email.

**Auth required:** No

**URL Parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| uidb64 | string | Base64-encoded user ID from the activation link. |
| token | string | Signed activation token from the activation link. |

**Success Response `200`**

```json
{
  "message": "Account successfully activated."
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Account activated successfully. |
| 400  | Invalid or expired token, malformed `uidb64`, unknown user, or account already activated. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Permissions:** No permissions required

---

### POST /login/

Authenticates a user and sets the access and refresh tokens as HttpOnly cookies.

**Auth required:** No

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success Response `200`**

```json
{
  "detail": "Login successful"
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Login successful. |
| 400  | Invalid request data. |
| 401  | Invalid credentials or account not yet activated. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Permissions:** No permissions required
**Extra Information:** Sets HttpOnly cookies `access_token` and `refresh_token`. The response body carries no token data, since authentication is handled entirely via cookies.

---

### POST /token/refresh/

Reads the refresh token from the `refresh_token` cookie and issues a new access token as a cookie.

**Auth required:** No (valid `refresh_token` cookie required)

**Request Body:** None – the refresh token is read from the cookie.

**Success Response `200`**

```json
{
  "detail": "Access-Token refreshed"
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Access token refreshed successfully. |
| 400  | Refresh token cookie not found. |
| 401  | Refresh token is invalid or expired. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Extra Information:** Sets a new HttpOnly `access_token` cookie.

---

### POST /logout/

Blacklists the refresh token and deletes both auth cookies.

**Auth required:** Yes
**Permissions:** Authenticated user

**Request Body:** None – the refresh token is read from the cookie.

**Success Response `200`**

```json
{
  "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Logout successful. |
| 400  | Refresh token cookie not found or invalid. |
| 401  | User is not authenticated. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Extra Information:** The refresh token is blacklisted server-side; both `access_token` and `refresh_token` cookies are deleted.

---

### POST /password_reset/

Sends a password-reset email to the user matching the given email.

**Auth required:** No

**Request Body**

```json
{
  "email": "user@example.com"
}
```

**Success Response `200`**

```json
{
  "detail": "An email has been sent to reset your password."
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Password-reset email sent successfully. |
| 404  | No active user found for the given email. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Permissions:** No permissions required

---

### POST /password_confirm/{uidb64}/{token}/

Sets a new password for the user identified by `uidb64`, after validating the reset token.

**Auth required:** No

**URL Parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| uidb64 | string | Base64-encoded user ID from the password-reset link. |
| token | string | Signed reset token from the password-reset link. |

**Request Body**

```json
{
  "new_password": "newSecurePassword123",
  "confirm_password": "newSecurePassword123"
}
```

**Success Response `200`**

```json
{
  "detail": "Your Password has been successfully reset."
}
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Password reset successfully. |
| 400  | Invalid or expired token, inactive account, or passwords do not match. |
| 404  | Unknown user for the given `uidb64`. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Permissions:** No permissions required

---

## Video Library

### GET /video/

Returns a list of all videos in the video library.

**Auth required:** Yes
**Permissions:** Authenticated user

**Success Response `200`**

```json
[
  {
    "id": 1,
    "title": "Big Buck Bunny",
    "description": "A short animated film.",
    "thumbnail_url": "http://127.0.0.1:8000/media/thumbnails/big_buck_bunny.jpg",
    "created_at": "2026-07-01T10:00:00Z",
    "category": "Animation"
  }
]
```

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Video list returned successfully. |
| 401  | User is not authenticated. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Extra Information:** The response is cached server-side for 15 minutes and invalidated automatically whenever a video is created, updated, or deleted.

---

### GET /video/{movie_id}/{resolution}/index.m3u8

Returns the HLS playlist file (`index.m3u8`) for a video at the requested resolution.

**Auth required:** Yes
**Permissions:** Authenticated user

**URL Parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| movie_id | integer | ID of the video. |
| resolution | string | Requested resolution: `480p`, `720p`, or `1080p`. |

**Success Response `200`**

Returns the raw `index.m3u8` playlist file with content type `application/vnd.apple.mpegurl`.

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Playlist file returned successfully. |
| 401  | User is not authenticated. |
| 404  | Video not found, resolution unavailable, or playlist not yet generated. |
| 500  | Internal server error. |

**Rate Limits:** No limit
**Extra Information:** HLS files are generated asynchronously after upload; the playlist may not exist yet for a freshly uploaded video.

---

### GET /video/{movie_id}/{resolution}/{segment}/

Returns a single HLS video segment (`.ts` file) of a video.

**Auth required:** Yes
**Permissions:** Authenticated user

**URL Parameters**

| Name | Type | Description |
| ---- | ---- | ----------- |
| movie_id | integer | ID of the video. |
| resolution | string | Requested resolution: `480p`, `720p`, or `1080p`. |
| segment | string | Segment file name, e.g. `segment_00000.ts`. |

**Success Response `200`**

Returns the raw `.ts` segment file with content type `video/MP2T`.

**Status Codes**

| Code | Description |
| ---- | ----------- |
| 200  | Segment file returned successfully. |
| 401  | User is not authenticated. |
| 404  | Video not found, resolution unavailable, or segment not found. |
| 500  | Internal server error. |

**Rate Limits:** No limit
