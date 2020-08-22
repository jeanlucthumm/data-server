SELECT name, DATETIME(startTime, 'unixepoch', 'localtime')
FROM Tasks
WHERE startTime > DATE('2020-08-05')
ORDER BY startTime DESC;
