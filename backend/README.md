# Backend for KaoQin System

This is the server-side component of KaoQin management system, designed to handle activities, users, and participations. This system is built using the `FastAPI` framework and utilizes a `SQLite` database for data storage.

## Features

- **Activities Management:** Create, update, delete, and list activities. Activities can be categorized as lectures or association events.

- **Participations:** Record user participation in activities, including tracking involvement and staff status.

- **Users:** Manage user information, superuser privileges, and password reset functionalities.

- **Authentication:** Utilize OAuth2 for user authentication, issuing access tokens for secured API access.

- **Data Export:** Generate Excel reports containing participation statistics and details for users and activities.

## Setup

1. **Clone the Repository:**

```bash
git clone https://github.com/Evlpsrfc/kaoqin.git
cd kaoqin/backend
```

2. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure Database:**

```bash
python -m app.db.init
```

**NOTE**: Before running the script, make sure you have the files required. You can get some of them by running [scripts/download.py](https://github.com/Evlpsrfc/kaoqin/blob/main/scripts/download.py).

4. **Run the Application:**

```bash
uvicorn app.main:app --reload
```

5. **Access the API Documentation:**

Open your web browser and navigate to http://localhost:8000/docs to access the interactive API documentation provided by `Swagger UI`.

## API Endpoints

- **Activities:** CRUD operations for managing activities.
  - `/activities/`: List activities and supports filtering, skipping, and limiting.
  - `/activities/{id}`: Update or delete an activity by ID.

- **Participations:** Manage user participation records.
  - `/particips/`: List participation records and supports filtering, skipping, and limiting.
  - `/particips/download`: Download Excel reports containing participation statistics and details.
  - `/particips/upload`: Upload Excel files to create participation records.

- **Users:** Manage user information and authentication.
  - `/users/`: List users and supports filtering, skipping, and limiting.
  - `/users/me`: Retrieve authenticated user's details.
  - `/users/{student_number}/reset-password`: Reset user's password (requires superuser privileges).
  - `/users/{student_number}/set-superuser`: Set/unset superuser status for a user (requires superuser privileges).

- **Authentication:**
  - `/login/access-token`: Obtain an access token using OAuth2 password grant.
  - `/login/test-token`: Test the validity of an access token.

## Contributing

Contributions are welcome! If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Submit a pull request to the main repository.
