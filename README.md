# Video Game Soundstrack Server

This is a temporary, dirty, companion project to [vgsgo](https://github.com/boberle/vgsgo) (video game soundtrack player in go). It just distributes audio files and ratings remotely.

The endpoints are:

- `/songs/random/` (get): get a random song. Return a JSON:

```json
{
  "id": "md5 hash of the `path` property",
  "title": "Song Title",
  "game_title": "Game Title",
  "duration": 123.456,
  "loop_start": 123,
  "loop_end": 123,
  "path": "path/to/song.brstm"
}
```

- `/songs/SONG_ID/file/` (get): return bytes
- `/songs/SONG_ID/play/` (post), the body has the format:

```json
{
  "timestamp": 123,
  "rating": 1
}
```

The rating is an integer between 0 and 5 (incl.).

- `/ratings/export/` (get): return a JSON with the ratings (see `vgsgo`)
- `/ratings/import/` (post): import a JSON with the ratings (see `vgsgo`)

All the endpoints are protected by a basic authentication scheme. Just add a header `Authorization` with a `Basic` scheme.

To run the server:

```bash
PYTHONPATH=src VGSSERVER_METADATA_PATH=/path/to/metadata.json VGSSERVER_USER_PATH=/path/to/users.json VGSSERVER_RATING_DIR_PATH=/path/to/ratings/ uvicorn app:app
```

The metadata and rating file formats is describe in `vgsgo`.

The user file is a JSON file like this:

```json
[
  {
    "username": "testuser",
    "password_hash": "$2b$12$0BR.NH/SzWS5Bs7B326u.eYkEootgGnAT5Gx5RxjEOOy472EzYLEi"
  }
]
```

`VGSSERVER_RATING_DIR_PATH` is a directory that is created if it doesn't exist and contain a rating file for each user (using the username).


## Want to talk?

Contact me at bruno@boberle.com.
