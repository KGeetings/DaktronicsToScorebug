//
//  Add any player guids whose names should be hidden from iScorecasts
//
var _g_hide_players = {
	'EXP_10112': true
};

var _game;

var POSSESSION_HOME_TEAM = 0
var POSSESSION_VISITOR_TEAM = 1

var EVENT_GAME_START = "GS";

var _ignore = 0;

function timeFromSeconds(seconds) {
	var seconds = parseInt(seconds);
	var secs = (seconds % 60);
	var secStr = "" + secs;
	if (secs < 10) secStr = "0" + secs;

	return "" + Math.floor(seconds / 60) + ":" + secStr;

}

function FBEvent(type, b, f) {
	this.m_type = type;

	this.type = type;
	this.player = b;
	this.param = f;

	this.getType = function () { return this.m_type; }
	this.getPlayer = function () { return this.player; }
	this.getParam = function () { return this.param; }

}

function Shot(x, y, pts) {
	this.x = x;
	this.y = y;
	this.pts = pts;

	this.tx = 0;
	this.ty = 0;
}

function StatsRecord() {
	this.games = 0;
	this.points = 0;
	this.fouls = 0;
	this.assists = 0;
	this.rebounds = 0;
	this.fga3 = 0;
	this.fgm3 = 0;
	this.fga2 = 0;
	this.fgm2 = 0;
	this.fta = 0;
	this.ftm = 0;
	this.blocks = 0;
	this.steals = 0;
	this.turnovers = 0;
	this.offRebounds = 0;
	this.defRebounds = 0;
	this.deflections = 0;
	this.pm = 0;

}

function PlayerGameRecord() {
	this.playerName;
	this.playerGuid;
	this.playerGameGuid;
	this.playerNumber;
	this.fieldingPosition;
	this.battingPosition;
	this.isStarter;

	this.statsToday = new StatsRecord();
	this.statsCareer = new StatsRecord();
	this.shots = new Array();

	this.addShot = function (x, y, pts) {
		this.shots[this.shots.length] = new Shot(x, y, pts);
	}

	this.getDisplayNameWithNumber = function () {
		//	alert(this.playerNumber);
		var str = "";
		if (this.playerNumber == 100)
			str = "#00 " + this.playerName;
		else if (this.playerNumber < 1)
			str = this.playerName;
		else
			str = "#" + this.playerNumber + " " + this.playerName;

		return "<A HREF='javascript:void(null);' onclick='showIndividualStats(event,\"" + this.playerGameGuid + "\");'>" + str + "</A>";

	}
}

