# CLI HTTP Client

This tool is a custom-built HTTP client operated via the command line. It supports URL validation, method selection, custom headers, query parameters, body payloads, file input, and response parsing.

## Implemented Features

- **URL Handling**  
  The client validates and accepts standard HTTP/HTTPS URLs. Improperly formed URLs trigger an error and halt execution.

- **HTTP Methods**  
  Supported methods include: `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`. Any unsupported method results in an error.

- **Headers**  
  Custom headers can be passed using repeated `--headers` or `-H` arguments. Multiple key-value pairs are accepted per flag, comma-separated. Later headers override earlier ones with the same key. All headers are normalized to lowercase before dispatch.

- **Query Parameters**  
  Query parameters can be set using `--query` or `-Q` with the same format and behavior as headers. Parameters are automatically appended to the provided URL.

- **Body Data**  
  The `--data` or `-D` flag sets the request body in `application/x-www-form-urlencoded` format. The structure is not corrected; if invalid, a warning is displayed. The client still sends the data as-is.

- **JSON Support**  
  The `--json` flag enables sending raw JSON data. It sets the `Content-Type: application/json` header unless explicitly overridden. Invalid JSON does not block the request but generates a warning.

- **File Uploads**  
  The `--file` flag accepts a file path to use as the body payload. If no content type is specified, it defaults to `application/octet-stream`. Header precedence is respected.

- **Timeouts**  
  The `--timeout` flag defines the max wait time (in seconds) for receiving the first response byte. The client aborts requests exceeding this limit and notifies the user. The timeout applies only during the waiting phase, not during data reception.

- **Response Handling**  
  The client prints response status code, message, headers, and body with readable formatting. If the response body is binary or a known file type (e.g., PDF, image), the body is dumped to console and optionally saved (if implemented).

- **Loading Indicator (Optional Feature)**  
  A loading bar or percentage animation is shown from request initiation until the full response is received. This feature is compatible with timeout tracking.

- **Error Handling and Warnings**  
  All inputs are validated. Errors (e.g., malformed URLs, invalid methods) halt execution. Non-blocking issues (e.g., malformed body format) trigger warnings but do not stop the request.

## Behavior Summary

The client operates via a single-step CLI execution. All parameters must be passed explicitly. No interactive prompts are used. Input parsing supports repeated and compound arguments. The tool mimics the behavior of `curl` while offering structured validation and layered override logic for headers and content types.
