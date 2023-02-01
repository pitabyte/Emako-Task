# Emako-Task

## First task

### API choice:
I decided to fetch weather data from two different APIs, because I wasn't able to find a single one that would have free access to both current weather and history weather.</br>

### Caching:
Only history data is cached, as every next 'current weather' call might have a different result.</br>

### CSV file fields choice:
History weather has TemperatureMax and TemperatureMin fields, but current weather only has Temperature field. For example if a 'current weather'
request happened at 1 AM, then saving TempMax and TempMin in a file for that day could be misleading for future use, because those values can be very different as the
day progresses. 

Essentially 'history weather' and 'current weather' are different from each other, hence the division.

