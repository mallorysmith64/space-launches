# Space Launches

A web app for browsing space launches from different companies, with a mission gallery and an admin panel for managing mission data.

## Tech Stack

- **Frontend:** Vue 3 + TypeScript + Vite
- **Backend:** Flask, Python
- **Data storage:** JSON files — one file per company, e.g. `src/data/spacex-mission-data.json`, `src/data/jaxa-mission-data.json`
- **Images:** JPEG mission photos stored under `src/images/`, served via Flask and bundled by Vite

## Features

- **Home page** with a hero section and a mission gallery

- **Mission gallery**
  - Grid of mission cards (image, name, date, rocket, mission type, description)
  - Filter by company and by rocket
  - Expandable descriptions for cards where the text is truncated

- **Admin panel**
  - Session-based login
  - Create a new mission with a required image upload
  - Edit an existing mission's title, description, date, rocket type, mission type, and image
  - Delete a mission

## Admin API Reference

All admin routes are prefixed `/api/admin` and aside from login/status require an active session.

| Method | Route | Description |

|---|---|---|
| POST | `/api/admin/login` | Log in with `username`/`password` |
| GET | `/api/admin/logout` | Log out and clear the session |
| GET | `/api/admin/status` | Check whether the current session is authenticated |
| GET | `/api/admin/dashboard` | Protected dashboard placeholder |
| POST | `/api/admin/create-mission` | Create a mission (multipart form: `title`, `date`, `rocketType`, `missionType`, `description`, `file`) |
| POST | `/api/admin/upload-image` | Update an existing mission's fields and/or image (multipart form, requires `missionId`) |
| POST | `/api/admin/delete-mission` | Delete a mission by `missionId` (JSON body) |

Uploaded images must be JPEG and under 5MB. Mission images are stored in `src/images/` and referenced in the JSON data by path.

## Mission Data Format

Each mission in the JSON files follows this shape:

```json
{
  "id": "uuid",
  "name": "Mission name",
  "date": "YYYY-MM-DD",
  "description": "Mission description",
  "image": "/src/images/mission-name.jpeg",
  "rocketName": "Rocket name",
  "missionType": "Mission type"
}
```

## Adding a New Company

To add another company to the gallery:

1. Add a new JSON data file under `src/data/` following the mission data format above.
2. Import it in `MissionGallery.vue`, add the company to the `Company` type and `COMPANY_LABELS`/`companyOptions`, and include it in `loadMissions()`.
3. Drop the company's images into `src/images/`.
