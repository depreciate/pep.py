from common.log import logUtils as log
from constants import clientPackets
from constants import serverPackets
from objects import glob
from common.constants import mods

def handle(userToken, packetData):
	# Get usertoken data
	userID = userToken.userID
	username = userToken.username

	# Make sure we are not banned
	#if userUtils.isBanned(userID):
	#	userToken.enqueue(serverPackets.loginBanned())
	#	return

	# Send restricted message if needed
	#if userToken.restricted:
	#	userToken.checkRestricted(True)

	# Change action packet
	packetData = clientPackets.userActionChange(packetData)

	# If we are not in spectate status but we're spectating someone, stop spectating
	'''
if userToken.spectating != 0 and userToken.actionID != actions.WATCHING and userToken.actionID != actions.IDLE and userToken.actionID != actions.AFK:
	userToken.stopSpectating()

# If we are not in multiplayer but we are in a match, part match
if userToken.matchID != -1 and userToken.actionID != actions.MULTIPLAYING and userToken.actionID != actions.MULTIPLAYER and userToken.actionID != actions.AFK:
	userToken.partMatch()
		'''

	# Update cached stats if our pp changed if we've just submitted a score or we've changed gameMode
	#if (userToken.actionID == actions.PLAYING or userToken.actionID == actions.MULTIPLAYING) or (userToken.pp != userUtils.getPP(userID, userToken.gameMode)) or (userToken.gameMode != packetData["gameMode"]):

	# Update cached stats if we've changed gamemode
	if userToken.gameMode != packetData["gameMode"]:
		userToken.gameMode = packetData["gameMode"]
		userToken.updateCachedStats()

	# Always update action id, text, md5 and beatmapID
	userToken.actionID = packetData["actionID"]
	userToken.actionText = packetData["actionText"]
	userToken.actionMd5 = packetData["actionMd5"]
	userToken.actionMods = packetData["actionMods"]
	userToken.beatmapID = packetData["beatmapID"]
	log.info(bool(packetData["actionMods"] & 128))
	log.info(userToken.relaxing)
	log.info(userToken.relaxAnnounce)
	
	if userToken.actionMods & 128 == 128 and userToken.relaxing == False and userToken.relaxAnnounce == False:
		userToken.relaxing = True
		userToken.relaxAnnounce = True
		serverPackets.notification("Hey, you've just enabled relax! The leaderboards should now change.")
	elif userToken.actionMods != 128 and userToken.relaxing == True and userToken.relaxAnnounce == True:
		userToken.relaxing = False
		userToken.relaxAnnounce = False
		serverPackets.notification("Hey, you've just disabled relax! The leaderboards will now go back to normal.")


	# Enqueue our new user panel and stats to us and our spectators
	recipients = [userToken]
	if len(userToken.spectators) > 0:
		for i in userToken.spectators:
			if i in glob.tokens.tokens:
				recipients.append(glob.tokens.tokens[i])

	for i in recipients:
		if i is not None:
			# Force our own packet
			force = True if i == userToken else False
			i.enqueue(serverPackets.userPanel(userID, force))
			i.enqueue(serverPackets.userStats(userID, force))

	# Console output
	log.info("{} changed action: {} [{}][{}][{}]".format(username, str(userToken.actionID), userToken.actionText, userToken.actionMd5, userToken.beatmapID))
