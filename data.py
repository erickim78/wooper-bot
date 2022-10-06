import numpy

conchResponses = ["IT IS CERTAIN.", "IT IS DECIDEDLY SO.", "WITHOUT A DOUBT", "YES - DEFINITELY", "YOU MAY RELY ON IT.", "AS I SEE IT, YES.", "MOST LIKELY.", "SIGNS POINT TO YES.", "TRY ASKING AGAIN",
        "ASK AGAIN LATER.", "BETTER NOT TELL YOU NOW.", "CANNOT PREDICT NOW", "CONCENTRATE AND ASK AGAIN.", " DON'T COUNT ON IT.", "MY REPLY IS NO.", "MY SOURCES SAY NO.", "OUTLOOK NOT SO GOOD.", "VERY DOUBTFUL"]

rings = ["Ring of Restraint", "Weapon Jump S Ring", "Weapon Jump I Ring", "Weapon Jump L Ring", "Weapon Jump D Ring", "Ultimatum Ring", "Risk Taker Ring", "Totalling Ring", "Critical Damage Ring",
        "Crisis HM Ring", "Tower Boost Ring", "Cleansing Ring", "Overdrive Ring", "Level Jump S Ring", "Level Jump I Ring", "Level Jump L Ring", "Level Jump D Ring", "Health Cut Ring", "Critical Defense Ring", 
        "Limit Ring", "Durability Ring", "Clean Defense Ring", "Berserker Ring", "Mana Cut Ring", "Crisis H Ring", "Crisis M Ring", "Critical Shift Ring", "Stance Shift Ring", "Clean Stance Ring", "Swift Ring",
        "Reflective Ring", "Ocean Glow Earrings", "Broken Box Piece x5" , "Oz Point Pouch x5", "2x EXP Coupon (15 Minute) x3"]

hiddenBox = ["Ring of Restraint", "Weapon Jump S Ring", "Weapon Jump I Ring", "Weapon Jump L Ring", "Weapon Jump D Ring", "Ultimatum Ring", "Risk Taker Ring", "Totalling Ring", "Critical Damage Ring",
        "Crisis HM Ring", "Tower Boost Ring", "Cleansing Ring", "Overdrive Ring", "Level Jump S Ring", "Level Jump I Ring", "Level Jump L Ring", "Level Jump D Ring", "Health Cut Ring", "Critical Defense Ring", 
        "Limit Ring", "Durability Ring", "Clean Defense Ring", "Berserker Ring", "Mana Cut Ring", "Crisis H Ring", "Crisis M Ring", "Critical Shift Ring", "Stance Shift Ring", "Clean Stance Ring", "Swift Ring",
        "Reflective Ring"]

shinyBox = ["Ring of Restraint", "Weapon Jump S Ring", "Weapon Jump I Ring", "Weapon Jump L Ring", "Weapon Jump D Ring", "Ultimatum Ring", "Risk Taker Ring", "Totalling Ring", "Critical Damage Ring",
        "Crisis HM Ring", "Tower Boost Ring", "Cleansing Ring", "Overdrive Ring", "Level Jump S Ring", "Level Jump I Ring", "Level Jump L Ring", "Level Jump D Ring", "Health Cut Ring", "Critical Defense Ring", 
        "Limit Ring"]


leaderboardRings = ["Ring of Restraint", "Weapon Jump Rings (All)", "Weapon Jump S Ring", "Weapon Jump I Ring", "Weapon Jump L Ring", "Weapon Jump D Ring", "Risk Taker Ring", "Totalling Ring", "Critical Damage Ring",
        "Crisis HM Ring", "Tower Boost Ring", "Reflective Ring"]

categories = ["Online Time", "Streaming Time", "AFK Time", "Reactions Farmed", "Profanities Used", "Messages Sent"]
categoriesDict = {"Streaming Time":"streamTable", "AFK Time":"afkTable","Reactions Farmed":"reactionTable", "Profanities Used":"profanitiesTable", "Messages Sent":"messagesTable", "Times Mentioned": "mentionsTable"}
periods = ["All Time", "Today", "Last 3 Days", "Last 7 Days", "Last 30 Days"]
periodsDict = {"Last 3 Days":"2", "Last 7 Days":"6", "Last 30 Days":"29"}