function FBUpdateRecord(index, status, stats, ts) {
	this.m_index = index;
	this.m_status = status;
	this.m_ts = ts;

	this.callSound = 0;
	this.sndType = 0;
	// Initialize events for this update record
	this.m_events = new Array();

	// Add an event to this update record
	this.addEvent = function (event) { this.m_events[this.m_events.length] = event; }

	this.getIndex = function () { return this.m_index; }
	this.getStatus = function () { return this.m_status; }

	var arr = this.m_status.split(",");
	//alert(this.m_status);
	this.timeSeconds = parseInt(arr[0]);
	this.jumpPossession = parseInt(arr[1]);
	this.overtime = parseInt(arr[2]);
	this.period = parseInt(arr[3]);
	this.homeScore = parseInt(arr[4]);
	this.visitorScore = parseInt(arr[5]);
	this.possession = parseInt(arr[6]);
	this.playerPossession = arr[7];
	this.homeFouls = parseInt(arr[8]);
	this.visitorFouls = parseInt(arr[9]);
	this.playerX = parseInt(arr[10]);
	this.playerY = parseInt(arr[11]);
	this.homeOnLeft = parseInt(arr[12]) == 1;

	this.shotPlayer = "";
	this.stealPlayer = "";
	this.deflectPlayer = "";

	this.getPlayerByGuid = function (guid) {
		return _game.getPlayerByGuid(guid);
	}

	this.getPlayerLink = function (playerStr) {
		var playerGuid = "";
		var players = playerStr.split(",");
		if (players.length > 0)
			playerGuid = players[0];

		var pgr = this.getPlayerByGuid(playerGuid);
		if (pgr == null) return "Unknown Player";
		var pName = pgr.getDisplayNameWithNumber();
		if (playerGuid == null)
			return pName;
		return "<a class='pbp-link' href='javascript:void(null)' onClick='showIndividualStats(event,\"" + playerGuid + "\")'>" + pName + "</a>";

	}


	this.htmlClock = function () {
		var secs = (this.timeSeconds % 60);
		var secStr = "" + secs;
		if (secs < 10) secStr = "0" + secs;

		return "" + Math.floor(this.timeSeconds / 60) + ":" + secStr;
	}

	this.hasEvent = function (eventType) {
		for (var i = 0; i < this.m_events.length; i++) {
			var ev = this.m_events[i];
			if (ev.m_type == eventType) return true;
		}

		return false;
	}

	this.hasEventWithParam = function (eventType, param) {
		for (var i = 0; i < this.m_events.length; i++) {
			var ev = this.m_events[i];
			if (ev.m_type == eventType && ev.param == param) return true;
		}

		return false;
	}

	this.hasShot = function () {
		if (this.hasEvent("FG") || this.hasEvent("MISS") || this.hasEvent("BLOCKED"))
			return true;
		return false;
	}

	this.hasSteal = function () {
		if (this.hasEventWithParam("TURNOVER", "STEAL"))
			return true;
		return false;
	}

	this.hasDeflection = function () {
		if (this.hasEvent("DEFLECTION"))
			return true;
		return false;
	}


	this.getDisplayNameWithNumber = function (player) {
		if (player != null)
			return player.getDisplayNameWithNumber();
		else
			return "Unknown Player";
	}


	this.getShooter = function () {
		return this.getPlayerByGuid(this.shotPlayer);

	}

	this.getStealer = function () {
		return this.getPlayerByGuid(this.stealPlayer);

	}

	this.getDeflector = function () {
		return this.getPlayerByGuid(this.deflectPlayer);

	}

	// Display the HTML for this update record
	this.getHtml = function (lastur) {
		var updateStats = true;
		if (lastur == null)
			updateStats = false;
		try {
			//alert(this.pitchType+":"+this.pitchSpeed+":"+this.pitchX+":"+this.pitchY);

			var vTeam = _game.getVisitorTeamName();
			var hTeam = _game.getHomeTeamName();

			var html = new StringBuilder("");
			var notesText = new StringBuilder("");
			var playName = "";
			var pitchText = "";

			var pAtBat = 0;

			var playerList = _game.playerList;

			if (lastur != null) {
				//if(this.period!=lastur.period)
				//	update = true;
				//alert(this.visitorScore)
				if (lastur.overtime == 0) {
					_game.calc_periods = lastur.period;
				}
				_game.t_visitorPoints[lastur.period] = this.visitorScore;
				_game.t_homePoints[lastur.period] = this.homeScore;
			}

			//alert(pAtBat);


			var fieldErrors = new Object();
			if (this.m_events != null) {
				for (var j = 0; j < this.m_events.length; j++) {
					var ev = this.m_events[j];
					//alert(ev.type);
					if (ev.type == "GS") {
						pitchText += "Game Starts";


						currentHomeList = new Array();
						currentVisitorList = new Array();

						_game.visitorPlayersArray = new Array();
						_game.homePlayersArray = new Array();

						var visitorStr = ev.param;
						//var index = visitorStr.indexOf(":");
						//visitorTeamName = visitorStr.substring(0,index);
						//visitorStr = visitorStr.substring(index+1);
						var p = visitorStr.split(",");
						for (var k = 0; k < p.length; k++) {
							var playerInfo = p[k].split(":");
							if (k == 0 && playerInfo.length == 7) {
								visitorTeamName = playerInfo[0];
								playerInfo.splice(0, 1);	//weird issue with GS where first item has Team Name:
							}

							var isStarter = parseInt(playerInfo[4]) == 1;

							var newPlayerInfo = new PlayerGameRecord();
							newPlayerInfo.playerGuid = playerInfo[0];
							newPlayerInfo.playerGameGuid = playerInfo[1];
							newPlayerInfo.playerNumber = parseInt(playerInfo[2]);
							newPlayerInfo.playerName = (_g_hide_players[newPlayerInfo.playerGuid] ? "-----" : unescape(playerInfo[5]));
							//							newPlayerInfo.playerName = unescape(playerInfo[5]);
							newPlayerInfo.playerLabel = "#" + newPlayerInfo.playerNumber + " " + newPlayerInfo.playerName;
							newPlayerInfo.position = parseInt(playerInfo[3]);
							newPlayerInfo.active = isStarter;

							playerList[newPlayerInfo.playerGameGuid] = newPlayerInfo;
							currentVisitorList[currentVisitorList.length] = newPlayerInfo;

							_game.visitorPlayers[newPlayerInfo.playerGameGuid] = newPlayerInfo;
							_game.visitorPlayersArray[_game.visitorPlayersArray.length] = newPlayerInfo;
						}

						var newPlayerInfo = new PlayerGameRecord();
						newPlayerInfo.playerGuid = "TEAM_VISITOR";
						newPlayerInfo.playerGameGuid = "TEAM_" + _game.m_vtg;
						newPlayerInfo.playerNumber = "";
						newPlayerInfo.playerName = "Team";
						newPlayerInfo.playerLabel = newPlayerInfo.playerNumber + " " + newPlayerInfo.playerName;
						newPlayerInfo.position = "";
						newPlayerInfo.active = false;

						playerList[newPlayerInfo.playerGameGuid] = newPlayerInfo;
						currentVisitorList[currentVisitorList.length] = newPlayerInfo;

						_game.visitorPlayers[newPlayerInfo.playerGameGuid] = newPlayerInfo;
						_game.visitorPlayersArray[_game.visitorPlayersArray.length] = newPlayerInfo;

						var homeStr = ev.player;
						//var index = homeStr.indexOf(":");
						//homeTeamName = homeStr.substring(0,index);
						//homeStr = homeStr.substring(index+1);
						p = homeStr.split(",");
						//						p = ev.player.split(",");
						for (var k = 0; k < p.length; k++) {
							var playerInfo = p[k].split(":");
							if (k == 0 && playerInfo.length == 7) {
								visitorTeamName = playerInfo[0];
								playerInfo.splice(0, 1);	//weird issue with GS where first item has Team Name:
							}

							var isStarter = parseInt(playerInfo[4]) == 1;

							var newPlayerInfo = new PlayerGameRecord();
							newPlayerInfo.playerGuid = playerInfo[0];
							newPlayerInfo.playerGameGuid = playerInfo[1];
							newPlayerInfo.playerNumber = parseInt(playerInfo[2]);
							newPlayerInfo.playerName = (_g_hide_players[newPlayerInfo.playerGuid] ? "-----" : unescape(playerInfo[5]));
							//							newPlayerInfo.playerName = unescape(playerInfo[5]);
							newPlayerInfo.playerLabel = "#" + newPlayerInfo.playerNumber + " " + newPlayerInfo.playerName;
							newPlayerInfo.position = parseInt(playerInfo[3]);
							newPlayerInfo.active = isStarter;

							playerList[newPlayerInfo.playerGameGuid] = newPlayerInfo;
							currentHomeList[currentHomeList.length] = newPlayerInfo;

							_game.homePlayers[newPlayerInfo.playerGameGuid] = newPlayerInfo;
							_game.homePlayersArray[_game.homePlayersArray.length] = newPlayerInfo;
						}

						var newPlayerInfo = new PlayerGameRecord();
						newPlayerInfo.playerGuid = "TEAM_HOME";
						newPlayerInfo.playerGameGuid = "TEAM_" + _game.m_htg;
						newPlayerInfo.playerNumber = "";
						newPlayerInfo.playerName = "Team";
						newPlayerInfo.playerLabel = newPlayerInfo.playerNumber + " " + newPlayerInfo.playerName;
						newPlayerInfo.position = "";
						newPlayerInfo.active = false;

						playerList[newPlayerInfo.playerGameGuid] = newPlayerInfo;
						currentHomeList[currentHomeList.length] = newPlayerInfo;

						_game.homePlayers[newPlayerInfo.playerGameGuid] = newPlayerInfo;
						_game.homePlayersArray[_game.homePlayersArray.length] = newPlayerInfo;
					}
					else if (ev.type == "GE") {
						pitchText += "Game Over. ";
						_game.gameOver = true;

					}
					else if (ev.type == "SUB") {
						if (pitchText.indexOf("Substitution") == -1)
							pitchText += "Substitution ";
						hasSub = true;
						var count = 1;
						var param = ev.param;
						var subPlayers = ev.player.split(",");

						var teamPlayerList;
						if (param == "HOME")
							teamPlayerList = currentHomeList;
						else
							teamPlayerList = currentVisitorList;

						for (var i = 0; i < teamPlayerList.length; i++)
							teamPlayerList[i].active = false;

						pitchText += " " + param + ": ";
						for (var i = 0; i < subPlayers.length; i++) {
							playerList[subPlayers[i]].active = true;
							if (i > 0)
								pitchText += ", ";
							pitchText += this.getPlayerLink(subPlayers[i])
						}
						/*
						var sortList = new Array();
						for(var i=teamPlayerList.length-1;i>=0;i--)
						{
							if(teamPlayerList[i].active)
								sortList.addItemAt(teamPlayerList[i],0);
							else
								sortList.addItem(teamPlayerList[i]);
						}
						if(param=="HOME")
							currentHomeList = sortList.source;
						else
							currentVisitorList = sortList.source;
						*/
						if (param == "HOME")
							currentHomeList = teamPlayerList;
						else
							currentVisitorList = teamPlayerList;

						pitchText += " are now in.";
					}
					else {
						//if(lastur==null)
						//	return;

						var offPlayerName = "Offensive Player";
						var secPlayerName = "Defender";
						var offPlayer = playerList[this.playerPossession];
						//alert(this.playerPossession+":"+offPlayer);
						if (offPlayer != null)
							offPlayerName = this.getPlayerLink(this.playerPossession);//offPlayer.playerLabel
						var secPlayer = playerList[ev.player];
						if (secPlayer != null)
							secPlayerName = this.getPlayerLink(ev.player);//secPlayer.playerLabel
						if (ev.type == "FG") {
							hasShot = true;
							madeShot = true;

							if (playerList[ev.player] == null)
								;//alert(ev.player);

							if (updateStats) {
								playerList[ev.player].statsToday.points += parseInt(ev.param);
								if (ev.param == "3") {
									playerList[ev.player].statsToday.fga3++;
									playerList[ev.player].statsToday.fgm3++;
									playerList[ev.player].addShot(this.playerX, this.playerY, 3);
								}
								else {
									playerList[ev.player].statsToday.fga2++;
									playerList[ev.player].statsToday.fgm2++;
									playerList[ev.player].addShot(this.playerX, this.playerY, 2);
								}
							}

							pitchText += offPlayerName + " makes a " + ev.param + " point shot ";
							this.shotPlayer = this.playerPossession;
						}
						else if (ev.type == "MISS") {
							hasShot = true;
							madeShot = false;

							if (playerList[ev.player] == null) {
								//							alert(ev.player);
							}

							if (updateStats) {
								if (ev.param == "3") {
									playerList[ev.player].statsToday.fga3++;
								}
								else {
									playerList[ev.player].statsToday.fga2++;
								}
								playerList[ev.player].addShot(this.playerX, this.playerY, 0);
							}

							pitchText += secPlayerName + " misses a " + ev.param + " point shot ";
							this.shotPlayer = ev.player;
						}
						else if (ev.type == "PUTBACK") {
							if (playerList[ev.player] == null)
								pitchText = "A putback is made";
							else
								pitchText += secPlayerName + " makes a putback";

							if (updateStats) {
								playerList[ev.player].statsToday.points += 2;
								playerList[ev.player].statsToday.fga2++;
								playerList[ev.player].statsToday.fgm2++;
								playerList[ev.player].statsToday.rebounds++;
								playerList[ev.player].statsToday.offRebounds++;
							}

							this.shotPlayer = ev.player;
						}
						else if (ev.type == "ASSIST") {
							if (updateStats)
								playerList[ev.player].statsToday.assists++;

							if (secPlayerName != "Defender")
								pitchText += secPlayerName + " gets an assist ";
							//pitchText += " with an assist by " + secPlayerName;
						}
						else if (ev.type == "GOALTEND") {
							pitchText += " while " + secPlayerName + " is charged with goaltending ";
						}
						else if (ev.type == "BLOCKED") {
							var blocker = secPlayer;

							var player = offPlayer;
							if (player == null && blocker == null && ev.param.length == 0)
								pitchText = "A shot is blocked";
							else {
								if (ev.param.length == 0)
									pitchText = offPlayerName + " blocks a shot. ";
								else {
									if (player != null) {
										if (blocker == null)
											pitchText = "The " + ev.param + " point shot by " + offPlayerName + " is blocked. ";
										else
											pitchText = "The " + ev.param + " point shot by " + offPlayerName + " is blocked by " + secPlayerName + ". ";

									}
									else {
										if (blocker == null)
											pitchText = "The " + ev.param + " point shot is blocked. ";
										else
											pitchText = "The " + ev.param + " point shot is blocked by " + secPlayerName + ". ";
									}
								}
							}


							if (updateStats) {
								playerList[this.playerPossession].statsToday.fga2++;
								playerList[ev.player].statsToday.blocks++;
								playerList[this.playerPossession].addShot(this.playerX, this.playerY, 0);
							}
							this.shotPlayer = this.playerPossession;
						}
						else if (ev.type == "PERIODOVER") {
							pitchText += "End of Period " + this.period;
						}
						else if (ev.type == "PERIODSTARTED" || ev.type == "PERIOSTARTED") {
							pitchText += "Start of Period " + this.period;
						}
						else if (ev.type == "MISSRESULT") {
							if (ev.param == "RBO") {
								if (updateStats) {
									playerList[ev.player].statsToday.rebounds++;
									playerList[ev.player].statsToday.offRebounds++;
								}
								if (secPlayerName != "Defender")
									pitchText += "" + secPlayerName + " gets the offensive rebound ";
							}
							else if (ev.param == "RBD") {
								if (updateStats) {
									playerList[ev.player].statsToday.rebounds++;
									playerList[ev.player].statsToday.defRebounds++;
								}
								if (secPlayerName != "Defender")
									pitchText += "" + secPlayerName + " gets the defensive rebound ";
							}
							else if (ev.param == "OOB")
								pitchText += "and the ball goes out of bounds";
							else
								pitchText += "";
						}
						else if (ev.type == "DEFLECTION") {
							var deflector = playerList[ev.player];
							if (updateStats)
								playerList[ev.player].statsToday.deflections++;

							var player = playerList[this.playerPossession];
							if (player != null) {
								if (deflector == null)
									pitchText = "The ball is deflected away from " + this.getPlayerLink(this.playerPossession) + ". ";
								else if (ev.player == this.playerPossession)
									pitchText = this.getPlayerLink(ev.player) + " deflects the ball. ";
								else
									pitchText = this.getPlayerLink(ev.player) + " deflects the ball away from " + this.getPlayerLink(this.playerPossession) + ". ";

							}
							else {
								if (deflector == null)
									pitchText = "The ball is deflected. ";
								else
									pitchText = this.getPlayerLink(ev.player) + " deflects the ball. ";
							}
							if (deflector != null)
								this.deflectPlayer = ev.player;


						}
						else if (ev.type == "TURNOVER") {
							if (ev.param == "OOB") {
								pitchText = offPlayerName + " lets the ball go out of bounds ";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "INT") {
								var player1 = "Player";
								var player2 = "";
								var p = ev.player.split(":");
								if (p.length > 0 && p[0] != "") {
									player1 = playerList[p[0]].playerLabel;
									if (updateStats)
										playerList[p[0]].statsToday.turnovers++;
								}
								if (p.length > 1 && p[1] != "")
									player2 = " by " + playerList[p[1]].playerLabel;

								pitchText = player1 + " loses the ball to an interception" + player2;
							}
							else if (ev.param == "STEAL") {

								var player1 = "Player";
								var player2 = "";
								var p = ev.player.split(":");
								if (p.length > 0 && p[0] != "") {
									player1 = this.getPlayerLink(p[0]);;//playerList[p[0]].playerLabel;
									if (updateStats)
										playerList[p[0]].statsToday.turnovers++;
								}
								if (p.length > 1 && p[1] != "") {
									player2 = " by " + this.getPlayerLink(p[1]);//playerList[p[1]].playerLabel;
									playerList[p[1]].statsToday.steals++;
									this.stealPlayer = p[1]
								}

								pitchText = player1 + " loses the ball to an steal" + player2;

							}
							else if (ev.param == "TRAV") {
								pitchText = offPlayerName + " is called for traveling";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "PALM") {
								pitchText = offPlayerName + " is called for palming";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "DD") {
								pitchText = offPlayerName + " is called for double dribble";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "THROWERR") {
								pitchText = offPlayerName + " has a throw-in error";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "ILLEG") {
								pitchText = offPlayerName + " commits an illegal assist";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "KB") {
								pitchText = offPlayerName + " loses possession due to a kicked ball";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "BACKCOURT") {
								pitchText = offPlayerName + " loses possession due to a a backcourt ball";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "BASKETBELOW") {
								pitchText = offPlayerName + " shoots a basket from below and loses possession";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "VCHARGE") {
								pitchText = offPlayerName + " loses possession because of charging";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "KEYCLOCK") {
								pitchText = offPlayerName + " loses possession due to a clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "SHOTCLOCK") {
								pitchText = offPlayerName + " loses possession due to a shot clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "IBCLOCK") {
								pitchText = offPlayerName + " loses possession due to a inbound clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "BCCLOCK") {
								pitchText = offPlayerName + " loses possession due to a backcourt clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "FTCLOCK") {
								pitchText = offPlayerName + " loses possession due to a free throw clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else if (ev.param == "BACKTONETCLOCK") {
								pitchText = offPlayerName + " loses possession due to a back to net clock violation";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
							else {
								pitchText = offPlayerName + " has a turnover";
								if (updateStats)
									playerList[this.playerPossession].statsToday.turnovers++;
							}
						}
						else if (ev.type == "FT") {
							var p = ev.param.split(":");

							pitchText += offPlayerName + " gets " + p[0] + " free throw" + (p[0] == "1" ? "" : "s") + ". ";

							var p2 = p[1].split("-");
							for (var i = 0; i < p2.length; i++) {
								if (p2[i] == "1") {
									pitchText += " Makes the " + (i == 0 ? "first" : (i == 1 ? "second" : "third")) + " ";
									if (updateStats) {
										playerList[ev.player].statsToday.points += 1;
										playerList[ev.player].statsToday.fta += 1;
										playerList[ev.player].statsToday.ftm += 1;
									}
								}
								else {
									pitchText += " Misses the " + (i == 0 ? "first" : (i == 1 ? "second" : "third")) + " ";
									if (updateStats)
										playerList[ev.player].statsToday.fta += 1;
									if (p[0] == "1+1")
										break;
								}
							}

						}
						else if (ev.type == "CLOCKSET") {
							pitchText = "Clock is adjusted";
						}
						else if (ev.type == "SCOREADJUST") {
							pitchText = "Score is adjusted";
						}
						else if (ev.type == "TIMEOUT") {
							hasTimeout = true;
							if (ev.param == "HOME")
								pitchText = "Home timeout";
							if (ev.param == "GUEST")
								pitchText = "Guest timeout";
						}
						else if (ev.type == "FOUL") {
							var fouler = "";
							var foulee = "";

							var p = ev.player.split(":");
							if (p.length > 0 && p[0] != "") {
								var pguid = p[0];
								if (pguid == "COACH")
									fouler = "The coach";
								else if (pguid == "BENCH")
									fouler = "The bench";
								else {
									fouler = playerList[pguid].playerLabel;
									if (updateStats)
										playerList[pguid].statsToday.fouls++;

								}
							}
							if (p.length > 1 && p[1] != "")
								foulee = playerList[p[1]].playerLabel;

							if (foulee != "")
								foulee = " against " + foulee;
							if (fouler == "")
								fouler = "Player";

							if (ev.param == "DPBLOCK")
								pitchText += fouler + " commits a defensive blocking foul" + foulee;
							else if (ev.param == "DPTRIP")
								pitchText += fouler + " commits a defensive tripping foul" + foulee;
							else if (ev.param == "DPREACH")
								pitchText += fouler + " commits a defensive reaching in foul" + foulee;
							else if (ev.param == "DPHANDCHECK")
								pitchText += fouler + " commits a defensive hand checking foul" + foulee;
							else if (ev.param == "DPPUSH")
								pitchText += fouler + " commits a defensive pushing foul" + foulee;
							else if (ev.param == "DPHOLD")
								pitchText += fouler + " commits a defensive holding foul" + foulee;
							else if (ev.param == "DPILLHAND")
								pitchText += fouler + " commits a defensive illegal hands foul" + foulee;
							else if (ev.param == "DPILLELBOW")
								pitchText += fouler + " commits a defensive elbowing foul" + foulee;
							else if (ev.param == "DPFLAGRANT")
								pitchText += fouler + " commits a defensive flagrant foul" + foulee;
							else if (ev.param == "DPCLEARPATH")
								pitchText += fouler + " commits a defensive clear path foul" + foulee;
							else if (ev.param == "DPOTHER")
								pitchText += fouler + " commits a defensive foul" + foulee;

							else if (ev.param == "OPCHARGE")
								pitchText += fouler + " commits a offensive charging foul" + foulee;
							else if (ev.param == "OPTRIP")
								pitchText += fouler + " commits a offensive tripping foul" + foulee;
							else if (ev.param == "OPSCREEN")
								pitchText += fouler + " commits a offensive screening foul" + foulee;
							else if (ev.param == "OPPUNCH")
								pitchText += fouler + " commits a offensive punching foul" + foulee;
							else if (ev.param == "OPDRIB")
								pitchText += fouler + " commits a offensive dribbling foul" + foulee;
							else if (ev.param == "OPPUSH")
								pitchText += fouler + " commits a offensive pushing foul" + foulee;
							else if (ev.param == "OPHOLD")
								pitchText += fouler + " commits a offensive holding foul" + foulee;
							else if (ev.param == "OPILLHAND")
								pitchText += fouler + " commits a offensive illegal hands foul" + foulee;
							else if (ev.param == "OPILLELBOW")
								pitchText += fouler + " commits a offensive illegal elbows foul" + foulee;

							else if (ev.param == "DTUNSPORT")
								pitchText += fouler + " commits a defensive technical foul unsportsmanlike conduct" + foulee;
							else if (ev.param == "DTFIGHT")
								pitchText += fouler + " commits a defensive technical fighting foul" + foulee;
							else if (ev.param == "DTPROFANITY")
								pitchText += fouler + " commits a defensive technical profanity foul" + foulee;
							else if (ev.param == "DTILLSUB")
								pitchText += fouler + " commits a defensive technical substitution foul" + foulee;
							else if (ev.param == "DTGOALTEND")
								pitchText += fouler + " commits a defensive technical goaltending foul" + foulee;
							else if (ev.param == "DTOUTBOUND")
								pitchText += fouler + " commits a defensive technical out of bounds foul" + foulee;
							else if (ev.param == "DTLIFT")
								pitchText += fouler + " commits a defensive technical lifting foul" + foulee;
							else if (ev.param == "DTDELAY")
								pitchText += fouler + " commits a defensive technical delay of game foul" + foulee;
							else if (ev.param == "DTTOOMANY")
								pitchText += fouler + " commits a defensive technical too many players foul" + foulee;
							else if (ev.param == "DTTIMEOUT")
								pitchText += fouler + " commits a defensive technical timeout foul" + foulee;
							else if (ev.param == "DTLEFTBOX")
								pitchText += fouler + " commits a defensive technical left the box foul" + foulee;
							else if (ev.param == "DTOTHER")
								pitchText += fouler + " commits a defensive technical foul" + foulee;

							else if (ev.param == "OTUNSPORT")
								pitchText += fouler + " commits a offensive technical foul unsportsmanlike conduct" + foulee;
							else if (ev.param == "OTFIGHT")
								pitchText += fouler + " commits a offensive technical fighting foul" + foulee;
							else if (ev.param == "OTPROFANITY")
								pitchText += fouler + " commits a offensive technical profanity foul" + foulee;
							else if (ev.param == "OTILLSUB")
								pitchText += fouler + " commits a offensive technical substitution foul" + foulee;
							else if (ev.param == "OTGOALTEND")
								pitchText += fouler + " commits a offensive technical goaltending foul" + foulee;
							else if (ev.param == "OTOUTBOUND")
								pitchText += fouler + " commits a offensive technical out of bounds foul" + foulee;
							else if (ev.param == "OTLIFT")
								pitchText += fouler + " commits a offensive technical lifting foul" + foulee;
							else if (ev.param == "OTDELAY")
								pitchText += fouler + " commits a offensive technical delay of game foul" + foulee;
							else if (ev.param == "OTTOOMANY")
								pitchText += fouler + " commits a offensive technical too many players foul" + foulee;
							else if (ev.param == "OTTIMEOUT")
								pitchText += fouler + " commits a offensive technical timeout foul" + foulee;
							else if (ev.param == "OTLEFTBOX")
								pitchText += fouler + " commits a offensive technical left the box foul" + foulee;
							else if (ev.param == "OTOTHER")
								pitchText += fouler + " commits a offensive technical foul" + foulee;
						}
						else if (ev.type == "PLAYERADJUST") {
							//ps  = (BasketballPlayerStats *)[playerStatsDictionary objectForKey:ev.player];
							//if(ps!=NULL)
							pitchText += offPlayerName + " stats adjusted";
							{
								if (ev.param == "2MADEP") {
									playerList[ev.player].statsToday.points += 2;
									playerList[ev.player].statsToday.fgm2++;
									playerList[ev.player].statsToday.fga2++;
								}
								else if (ev.param == "2MADEM") {
									playerList[ev.player].statsToday.points -= 2;
									playerList[ev.player].statsToday.fgm2--;
									playerList[ev.player].statsToday.fga2--;
								}
								else if (ev.param == "2MISSP") {
									playerList[ev.player].statsToday.fga2++;
								}
								else if (ev.param == "2MISSM") {
									playerList[ev.player].statsToday.fga2--;
								}
								else if (ev.param == "3MADEP") {
									playerList[ev.player].statsToday.points += 3;
									playerList[ev.player].statsToday.fgm3++;
									playerList[ev.player].statsToday.fga3++;
								}
								else if (ev.param == "3MADEM") {
									playerList[ev.player].statsToday.points -= 3;
									playerList[ev.player].statsToday.fgm3--;
									playerList[ev.player].statsToday.fga3--;
								}
								else if (ev.param == "3MISSP") {
									playerList[ev.player].statsToday.fga3++;
								}
								else if (ev.param == "3MISSM") {
									playerList[ev.player].statsToday.fga3--;
								}
								else if (ev.param == "FTMADEP") {
									playerList[ev.player].statsToday.points++;
									playerList[ev.player].statsToday.ftm++;
									playerList[ev.player].statsToday.fta++;
								}
								else if (ev.param == "FTMADEM") {
									playerList[ev.player].statsToday.points--;
									playerList[ev.player].statsToday.ftm--;
									playerList[ev.player].statsToday.fta--;
								}
								else if (ev.param == "FTMISSP") {
									playerList[ev.player].statsToday.fta++;
								}
								else if (ev.param == "FTMISSM") {
									playerList[ev.player].statsToday.fta--;
								}
								else if (ev.param == "PFP") {
									playerList[ev.player].statsToday.fouls++;
								}
								else if (ev.param == "PFM") {
									playerList[ev.player].statsToday.fouls--;
								}
								else if (ev.param == "DRBDP") {
									playerList[ev.player].statsToday.defRebounds++;
									//ps.defensiveRebounds++;
								}
								else if (ev.param == "ORBDP") {
									playerList[ev.player].statsToday.offRebounds++;
									//ps.offensiveRebounds++;
								}
								else if (ev.param == "DRBDM") {
									playerList[ev.player].statsToday.defRebounds--;
									//ps.defensiveRebounds--;
								}
								else if (ev.param == "ORBDM") {
									playerList[ev.player].statsToday.offRebounds--;
									//ps.offensiveRebounds--;
								}
								else if (ev.param == "TOP") {
									playerList[ev.player].statsToday.turnovers++;
								}
								else if (ev.param == "TOM") {
									playerList[ev.player].statsToday.turnovers--;
								}
								else if (ev.param == "ASSISTP") {
									playerList[ev.player].statsToday.assists++;
									//ps.assists++;
								}
								else if (ev.param == "ASSISTM") {
									playerList[ev.player].statsToday.assists--;
									//ps.assists--;
								}
								else if (ev.param == "BLOCKP") {
									playerList[ev.player].statsToday.blocks++;
								}
								else if (ev.param == "BLOCKM") {
									playerList[ev.player].statsToday.blocks--;
								}
								else if (ev.param == "STEALP") {
									playerList[ev.player].statsToday.steals++;
								}
								else if (ev.param == "STEALM") {
									playerList[ev.player].statsToday.steals--;
								}
							}
						}
					}
				}
			}

			if (pitchText == "" && lastur != null) {
				if (this.possession == lastur.possession && lastur.m_events.length == 0) {
					if (lastur.playerPossession == this.playerPossession)
						pitchText = "";
					else
						pitchText = "Pass to " + this.getPlayerLink(this.playerPossession);
				}
				else
					pitchText = this.getPlayerLink(this.playerPossession) + " gains possession";
			}

			/*
					var eCount = 0;
					for(var x in fieldErrors)
						eCount++;
					if(lastur!=null)
					{
						if(lastur.topInning==0)
							_game.homeErrors+=eCount;
						else
							_game.visitorErrors+=eCount;
					}
			*/
		}
		catch (e) {
			pitchText = "";
		}

		return pitchText;
		//html.append("</BODY>");
		//return playName+html.toString();
	}


}

// Create / load an iScorecast game from a particular device / guid combo
// gg  - GUID of game to load
// dg  - (optional) Full GUID of device to get game from
// cg  - (optional) 10 character Customer GUID of device to get game from
// pwd - (future) password to load this game
function FBGame(gg, dg, cg, pwd, loadedCallback) {

	//get this from the metadata
	this.periods = 4;
	this.calc_periods = 0;
	this.periodLength = 12;
	this.technicalFoulsAsPersonal = false;

	//These keep the players in adictionary. Important for quick lookup by playergameguid
	this.homePlayers = new Array();
	this.visitorPlayers = new Array();
	//these keep the players in the order they were listed. Important for stats
	this.homePlayersArray = new Array();
	this.visitorPlayersArray = new Array();
	this.m_updates = new Array();

	//set this from metadata
	this.outfieldDistance = 400;

	this.visitorHits = 0;
	this.homeHits = 0;

	this.visitorErrors = 0;
	this.homeErrors = 0;

	this.gameOver = false;

	this.addUpdate = function (update) { this.m_updates[this.m_updates.length] = update; }

	this.getHomeTeamName = function () { return this.m_htn; }
	this.getVisitorTeamName = function () { return this.m_vtn; }

	this.guid = gg;
	this.dg = dg;

	_game = this;

	this.statsByName = null;
	this.statsByCid = null;
	this.statsByCatCode = null;
	this.m_images = new Array();

	this.t_visitorPoints = new Array();
	this.t_homePoints = new Array();

	//	this.visitorBattingList=new Array();
	//	this.homeBattingList=new Array();
	//	this.visitorFieldingList=new Array();
	//	this.homeFieldingList=new Array();

	this.playerList = new Array();

	this.stat_vp = new Object();
	this.stat_hp = new Object();

	this.getPeriods = function () {
		if (this.periods == null || this.periods == "")
			return this.calc_periods;
		return this.periods;
	}

	this.getImagesForPlay = function (n) {
		var imageList = new Array();
		for (var i = 0; i < this.m_images.length; i++) {
			var img = this.m_images[i];
			if (img["seq"] == n) imageList[imageList.length] = img;
		}

		return imageList;
	}

	this.statsSuccess = function (xml) {
		//alert((new XMLSerializer()).serializeToString(xml))
		var game = _game;
		$(xml).find("STAT").each(function () {
			var obj = new StatsRecord();
			var playerGuid = $(this).attr("player_guid");
			obj.startDate = $(this).attr("first_game_dt");
			obj.endDate = $(this).attr("last_game_dt") == null ? 0 : $(this).attr("last_game_dt");
			obj.games = $(this).attr("games") == null ? 0 : $(this).attr("games");
			obj.points = $(this).attr("points") == null ? 0 : $(this).attr("points");
			obj.fga3 = parseInt($(this).attr("three_pointers_attempted") == null ? "0" : $(this).attr("three_pointers_attempted"));
			obj.fgm3 = parseInt($(this).attr("three_pointers_made") == null ? "0" : $(this).attr("three_pointers_made"));
			obj.fga2 = parseInt($(this).attr("two_pointers_attempted") == null ? "0" : $(this).attr("two_pointers_attempted"));
			obj.fgm2 = parseInt($(this).attr("two_pointers_made") == null ? "0" : $(this).attr("two_pointers_made"));
			obj.fta = parseInt($(this).attr("free_throws_attempted") == null ? "0" : $(this).attr("free_throws_attempted"));
			obj.ftm = parseInt($(this).attr("free_throws_made") == null ? "0" : $(this).attr("free_throws_made"));
			obj.blocks = $(this).attr("blocks") == null ? 0 : $(this).attr("blocks");
			obj.steals = $(this).attr("steals") == null ? 0 : $(this).attr("steals");
			obj.turnovers = $(this).attr("turnovers") == null ? 0 : $(this).attr("turnovers");
			obj.offRebounds = $(this).attr("offensive_rebounds") == null ? 0 : $(this).attr("offensive_rebounds");
			obj.defRebounds = $(this).attr("defensive_rebounds") == null ? 0 : $(this).attr("defensive_rebounds");
			obj.rebounds = $(this).attr("rebounds") == null ? 0 : $(this).attr("rebounds");
			obj.deflections = $(this).attr("deflections") == null ? 0 : $(this).attr("deflections");
			obj.fouls = $(this).attr("personal_fouls") == null ? 0 : $(this).attr("personal_fouls");
			obj.assists = $(this).attr("assists") == null ? 0 : $(this).attr("assists");
			obj.pm = $(this).attr("plusMinus") == null ? 0 : $(this).attr("plusMinus");

			//alert(obj.playerGuid+":"+obj.bat_1b);

			//alert(game.vp[obj.playerGuid]!=null)
			//if(game.playerList[playerGuid]!=null) game.playerList[playerGuid].statsCareer = obj;

			playerStats[playerGuid] = obj;
			//if(game.stat_hp[playerGuid]!=null) homeStats[obj.playerGuid] = obj;


		});
		//alert((new XMLSerializer()).serializeToString(xml))

	}
	//FB_loadAbbreviations(abbrevSuccess,abbrevFailed);
	this.success = function (xml) {
		//alert((new XMLSerializer()).serializeToString(xml))
		// Need a reference to this game because "this" changes when looping below
		var game = this;

		//clean out all of the calculated fields
		this.gameOver = false;
		this.homePlayers = new Array();
		this.visitorPlayers = new Array();
		this.homePlayersArray = new Array();
		this.visitorPlayersArray = new Array();
		this.m_updates = new Array();
		this.playerList = new Array();

		this.visitorHits = 0;
		this.homeHits = 0;

		this.visitorErrors = 0;
		this.homeErrors = 0;
		//this.t_visitorPoints = new Array();
		//this.t_homePoints = new Array();

		//		this.visitorBattingList=new Array();
		//		this.homeBattingList=new Array();
		//		this.visitorFieldingList=new Array();
		//		this.homeFieldingList=new Array();

		// Read metadata for this game and pull out relevant info
		$(xml).find("METADATA").each(function () {
			game.m_scheduled = $(this).attr("scheduled");
			game.m_htg = $(this).attr("htg");
			game.m_vtg = $(this).attr("vtg");
			game.m_htn = unescape($(this).attr("htn"));
			game.m_vtn = unescape($(this).attr("vtn"));
			game.m_sport = $(this).attr("sport");
			game.m_start = $(this).attr("start");
			game.m_end = $(this).attr("end");
			game.m_htsn = unescape($(this).attr("htsn"));
			game.m_vtsn = unescape($(this).attr("vtsn"));
			game.m_htc = unescape($(this).attr("htc"));
			game.m_vtc = unescape($(this).attr("vtc"));
			game.m_gn = unescape($(this).attr("gn"));
			game.m_fc = unescape($(this).attr("fc"));
			game.m_fl = unescape($(this).attr("fl"));
			game.m_w = unescape($(this).attr("w"));
			game.m_att = unescape($(this).attr("att"));
			game.mode = unescape($(this).attr("mode"));

			game.periods = $(this).attr("per");
			if (game.periods == null || game.periods == "")
				;//	game.periods = "4";
			else
				game.periods = parseInt(game.periods);

			game.periodLength = $(this).attr("plen");
			if (game.periodLength == null || game.periodLength == "")
				game.periodLength = "12";
			game.periodLength = parseInt(game.periodLength);

			game.technicalFoulsAsPersonal = unescape($(this).attr("tasp")) == "Yes";

		});

		if (game.m_htn == null)
			game.m_htn = "Home Team";
		if (game.m_vtn == null)
			game.m_vtn = "Visitor Team";

		if (game.m_htc == "") game.m_htc = "#FFFFFF";
		if (game.m_vtc == "") game.m_vtc = "#666666";

		if (game.m_htsn == null || game.m_htsn == "") game.m_htsn = game.m_htn.substring(0, 7);
		if (game.m_vtsn == null || game.m_vtsn == "") game.m_vtsn = game.m_vtn.substring(0, 7);

		// Loop through each UPDATE record
		$(xml).find("UPDATE").each(function () {
			var ur = new FBUpdateRecord($(this).attr("index"), $(this).attr("status"), $(this).attr("stats"), $(this).attr("ts"));

			// Add all the EVENTs to the update record
			$("EVENT", this).each(function () {
				var event = new FBEvent($(this).attr("type"), $(this).attr("player"), $(this).attr("param"));
				ur.addEvent(event);

				var playersStr = "";
				if (event.type == "GS") {
					var arr = event.param.split(",");
					for (var j = 0; j < arr.length; j++) {
						var p = new PlayerGameRecord();
						var paramList = arr[j].split(":");
						if (j == 0 && paramList.length == 7) paramList.splice(0, 1);	//weird issue with GS where first item has Team Name:
						p.playerGuid = paramList[0];
						p.playerGameGuid = paramList[1];
						p.playerNumber = paramList[2];
						p.position = paramList[3];
						p.isStarter = paramList[4];
						p.playerName = unescape(paramList[5]);
						game.stat_vp[p.playerGuid] = p;
						//game.visitorPlayers[p.playerGameGuid] = p;
						//game.visitorPlayersArray[j] = p;

						if (playerStats[p.playerGuid] == null) {
							if (playersStr != "") playersStr += ",";
							playersStr += p.playerGuid;
						}
					}
					var arr = event.player.split(",");
					for (var j = 0; j < arr.length; j++) {
						var p = new PlayerGameRecord();
						var paramList = arr[j].split(":"); 	//weird issue with GS where first item has Team Name:
						if (j == 0 && paramList.length == 7) paramList.splice(0, 1);
						p.playerGuid = paramList[0];
						p.playerGameGuid = paramList[1];
						p.playerNumber = paramList[2];
						p.position = paramList[3];
						p.isStarter = paramList[4];
						p.playerName = unescape(paramList[5]);
						game.stat_hp[p.playerGuid] = p;
						//game.homePlayers[p.playerGameGuid] = p;
						//game.homePlayersArray[j] = p;

						//alert(p.playerGuid+"    "+p.playerGameGuid+"     "+p.playerName);
						if (playerStats[p.playerGuid] == null) {
							if (playersStr != "") playersStr += ",";
							playersStr += p.playerGuid;
						}
					}

					if (playersStr != "") {
						var statsStr = "games,points,field_goals_made,field_goals_attempted,field_goals_percent,two_pointers_made,two_pointers_attempted,two_pointers_percent,three_pointers_made,three_pointers_attempted,three_pointers_percent,free_throws_made,free_throws_attempted,free_throws_percent,offensive_rebounds,defensive_rebounds,rebounds,assists,steals,deflections,blocks,turnovers,personal_fouls,plusMinus";
						//alert(playersStr+"###"+game.dg+"###"+statsStr+"###"+game.m_vtg+","+game.m_htg+statsStr+"###"+(_game.m_start-1));
						//alert("###"+game.m_vtg+","+game.m_htg+"###"+(_game.m_start-1));
						$.ajax({
							context: this,
							type: "POST",
							url: "http://data.iscorecentral.com/stats_historical.php",
							data: { sport: "basketball", dg: game.dg, stats: statsStr, players: playersStr, tg: game.m_vtg + "," + game.m_htg, asof: _game.m_start - 1 },
							dataType: "xml",
							success: game.statsSuccess,
							error: function () {
								alert("Failed to retrieve career stats from server");
							}
						});
					}
				}

				//http://data.iscorecentral.com/stats_historical.php?sport=baseball&dg=5ea42d3219d18e4881b13950dc30bba81e1f722c&stats=bat_ab,bat_runs,bat_1b&players=w85c8431a09022ead451be6d89993909f,w593b503c505219c2749bbdb6d153976c
			});
			game.addUpdate(ur);
		});

		// Loop through photos and create an array
		$(xml).find("IMAGE").each(function () {
			var imgObject = new Array();

			var seq = $(this).attr("seq");
			var ts = $(this).attr("time");

			if (!seq || seq.length < 1) {
				//
				// Start with sequence being at end of event --- any photos taken
				// after last event will be at end
				//
				seq = game.m_updates.length;
				for (var i = 0; i < game.m_updates.length; i++) {
					var ur = game.m_updates[i];

					// As soon as we find a timestamp "after" the pictures timestamp, we know
					// this should be the sequence number
					if (parseFloat(ur.m_ts) > parseFloat(ts)) {
						seq = i - 1;
						break;
					}
				}
			}

			imgObject["time"] = ts;
			imgObject["seq"] = seq;
			imgObject["img"] = $(this).attr("img");

			game.m_images[game.m_images.length] = imgObject;
		});


		if (typeof loadedCallback == 'function') {
			loadedCallback(game);
		}
	}

	$.ajax({
		context: this,
		type: "GET",
		//		url: "http://data.iscorecentral.com/gamesync.php",
		url: "http://dc.iscorecast.com/gamesync.jsp",
		data: { g: gg, c: cg, dg: dg, p: pwd, m: 1, ignore: _ignore, rand: Math.round(Math.random() * 100000) },
		//		data: { g:gg, c:cg, d:dg, p:pwd, m:1, skipundo:1, ignore:_ignore },
		dataType: "jsonp xml",
		success: this.success,
		error: function () {
			alert("failed to retrieve Game from server");
		}
	});

	if (_ignore != 1) _ignore = 1;

	this.getPlayerByGuid = function (guid) {
		var pg = this.homePlayers[guid];
		if (pg == null)
			pg = this.visitorPlayers[guid];
		return pg;
	}

	this.getHomeBatterName = function (index) {
		var n = "Unknown Player";
		var p = _game.homeBattingList[index];
		if (p != null)
			n = p.getDisplayNameWithNumber();
		return n;
	}
	this.getVisitorBatterName = function (index) {
		var n = "Unknown Player";
		var p = _game.visitorBattingList[index];
		if (p != null)
			n = p.getDisplayNameWithNumber();
		return n;
	}



}

function FBGameDef(guid, name, dg, hn, vn, hs, vs, period) {
	this.m_guid = guid;
	this.m_name = name;
	this.m_dg = dg;
	this.m_homeName = hn;
	this.m_visitorName = vn;
	this.m_homeScore = hs;
	this.m_visitorScore = vs;
	this.m_period = period;

	this.getGuid = function () { return this.m_guid; }
	this.getName = function () { return this.m_name != null ? this.m_name : (this.m_visitorName + " at " + this.m_homeName); }
	this.getDeviceGuid = function () { return this.m_dg; }
	this.getVisitorTeam = function () { return this.m_visitorName; }
	this.getHomeTeam = function () { return this.m_homeName; }
	this.getVisitorScore = function () { return this.m_visitorScore; }
	this.getHomeScore = function () { return this.m_homeScore; }
	this.getPeriod = function () { return this.m_period; }
}

//
// Return a list of Games
//  cg - Customer GUID (10 characters or team name for team websites)
//  pwd - Password if data is password protected
//  loadedCallback - callback when load is complete
//


function FBGameList(cg, pwd, loadedCallback, failedCallback) {
	this.m_games = new Array();

	this.getGames = function () { return m_games; }

	this.success = function (xml) {
		//alert((new XMLSerializer()).serializeToString(xml))
		//
		// <GAMES><GAME guid="6d664a53-0e67-4742-8c56-6be6e4dd0384" custID="5ea42d3219d18e4881b13950dc30bba81e1f722c" gameName="%38/1/11%20Redskins%20at%20Saints%20"/>
		//
		// Need a reference to this game because "this" changes when looping below
		var games = this;

		// Loop through each UPDATE record
		var period = "";
		$(xml).find("GAME").each(function () {
			var metadata_xml = $(this).attr("metadata");

			/////////// get the period or final
			var lastur_xml = $(this).attr("game_state");
			var status = $(lastur_xml).attr("status");
			if (status != null) {
				var arr = status.split(",");
				period = arr[3];
			}
			$(lastur_xml).find("EVENT").each(function () {
				if ($(this).attr("type") == "GE") {
					period = "F";
				}

			});
			////////////////////////

			var gameName = $(metadata_xml).attr("gn");
			if (gameName == null)
				gameName = $(this).attr("vtn") + " at " + $(this).attr("htn");
			gameName = unescape(gameName);
			var gd = new FBGameDef($(this).attr("gg"), gameName, $(this).attr("dg"), $(this).attr("htn"), $(this).attr("vtn"), $(this).attr("home_score"), $(this).attr("visitor_score"), period);

			games.m_games[games.m_games.length] = gd;
		});

		if (typeof loadedCallback == 'function') {
			loadedCallback(games);
		}
	}

	this.failed = function () {
		if (typeof failedCallback == 'function') {
			alert("failed to retrieve Game List from server");
			failedCallback();
		}

	}

	$.ajax({
		context: this,
		type: "GET",
		url: "http://data.iscorecentral.com/iscorecast/lf_search_games.php",
		data: { cg: cg, p: pwd, m: "1", sport: "basketball" },
		dataType: "xml",
		success: this.success,
		error: this.failed
	});
}

var playerStats = new Array();

function StringBuilder(value) {
	this.strings = new Array("");
	this.append(value);
}

// Appends the given value to the end of this instance.
StringBuilder.prototype.append = function (value) {
	if (value) {
		this.strings.push(value);
	}
}

// Clears the string buffer
StringBuilder.prototype.clear = function () {
	this.strings.length = 1;
}

// Converts this instance to a String.
StringBuilder.prototype.toString = function () {
	return this.strings.join("");
}

function FB_loadAbbreviations(successCallback, failCallback) {
	$.ajax({
		context: this,
		type: "GET",
		url: "http://data.iscorecentral.com/football_stats.xml",
		data: {},
		dataType: "xml",
		success: function (xml) {
			var statByName = new Array();
			var statByCatCode = new Array();
			var statByCid = new Array();

			// Loop through each UPDATE record
			$(xml).find("FIELD").each(function () {
				var field = {
					name: $(this).attr("name"),
					type: $(this).attr("type"),
					code: $(this).attr("code"),
					cat: $(this).attr("cat"),
					group: $(this).attr("group"),
					desc: $(this).attr("desc"),
					cid: $(this).attr("cid"),

					toString: function () {
						return "name: " + this.name + ", type: " + this.type + ", code: " + this.code + ", cat: " + this.cat + ", group: " + this.group + ", desc=" + this.desc + ", cid=" + this.cid;
					}
				};

				statByName[field.name] = field;
				statByCatCode[field.cat + "\t" + field.code] = field;
				statByCid[field.cid] = field;
			});

			if (typeof successCallback == 'function') {
				successCallback(statByName, statByCid, statByCatCode);
			}
		},
		error: function () {
			if (typeof failCallback == 'function') {
				failCallback();
			}
			else {
				alert("failed to retrieve Stat Abbreviations");
			}
		}
	});
}

function abbrevSuccess(statsByName, statsByCid, statsByCatCode) {
	_game.statsByName = statsByName;
	_game.statsByCid = statsByCid;
	_game.statsByCatCode = statsByCatCode;
}

function abbrevFailed() {

}