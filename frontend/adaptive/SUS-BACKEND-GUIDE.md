# SUS Survey Backend Guide

## Purpose

The frontend submits a completed System Usability Scale (SUS) questionnaire so the backend can validate, score, and store the result. Implement `POST /api/sus` for this flow.

## Request

The frontend sends exactly ten integer ratings, in question order. Each rating must be from 1 (strongly disagree) to 5 (strongly agree).

```http
POST /api/sus
Content-Type: application/json
X-Session-Id: <temporary-session-id>
```

```json
{
  "questionnaire": "SUS",
  "version": "brooke-1996",
  "answers": [4, 2, 4, 1, 5, 2, 4, 1, 4, 2]
}
```

The request does not include conversation messages, the participant's name, or other direct identity fields. Treat `X-Session-Id` as a pseudonymous session identifier, not as proof of identity. The survey is submitted only when the participant presses **Submit answers**.

## Validation and scoring

- Accept only `questionnaire: "SUS"`, `version: "brooke-1996"`, and an `answers` array containing exactly ten integer values from 1 through 5.
- Preserve the raw answers in question order.
- Score odd-numbered items (1, 3, 5, 7, 9) as `answer - 1`.
- Score even-numbered items (2, 4, 6, 8, 10) as `5 - answer`.
- Sum the ten adjusted values and multiply by 2.5. Store the resulting SUS score on the 0–100 scale; it is not a percentage.

For example, `[4, 2, 4, 1, 5, 2, 4, 1, 4, 2]` produces adjusted values `[3, 3, 3, 4, 4, 3, 3, 4, 3, 3]`, totaling 33, for a SUS score of 82.5.

## Storage

Store one record per accepted submission with:

- A server-generated submission ID
- Questionnaire name and version
- The ten raw answers
- The calculated SUS score
- The `X-Session-Id` value, if provided
- A server-generated UTC submission timestamp

Do not store conversation history with the SUS response. Configure CORS to allow the `X-Session-Id` request header.

## Response and errors

Return `201 Created` after the response is stored:

```json
{
  "status": "accepted",
  "submission_id": "generated-id"
}
```

Return `400 Bad Request` for invalid questionnaire fields or ratings. Return a server error if storage fails. The frontend displays a success message only for an HTTP success response; on failure it keeps the answers in the open modal and allows the participant to retry.
