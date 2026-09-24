"""
Single source of the full devils' text and metadata, used by gen_data.py (language file, loot tables) and
gen_devils.py (essence/icon art, item models).

Each devil: type id (HybridType.id), entity registry name, display names, the essence tooltip, the message shown on
becoming it, and its moves (ability id -> name, description).
"""

DEVILS = [
    dict(id="control", entity="makima", name="Makima", form="Control Devil", color=(184, 50, 42), boss=True,
         essence="Control Devil's Essence",
         tooltip="Warm, and watching you. It wants to be obeyed.",
         became="You are the Control Devil now. Everyone beneath you is yours. Press V for the ability wheel, G to let the "
                "devil show in your eyes.",
         trigger=("control_devil", "Control Devil",
                  "Let the Control Devil show: your ringed eyes light up and your power over lesser beings is complete."),
         moves={
             "control_bang": ("Bang", "Point a finger gun at a target and say it. An unseen force crushes it where it "
                                      "stands, from any distance, through armour."),
             "control_chains": ("Chains", "Chains burst out of the ground, bind everything in front of you and drag it "
                                          "to your feet."),
             "control_domination": ("Domination", "Every creature around you that is beneath you becomes your thrall for "
                                                  "a minute and turns on whatever you fight."),
             "control_kneel": ("Kneel", "Everyone around you is slammed to the floor and can't get up for a moment."),
             "control_contract": ("The Prime Minister's Contract", "For 20 seconds, every injury meant for you lands on "
                                                                   "some creature nearby instead."),
         },
         lore="Makima's lethal wounds are redirected to creatures around her. Only Chainsaw Man's blows land for sure."),
    dict(id="bat", entity="bat_devil", name="Bat Devil", form="Bat Devil", color=(122, 90, 138), boss=False,
         essence="Bat Devil's Essence",
         tooltip="It flutters when you breathe on it.",
         became="You are the Bat Devil now. Press V for the ability wheel, G to spread your wings (you can fly in that "
                "form).",
         moves={
             "bat_bite": ("Blood Bite", "Lunge and sink your fangs in. The blood you drink heals you."),
             "bat_air_cannon": ("Air Cannon", "Your maw stretches into a gun barrel and fires a blast of compressed air "
                                              "that hurls everything in its path."),
             "bat_swoop": ("Swoop", "Dive onto your prey, snatch it, haul it high into the air and let it fall."),
             "bat_screech": ("Screech", "A screech that scrambles everything around you."),
         }),
    dict(id="leech", entity="leech_devil", name="Leech Devil", form="Leech Devil", color=(122, 74, 86), boss=False,
         essence="Leech Devil's Essence", tooltip="It sucks at your fingers.",
         moves={
             "leech_tongue": ("Piercing Tongue", "Your tongue stabs out and runs through the first thing in its way. You "
                                                 "drink what it hits."),
             "leech_grab": ("Sucker Grab", "Sucker-lined tentacles lash out and drag up to three victims into reach "
                                           "of your mouth."),
             "leech_devour": ("Devour", "The whole front of you is a mouth. Bite down on whatever is in front of you."),
             "leech_drain": ("Drain", "Latch onto your prey and drink it dry for two seconds."),
         }),
    dict(id="zombie", entity="zombie_devil", name="Zombie Devil", form="Zombie Devil", color=(122, 138, 90), boss=False,
         essence="Zombie Devil's Essence", tooltip="It stinks of rot, and something inside it twitches.",
         moves={
             "zombie_bite": ("Infectious Bite", "A bite that turns: anything that dies in the next ten seconds gets back "
                                                "up as one of your zombies."),
             "zombie_horde": ("Call the Horde", "Your tendrils plunge into the ground and the dead crawl up around your "
                                                "prey. They obey you for two minutes."),
             "zombie_tendrils": ("Brain Tendrils", "The tendrils sprouting from your brain whip all around you."),
             "zombie_feast": ("Blood Feast", "Gorge on your own zombies (or on stored blood) to heal."),
         }),
    dict(id="tomato", entity="tomato_devil", name="Tomato Devil", form="Tomato Devil", color=(216, 58, 42), boss=False,
         essence="Tomato Devil's Essence", tooltip="Full of seeds. It looks back at you.",
         moves={
             "tomato_slam": ("Arm Slam", "Your front arms rear up and slam down on whatever is in front of you."),
             "tomato_seeds": ("Seed Spray", "Squeeze and spit a spray of hard seeds."),
             "tomato_burst": ("Juice Burst", "Swell up and burst a spray of stinging juice all round you. It blinds."),
             "tomato_grab": ("Many Hands", "Two of your eight hands grab hold and pummel."),
         },
         lore="A Tomato Devil that dies comes back from its seeds ten seconds later - unless it was burned."),
    dict(id="sea_cucumber", entity="sea_cucumber_devil", name="Sea Cucumber Devil", form="Sea Cucumber Devil",
         color=(160, 122, 98), boss=False, essence="Sea Cucumber Devil's Essence",
         tooltip="Slimy. Fingers grow out of it.",
         moves={
             "seacu_grab": ("Finger Grab", "The fingers all over your body seize whatever is close and hold it."),
             "seacu_spew": ("Spew Guts", "Throw out your own guts like a real sea cucumber: sticky and poisonous."),
             "seacu_slam": ("Body Slam", "Topple onto your prey with all your weight."),
             "seacu_regen": ("Regenerate", "Knit yourself back together."),
         }),
    dict(id="eternity", entity="eternity_devil", name="Eternity Devil", form="Eternity Devil", color=(200, 154, 138),
         boss=True, essence="Eternity Devil's Essence", tooltip="Its clock is stuck at 8:18.",
         moves={
             "eternity_loop": ("The Infinite Floor", "Everything around you is trapped in a loop for 20 seconds: walk out "
                                                     "of the ring and you walk back in on the far side."),
             "eternity_tide": ("Tide of Flesh", "A tide of arms and heads surges out of you and over whatever is in "
                                                "front of you."),
             "eternity_swallow": ("Swallow", "Your mouths close over whatever is close. It heals you."),
             "eternity_endless": ("Endless", "You can't be killed the ordinary way: knit yourself back together."),
         },
         lore="The Eternity Devil regenerates constantly."),
    dict(id="darkness", entity="darkness_devil", name="Darkness Devil", form="Darkness Devil", color=(90, 90, 112),
         boss=True, essence="Darkness Devil's Essence", tooltip="The light around it goes out.",
         moves={
             "darkness_sever": ("Severance", "One sweep of your hand and everyone around you loses their arms: whatever "
                                             "they held falls, and they can barely fight."),
             "darkness_hell": ("Hell's Darkness", "Drown everything around you in darkness. Nothing can see; you can."),
             "darkness_cut": ("Unseen Cut", "An unseen force splits everything along a line. The wounds won't heal."),
             "darkness_rake": ("Rake", "Both clawed hands tear down."),
         },
         lore="The Darkness Devil burns twice as badly and bright light hurts it."),
    dict(id="gun_devil", entity="gun_devil", name="Gun Devil", form="Gun Devil", color=(138, 142, 150), boss=True,
         essence="Gun Devil's Essence", tooltip="Heavier than it looks. It smells of gunpowder.",
         moves={
             "gundevil_massacre": ("Massacre", "In a heartbeat, a bullet for every living thing you can see within 48 "
                                               "blocks."),
             "gundevil_volley": ("Rifle Volley", "Both rifle arms swing up and pour fire at your target."),
             "gundevil_belts": ("Belt Lash", "The ammunition belts you have for legs whip round you."),
             "gundevil_storm": ("Bullet Storm", "Barrels erupt all over your body and fire in every direction."),
         }),
    dict(id="typhoon", entity="typhoon_devil", name="Typhoon Devil", form="Typhoon Devil", color=(154, 176, 200),
         boss=True, essence="Typhoon Devil's Essence", tooltip="A wind blows out of it that never stops.",
         moves={
             "typhoon_charge": ("Demolishing Charge", "Charge straight through everything - walls included - and hurl "
                                                      "whatever you hit."),
             "typhoon_gale": ("Gale", "A blast of wind that flings everything in front of you away."),
             "typhoon_tornado": ("Tornado", "Become the eye of a storm: everything around you is sucked in, lifted and "
                                            "battered, then flung away."),
             "typhoon_hurl": ("Hurl Debris", "Tear up rubble and hurl it."),
         }),
    dict(id="fox", entity="fox_devil", name="Fox Devil", form="Fox Devil", color=(232, 160, 96), boss=False,
         essence="Fox Devil's Essence", tooltip="Covered in fur and eyes. It is hungry.",
         moves={
             "fox_kon": ("Kon!", "Your jaws lunge out of nowhere at whatever you point at and bite it clean through."),
             "fox_claw": ("Eyed Claw", "A swipe of the forepaw covered in eyes."),
             "fox_pounce": ("Pounce", "Spring at your prey from far off and land on it with all your weight."),
             "fox_devour": ("Devour", "Catch your prey in your jaws, shake it like a rabbit, then fling what's left. It "
                                      "heals you."),
         },
         lore="The Fox Devil only lends its head to hunters it likes."),
    dict(id="curse", entity="curse_devil", name="Curse Devil", form="Curse Devil", color=(216, 208, 184), boss=True,
         essence="Curse Devil's Essence", tooltip="A rusty nail is driven through it.",
         moves={
             "curse_nail": ("The Nail", "Stab. Stab the same thing three times within 30 seconds and the Curse takes it "
                                        "in its hand and wrings it."),
             "curse_grip": ("Crushing Grip", "A hand bigger than a man closes round your prey, lifts it, wrings it and "
                                             "slams it down."),
             "curse_hex": ("Hex", "Curse everything in front of you: slowed, sapped, its wounds won't close, and it "
                                  "carries a nail's worth of your curse."),
             "curse_rise": ("Grave Hands", "Bony hands claw up out of the ground around you and drag everything "
                                           "down."),
         },
         lore="The Curse Devil takes a heavy price for every life it takes."),
    dict(id="future", entity="future_devil", name="Future Devil", form="Future Devil", color=(200, 168, 112), boss=False,
         essence="Future Devil's Essence", tooltip="The future is the best!",
         moves={
             "future_foresight": ("Foresight", "See what's coming: the next five blows aimed at you in 15 seconds miss, "
                                               "and everything nearby is revealed."),
             "future_glimpse": ("Glimpse of Death", "Show your target how it dies. Three seconds later it comes true - "
                                                    "a little."),
             "future_reach": ("Long Reach", "Your long, many-jointed arm unfolds and swats."),
             "future_best": ("Future's the Best!", "Dance! You heal, and you hit harder and stand firmer for 20 "
                                                   "seconds."),
         },
         lore="The Future Devil never leaves its cell. Sometimes it dodges blows before they are thrown."),
    dict(id="ghost", entity="ghost_devil", name="Ghost Devil", form="Ghost Devil", color=(232, 224, 240), boss=False,
         essence="Ghost Devil's Essence", tooltip="You can barely see it. It is cold.",
         moves={
             "ghost_strangle": ("Strangle", "Hands no one can see close round a throat and lift it off the ground."),
             "ghost_snatch": ("Snatch", "An unseen hand snatches your prey up and throws it aside."),
             "ghost_intangible": ("Intangible", "For six seconds nothing can touch you, or see you."),
             "ghost_fear": ("Smell Fear", "Everything nearby shows itself and weakens; the badly hurt freeze in "
                                          "terror."),
         },
         lore="The Ghost Devil can be seen only by its contractor."),
    dict(id="angel", entity="angel_devil", name="Angel Devil", form="Angel Devil", color=(240, 224, 176), boss=False,
         essence="Angel Devil's Essence", tooltip="A feather and a halo. Touching it makes you tired.", moves={}),
    dict(id="war", entity="yoru", name="Yoru", form="War Devil", color=(176, 40, 40), boss=True,
         essence="War Devil's Essence", tooltip="Everything you own looks like a weapon now.", moves={}),
    dict(id="famine", entity="fami", name="Fami", form="Famine Devil", color=(232, 144, 176), boss=True,
         essence="Famine Devil's Essence", tooltip="You are starving just holding it.", moves={}),
    dict(id="falling", entity="falling_devil", name="Falling Devil", form="Falling Devil", color=(240, 240, 240),
         boss=True, essence="Falling Devil's Essence", tooltip="It pulls upward.", moves={}),
    dict(id="justice", entity="justice_devil", name="Justice Devil", form="Justice Devil", color=(138, 154, 90),
         boss=True, essence="Justice Devil's Essence", tooltip="It squirms like a caterpillar.", moves={}),
]

