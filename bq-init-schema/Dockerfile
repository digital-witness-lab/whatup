FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

COPY run.sh /
RUN chmod +x /run.sh

ARG ENVIRONMENT="dev"
ENV ENVIRONMENT=$ENVIRONMENT

CMD ["/run.sh"]
