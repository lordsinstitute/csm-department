# Research on SeaTreasure Target Detection Technology Based on Improved YOLOv7-Tiny

SeaTreasure Detect is a Django-based underwater object detection platform for identifying sea cucumbers, sea urchins, and shells from uploaded images or live camera input. This repository contains the implementation for the project "Research on SeaTreasure Target Detection Technology Based on Improved YOLOv7-Tiny."

## Features

- User login and profile management
- Upload-based sea object detection
- Live camera detection view
- Detection history and analytics dashboard
- Dataset management pages
- Optional YOLO model integration with fallback demo mode

## Tech Stack

- Python
- Django
- OpenCV
- Ultralytics YOLO
- Bootstrap 5

## Project Structure

- `accounts/` authentication and user profiles
- `core/` landing pages and shared layout
- `dashboard/` user and admin dashboards
- `datasets/` dataset upload and catalog flow
- `detection/` inference, live feed, and result tracking
- `sea_treasure/` Django project settings and routing

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables if needed. By default the project falls back to SQLite, so MySQL is optional.
4. Run migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

## Notes

- Generated files such as uploaded media, trained weights, datasets, and virtual environments are intentionally excluded from submission.
- If no YOLO weights are available, the app still runs in fallback demo mode.

## LIET Submission Name

`Research_on_SeaTreasure_Target_Detection_Technology_Based_on_Improved_YOLOv7-Tiny | 160922748130`
