#language:en
@suiteId:59
Feature: test

@tc:58
Scenario: If it fits it sits
    Given that the cat found a place
    And the place is called Shelf
    And it fits
    When it try to sit
    Then it says "Sitting in the shelf"