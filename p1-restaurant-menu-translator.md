# Restaurant Menu Translator

## Objective

Develop a menu-management backend for a restaurant group serving a
linguistically diverse customer base, where today a menu only exists in
whatever single language the kitchen wrote it in — leaving non-native
speakers guessing at dish names on a paper menu or a static PDF. The
system should make it easy to manage restaurants and their menu items, and
automatically detect each item's written language via **Amazon
Comprehend** and render the full menu into whatever language a diner
requests via **Amazon Translate** — so a menu built once in the kitchen's
language becomes readable to any customer on demand. Retyping an entire
paper menu by hand is also its own barrier to entry, so staff should be
able to photograph a printed menu page and have **Amazon Textract** pull
out candidate item text automatically instead of typing every dish in by
hand. Prioritize correctness on the data layer — a menu item's detected
source language and its price/category are explicit, queryable fields,
and requested translations are generated on demand rather than baked in
and going stale if the source text changes. The deliverable is a
containerized service that runs locally via `docker compose up` and
exposes a documented REST API, backed by a real PostgreSQL database and
real (in production) calls to three chained AWS managed AI services.

## Functional Requirements

### Restaurant Management

- **Add New Restaurant:**
  - Admins should be able to create a new restaurant by specifying its
    name, cuisine type, and default menu language.
- **View Restaurants:**
  - Provide a dashboard endpoint listing all restaurants with their core
    metadata and menu item count.
- **Edit Restaurant:**
  - Allow updating a restaurant's name, cuisine type, or default language.
- **Delete Restaurant:**
  - Implement deletion with a confirmation requirement (such as requiring
    the restaurant id in the request body). Decide (and document in your
    README) whether deleting a restaurant cascades to delete its menu items.

### Menu Item Management

- **Add Menu Item:**
  - Restaurant staff should be able to add a menu item by specifying a
    name, description, price, and category
    (`Literal["appetizer", "entree", "dessert", "beverage"]`), written in
    the restaurant's own language.
- **View Menu:**
  - Provide an endpoint listing all menu items for a restaurant, with
    filter support by category. Support an optional `?lang=` query
    parameter that returns the name/description translated into the
    requested language on the fly.
- **Edit Menu Item:**
  - Allow updating an item's name, description, price, or category.
    Decide (and document in your README) whether an edited name/description
    re-runs language detection.
- **Delete Menu Item:**
  - Implement deletion with a confirmation requirement (such as requiring
    the item id in the request body).
- **Upload Menu Photo for Bulk Import:**
  - Accept a `multipart/form-data` upload of a photographed menu page (JPG
    or PNG) tied to a restaurant. Store the raw image in S3 and return a
    list of candidate menu items extracted from it for staff to review —
    extracted items are **not** saved automatically (see AI-Assisted
    Feature below).

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict, upstream AI-service
    failure) should return a consistent JSON shape with an error code,
    human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose `/live` and `/ready` endpoints. `/live` confirms the process is
    up; `/ready` confirms downstream dependencies (the database) are
    reachable. Comprehend/Translate/Textract reachability is *not* part of
    `/ready` — see Edge Case Handling below.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method,
    path, status code, duration, and correlation id, as machine-parseable JSON.
- **Filtered Listings:**
  - The menu endpoint should support filter + sort query parameters
    across `category`, `price` range, and item name (partial match).

### Edge Case Handling

- **Comprehend or Translate Is Unavailable:**
  - Decide how menu item creation behaves if language detection fails, and
    how a menu request behaves if translation fails. Should the item save
    with detection `pending` and the menu request fall back to the
    original-language text with a warning flag? Document your choice and
    reasoning.
- **Requested Translation Target Equals Source Language:**
  - Decide how `?lang=fr` should behave when an item is already written in
    French — calling Translate anyway (wasteful but simple) or
    short-circuiting to return the original text unchanged. Document your choice.
- **Very Short Item Name for Language Detection:**
  - A short dish name like `"Pho"` may not give Comprehend enough signal
    to confidently detect a language. Decide on a confidence threshold
    below which you fall back to the restaurant's configured default
    language, and document it.
- **Invalid Price or Category:**
  - Pydantic should validate every request body at the boundary and
    return a 422 with a clear field-by-field error envelope on malformed
    input (e.g., a negative price).
- **Textract Is Unavailable, or a Menu Photo Is Unreadable:**
  - Decide how the upload endpoint behaves if text extraction fails or
    returns nothing usable (a blurry photo, a menu with only illustrations
    on that page) — return an empty candidate list with a clear status,
    never a 500. Reject non-JPG/PNG uploads with a 422 naming accepted
    formats, and enforce a maximum file size.
- **OCR Text Doesn't Cleanly Split Into Name / Description / Price:**
  - Textract returns lines of text, not structured fields. Decide on (and
    document) your parsing heuristic for turning a line like `"Margherita
    Pizza ... 14.00"` into a name and a price, and what happens to a line
    your heuristic can't parse — it should still appear in the candidate
    list as raw text for a human to fix, not silently disappear.
- **Concurrent Mutations:**
  - Describe what happens if two staff members edit the same menu item at
    the same time, or a restaurant is deleted while a menu translation
    request against it is in flight. Document the expected behavior.

### AI-Assisted Feature (Required)

> **Sequencing — build this last.** This feature is a required, graded
> part of the deliverable, not an optional stretch goal. Implement it only
> after the core CRUD service is complete and working end to end — the AI
> pipeline should be layered on top of a finished functional deliverable,
> not built in parallel with it. A complete core with the AI feature added
> last scores well; an AI pipeline bolted onto an incomplete or broken core
> does not.

