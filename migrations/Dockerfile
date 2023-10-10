FROM migrate/migrate

# Add python3 package so we can encode the DB URL.
# https://github.com/golang-migrate/migrate#database-urls
RUN apk add --no-cache python3 tini bash

WORKDIR /migrations

COPY *.sql .

WORKDIR /

COPY *.sh .

RUN chmod +x ./run_migrations.sh

ENTRYPOINT ["/sbin/tini", "--"]
