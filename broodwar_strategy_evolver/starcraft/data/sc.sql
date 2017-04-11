-- COUNT REPLAYS
SELECT COUNT(*) FROM replay

-- LIST WINNERS BY RACE
SELECT RaceID, COUNT(*)
FROM replay, playerreplay
WHERE replay.ReplayID = playerreplay.ReplayID 
AND playerreplay.Winner = 1
GROUP BY RaceID;

-- COUNT GAMES WITH WINNER
SELECT COUNT(*)
FROM replay, playerreplay
WHERE replay.ReplayID = playerreplay.ReplayID 
AND playerreplay.Winner = 1;

-- LIST GAMES WITH WINNER
SELECT replay.ReplayID, replay.ReplayName, RaceID AS WinnerRace, PlayerName AS WinnerPlayerName
FROM replay, playerreplay
WHERE replay.ReplayID = playerreplay.ReplayID 
AND playerreplay.Winner = 1
LIMIT 10;

-- LIST WINS AND LOSSES FROM GAMES WITH WINNER
SELECT playrep.RaceID, playrep.Winner, COUNT(*)
FROM 
(
	SELECT replay.*
	FROM replay, playerreplay
	WHERE replay.ReplayID = playerreplay.ReplayID 
	AND playerreplay.Winner = 1
) rep, 
playerreplay AS playrep
WHERE rep.ReplayID = playrep.ReplayID 
GROUP BY playrep.Winner, playrep.RaceID;

-- LIST GAMES WITHOUT WINNER
SELECT * FROM replay
WHERE replay.ReplayID NOT IN
	(SELECT r.ReplayID
	FROM replay AS r, playerreplay AS pr
	WHERE r.ReplayID = pr.ReplayID 
	AND pr.Winner = 1)
LIMIT 10;

-- MAP POPULARITY
SELECT COUNT(winnerreplay.ReplayID) AS used, map.MapName 
FROM map, winnerreplay
WHERE map.MapID = winnerreplay.MapID
GROUP BY (map.MapName)
ORDER BY used DESC;

-- ALL UNIT EVENTS IN REPLAY
SELECT winnerreplay.ReplayName, playerreplay.PlayerName, event.Frame, SEC_TO_TIME(event.Frame / 23.81) AS time, event.UnitID, unit.UnitTypeID, event.EventTypeID 
FROM event, unit, winnerreplay, playerreplay
WHERE event.ReplayID = 2 
AND unit.UnitID = event.UnitID 
AND event.ReplayID = winnerreplay.ReplayID
AND winnerreplay.ReplayID = playerreplay.ReplayID
AND unit.PlayerReplayID = playerreplay.PlayerReplayID 
AND playerreplay.RaceID != 5
AND event.Frame != 0
AND (event.EventTypeID=13)
ORDER BY event.Frame ASC
LIMIT 30;

--AND (event.EventTypeID=13 OR event.EventTypeID=14)
-- Table size
SELECT (data_length+index_length)/power(1024,3) tablesize_gb FROM information_schema.tables WHERE table_schema='sc_pvt' and table_name='action';

------------
-- TABLES --
------------

CREATE TABLE eventtype
(
EventTypeID int NOT NULL,
EventName varchar(255) NOT NULL
);

CREATE TABLE unittype
(
UnitTypeID int NOT NULL,
UnitName varchar(255) NOT NULL,
RaceID int NOT NULL
);

CREATE TABLE race
(
RaceID int NOT NULL,
RaceName varchar(255) NOT NULL
);

-----------
-- VIEWS --
-----------

CREATE VIEW winnerreplay AS
SELECT replay.*, winner.RaceID AS WinnerRaceID, looser.RaceID AS LooserRaceID, winner.PlayerName as Winner, looser.PlayerName as Looser
FROM replay, playerreplay AS winner, playerreplay AS looser
WHERE replay.ReplayID = winner.ReplayID and replay.ReplayID = looser.ReplayID AND winner.Winner = 1 and looser.winner = 0 and looser.RaceID != 5

CREATE VIEW nowinnerreplay AS
SELECT *, NULL as WinnerRaceID, NULL as LooserRaceID, NULL as Winner, NULL as Looser FROM replay
WHERE ReplayID NOT IN (SELECT ReplayID FROM winnerreplay)

-- For PvT
CREATE VIEW allreplay AS
SELECT replay.*, a.RaceID AS ARaceID, b.RaceID AS BRaceID, a.PlayerName as A, b.PlayerName as B
FROM replay, playerreplay AS a, playerreplay AS b
WHERE replay.ReplayID = a.ReplayID and replay.ReplayID = b.ReplayID AND a.RaceID = 1 AND b.RaceID = 2