HUMANOID_TRIGGERS = {"control": "control_devil", "angel": "angel_wings", "war": "yoru_takes_over",
                     "famine": "famine_hunger"}


def essence_item(d):
    return ("gun" if d["id"] == "gun_devil" else d["id"]) + "_devil_essence"


def lang():
    out = {
        "ability.csm.manifest": "Manifest",
        "ability.csm.manifest.desc": "Let your true form out: the devil tears out of the human shell you wear. Use it "
                                     "again to take human shape. Needs room to stand up in.",
        "tooltip.csm.essence_use": "Hold Use to swallow it. The devil pours into you and you become it",
        "msg.csm.no_room": "Not enough room for your true form here.",
        "msg.csm.dominated": "%s creatures obey you now.",
        "msg.csm.kneel": "\"Kneel.\"",
        "msg.csm.contract": "The Prime Minister's contract is in force: your injuries go elsewhere.",
        "msg.csm.eternity_loop": "The corridor loops back on itself. Every clock says 8:18.",
        "msg.csm.severed": "Your arms are gone.",
        "effect.csm.unhealing": "Unhealing Wound",
        "effect.csm.severed": "Severed Arms",
    }
    for d in DEVILS:
        i = d["id"]
        out["entity.csm." + d["entity"]] = d["name"]
        out["item.csm." + essence_item(d)] = d["essence"]
        out["item.csm." + d["entity"] + "_spawn_egg"] = d["name"] + " Spawn Egg"
        out["hybrid.csm." + i] = d["form"]
        out["tooltip.csm.essence." + i] = d["tooltip"]
        out["msg.csm.became_devil." + i] = d.get("became", "You are the %s now. Press V for the ability wheel, G to "
                                                           "manifest your true form." % d["form"])
        out["msg.csm.revived." + i] = "Devils don't die that easily."
        out["msg.csm.trigger_failed." + i] = "Not enough blood to let the devil out."
        if "trigger" in d:
            tid, tname, tdesc = d["trigger"]
            out["ability.csm." + tid] = tname
            out["ability.csm." + tid + ".desc"] = tdesc
        for aid, (name, desc) in d["moves"].items():
            out["ability.csm." + aid] = name
            out["ability.csm." + aid + ".desc"] = desc
    return out


def loot_table(d):
    """A boss always leaves its essence when a player kills it; lesser devils sometimes do. All of them bleed."""
    essence = {"type": "minecraft:item", "name": "csm:" + essence_item(d)}
    pools = []
    if d["boss"]:
        pools.append({"rolls": 1, "entries": [essence], "conditions": [{"condition": "minecraft:killed_by_player"}]})
    else:
        pools.append({"rolls": 1, "entries": [essence], "conditions": [
            {"condition": "minecraft:killed_by_player"},
            {"condition": "minecraft:random_chance_with_looting", "chance": 0.12, "looting_multiplier": 0.04}]})
    pools.append({"rolls": {"type": "minecraft:uniform", "min": 0, "max": 2},
                  "entries": [{"type": "minecraft:item", "name": "csm:blood_vial"}]})
    return {"type": "minecraft:entity", "pools": pools}
