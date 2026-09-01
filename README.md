# Restaurant-Menu-Translator

## Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate (macOS)
```

## Activate virtual environment

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


## Edge Case Handling

### Comprehend or Translate Is Unavailable

If Comprehend fails when I am trying to detect the language of a menu item, I catch the AWS error and return my own `AWSError`.

In this case I do not save the menu item because I don't have a reliable source language.

I handle Translate errors in a similar way. If the translation call fails, I return an application error

instead of exposing the original AWS error to the client.


### Requested Language Is the Same as the Source Language

If the user requests the same language that the menu item is already written in, I don't call Translate.

I just return the original menu item to avoid making an unnecessary AWS call.


### Short Item Name

Short menu item names may not give Comprehend enough text to reliably detect a language.

To help with this, I send both the name and description to Comprehend.

I use a confidence threshold of `0.70`. If the confidence is lower than that, or no language is returned, I use the restaurant's `default_menu_language` instead.


### Invalid Price or Category

Pydantic validates the request data before it gets to the main service logic.

For example, a negative price or an invalid category will return a `422` response instead of being saved to the database.

The supported categories are:

- appetizer
- entree
- dessert
- beverage


### Textract Is Unavailable or Cannot Read the Image

Menu uploads only allow JPG, JPEG, and PNG files, and I limit the upload size to 5 MB.

If the file type is not supported, the endpoint returns a `422`. If the Textract call fails, I return `text_extraction_failed`

with an empty list of candidates instead of returning a 500 error.

If Textract works but doesn't find any usable text, I return `no_text_found` with an empty candidate list.


### OCR Text Cannot Be Parsed

Textract gives numerous lines of text, so I use a simple regex to look for lines where a price appears at the end, for example:

`Pizza ... 14.00`

If I can find a name and price, I return the candidate with `parsed: true`

If the line couldn't be parsed, I still return the original line as `raw_text` and set `parsed: false`

I chose to keep the raw text so that someone can review it manually instead of losing the data. 

The candidates are also not automatically saved to the database. Once a restaurant staff member reviews it,

there could be a decision to save the menu to the database.


### Concurrent Mutations

I did not add special locking for concurrent updates. If two users update the same menu item at around the same time,

the last update that is committed may overwrite the earlier one. I rely on the normal SQLAlchemy and PostgreSQL behavior.

Advanced locking or version checking could be added later if needed.