import numpy

conchResponses = ["IT IS CERTAIN.", "IT IS DECIDEDLY SO.", "WITHOUT A DOUBT", "YES - DEFINITELY", "YOU MAY RELY ON IT.", "AS I SEE IT, YES.", "MOST LIKELY.", "SIGNS POINT TO YES.", "TRY ASKING AGAIN",
        "ASK AGAIN LATER.", "BETTER NOT TELL YOU NOW.", "CANNOT PREDICT NOW", "CONCENTRATE AND ASK AGAIN.", " DON'T COUNT ON IT.", "MY REPLY IS NO.", "MY SOURCES SAY NO.", "OUTLOOK NOT SO GOOD.", "VERY DOUBTFUL"]

rings = ["Ring of Restraint", "Weapon Jump S Ring", "Weapon Jump I Ring", "Weapon Jump L Ring", "Weapon Jump D Ring", "Ultimatum Ring", "Risk Taker Ring", "Totalling Ring", "Critical Damage Ring",
        "Crisis HM Ring", "Tower Boost Ring", "Cleansing Ring", "Overdrive Ring", "Level Jump S Ring", "Level Jump I Ring", "Level Jump L Ring", "Level Jump D Ring", "Health Cut Ring", "Critical Defense Ring", 
        "Limit Ring", "Durability Ring", "Clean Defense Ring", "Berserker Ring", "Mana Cut Ring", "Crisis H Ring", "Crisis M Ring", "Critical Shift Ring", "Stance Shift Ring", "Clean Stance Ring", "Swift Ring",
        "Reflective Ring", "Ocean Glow Earrings", "Broken Box Piece x 5" , "Oz Point Pouch x 5", "2x EXP Coupon (15 Minute) x 3"]

nonRings = ["Ocean Glow Earrings", "Broken Box Piece x 5" , "Oz Point Pouch x 5", "2x EXP Coupon (15 Minute) x 3"]

ringOdds = [0.0424955, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0262206, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353, 0.0185353,
        0.0185353, 0.0185353, 0.0185353, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0162749, 0.0049729, 0.2441230, 0.0587703, 0.0723327]
ringOdds[-1] = 1 - numpy.sum(ringOdds[0:-1])

ringLevels = ['Level 1','Level 2','Level 3','Level 4']
ringLevelOdds = [0.41,0.28,0.20,0.11]