rewardLinks = {}
rewardLinks["Ring of Restraint"] = "https://static.wikia.nocookie.net/maplestory/images/4/4d/Eqp_Ring_of_Restraint.png/revision/latest?cb=20160210033306"
rewardLinks["Weapon Jump S Ring"] = "https://static.wikia.nocookie.net/maplestory/images/2/27/Eqp_Weapon_Jump_Ring.png/revision/latest?cb=20190925072314"
rewardLinks["Weapon Jump I Ring"] = "https://static.wikia.nocookie.net/maplestory/images/2/27/Eqp_Weapon_Jump_Ring.png/revision/latest?cb=20190925072314"
rewardLinks["Weapon Jump L Ring"] = "https://static.wikia.nocookie.net/maplestory/images/2/27/Eqp_Weapon_Jump_Ring.png/revision/latest?cb=20190925072314"
rewardLinks["Weapon Jump D Ring"] = "https://static.wikia.nocookie.net/maplestory/images/2/27/Eqp_Weapon_Jump_Ring.png/revision/latest?cb=20190925072314"
rewardLinks["Ultimatum Ring"] = "https://static.wikia.nocookie.net/maplestory/images/4/4b/Eqp_Ultimatum_Ring.png/revision/latest?cb=20160217030325"
rewardLinks["Risk Taker Ring"] = "https://static.wikia.nocookie.net/maplestory/images/0/0f/Eqp_Risk_Taker_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Totalling Ring"] = "https://static.wikia.nocookie.net/maplestory/images/c/c3/Eqp_Totalling_Ring.png/revision/latest?cb=20210326132454"
rewardLinks["Critical Damage Ring"] = "https://static.wikia.nocookie.net/maplestory/images/b/b6/Eqp_Critical_Damage_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Crisis HM Ring"] = "https://static.wikia.nocookie.net/maplestory/images/d/dc/Eqp_Crisis_HM_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Tower Boost Ring"] = "https://static.wikia.nocookie.net/maplestory/images/f/fb/Eqp_Tower_Boost_Ring.png/revision/latest?cb=20151128060245"
rewardLinks["Cleansing Ring"] = "https://static.wikia.nocookie.net/maplestory/images/b/b4/Eqp_Cleansing_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Overdrive Ring"] = "https://static.wikia.nocookie.net/maplestory/images/8/85/Eqp_Overdrive_Ring.png/revision/latest?cb=20160214061639"
rewardLinks["Level Jump I Ring"] = "https://static.wikia.nocookie.net/maplestory/images/c/c4/Eqp_Level_Jump_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Level Jump L Ring"] = "https://static.wikia.nocookie.net/maplestory/images/c/c4/Eqp_Level_Jump_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Level Jump D Ring"] = "https://static.wikia.nocookie.net/maplestory/images/c/c4/Eqp_Level_Jump_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Level Jump S Ring"] = "https://static.wikia.nocookie.net/maplestory/images/c/c4/Eqp_Level_Jump_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Health Cut Ring"] = "https://static.wikia.nocookie.net/maplestory/images/0/06/Eqp_Health_Cut_Ring.png/revision/latest?cb=20170829022018"
rewardLinks["Critical Defense Ring"] = "https://static.wikia.nocookie.net/maplestory/images/5/5f/Eqp_Critical_Defense_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Limit Ring"] = "https://static.wikia.nocookie.net/maplestory/images/d/d3/Eqp_Limit_Ring.png/revision/latest?cb=20170829015203"
rewardLinks["Durability Ring"] = "https://static.wikia.nocookie.net/maplestory/images/b/b8/Eqp_Durability_Ring.png/revision/latest?cb=20171016183528"
rewardLinks["Clean Defense Ring"] = "https://static.wikia.nocookie.net/maplestory/images/0/0f/Eqp_Clean_Defense_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Berserker Ring"] = "https://static.wikia.nocookie.net/maplestory/images/3/36/Eqp_Berserker_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Mana Cut Ring"] = "https://static.wikia.nocookie.net/maplestory/images/e/ec/Eqp_Mana_Cut_Ring.png/revision/latest?cb=20170829055212"
rewardLinks["Crisis H Ring"] = "https://static.wikia.nocookie.net/maplestory/images/e/e6/Eqp_Crisis_H_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Crisis M Ring"] = "https://static.wikia.nocookie.net/maplestory/images/f/fe/Eqp_Crisis_M_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Critical Shift Ring"] = "https://static.wikia.nocookie.net/maplestory/images/2/27/Eqp_Critical_Shift_Ring.png/revision/latest?cb=20160214055648"
rewardLinks["Stance Shift Ring"] = "https://static.wikia.nocookie.net/maplestory/images/7/7f/Eqp_Stance_Shift_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Clean Stance Ring"] = "https://static.wikia.nocookie.net/maplestory/images/1/11/Eqp_Clean_Stance_Ring.png/revision/latest?cb=20210326132453"
rewardLinks["Swift Ring"] = "https://static.wikia.nocookie.net/maplestory/images/e/e0/Eqp_Swift_Ring.png/revision/latest?cb=20210326132454"
rewardLinks["Reflective Ring"] = "https://static.wikia.nocookie.net/maplestory/images/e/ef/Eqp_Reflective_Ring.png/revision/latest?cb=20160214043850"
rewardLinks["Ocean Glow Earrings"] = "https://static.wikia.nocookie.net/maplestory/images/b/b0/Eqp_Ocean_Glow_Earrings.png/revision/latest?cb=20181210205550"
rewardLinks["Broken Box Piece x5"] = "https://static.wikia.nocookie.net/maplestory/images/3/36/Use_Broken_Box_Piece.png/revision/latest?cb=20210910011106"
rewardLinks["Oz Point Pouch x5"] = "https://static.wikia.nocookie.net/maplestory/images/c/cd/Use_Oz_Point_Pouch.png/revision/latest?cb=20210910003310"
rewardLinks["2x EXP Coupon (15 Minute) x3"] = "https://static.wikia.nocookie.net/maplestory/images/f/f3/Use_2x_EXP_Coupon.png/revision/latest?cb=20220712230445"

