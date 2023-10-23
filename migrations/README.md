# DB Migrations

We use [`golang-migrate/migrate`](https://github.com/golang-migrate/migrate) to apply DB migrations.
Each new migration file must follow this format:

```
<seq>_<name>.up.sql
```

...where `<seq>` is the next number in the sequence.
