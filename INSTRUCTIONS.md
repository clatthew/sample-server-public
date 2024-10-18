# The NC Merch API

This API concerns sales of highly desirable merch from the coffers of Northcoders.

To run the API locally, you will need a file of environment variables that is not saved in source control. If you are authorised to view this API, you will have received the relevant file. Then:
1. Fork and clone the repo.
1. Ensure that your Python interpreter is Python at least 3.11.x - you may use a tool like `pyenv`.
1. In the root of the project, create the run environment with:
    ```bash
    make requirements
    ```
1. Set up the required dev tools:
    ```bash
    make dev-setup
    ```
1. Add the supplied `.env` file to the root level of the project.
1. Run the tests.
    ```bash
    make run-checks
    ```
1. Start the server by running:
    ```bash
    make start-server
    ```
1. In your browser, navigate to `localhost:8000/docs/` to view the API documentation page.
1. Then you can navigate to the endpoint of your choice, e.g. `localhost:8000/api/categories`.

API logs are available in `logs/app.log`.