nonRings = ["Ocean Glow Earrings", "Broken Box Piece x5" , "Oz Point Pouch x5", "2x EXP Coupon (15 Minute) x3"]

ringOdds = [0.0424955, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353,
        0.0185353, 0.0185353, 0.0185353, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0049729, 0.2441230, 0.0587703, 0.0723327]
ringOdds[-1] = 1 - numpy.sum(ringOdds[0:-1])

hiddenRingOdds = [0.0068027, 0.0068027, 0.0068027, 0.0068027, 0.0068027, 0.0068027, 0.0068027, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0272109, 
        0.0272109, 0.0272109, 0.0272109, 0.0272109, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218, 0.0544218]
hiddenRingOdds[-1] = 1 - numpy.sum(hiddenRingOdds[0:-1])

shinyRingOdds = [0.0348837, 0.0348837, 0.0348837, 0.0348837, 0.0348837, 0.0348837, 0.0348837, 0.0581395, 0.0581395, 0.0581395, 0.0581395, 0.0581395, 0.0581395, 0.0581395, 0.0581395, 0.0581395,
         0.0581395, 0.0581395, 0.0581395,  0.0581395]
shinyRingOdds[-1] = 1 - numpy.sum(shinyRingOdds[0:-1])

ringLevels = ['Level 1','Level 2','Level 3','Level 4']
ringLevelOdds = [0.41,0.28,0.20,0.11]

shinyBoxLevels = ['Level 3', 'Level 4']
shinyBoxlevelOdds = [0.75, 0.25]