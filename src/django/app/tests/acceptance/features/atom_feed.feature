Feature: Weather Forecast as an Atom Feed

  As a user
  I want to subscribe to the weather forecast via an Atom feed
  so that I can stay informed about the latest updates

  Scenario: Retrieve the weather forecast as an Atom feed
    Given the URL to the weather forecast's Atom feed
    When the feed is requested
    Then the feed is returned successfully
    And it is in Atom feed format
