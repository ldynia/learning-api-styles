Feature: City Weather Forecast

  As a user
  I want to view the weather forecast page for a specific city
  so that I can plan my activities

  Scenario: Retrieve the city's weather forecast page as HTML
    Given a city
    When the city's weather forecast page is requested
    Then the page is loaded successfully
    And it is an HTML page

  Scenario: Fail to retrieve the weather forecast page for a non-existent city
    Given a non-existent city
    When the non-existent city's weather forecast page is requested
    Then the page is not found
