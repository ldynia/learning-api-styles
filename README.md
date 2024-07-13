<div align="center">
  <a href="https://learningapistyles.com" target="_blank" title="Learning API Styles">
    <img src="./assets/cover.png" width="50%" style="box-shadow: 1px 1px 2px #000;" alt="Learning API Styles"/>
  </a>
</div>

This repository provides supplementary content for the book.
You'll find material that wasn't included in the book, along with selected examples.
We also recorded the examples as videos, which can be found in [this YouTube playlist](https://www.youtube.com/playlist?list=PLRkB-vSK4koOHYIhpKXuXpipVpByEKuPu).

For more information about the book, visit [learningapistyles.com](https://learningapistyles.com)

## Table of Contents

| Chapter | Tests |
|---|---|
| 1. API Concepts |  |
| 2. API Design |  |
| 3. [Network](./src/network/README.md) | [![src/network](https://github.com/ldynia/learning-api-styles/actions/workflows/src-network-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-network-tests.yaml) |
| 4. [Web Protocols](./src/http/README.md) | [![src/http](https://github.com/ldynia/learning-api-styles/actions/workflows/src-http-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-http-tests.yaml) |
| 5. [REST](./src/django/docs/REST.md) | [![src/django rest](https://github.com/ldynia/learning-api-styles/actions/workflows/src-rest-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-rest-tests.yaml) |
| 6. [GraphQL](./src/django/docs/GRAPHQL.md) | [![src/django graphql](https://github.com/ldynia/learning-api-styles/actions/workflows/src-graphql-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-graphql-tests.yaml) |
| 7. [Web Feeds](./src/django/docs/WEB-FEEDS.md) | [![src/django atom](https://github.com/ldynia/learning-api-styles/actions/workflows/src-atom-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-atom-tests.yaml) |
| 8. [gRPC](./src/grpc/README.md) | [![src/grpc](https://github.com/ldynia/learning-api-styles/actions/workflows/src-grpc-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-grpc-tests.yaml) |
| 9. [Webhooks](./src/django/docs/WEBHOOKS.md) | [![src/django webhooks](https://github.com/ldynia/learning-api-styles/actions/workflows/src-webhooks-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-webhooks-tests.yaml) |
| 10. [WebSocket](./src/django/docs/WEBSOCKET.md) | [![src/django websocket](https://github.com/ldynia/learning-api-styles/actions/workflows/src-websocket-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-websocket-tests.yaml) |
| 11. [Messaging](./src/rabbitmq/README.md) | [![src/messaging](https://github.com/ldynia/learning-api-styles/actions/workflows/src-messaging-tests.yaml/badge.svg)](https://github.com/ldynia/learning-api-styles/actions/workflows/src-messaging-tests.yaml) |

## System Overview

The weather forecast service (WFS) is a Django-based application that aggregates the majority of API styles described in this book.
Illustrated below, the [C4 container diagram](https://c4model.com/) shows WFS' main actors and components.

<figure>
  <img src="./src/django/docs/assets/app-design/wfs-c4-container.png" alt="WFS C4 container diagram" title="WFS C4 container diagram">
</figure>
