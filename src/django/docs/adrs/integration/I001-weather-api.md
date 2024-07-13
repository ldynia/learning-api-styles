### Title

3rd party weather API

### Date

05.08.2023

### Status

ACCEPTED

### Context

The WFS needs to provide real data for current, future and past weather events. Therefore, we need to choose a 3rd party weather API that will provide this data. The API should be free to use and provide the following:

- Current weather data
- Forecast weather data
- Historical weather data

### Decision

We will use https://open-meteo.com API.

### Consequences

#### Positive

* The API is free to use and provides all the data we need.

#### Negative

* The API has limits on the number of requests per day.

#### Risks

* API might be discontinued in the future.
* Reaching daily limits might be a problem.
