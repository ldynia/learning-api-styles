# Exercise 1

The documentation section of this chapter describes how to create OAS using a semi-manual approach, and how to convert it to [Swagger UI](https://swagger.io/tools/swagger-ui) but without an external library. A rendered Swagger UI must be accessible at [localhost:8080](http://localhost:8080). Hint: Use [swaggerapi/swagger-ui](https://hub.docker.com/r/swaggerapi/swagger-ui) Docker image.

## Solution

```bash
curl -so wfs.manual.schema.yaml http://localhost:8000/api/docs/v1/schema/manual
docker run --rm -v .:/usr/src/ -p 8080:8080 -e SWAGGER_JSON#/usr/src/wfs.manual.schema.yaml swaggerapi/swagger-ui
```

# Exercise 2

OAS has a well-established position in the API specification space. In this exercise, you will try an alternative solution to OAS, which is [ReDoc](https://redoc.ly/). Your task is to convert the OAS to an HTML page using the _redoc_ CLI.

## Solution

```bash
curl --silent --output schema.yaml http://localhost:8000/api/docs/v1/schema/manual
docker run -it --rm \
       --publish 8888:80 \
       --env SPEC_URL=schema.yaml \
       --volume ${PWD}/schema.yaml:/usr/share/nginx/html/schema.yaml \
       redocly/redoc
```
