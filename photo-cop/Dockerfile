ARG CONFIGURE_VM_SECRETS_REPO=configure-vm-secrets:latest
ARG LOG_CLEANER_REPO=log-cleaner:latest

FROM $CONFIGURE_VM_SECRETS_REPO AS configure-vm-secrets
FROM $LOG_CLEANER_REPO AS log-cleaner

FROM gradle:8.9.0-jdk21-jammy AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src

RUN --mount=type=cache,target=/home/gradle/.gradle/caches/ \
    gradle build --no-daemon 

FROM ibmjava:8-jre

EXPOSE 50051

RUN mkdir /app

COPY ./run.sh /app/
COPY --from=build /home/gradle/src/build/libs/photocop*.jar /app/photocop.jar
COPY --from=build /home/gradle/src/build/libs/photocop*.jar /app/

COPY --from=configure-vm-secrets /configureVmSecrets /configureVmSecrets
COPY --from=log-cleaner /log-cleaner /log-cleaner

ENTRYPOINT ["/app/run.sh"]
