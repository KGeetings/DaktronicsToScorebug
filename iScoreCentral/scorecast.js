var lastUpdateIndex = -1;
var pitchTooltip;

/*
function hideit()
{
		if(pitchTooltip!=null)
			pitchTooltip.data("tooltip").hide();

}
*/
function Controller(playByPlay, photos, pitchPhotos, boxscore, pitchLocation) {
	this.game = null;
	this.playByPlay = playByPlay;
	this.photos = photos;
	this.pitchPhotos = pitchPhotos;
	this.boxscore = boxscore;
	this.pitchLocation = pitchLocation;
	this.currentUpdateIndex = -1;
	this.replayIndex = -1

	this.setGame = function (game) {

		var isLoaded = true;
		if (this.game == null)
			isLoaded = false;

		this.game = game;

	}

	this.nextPlay = function () {
		this.showPlay(this.replayIndex + 1);
		if (this.replayIndex == this.game.m_updates.length - 1)
			return false;
		return true;
	}

	this.showNewest = function () {
		if (this.currentUpdateIndex == -1)
		//if(false)
		{
			this.updatePlaByPlay(this.game.m_updates.length, true)
			this.postPlayAction();
			lastUpdateIndex = this.game.m_updates.length - 1;
			this.currentUpdateIndex = this.game.m_updates.length - 1;
		}
		else {
			this.updatePlaByPlay(lastUpdateIndex, true)
			this.currentUpdateIndex = this.game.m_updates.length - 1;
			this.doUpdate();
		}
	}

	this.doUpdate = function () {
		if (lastUpdateIndex < this.currentUpdateIndex) {
			lastUpdateIndex++;
			var ur = this.game.m_updates[lastUpdateIndex];

			/*
						var animate = lastIndex!=-1 && ur.m_index>lastIndex;
						controller.updatePlaByPlay(true)
						delayUpdate = this.showBatter(animate);
			*/
			if ((ur.playerX != -1 && ur.playerY != -1 && ur.hasShot()) || ur.hasSteal() || ur.hasDeflection()) {
				var lastur = this.game.m_updates[lastUpdateIndex - 1];
				if (ur.hasSteal())
					this.positionStealPlayer(ur, lastur);
				else if (ur.hasDeflection())
					this.positionDeflectionPlayer(ur, lastur);
				else
					this.positionPlayer(ur, lastur);

				if (lastUpdateIndex < this.currentUpdateIndex)
					window.setTimeout("controller.doUpdate()", 5000);
				else
					window.setTimeout("controller.doUpdate()", 1);
			}
			else
				window.setTimeout("controller.doUpdate()", 1);

			this.updatePlaByPlay(lastUpdateIndex, true)

		}
		else {
			this.updatePlaByPlay(this.game.m_updates.length, true)
			this.postPlayAction();
			lastUpdateIndex = this.game.m_updates.length - 1;
		}

	}

	this.viewPlay = function (index) {
		var ur = this.game.m_updates[index];
		/*
		while(ur != null && ur.m_events.length==0)
		{
			index++;
			ur = this.game.m_updates[index];
		}
		*/
		if (ur == null) {
			return;
			//alert(index);
		}

		if ((ur.hasShot()) || ur.hasSteal() || ur.hasDeflection()) {
			lastur = this.game.m_updates[index - 1];
			if (ur.hasSteal())
				this.positionStealPlayer(ur, lastur);
			else if (ur.hasDeflection())
				this.positionDeflectionPlayer(ur, lastur);
			else
				this.positionPlayer(ur, lastur);
		}
	}

	this.showPlay = function (index) {
		var ur = this.game.m_updates[index];
		while (ur != null && ur.m_events.length == 0) {
			index++;
			ur = this.game.m_updates[index];
		}

		if (ur == null) {
			return;
			//alert(index);
		}

		this.updatePlaByPlay(index + 1, true);
		//if((ur.playerX != -1 && ur.playerY != -1 && ur.hasShot()) || ur.hasSteal() || ur.hasDeflection())
		if ((ur.hasShot()) || ur.hasSteal() || ur.hasDeflection()) {
			lastur = this.game.m_updates[index - 1];
			if (ur.hasSteal())
				this.positionStealPlayer(ur, lastur);
			else if (ur.hasDeflection())
				this.positionDeflectionPlayer(ur, lastur);
			else
				this.positionPlayer(ur, lastur);
		}
		this.updateBoxscore(index);
		this.updateGameState(index);

		this.replayIndex = index;
	}


	this.showAllPlayerShots = function (player) {
		$("#playerActionContainer").html("");
		var iconWidth = 32;
		var iconHeight = 20;
		for (var i = 0; i < player.shots.length; i++) {
			var shot = player.shots[i];
			if (shot.x == -1 && shot.y == -1)
				continue;

			this.transformPosition(shot);

			var src = "miss.png";
			if (shot.pts == 2)
				src = "made2.png"
			if (shot.pts == 3)
				src = "made3.png"

			var $pObj = $("<IMG  src='images/" + src + "' width='" + iconWidth + "' style='position:absolute;left:" + (shot.tx - (iconWidth / 2) + 5) + ";bottom:" + (shot.ty - (iconHeight / 2) + 5) + "' >");

			$("#playerActionContainer").append($pObj);
			//$pObj.fadeOut(15000,function() {
			//	$(this).remove();
			//});
		}
	}

	this.transformPosition = function (shot) {
		var m_x = shot.x;
		var m_y = shot.y;

		//var playerIconWidth=30;
		var w = 470;
		var h = 250;
		var scale = 2.7
		var centerX = w / 2;
		var centerY = h / 2;

		var yskew = Math.sin(Math.PI * ((45 + (m_y / h * 45)) / 180)) + .18

		var originY = 14;

		var infoOffset = 0;
		if (m_x > centerX)
			infoOffset = -430;

		var x = m_x - centerX;
		var y = h - m_y;
		var slope = 46 / 16;


		var ratio = y == 0 ? 0 : h / y
		//var yskew = (.75+(.25*ratio))*.88; //center of the court is not centered vertically so this accounts for that

		x = x - ((y / slope) * x / centerX) + centerX;
		x = x * scale;
		//x-= playerIconWidth/2
		y = y * scale / slope * yskew;
		y = originY + y;

		shot.tx = x;
		shot.ty = y;

	}

	this.positionDeflectionPlayer = function (ur, lastur) {
		var infoOffset = -230;
		var playerIconWidth = 70;
		var stealIcon = "steal.png";
		var player = ur.getDeflector();
		var src = "http://data.iscorecentral.com/iscorecast/unknown.png";
		if (player != null) {
			src = "http://data.iscorecentral.com/getplayerimages.php?display=1&pg=" + player.playerGuid + "&dg=" + _game.dg + "&sport=basketball";
			this.showIndividualStats(player);
		}

		var playInfo = ur.getHtml(null);

		var $pObj = $("<DIV style='position:absolute;width:" + playerIconWidth + ";bottom:120;left:600'><IMG src='images/playinfo.png' style='position:absolute;left:" + (infoOffset + 20) + ";top:-110'><IMG  src='images/" + stealIcon + "' width='" + playerIconWidth + "' ><DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 210) + ";top:-82;width:190'>" + ur.getPlayerLink(player.playerGameGuid) + "</DIV><DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 172) + ";top:-54;width:235;height:40;overflow:hidden;font-size:9pt'>" + playInfo + "</DIV><IMG height=94 src='" + src + "' style='position:absolute;left:" + (infoOffset + 40) + ";top:-93;background-color:#FFFFFF'></DIV>");

		$("#playerActionContainer").append($pObj);
		$pObj.fadeOut(10000, function () {
			$(this).remove();
		});

	}

	this.positionStealPlayer = function (ur, lastur) {
		var infoOffset = -230;
		var playerIconWidth = 70;
		var stealIcon = "steal.png";
		var player = ur.getStealer();
		var src = "http://data.iscorecentral.com/iscorecast/unknown.png";
		if (player != null) {
			src = "http://data.iscorecentral.com/getplayerimages.php?display=1&pg=" + player.playerGuid + "&dg=" + _game.dg + "&sport=basketball";
			this.showIndividualStats(player);
		}

		var playInfo = ur.getHtml(null);

		var playerGameGuid = "";
		if (player != null)
			playerGameGuid = player.playerGameGuid;

		var $pObj = $("<DIV style='position:absolute;width:" + playerIconWidth + ";bottom:120;left:600'><IMG src='images/playinfo.png' style='position:absolute;left:" + (infoOffset + 20) + ";top:-110'><IMG  src='images/" + stealIcon + "' width='" + playerIconWidth + "' ><DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 210) + ";top:-82;width:190'>" + ur.getPlayerLink(playerGameGuid) + "</DIV><DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 172) + ";top:-54;width:235;height:40;overflow:hidden;font-size:9pt'>" + playInfo + "</DIV><IMG height=94 src='" + src + "' style='position:absolute;left:" + (infoOffset + 40) + ";top:-93;background-color:#FFFFFF'></DIV>");

		$("#playerActionContainer").append($pObj);
		$pObj.fadeOut(10000, function () {
			$(this).remove();
		});

	}

	this.positionPlayer = function (ur, lastur) {
		var index = ur.m_index;
		var m_x = ur.playerX;
		var m_y = ur.playerY;
		//alert(m_x+":"+m_y);
		//alert(Math.sin(Math.PI * (90/180))+":"+Math.sin(Math.PI * (45/180)))
		var w = 470;
		var h = 250;
		var scale = 2.7
		//var yscale = .88

		var yskew = Math.sin(Math.PI * ((45 + (m_y / h * 45)) / 180)) + .18


		var playerIconWidth = 34 * (1.0 + (.25 * m_y / h)); //icon has to get bigger closer to the camera

		var centerX = w / 2;
		var centerY = h / 2;

		var hidePlayer = false;
		if (m_x == -1 && m_y == -1) {
			m_x = centerX - 140;
			hidePlayer = true;
		}

		var originY = 14;

		var infoOffset = 10;
		if (m_x > centerX)
			infoOffset = -430;

		var x = m_x - centerX;
		var y = h - m_y;
		var slope = 46 / 16;


		var ratio = y == 0 ? 0 : h / y
		//var yskew = (.75+(.25*ratio))*.88; //center of the court is not centered vertically so this accounts for that

		x = x - ((y / slope) * x / centerX) + centerX;
		x = x * scale;
		x -= (playerIconWidth / 2) - 3;
		y = y * scale / slope * yskew;
		y = originY + y;

		var playInfo = ur.getHtml(null);

		// need to get the shooter from the ur itself. playerPossession will be different between coach and game modes.
		// need to get the player shooting direction by determining if the shooter is on the home team and comparing that with homeOnLeft
		// dont use lastur possesion because that will be diferent between coach and game modes

		var player = ur.getShooter();
		//alert(ur.playerPossession+":"+ur.getPlayerLink(ur.playerPossession))
		//alert(x+":"+y);
		//var player = ur.getPlayerByGuid(ur.playerPossession);
		var src = "http://data.iscorecentral.com/iscorecast/unknown.png";
		if (player != null) {
			src = "http://data.iscorecentral.com/getplayerimages.php?display=1&pg=" + player.playerGuid + "&dg=" + _game.dg + "&sport=basketball";
			this.showIndividualStats(player);
		}
		else
			return;

		var onLeft = ((_game.visitorPlayers[player.playerGameGuid] != null && !ur.homeOnLeft) || (_game.homePlayers[player.playerGameGuid] != null && ur.homeOnLeft))

		var shooterIcon = "male_1_shot_1.png";
		var m = Math.atan2(m_y - (h / 2), m_x < (w / 2) ? m_x : -w + m_x);
		//alert(onLeft+":"+m+":"+ur.homeOnLeft)
		if (onLeft) {
			//alert(m)
			if (m < -2.4)
				shooterIcon = "male_1_shot_1.png";
			else if (m < -1.2)
				shooterIcon = "male_1_shot_2.png";
			else if (m < -.8)
				shooterIcon = "male_1_shot_3.png";
			else if (m < .2)
				shooterIcon = "male_1_shot_4.png";
			else if (m < 1.90)
				shooterIcon = "male_1_shot_5.png";
			else if (m < 2.5)
				shooterIcon = "male_1_shot_6.png";
		}
		else {
			if (m < -1.5708)
				shooterIcon = "male_1_shot_2.png";
			else if (m < -.8)
				shooterIcon = "male_1_shot_3.png";
			else if (m < .2)
				shooterIcon = "male_1_shot_4.png";
			else if (m < 1.0)
				shooterIcon = "male_1_shot_5.png";
			else if (m < 2.5)
				shooterIcon = "male_1_shot_6.png";
		}
		/*
		if(_game.visitorPlayers[player.playerGameGuid]!=null)
		{
			if(!ur.homeOnLeft)
			{
				x+=10;
				shooterIcon = "male_1_shot_1.png"
			}
		}
		if(_game.homePlayers[player.playerGameGuid]!=null)
		{
			if(ur.homeOnLeft)
			{
				x+=10;
				shooterIcon = "male_1_shot_1.png"
			}
		}
		*/
		/*
				if((lastur.possession==0 && lastur.homeOnLeft) || (lastur.possession==1 && !lastur.homeOnLeft))
				{
					x+=10;
					shooterIcon = "shooter_7.png"
				}
		*/
		//alert(playInfo+":"+playInfo.length)
		//var $pObj = $("<DIV style='position:absolute;width:"+playerIconWidth+";bottom:"+y+";left:"+x+"'><IMG src='images/playinfo.png' style='position:absolute;left:"+(infoOffset+20)+";top:-110'><IMG  src='images/shooter.png' width='"+playerIconWidth+"' ><DIV class='playerInfo' style='position:absolute;left:"+(infoOffset+210)+";top:-82;width:190'>"+ur.getPlayerLink(ur.playerPossession)+"</DIV><DIV class='playerInfo' style='position:absolute;left:"+(infoOffset+172)+";top:-54;width:235;height:40;overflow:hidden"+(playInfo.length>55?";font-size:9pt":";font-size:16pt")+"'>"+playInfo+"</DIV><IMG height=94 src='"+src+"' style='position:absolute;left:"+(infoOffset+40)+";top:-93;background-color:#FFFFFF'></DIV>");
		var $pObj = $("<DIV style='position:absolute;width:" + playerIconWidth + ";bottom:" + y + ";left:" + x + "'><IMG src='images/playinfo.png' style='position:absolute;left:" + (infoOffset + 20) + ";top:-110'>" + (hidePlayer ? "" : "<IMG  src='images/" + shooterIcon + "' width='" + playerIconWidth + "' >") + "<DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 210) + ";top:-82;width:190'>" + ur.getPlayerLink(player.playerGameGuid) + "</DIV><DIV class='playerInfo' style='position:absolute;left:" + (infoOffset + 172) + ";top:-54;width:235;height:40;overflow:hidden;font-size:9pt'>" + playInfo + "</DIV><IMG height=94 src='" + src + "' style='position:absolute;left:" + (infoOffset + 40) + ";top:-93;background-color:#FFFFFF'></DIV>");

		$("#playerActionContainer").append($pObj);
		$pObj.fadeOut(10000, function () {
			$(this).remove();
		});


	}

	this.postPlayAction = function () {
		controller.showPhotos()
		controller.updateBoxscore(-1);
		controller.updateGameState(-1);
	}


	this.updatePlaByPlay = function (toIndex, reverse) {
		var p_html = new StringBuilder("");

		p_html.append("<table class='pbp-container' style='padding:0' border='0' width='100%' border=0 cellpadding='4' cellspacing='0'>");

		var rowArray = new Array();
		count = 0;
		//alert(this.currentUpdateIndex);
		for (var i = 0; i < toIndex; i++) {
			var ur = _game.m_updates[i];
			if (ur == null) continue;

			var lastUr = null;
			if (i > 0)
				lastUr = _game.m_updates[i - 1];

			if (lastUr == null) {
				var html = new StringBuilder("");
				html.append("<tr valign='top' class='odd' >");
				html.append("	<td colspan=4 nowrap class='rowCell headerCell' align=center >Period " + ur.period + "</td>");
				html.append("</tr>");

				rowArray[count++] = html.toString();
				delete html;
				html = null;
			}

			/*
			if(i==1)
			{
				var html = new StringBuilder("");
				html.append("<tr valign='top' class='odd' >");
				html.append("	<td colspan=2 nowrap class='rowCell playerCell' align=center >Now batting: "+_game.getVisitorBatterName(ur.visitorLineupPositionAtBat)+"</td>");
				html.append("</tr>");

				rowArray[count++] = html.toString();
				delete html;
				html=null;
			}
			*/
			var ss = ur.getHtml(lastUr)
			if (ss != "") {
				var html = new StringBuilder("");
				html.append("<tr valign='top' class='" + ((i % 2) ? "even" : "odd") + "' onclick='showPlay(" + i + ");'>");

				if (_game.getImagesForPlay(i - 1).length)
					html.append("	<td class='rowCell' align=center ><IMG src='images/eye.png' width=16 onclick='showPlayPhotos(" + (i - 1) + ");'></td>");
				else
					html.append("	<td class='rowCell' align=center >&nbsp;</td>");

				if (lastUr != null && ur.possession == 1)
					html.append("	<td width=5 class='rowCell' align=center valign=middle style='font-size:6pt;border-left-width:4;border-left-style:solid;border-left-color:" + _game.m_vtc + "'>A W A Y</td>");
				else
					html.append("	<td width=5 class='rowCell' align=center valign=middle style='font-size:6pt'>&nbsp;</td>");
				html.append("	<td width=100% class='rowCell'align=left>" + ss + "</td>");
				if (lastUr != null && ur.possession == 0)
					html.append("	<td width=5 class='rowCell' align=center valign=middle style='font-size:6pt;border-right-width:4;border-right-style:solid;border-right-color:" + _game.m_htc + "'>H O M E</td>");
				else
					html.append("	<td width=5 class='rowCell' align=center valign=middle style='font-size:6pt'>&nbsp;</td>");

				html.append("</tr>");

				rowArray[count++] = html.toString();
				delete html;
				html = null;
			}

			if (lastUr != null && lastUr.period != ur.period) {
				var html = new StringBuilder("");

				html.append("<tr valign='top' class='odd' >");
				html.append("	<td colspan=4 nowrap class='rowCell headerCell' align=center >Period " + ur.period + "</td>");
				html.append("</tr>");

				rowArray[count++] = html.toString();
				delete html;
				html = null;
			}

		}


		if (reverse) {
			for (var i = rowArray.length - 1; i >= 0; i--) {
				p_html.append(rowArray[i]);

			}

		}
		else {
			for (var i = 0; i < rowArray.length; i++) {
				p_html.append(rowArray[i]);

			}
		}

		p_html.append("</table>");

		this.playByPlay.html(p_html.toString());



	}

	this.updateBoxscore = function (index) {
		if (_game.m_updates.length <= 0) {
			this.boxscore.html("<BR><DIV width='100%' height='100%' class='boxscore_row'>Waiting for the game to start...</DIV>");
			return;
		}

		var period = _game.m_updates[index == -1 ? _game.m_updates.length - 1 : index].period;

		var html = new StringBuilder("");

		html.append("<table border='0' cellpadding='3' cellspacing='0'>");

		var htmlHeader = new StringBuilder("<TR>");
		var htmlVisitor = new StringBuilder("<TR>");
		var htmlHome = new StringBuilder("<TR>");

		htmlHeader.append("<td class='boxscore_header' align=center width=1>&nbsp;</td>");
		htmlVisitor.append("<td class='boxscore_row' align=center width=1><IMG src='" + ("http://data.iscorecentral.com/getteamlogo.php?tg=" + (_game.m_vtg) + "&dg=" + _game.dg + "&size=24&search=1") + "'></td>");
		htmlHome.append("<td class='boxscore_row' align=center width=1><IMG src='" + ("http://data.iscorecentral.com/getteamlogo.php?tg=" + (_game.m_htg) + "&dg=" + _game.dg + "&size=24&search=1") + "'></td>");

		htmlHeader.append("<td class='boxscore_header' align=center >&nbsp;</td>");
		htmlVisitor.append("<td nowrap class='boxscore_row' align=left >" + _game.m_vtsn + "</td>");
		htmlHome.append("<td nowrap class='boxscore_row' align=left >" + _game.m_htsn + "</td>");

		htmlHeader.append("<td class='boxscore_header' align=center width=10>&nbsp;</td>");
		htmlVisitor.append("<td class='boxscore_row' align=center width=10>&nbsp;</td>");
		htmlHome.append("<td class='boxscore_row' align=center width=10>&nbsp;</td>");

		var scheduledPeriods = _game.getPeriods();
		var currentPeriods = _game.t_visitorPoints.length - 1;
		//alert(scheduledPeriods+":"+currentPeriods)
		var vPoints = 0;
		var hPoints = 0;
		var max = currentPeriods > scheduledPeriods ? currentPeriods : scheduledPeriods;

		for (var i = 1; i <= max; i++) {
			if (i > currentPeriods) {
				htmlHeader.append("<td class='boxscore_header' align=center width=20>" + (i) + "</td>");
				htmlVisitor.append("<td class='boxscore_row' align=center width=20></td>");
				htmlHome.append("<td class='boxscore_row' align=center width=20></td>");
				continue;
			}

			var v = parseInt((_game.t_visitorPoints[i] == null || _game.t_visitorPoints[i] == "") ? 0 : _game.t_visitorPoints[i]) - vPoints;
			var h = parseInt((_game.t_homePoints[i] == null || _game.t_homePoints[i] == "") ? 0 : _game.t_homePoints[i]) - hPoints;

			htmlHeader.append("<td  class='boxscore_header' align=center width=" + (i > scheduledPeriods ? "60" : "20") + " nowrap>" + (i > scheduledPeriods ? "O" + (i - scheduledPeriods) : i) + "</td>");
			htmlVisitor.append("<td class='boxscore_row' align=center width=20>" + v + "</td>");
			htmlHome.append("<td class='boxscore_row' align=center width=20>" + h + "</td>");

			vPoints += v;
			hPoints += h;


		}

		/*
				for(var i=period+1;i<=_game.scheduledInnings;i++)
				{
					htmlHeader.append("<td class='boxscore_header' align=center width=20>"+(i)+"</td>");
					htmlVisitor.append("<td class='boxscore_row' align=center width=20></td>");
					htmlHome.append("<td class='boxscore_row' align=center width=20></td>");

				}
		*/


		htmlHeader.append("<td class='boxscore_header' align=center width=5>&nbsp;</td>");
		htmlVisitor.append("<td class='boxscore_row' align=center width=5>&nbsp;</td>");
		htmlHome.append("<td class='boxscore_row' align=center width=5>&nbsp;</td>");

		htmlHeader.append("<td class='boxscore_header' align=center width=20>T</td>");
		htmlVisitor.append("<td class='boxscore_runs' align=center width=20>" + vPoints + "</td>");
		htmlHome.append("<td class='boxscore_runs' align=center width=20>" + hPoints + "</td>");


		htmlHeader.append("</TR>");
		htmlVisitor.append("</TR>");
		htmlHome.append("</TR>");

		html.append(htmlHeader.toString());
		html.append(htmlVisitor.toString());
		html.append(htmlHome.toString());

		html.append("</table>");

		this.boxscore.html(html.toString());

	}


	this.showIndividualStats = function (player) {
		//alert("here");
		this.showAllPlayerShots(player);

		var headerStr = "<TH align='left'>&nbsp;</TH><TH align='center'>G</TH><TH align='center'>PTS</TH><TH align='center'>FGM/A</TH><TH align='center'>FG%</TH><TH align='center'>FTM/A</TH><TH align='center'>FT%</TH>"

		var html = new StringBuilder("");
		html.append("<TABLE class='roster' width='100%' cellspacing=1 cellpadding=1>");

		//html.append("<TR><TD colspan='5'>Career</TD></TR>");
		html.append("<TR style='color:#AAAAAA'>" + headerStr + "</TR>");

		var name = "?";
		var pos = 0;

		var statsStr = "";
		var isHome = false;

		if (player != null) {
			if (_game.homePlayers[player.playerGameGuid] != null)
				isHome = true;

			var statsObj = player.statsToday;


			statsStr += "<TR height=21>";
			statsStr += "<TD align='left' width=65>Today</TD>";

			var fga = statsObj.fga3 + statsObj.fga2;
			var fgm = statsObj.fgm3 + statsObj.fgm2;

			statsStr += "<TD align='center'></TD>";
			statsStr += "<TD align='center'>" + statsObj.points + "</TD>";
			statsStr += "<TD align='center'>" + fgm + "/" + fga + "</TD>";
			//statsStr += "<TD align='center'>"+fga+"</TD>";
			statsStr += "<TD align='center'>" + (fga == 0 ? 0 : Math.round(1000 * fgm / fga) / 1000).toFixed(2) + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.ftm + "/" + statsObj.fta + "</TD>";
			//statsStr += "<TD align='center'>"+statsObj.fta+"</TD>";
			statsStr += "<TD align='center'>" + (statsObj.fta == 0 ? 0 : Math.round(1000 * statsObj.ftm / statsObj.fta) / 1000).toFixed(2) + "</TD>";
			statsStr += "</TR>";

			statsStr += "<TR>";
			statsStr += "<TD align='left'>Career</TD>";

			statsObj = playerStats[player.playerGuid];
			if (statsObj == null)
				statsObj = player.statsCareer;

			var fga = statsObj.fga3 + statsObj.fga2;
			var fgm = statsObj.fgm3 + statsObj.fgm2;

			statsStr += "<TD align='center'>" + statsObj.games + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.points + "</TD>";
			statsStr += "<TD align='center'>" + fgm + "/" + fga + "</TD>";
			//statsStr += "<TD align='center'>"+fga+"</TD>";
			statsStr += "<TD align='center'>" + (fga == 0 ? 0 : Math.round(1000 * fgm / fga) / 1000).toFixed(2) + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.ftm + "/" + statsObj.fta + "</TD>";
			//statsStr += "<TD align='center'>"+statsObj.fta+"</TD>";
			statsStr += "<TD align='center'>" + (statsObj.fta == 0 ? 0 : Math.round(1000 * statsObj.ftm / statsObj.fta) / 1000).toFixed(2) + "</TD>";
			statsStr += "</TR>";

			pos = player.fieldingPosition;
			name = player.getDisplayNameWithNumber();
		}
		html.append(statsStr);
		html.append("</TABLE>");
		$("#spot_statsOffense").html(html.toString());

		//########### COURT
		var headerStr = "<TH align='left'>&nbsp;</TH><TH align='center'>OR</TH><TH align='center'>DR</TH><TH align='center'>RB</TH><TH align='center'>AST</TH><TH align='center'>STL</TH><TH align='center'>DFL</TH><TH align='center'>BLK</TH><TH align='center'>TO</TH><TH align='center'>PF</TH><TH align='center'>PM</TH>"

		var html = new StringBuilder("");
		html.append("<TABLE class='roster' width='100%' cellspacing=1 cellpadding=1>");

		html.append("<TR style='color:#AAAAAA'>" + headerStr + "</TR>");

		var name = "?";
		var pos = 0;

		var statsStr = "";
		if (player != null) {
			var statsObj = player.statsToday;


			statsStr += "<TR height=21>";
			statsStr += "<TD align='left' width=65>Today</TD>";

			statsStr += "<TD align='center'>" + statsObj.offRebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.defRebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.rebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.assists + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.steals + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.deflections + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.blocks + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.turnovers + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.fouls + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.pm + "</TD>";

			statsStr += "</TR>";


			statsStr += "<TR>";
			statsStr += "<TD align='left'>Career</TD>";

			statsObj = playerStats[player.playerGuid];
			if (statsObj == null)
				statsObj = player.statsCareer;

			statsStr += "<TD align='center'>" + statsObj.offRebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.defRebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.rebounds + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.assists + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.steals + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.deflections + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.blocks + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.turnovers + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.fouls + "</TD>";
			statsStr += "<TD align='center'>" + statsObj.pm + "</TD>";

			statsStr += "</TR>";

			pos = player.fieldingPosition;
			name = player.getDisplayNameWithNumber();
		}
		html.append(statsStr);
		html.append("</TABLE>");
		$("#spot_statsDefense").html(html.toString());

		if (player == null)
			$("#spot_headshot").attr('src', "http://data.iscorecentral.com/iscorecast/unknown.png");
		else
			$("#spot_headshot").attr('src', "http://data.iscorecentral.com/getplayerimages.php?sport=basketball&display=1&pg=" + player.playerGuid + "&dg=" + _game.dg);

		$("#spot_team_logo").attr('src', "http://data.iscorecentral.com/getteamlogo.php?tg=" + (isHome ? _game.m_htg : _game.m_vtg) + "&dg=" + _game.dg + "&size=60&search=1")
		$("#spot_team_logo").show();

		$("#spot_playerName").html(name);
		$("#spot_team").html(isHome ? _game.m_htn : _game.m_vtn);

		$("#spot_color").css("background-color", isHome ? _game.m_htc : _game.m_vtc);

	}

	this.updateGameState = function (index) {
		var ur = _game.m_updates[_game.m_updates.length - 1];
		if (index != -1)
			ur = _game.m_updates[index];
		if (ur == null)
			return;

		$('#inning').html(ur.period + (ur.period == 1 ? "st" : (ur.period == 2 ? "nd" : (ur.period == 3 ? "rd" : "th"))));
		if (_game.gameOver && !isReplay)
			$('#inning').html("Final");



		//if(currentPlayerStatsGuid=="")
		//	this.showIndividualStats(p);
		//		alert(_game.m_end)
		if (!_game.gameOver || isReplay)
			$("#timeContainer").html(ur.htmlClock());
		else
			$("#timeContainer").html("Final");

		var html = new StringBuilder("");
		var headerStr = "<TH align='center'>PTS</TH><TH align='center'>PF</TH><TH align='center'>RB</TH><TH align='center'>AST</TH>"

		html.append("<TABLE class='roster' width='100%'>");
		//alert(_game.visitorBattingList.length)
		html.append("<TR><TD align='left' colspan=2 class='roster_teamname'>" + _game.m_vtn + "</TD></TR>");
		html.append("<TR><TH align='left' colspan=2>&nbsp;</TH>" + headerStr + "</TR>");
		for (var i = 0; i < _game.visitorPlayersArray.length; i++) {
			var p = _game.visitorPlayersArray[i];
			var name = "?";
			var pos = 0;

			var statsStr = "";
			if (p != null) {
				statsStr += "<TD align='center'>" + p.statsToday.points + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.fouls + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.rebounds + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.assists + "</TD>";

				name = p.getDisplayNameWithNumber();
			}

			var fieldPosition = "";

			html.append("<TR class='" + (i % 2 == 0 ? "even" : "odd") + "'><TD align='left'>" + name + "</TD><TD align='center'>" + fieldPosition + "</TD>" + statsStr + "</TR>");
		}
		html.append("<TR><TD align='left' colspan=2>&nbsp</TD></TR>");
		html.append("<TR><TD align='left' colspan=2 class='roster_teamname'>" + _game.m_htn + "</TD></TR>");
		html.append("<TR><TH align='left' colspan=2>&nbsp;</TH>" + headerStr + "</TR>");
		for (var i = 0; i < _game.homePlayersArray.length; i++) {
			var p = _game.homePlayersArray[i];
			var name = "?";
			var pos = 0;

			var statsStr = "";
			if (p != null) {
				statsStr += "<TD align='center'>" + p.statsToday.points + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.fouls + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.rebounds + "</TD>";
				statsStr += "<TD align='center'>" + p.statsToday.assists + "</TD>";

				name = p.getDisplayNameWithNumber();
			}

			var fieldPosition = "";
			html.append("<TR class='" + (i % 2 == 0 ? "even" : "odd") + "'><TD align='left'>" + name + "</TD><TD align='center'>" + fieldPosition + "</TD>" + statsStr + "</TR>");
		}
		html.append("</TABLE>");
		$("#visitorRoster").html(html.toString());

		$("#fieldSize1").html("" + _game.outfieldDistance);
		$("#fieldSize2").html("" + _game.outfieldDistance);
	}



	this.showPhotos = function () {
		var html = new StringBuilder("");
		html.append("<table class='pbp-container' style='padding:0' border='0' width='100%' border=0 cellpadding='3' cellspacing='0'>");

		for (var i = 0; i < _game.m_images.length; i++) {
			var imgStr = _game.m_images[i]["img"];
			html.append("<tr>");
			html.append("	<td  align=left>");
			html.append("	<a href='http://data.iscorecentral.com/userdata/" + dg.substring(0, 1) + "/" + dg.substring(1, 2) + "/" + dg.substring(2, 3) + "/" + dg + "/games/" + gg + "/images/zoom_" + imgStr + "' border=0 title='' alt='Click to see full size image'><img src='http://data.iscorecentral.com/userdata/" + dg.substring(0, 1) + "/" + dg.substring(1, 2) + "/" + dg.substring(2, 3) + "/" + dg + "/games/" + gg + "/images/thumb_" + imgStr + "' border=0 alt='' /></a>");
			html.append("	</td>");
			html.append("</tr>");

		}
		html.append("</table>");

		this.photos.html(html.toString());
		$('.gallery a').lightBox('.gallery a');
	}

	this.showPlayPhotos = function (index) {
		$('.gallery a').lightBox('.gallery a');
		var images = _game.getImagesForPlay(index);
		if (images.length == 1) {
			for (var i = 0; i < _game.m_images.length; i++) {
				if (_game.m_images[i] == images[0]) {
					$(".gallery a").eq(i).click();
					return true;
				}
			}
		}

		var html = new StringBuilder("");
		html.append("<table class='pbp-container' style='padding:0' border='0' width='100%' border=0 cellpadding='3' cellspacing='0'>");

		for (var i = 0; i < _game.getImagesForPlay(index).length; i++) {
			var imgStr = _game.getImagesForPlay(index)[i]["img"];
			html.append("<tr>");
			html.append("	<td  align=left>");
			html.append("	<a href='http://data.iscorecentral.com/userdata/" + dg.substring(0, 1) + "/" + dg.substring(1, 2) + "/" + dg.substring(2, 3) + "/" + dg + "/games/" + gg + "/images/zoom_" + imgStr + "' border=0 title='' alt='Click to see full size image'><img src='http://data.iscorecentral.com/userdata/" + dg.substring(0, 1) + "/" + dg.substring(1, 2) + "/" + dg.substring(2, 3) + "/" + dg + "/games/" + gg + "/images/thumb_" + imgStr + "' border=0 alt='' /></a>");
			html.append("	</td>");
			html.append("</tr>");
		}
		html.append("</table>");
		//alert(index+":"+html.toString());
		this.pitchPhotos.html(html.toString());

		$('.gallery a').lightBox('.gallery a');

		return false;
	}
}