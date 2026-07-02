Feature: Task management
  A pet owner keeps each pet's care tasks organized and up to date.

  Scenario: Scheduling a care task for a pet
    Given an owner with a dog named Mochi
    When the owner schedules a "Morning walk" at "08:00" for Mochi
    Then Mochi has 1 task on their list

  Scenario: Completing a care task
    Given an owner with a dog named Mochi
    And Mochi has a "Morning walk" task at "08:00"
    When the owner marks the "Morning walk" task complete
    Then the "Morning walk" task is completed
