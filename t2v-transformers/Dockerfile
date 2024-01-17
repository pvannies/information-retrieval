FROM semitechnologies/transformers-inference:custom

ARG T2V_TRANSFORMERS_MODEL_NAME

# TODO: add --start-interval=1s to speed up - feature not in Docker Desktop yet https://github.com/docker/cli/issues/4486
HEALTHCHECK --interval=60s --timeout=3s --start-period=30s \
  CMD curl -f http://localhost:8080/.well-known/ready

RUN apt-get -y update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Write the model name to a file so we can show at run time which model was used to create this container.
RUN echo "$T2V_TRANSFORMERS_MODEL_NAME" > /model_name.txt
RUN MODEL_NAME=$T2V_TRANSFORMERS_MODEL_NAME ./download.py

COPY --chmod=755 docker/entrypoint.sh /
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run"]
