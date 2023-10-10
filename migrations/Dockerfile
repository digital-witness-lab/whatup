FROM migrate/migrate

# Copy the migrations to its own folder,
# then restore the working dir of the
# upstream image.
WORKDIR /migrations

# Add python3 package so we can encode the DB URL.
# https://github.com/golang-migrate/migrate#database-urls
RUN apk add --no-cache python3 tini

COPY . .

RUN chmod +x ./run_migrations.sh

WORKDIR /go/src/github.com/golang-migrate/migrate

ENTRYPOINT ["/sbin/tini", "--"]
