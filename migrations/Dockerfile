FROM migrate/migrate

# Add python3 package so we can encode the DB password.
# https://github.com/golang-migrate/migrate#database-urls
RUN apk add --no-cache python3 tini bash

WORKDIR /

COPY ./migrations/ /migrations/
COPY *.sh .

RUN chmod +x ./run_migrations.sh

ENTRYPOINT ["/sbin/tini", "--"]
