# Restaurant Menu Translator

## Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Running the Application Locally

An explicit Flask command can be used to run the application locally:

```bash
python -m flask --app src/menu_translator/app.py:create_app run
```

If `FLASK_APP` is configured, the application can instead be started with:

```bash
flask run
```

## Build the Docker Image

To build the Docker image:

```bash
docker build -t restaurant-menu-translator .
```

## Run with Docker

To start the Flask API and PostgreSQL containers:

```bash
docker compose up
```

To build the image and start the containers:

```bash
docker compose up --build
```

# Edge Case Handling

## Comprehend or Translate Is Unavailable

If Comprehend fails while detecting the language of a menu item, the AWS exception is caught and converted into an application-level AWS error.

In this case, the menu item is not saved because the application does not have a reliable source language.

Translate errors are handled similarly. If the translation call fails, an application error is returned instead of exposing the original AWS exception to the client.

## Requested Language Is the Same as the Source Language

If the requested language is the same as the language of the original menu item, the application does not call Amazon Translate.

Instead, it returns the original menu item and avoids an unnecessary AWS request.

## Short Item Name

Short menu item names may not provide enough text for Amazon Comprehend to reliably detect a language.

To improve detection, both the item name and description are sent to Comprehend.

The application uses a confidence threshold of 0.70. If the confidence is below this threshold, or no language is returned, the restaurant's default_menu_language is used instead.

## Invalid Price or Category

Pydantic validates request data before it reaches the main service logic.

For example, a negative price or invalid category returns a `422` response instead of being saved to the database.

Supported categories are:

- appetizer
- entree
- dessert
- beverage

## Textract Is Unavailable or Cannot Read the Image

Menu uploads support JPG, JPEG, and PNG files with a maximum file size of 5 MB.

If the file type is unsupported, the endpoint returns a `422`.

If the Textract call fails, the application returns a `text_extraction_failed` status with an empty list of candidates.

If Textract succeeds but no usable text is found, the application returns `no_text_found` with an empty candidate list.

## OCR Text Cannot Be Parsed

Amazon Textract may return many lines of text, so the application uses a simple regular expression to identify lines where a price appears at the end.

For example: Pizza ... 14.00

If a name and price can be extracted, the candidate is returned with: parsed: true

If a line cannot be parsed, the original line is still returned as raw_text with: parsed: false

The raw text is preserved so that restaurant staff can manually review information that could not be parsed.

Candidate menu items are not automatically saved to the database. A restaurant staff member can review the extracted candidates before deciding whether they should be added to the actual menu.

## Concurrent Mutations

The application does not currently implement special locking for concurrent updates.

If two users update the same menu item at approximately the same time, the last committed update may overwrite the earlier update.

The application relies on normal SQLAlchemy and PostgreSQL behavior. Optimistic locking or version checking could be added in the future if needed.

# Dockerfile and Docker Compose

The Dockerfile defines how the application image is built.

Docker Compose is used to run multiple containers together. For this project, Docker Compose starts both the Flask application and PostgreSQL.

To build and start the application:

```bash
docker compose up --build
```

If the image has already been built:

```bash
docker compose up
```

# AWS EC2 Deployment

The `main` branch contains the code used for local development.

A separate `aws-deployment` branch contains the changes needed to deploy the project to Amazon EC2. These include the browser UI, HTML templates, and deployment-specific configuration changes.

The deployed application is currently available at: http://52.207.236.115/

The application is containerized with Docker, stored in a private Amazon ECR repository, and deployed to EC2 using Docker Compose.

AWS access from the deployed application is provided through an EC2 IAM role rather than AWS credentials stored inside the application.

# Pytest Test Suite

The project currently contains 23 passing tests covering both positive and negative paths.

All API endpoints are tested, and AWS service calls are mocked using `patch` from `unittest.mock`.

# Kanban Board

The Kanban board for this project is available at:

https://github.com/users/milenagrabovskiy/projects/1