- **Dominant Language Detection:**
  - When a menu item is created, call Comprehend's
    `DetectDominantLanguage` against its name and description and store
    the detected language code on the record.
- **On-Demand Menu Translation:**
  - When the menu is fetched with `?lang=<code>`, call Translate's
    `TranslateText` to render each item's name/description into the
    requested language, only when it differs from the detected source
    language — the actual "readable to any customer on demand" payoff
    from the Objective, not a translation baked in once and left to go stale.
- **Menu Photo OCR for Bulk Import:**
  - When a menu photo is uploaded, call Textract's `DetectDocumentText`
    against the stored image and parse the recovered lines into candidate
    menu items (per your Edge Case Handling parsing decision above),
    returned to staff for review — this is the actual "stop retyping the
    whole menu by hand" payoff from the Objective, layered on top of the
    manual entry path, not a replacement for it.
- **Isolated, Mockable AWS Clients:**
  - The Comprehend, Translate, and Textract calls (and S3 storage) must
    each go through their own single, injectable client module (mirroring
    the shared-session pattern from this course's Week 3 boto3 material)
    so your test suite can substitute fake/mocked clients and run without
    live AWS credentials.

## Stretch Goals

Stretch goals are features you want to add to an application, but they
aren't required. For this project, Stretch Goals are a way to go above and
beyond the minimum requirements and I look forward to seeing what unique
features you will add to your project. Here are some examples you might consider:

- **Deploy the App to AWS:**
  - Push your Docker image to Amazon ECR and run the stack on an AWS
    compute service of your choice (App Runner, ECS, or an EC2 instance).
    Document your deployment architecture and any cost/cleanup considerations.
- **Bedrock-Powered Dish Descriptions:**
  - Add an endpoint that takes a few ingredient bullet points and uses a
    foundation model via Bedrock's Converse API to draft an appealing menu
    description. This uses content not yet covered in lecture at the
    time this project is assigned — a good stretch goal for anyone who
    wants to explore ahead.
- **SageMaker Custom Model:**
  - Train a simple custom model that predicts a dish's likely popularity
    from its category and price, hosted behind a SageMaker endpoint. Also
    beyond the current curriculum — a good "go deeper" option.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle menu translation requests per client
    IP. Choose a sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support a `Restaurant Location` entity — the same
    restaurant brand with multiple physical locations, each with its own
    menu subset.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and lets
    a visitor pick a language and browse a translated menu.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table
    with timestamp, action, entity, and actor.
- **Bulk Import:**
  - Add an endpoint that accepts a CSV of menu items and inserts them for
    a restaurant in one transaction, with all-or-nothing semantics.
- **Translation Caching:**
  - Cache each item's translated text per target language (in a dedicated
    table) so repeated menu views in the same popular language don't
    re-pay for the same Translate call every time.

## Technical Requirements

Must be a backend solution consisting of:

- Python 3.11+
- Flask 3.x with the app-factory pattern and blueprints
- Pydantic v2 for HTTP-boundary validation
- PostgreSQL via SQLAlchemy 2.0 and Flask-Migrate, with a real migration
  history checked into the repo (no `create_all()` in production code paths)
- boto3, authenticated via a dedicated, least-privilege IAM user (never
  root/admin credentials) — the IAM policy JSON granting only
  `comprehend:DetectDominantLanguage`, `translate:TranslateText`,
  `textract:DetectDocumentText`, and `s3:PutObject`/`s3:GetObject` (scoped
  to your bucket) must be committed to the repo
- Separate, injectable client wrapper modules for Comprehend, Translate,
  Textract, and S3 — not `boto3.client(...)` called ad hoc from route handlers
- structlog for structured JSON logging with per-request correlation IDs
- pytest with fixtures and parametrize for the test suite; AWS calls must
  be mocked/stubbed in tests (e.g. `unittest.mock` or `botocore.stub.Stubber`)
  so the suite runs without live AWS credentials or network access
- Docker multi-stage Dockerfile + docker-compose.yml for a local
  api + db stack, with a database health check gating the API's startup
- pyproject.toml with a src/ layout and a `[project.optional-dependencies]` dev block
- Code should be available in a private GitHub repository, with the
  instructor added as a collaborator
- Possesses all required CRUD functionality
- Handles edge cases effectively

## Non-Functional Requirements

- Well-documented code (module docstrings + function docstrings on public surfaces)
- Code upholds industry best practices (SOLID / DRY / single-responsibility)
- Type hints on every function signature
- Test coverage on happy + error paths (at least 15 pytest tests, including
  at least one test per Comprehend-, Translate-, and Textract-backed
  endpoint using mocked clients)
- Structured logs (no print statements in production code paths)
- Container runnable via a single `docker compose up`
- README with one-line install and one-line run instructions, plus your
  documented decisions for every Edge Case Handling item above
- Pydantic models have explicit field constraints (Literal types, min/max
  length, ge on price)
- No mutable default arguments; use `field(default_factory=...)` for collections
- Errors raise typed exceptions from a DomainError hierarchy, not generic Exception
- Data model documented as an entity-relationship diagram (ERD) — every
  entity, its fields, and the cardinality of each relationship — checked
  into the repository
- A kanban board with a complete, prioritized backlog is set up **before
  development begins**; work is pulled from the board rather than started ad hoc
