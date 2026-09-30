# tg-mover

Moves messages from one Telegram channel to another **without the "Forwarded from" header**:
each message is copied to the destination, then deleted from the source.
Optionally only messages matching a regex are moved; the rest stay untouched.
Runs as your user account (via [Telethon](https://docs.telethon.dev)), so it can read full channel history.

## Setup

1. Get `api_id` and `api_hash` at <https://my.telegram.org> → *API development tools*.
2. Install deps:

   ```sh
   uv sync
   ```

3. Fill in credentials in `.env` (git-ignored):

   ```sh
   cp .env.example .env
   ```

   ```
   TG_API_ID=123456
   TG_API_HASH=abcdef...
   MATCH_REGEX=
   ```

### Filter (`MATCH_REGEX`)

- Empty or unset → **all** messages are moved.
- Set → only messages whose text matches (case-insensitive) are moved. Hidden links (`[label](url)`) count too.
- Wrap the value in single quotes so backslashes stay literal. Example — x.com / twitter.com / instagram.com links:

  ```
  MATCH_REGEX='(?<![\w.-])(?:https?://)?(?:www\.|mobile\.|m\.)?(?:x|twitter|instagram)\.com/'
  ```

The script prints the active filter on start, so you can check it before anything moves (Ctrl+C to abort).

## Usage

```sh
uv run --env-file .env tg-mover @source_channel @dest_channel
```

- Channels can be `@username`, a `t.me/...` link, or a numeric id (private channels: `-1001234567890`).
- You must be an admin with **delete messages** rights in the source and able to post in the destination.
- Run from the project folder: `.env` and the session file are looked up in the current directory.
- First run asks for your phone number and login code, then saves `tg_mover.session`.
  Keep it private — it is a logged-in session (already in `.gitignore`).

## Notes

- Messages are copied oldest → newest; service messages (pins, title changes) are skipped.
- Albums arrive as separate messages.
- **Deletion is permanent.** A source message is deleted only after it was copied successfully;
  failed copies stay in the source and are logged as `skipped`.
- Re-running is safe: moved messages are gone from the source, so only leftovers are retried.
- Paced at a random 2–5 s per moved message (`DELAY` in `src/tg_mover/cli.py`) to avoid account limits;
  ~1000 messages ≈ 1 hour. Flood-wait limits from Telegram are also waited out automatically.
- Tests: `uv run python tests/test_filter.py`.
