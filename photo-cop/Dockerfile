FROM gradle:8.9.0-jdk21-jammy AS build
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src

RUN --mount=type=cache,target=/home/gradle/.gradle/caches/ \
    gradle build --no-daemon 

FROM ibmjava:8-jre

EXPOSE 8080

RUN mkdir /app

COPY --from=build /home/gradle/src/build/libs/photocop*.jar /app/photocop.jar
COPY --from=build /home/gradle/src/build/libs/photocop*.jar /app/

ENTRYPOINT ["java", "-XX:+UnlockExperimentalVMOptions", "-XX:+UseCGroupMemoryLimitForHeap", "-Djava.security.egd=file:/dev/./urandom","-jar","/app/photocop.jar"]