CREATE VIEW unitevent AS
SELECT
	winnerreplay.ReplayID,
	winnerreplay.WinnerRaceID,
	playerreplay.PlayerName,
	playerreplay.RaceID,
	eventtype.EventTypeName,
	unittype.UnitTypeName,
	event.Frame,
	event.UnitID,
	unit.UnitTypeID,
	event.EventTypeID
FROM
	event,
	unit,
	winnerreplay,
	playerreplay,
	eventtype,
	unittype
WHERE
	unit.UnitID = event.UnitID
	AND event.ReplayID = winnerreplay.ReplayID
	AND winnerreplay.ReplayID = playerreplay.ReplayID
	AND unit.PlayerReplayID = playerreplay.PlayerReplayID
	AND eventtype.EventTypeID = event.EventTypeID
	AND unittype.UnitTypeID = unit.UnitTypeID
	AND playerreplay.RaceID != 5
ORDER BY event.Frame ASC;

CREATE VIEW unitevent AS
SELECT
	allreplay.ReplayID,
	playerreplay.PlayerName,
	playerreplay.RaceID,
	eventtype.EventTypeName,
	unittype.UnitTypeName,
	event.Frame,
	event.UnitID,
	unit.UnitTypeID,
	event.EventTypeID
FROM
	event,
	unit,
	allreplay,
	playerreplay,
	eventtype,
	unittype
WHERE
	unit.UnitID = event.UnitID
	AND event.ReplayID = allreplay.ReplayID
	AND allreplay.ReplayID = playerreplay.ReplayID
	AND unit.PlayerReplayID = playerreplay.PlayerReplayID
	AND eventtype.EventTypeID = event.EventTypeID
	AND unittype.UnitTypeID = unit.UnitTypeID
	AND event.Frame != 0
ORDER BY event.Frame ASC;

-- FOR PvP
CREATE VIEW unitevent AS
SELECT
	replay.ReplayID,
	playerreplay.PlayerName,
	playerreplay.RaceID,
	playerreplay.PlayerReplayID,
	eventtype.EventTypeName,
	unittype.UnitTypeName,
	event.Frame,
	event.UnitID,
	unit.UnitTypeID,
	event.EventTypeID
FROM
	event,
	unit,
	replay,
	playerreplay,
	eventtype,
	unittype
WHERE
	unit.UnitID = event.UnitID
	AND event.ReplayID = replay.ReplayID
	AND replay.ReplayID = playerreplay.ReplayID
	AND unit.PlayerReplayID = playerreplay.PlayerReplayID
	AND eventtype.EventTypeID = event.EventTypeID
	AND unittype.UnitTypeID = unit.UnitTypeID
	AND event.Frame != 0
ORDER BY event.Frame ASC;

CREATE VIEW upgraderesearch AS
select
	replay.ReplayID,
	playerreplay.PlayerReplayID,
	playerreplay.PlayerName,
	playerreplay.RaceID,
	action.Frame,
	action.TargetID,
	unitcommandtype.UnitCommandName
from
	action,
	unitcommandtype,
	playerreplay,
	replay
WHERE
	action.UnitCommandTypeID = unitcommandtype.UnitCommandTypeID AND
	action.PlayerReplayID = playerreplay.PlayerReplayID AND
	replay.ReplayID = playerreplay.ReplayID AND
	playerreplay.RaceID != 5 AND
	(unitcommandtype.UnitCommandName = 'Upgrade' OR unitcommandtype.UnitCommandName = 'Research')

CREATE VIEW geyser AS
SELECT
    Frame AS Frame, TargetX, TargetY, UnitTypeID, UnitTypeName, ReplayID, RaceID
FROM
    action, unittype, playerreplay
WHERE
    playerreplay.PlayerReplayID = action.PlayerReplayID AND
    TargetID = unittype.UnitTypeID AND
    (TargetID = 157 OR TargetID = 110) AND
    playerreplay.RaceID != 5
ORDER BY Frame ASC

CREATE VIEW visibility AS
SELECT
    viewer.RaceID as ViewerRaceID,
    unit.UnitID,
    ChangeTime as Frame,
    UnitTypeName,
    unittype.UnitTypeID,
    playerreplay.RaceID as OwnerRaceID,
    replay.ReplayID
FROM
    playerreplay as viewer,
    visibilitychange,
    unit,
    unittype,
    playerreplay,
    replay
WHERE
    visibilitychange.ViewerID = viewer.PlayerReplayID AND
    playerreplay.PlayerReplayID = unit.PlayerReplayID AND
    replay.ReplayID = playerreplay.ReplayID AND
    unittype.UnitTypeID = unit.UnitTypeID AND
    viewer.RaceID != 5 AND
    playerreplay.RaceID != 5 AND
    unit.UnitID = visibilitychange.UnitID AND
    ChangeVal = 1
ORDER BY
    ChangeTime ASC;