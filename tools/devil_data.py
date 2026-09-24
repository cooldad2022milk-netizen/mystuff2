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
    dict(id="fox", entity="fox_devil", name="Fox Devil", form="Fox Devil", color=(244, 240, 230), boss=False,
         contract=[("fox_devil_contract_paw", 0.25), ("fox_devil_contract_head", 0.06)],
         moves={
             "fox_kon": ("Kon!", "Your jaws lunge out of nowhere at whatever you point at and bite it clean through."),
             "fox_claw": ("Eyed Claw", "A swipe of the forepaw covered in eyes."),
             "fox_pounce": ("Pounce", "Spring at your prey from far off and land on it with all your weight."),
             "fox_devour": ("Devour", "Catch your prey in your jaws, shake it like a rabbit, then fling what's left. It "
                                      "heals you."),
         },
         lore="The Fox Devil only lends its head to hunters it likes."),
    dict(id="curse", entity="curse_devil", name="Curse Devil", form="Curse Devil", color=(216, 208, 184), boss=True,
         contract=[("curse_devil_contract", 1.0)],
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
         contract=[("future_devil_contract", 0.3)],
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
         contract=[("ghost_devil_contract", 0.25)],
         moves={
             "ghost_strangle": ("Strangle", "Hands no one can see close round a throat and lift it off the ground."),
             "ghost_snatch": ("Snatch", "An unseen hand snatches your prey up and throws it aside."),
             "ghost_intangible": ("Intangible", "For six seconds nothing can touch you, or see you."),
             "ghost_fear": ("Smell Fear", "Everything nearby shows itself and weakens; the badly hurt freeze in "
                                          "terror."),
         },
         lore="The Ghost Devil can be seen only by its contractor."),
    dict(id="angel", entity="angel_devil", name="Angel Devil", form="Angel Devil", color=(240, 224, 176), boss=False,
         essence="Angel Devil's Essence", tooltip="A feather and a halo. Touching it makes you tired.",
         trigger=("angel_wings", "Angel Wings", "Let the Angel out: halo alight, white wings spread. You can fly."),
         moves={
             "angel_touch": ("Lifespan Drain", "Touch a living thing and take years of its life. You keep them."),
             "angel_sword": ("Lifespan Sword", "Forge the years you have taken into a golden sword and cut."),
             "angel_spears": ("Lifespan Spears", "Raise a hand: the years you have taken rain down as spears."),
             "angel_gust": ("Wing Beat", "One hard beat of the wings blows everything in front of you away."),
         }),
    dict(id="war", entity="yoru", name="Yoru", form="War Devil", color=(176, 40, 40), boss=True,
         essence="War Devil's Essence", tooltip="Everything you own looks like a weapon now.",
         trigger=("yoru_takes_over", "Yoru Takes Over", "Let Yoru take the body: the scars open on your face and your "
                                                        "eyes ring red."),
         moves={
             "war_weaponize": ("Weaponize", "\"I'll make you into a weapon.\" Something weak enough becomes one, and "
                                            "your next blows land harder."),
             "war_sword": ("School Uniform Sword", "A crude blade made out of a school uniform: one heavy cut."),
             "war_spear": ("War Spear", "Hurl a spear with everything you have: it runs through everything in a "
                                        "line."),
             "war_arsenal": ("Arsenal", "Everything that has ever been a weapon, all at once: a barrage falls round "
                                        "your target."),
         }),
    dict(id="famine", entity="fami", name="Fami", form="Famine Devil", color=(232, 144, 176), boss=True,
         essence="Famine Devil's Essence", tooltip="You are starving just holding it.",
         trigger=("famine_hunger", "Hunger", "Let the Famine Devil show: your ringed eyes light up, and everything "
                                              "around you feels it in its stomach."),
         moves={
             "famine_starve": ("Starve", "Whatever you look at is suddenly, desperately hungry."),
             "famine_enthrall": ("Enthrall", "The starving will do anything for you: they turn on whatever you are "
                                             "fighting."),
             "famine_vanish": ("Vanish", "You are simply somewhere else - usually right behind them."),
             "famine_bite": ("Feast", "Eat. It heals you, and fills a stomach that is never full."),
         }),
    dict(id="falling", entity="falling_devil", name="Falling Devil", form="Falling Devil", color=(240, 240, 240),
         boss=True, essence="Falling Devil's Essence", tooltip="It pulls upward. It smells of cooking.",
         moves={
             "falling_fall": ("Fall", "Everything around you falls - up, into the sky - and comes back down."),
             "falling_course": ("The First Course", "Serve your prey the fall it fears most. It relives it: sick, "
                                                    "slow, weak and half blind."),
             "falling_plunge": ("Plunge", "Tip over and drop on your prey head first."),
         },
         lore="The Falling Devil wears a chef's dress over a body made of corpses, and walks on hands."),
    dict(id="justice", entity="justice_devil", name="Justice Devil", form="Justice Devil", color=(138, 154, 90),
         boss=True, essence="Justice Devil's Essence", tooltip="It squirms like a caterpillar.",
         moves={
             "justice_gavel": ("Gavel", "Your arm is a judge's gavel. Bring it down: the sentence is carried out."),
             "justice_lash": ("Tentacle Lash", "The tentacles you can't control whip out all round you."),
             "justice_jaw": ("Belly Jaw", "Your belly splits open into an enormous jaw and bites whatever is in "
                                          "front of you. It heals you."),
         },
         lore="The Justice Devil is blind, like Justice herself, and wears a judge's bib."),
    # Pochita's true form. Nobody eats its essence: it only ever comes out of a Chainsaw hybrid (Hero of Hell), and
    # beaten as a mob it leaves its heart - the one Pochita gave Denji.
    dict(id="chainsaw_devil", entity="chainsaw_devil", name="Chainsaw Devil", form="Chainsaw Devil (Hero of Hell)",
         color=(42, 42, 48), boss=True, takeover=True, drops=[("chainsaw_devil_heart", 1.0)],
         trigger=("hero_recede", "Let Denji Back",
                  "Pochita lets go: it goes back to sleep in your chest and you're yourself again, spent. It lets "
                  "go on its own after 30 seconds."),
         moves={
             "hero_rend": ("Four-Saw Rend", "Four saws - two out of each split forearm - tear through everything in "
                                            "front of you."),
             "hero_charge": ("Rev Charge", "Head down, the saw on your head screaming: run through everything in "
                                           "your way."),
             "hero_chains": ("Chain Whip", "The chains come off your saws and whip round you in a wide circle, then "
                                           "drag everything they caught to your feet."),
             "hero_devour": ("Devour", "Seize your prey and eat it. Anything weak enough is eaten outright - and a "
                                       "devil you eat is erased, gone from Hell and Earth for good. The rest lose a "
                                       "great bite of themselves. It heals you."),
             "hero_roar": ("Hero of Hell", "The roar devils fear above everything. Whatever hears it is weakened and "
                                           "slowed; devils break off and back away."),
         },
         lore="The Hero of Hell. What it eats is erased from existence."),
]

# Contracts (contract.Contract): what a hunter gets from the Fox, Curse, Future and Ghost devils. The Fox Devil only
# lends its head to hunters it finds handsome; everyone else it deals with gets its paw - two different contracts.
CONTRACTS = [
    dict(id="fox_head", item="fox_devil_contract_head", name="Fox Devil (Head)",
         item_name="Fox Devil Contract: Head", color=(244, 240, 230),
         tooltip="The Fox Devil likes your face. It will lend you its head.",
         price="Price: it bites off a little of you every time (1 heart).",
         signed="The Fox Devil takes its first mouthful of you. Make the fox with your hand and say \"Kon!\" (it is on "
                "your ability wheel, V).",
         moves={"contract_kon": ("Kon!", "Make the fox with your hand, point it and say the word. The Fox Devil's head - "
                                        "only its head - appears around your prey with its jaws wide open and bites down. "
                                        "Small prey is swallowed whole.",
                                 "Price: 1 heart of flesh")}),
    dict(id="fox_paw", item="fox_devil_contract_paw", name="Fox Devil (Paw)",
         item_name="Fox Devil Contract: Paw", color=(232, 210, 180),
         tooltip="The Fox Devil doesn't think much of your face. It will lend you a paw.",
         price="Price: it bites off a little of you every time (half a heart).",
         signed="The Fox Devil takes its first mouthful of you. It won't lend you its head, but its paw is yours (V).",
         moves={"contract_paw_slam": ("Fox Paw", "Point at your prey: the Fox Devil's huge paw, covered in eyes, comes down "
                                                 "on it out of the sky, claws first.",
                                      "Price: half a heart of flesh"),
                "contract_paw_swipe": ("Paw Swipe", "The paw sweeps across in front of you and bats everything aside.",
                                       "Price: half a heart of flesh")}),
    dict(id="curse", item="curse_devil_contract", name="Curse Devil",
         item_name="Curse Devil Contract", color=(216, 208, 184),
         tooltip="A rusty nail is pinned to it.",
         price="Price: every time the Curse comes, it takes a heart of your lifespan. For good.",
         signed="The Curse Devil will come for anything you drive the nail into three times. It will take your lifespan "
                "for it.",
         moves={"contract_curse_nail": ("Curse Nail", "Stab with the nail. Stab the same thing three times within 30 "
                                                      "seconds and the mouth on it counts down to zero: the Curse Devil "
                                                      "rises behind it, takes it by both arms and bites.",
                                        "Price: a heart of lifespan when the Curse comes")}),
    dict(id="future", item="future_devil_contract", name="Future Devil",
         item_name="Future Devil Contract", color=(200, 168, 112),
         tooltip="\"The future is the best!\"",
         price="Price: it lives in your right eye, and watches.",
         signed="The Future Devil moves into your right eye. It laughs: \"You will die the worst possible death!\"",
         moves={"contract_future_sight": ("Future Sight", "The Future Devil in your right eye shows you the next few "
                                                          "seconds: for 15 seconds the next four blows aimed at you miss, "
                                                          "and whatever means you harm shows itself. Now and then it "
                                                          "shows you a blow coming even when you don't ask.",
                                          "Price: none (it lives in your eye)")}),
    dict(id="ghost", item="ghost_devil_contract", name="Ghost Devil",
         item_name="Ghost Devil Contract", color=(232, 224, 240),
         tooltip="You can barely see the writing. It is cold.",
         price="Price: your right eye.",
         signed="The Ghost Devil takes your right eye. Its right arm is yours now: nobody else can see it.",
         moves={"contract_ghost_hand": ("Ghost Hand", "The Ghost Devil's invisible right arm reaches out, closes round a "
                                                      "throat, lifts it off the ground and squeezes.",
                                        "Price: none (your eye is already paid)"),
                "contract_ghost_fling": ("Ghost Fling", "The invisible hand snatches something up and hurls it aside.",
                                         "Price: none (your eye is already paid)")}),
    dict(id="snake", item="snake_devil_contract", name="Snake Devil",
         item_name="Snake Devil Contract", color=(90, 154, 58),
         tooltip="It is scaly. Something inside it swallows.",
         price="Price: a fingernail for every command (and a nosebleed to let something out).",
         signed="The Snake Devil takes your first fingernail. Command it with your hands, like Sawatari: \"Snake - "
                "swallow it.\"",
         moves={"contract_snake_swallow": ("Snake: Swallow", "The Snake Devil's huge green head bursts up out of the "
                                                             "ground under your target, its mouth of interlocking "
                                                             "hands wide open, and swallows it whole. Anything weak "
                                                             "enough stays in its belly (up to 3); the rest is badly "
                                                             "bitten.",
                                           "Price: a fingernail"),
                "contract_snake_release": ("Snake: Release", "The snake rises where you point and spits out the last "
                                                             "thing it swallowed: whole again, healed, and fighting "
                                                             "for you for two minutes.",
                                           "Price: a fingernail and a nosebleed"),
                "contract_snake_tail": ("Snake: Tail", "The Snake Devil's thick tail bursts out of the ground beside "
                                                       "you and swats everything in front of you away.",
                                        "Price: a fingernail")}),
    dict(id="octopus", item="octopus_devil_contract", name="Octopus Devil",
         item_name="Octopus Devil Contract", color=(154, 74, 122),
         tooltip="The ink on it never quite dries.",
         price="Price: between you and the devil. You come away starving: the bigger the call, the bigger the price.",
         signed="The Octopus Devil takes its price, whatever it was. Cross your index and middle fingers to call it, "
                "like Yoshida.",
         moves={"contract_octopus": ("Octopus", "Cross two fingers: the Octopus Devil's tentacles come up out of "
                                                "clouds of ink round your target, coil round it (and up to three "
                                                "things next to it), lift, squeeze, and smash them down.",
                                     "Price: hunger (a lot)"),
                "contract_octopus_ink": ("Ink", "The Octopus Devil sprays a cloud of ink round you. Everything in it is "
                                                "blinded and loses sight of you, and you slip away unseen.",
                                         "Price: hunger"),
                "contract_octopus_lift": ("Tentacle Lift", "A tentacle comes up out of a puddle of ink under your "
                                                           "feet and flings you the way you're looking.",
                                          "Price: hunger (a little)")}),
    dict(id="doll", item="doll_devil_contract", name="Doll Devil",
         item_name="Doll Devil Contract", color=(232, 200, 184),
         tooltip="A child's handwriting. It smells of Christmas.",
         price="Price: unknown. Santa Claus never said what she paid.",
         signed="The Doll Devil accepts. Whoever you touch is yours - and whoever they touch is yours too.",
         moves={"contract_doll_touch": ("Doll Touch", "Touch someone and they become your doll: they obey you, one "
                                                      "of their arms is a blade now, and there's no turning them "
                                                      "back. Anyone a doll hurts becomes a doll too. It does "
                                                      "nothing to devils, hybrids or fiends, and a doll you leave "
                                                      "behind (48 blocks) falls over, lifeless. Up to 12.",
                                        "Price: unknown"),
                "contract_doll_command": ("Doll Command", "Every doll you have turns on what you point at. Point at "
                                                          "nothing (or at a doll) and they come back to you.",
                                          "Price: unknown")}),
]

# chests a contract turns up in (the devil hunters who held it didn't all make it)
CONTRACT_LOOT = {
    "fox_devil_contract_paw": (["minecraft:chests/village/village_temple", "minecraft:chests/pillager_outpost",
                                "minecraft:chests/woodland_mansion", "minecraft:chests/simple_dungeon"], 0.05),
    "fox_devil_contract_head": (["minecraft:chests/woodland_mansion", "minecraft:chests/ancient_city",
                                 "minecraft:chests/stronghold_library"], 0.03),
    "curse_devil_contract": (["minecraft:chests/ancient_city", "minecraft:chests/stronghold_library",
                              "minecraft:chests/desert_pyramid"], 0.03),
    "future_devil_contract": (["minecraft:chests/stronghold_library", "minecraft:chests/end_city_treasure"], 0.04),
    "ghost_devil_contract": (["minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft",
                              "minecraft:chests/ancient_city"], 0.03),
    # Sawatari's snake: jungle temples, desert pyramids and the deep dark
    "snake_devil_contract": (["minecraft:chests/jungle_temple", "minecraft:chests/desert_pyramid",
                              "minecraft:chests/ancient_city", "minecraft:chests/stronghold_library"], 0.03),
    # Yoshida's octopus: the sea
    "octopus_devil_contract": (["minecraft:chests/shipwreck_treasure", "minecraft:chests/buried_treasure",
                                "minecraft:chests/underwater_ruin_big"], 0.04),
    # Santa Claus: snow, and old houses full of dolls
    "doll_devil_contract": (["minecraft:chests/igloo_chest", "minecraft:chests/woodland_mansion",
                             "minecraft:chests/stronghold_library"], 0.03),
}

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
        out["item.csm." + d["entity"] + "_spawn_egg"] = d["name"] + " Spawn Egg"
        out["hybrid.csm." + i] = d["form"]
        if "takeover" in d:
            out["msg.csm.revived." + i] = "Pochita keeps you going..."
        elif "contract" not in d:
            out["item.csm." + essence_item(d)] = d["essence"]
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
    for c in CONTRACTS:
        i = c["id"]
        out["contract.csm." + i] = c["name"]
        out["item.csm." + c["item"]] = c["item_name"]
        out["tooltip.csm.contract." + i] = c["tooltip"]
        out["tooltip.csm.contract_price." + i] = c["price"]
        out["msg.csm.contract_signed." + i] = c["signed"]
        for aid, (name, desc, price) in c["moves"].items():
            out["ability.csm." + aid] = name
            out["ability.csm." + aid + ".desc"] = desc
            out["price.csm." + aid] = price
    out.update({
        "tooltip.csm.contract_use": "Hold Use to bite your thumb and seal the contract in blood",
        "msg.csm.lifespan": "Years of life taken: %s",
        "msg.csm.weaponized": "\"I'll make you into a weapon.\" Your next blows land harder.",
        "msg.csm.contract_already": "You already have this contract.",
        "msg.csm.contract_missing": "You no longer have that contract.",
        "msg.csm.curse_count": "The mouth on it counts: \"%s...\"",
        "msg.csm.curse_toll": "The Curse Devil takes its price. Hearts of lifespan gone: %s",
        "msg.csm.future_sight": "You can see a few seconds ahead.",
        "msg.csm.ghost_nothing": "The ghost's hand closes on nothing. Look at what you want it to take.",
        "screen.csm.contractor": "Devil Hunter",
        "screen.csm.contracts": "Contracts: %s",
        "commands.csm.not_playable": "Nobody becomes the %s: make a contract with it instead (/csm contract).",
        "commands.csm.takeover_only": "The %s only comes out of a %s (its Hero of Hell move).",
        "msg.csm.snake_empty": "The snake's belly is empty. Have it swallow something first.",
        "msg.csm.snake_swallowed": "The snake swallowed the %s whole (%s/%s in its belly).",
        "msg.csm.snake_released": "The snake lets the %s out. It fights for you now.",
        "msg.csm.doll_nothing": "Your hand touches nothing. Get close enough to touch them.",
        "msg.csm.doll_immune": "The %s doesn't change. The Doll Devil can't touch devils, hybrids or fiends.",
        "msg.csm.doll_max": "You can't keep more than %s dolls.",
        "msg.csm.doll_made": "The %s is your doll now (%s dolls).",
        "msg.csm.doll_attack": "%s dolls turn on it.",
        "msg.csm.doll_recall": "%s dolls come back to you.",
        "commands.csm.contract_unknown": "Unknown contract: %s",
        "commands.csm.contract_add": "%s made a contract with the %s",
        "commands.csm.contract_remove": "%s's contract with the %s is broken",
        "commands.csm.contract_has": "%s already has a contract with the %s",
        "commands.csm.contract_hasnt": "%s has no contract with the %s",
        "commands.csm.contract_list": "%s's contracts: %s (hearts of lifespan the Curse has taken: %s)",
        "entity.csm.contract_summon": "Contract Devil",
    })
    return out


def loot_table(d):
    """A boss always leaves its essence when a player kills it; lesser devils sometimes do. All of them bleed.
    A contract devil leaves no essence: beaten, it offers a contract (the Fox its paw far more often than its head)."""
    pools = []
    if "contract" in d or "drops" in d:
        for item, chance in d.get("contract", d.get("drops")):
            conds = [{"condition": "minecraft:killed_by_player"}]
            if chance < 1:
                conds.append({"condition": "minecraft:random_chance_with_looting", "chance": chance,
                              "looting_multiplier": 0.03})
            pools.append({"rolls": 1, "entries": [{"type": "minecraft:item", "name": "csm:" + item}],
                          "conditions": conds})
        pools.append({"rolls": {"type": "minecraft:uniform", "min": 0, "max": 2},
                      "entries": [{"type": "minecraft:item", "name": "csm:blood_vial"}]})
        return {"type": "minecraft:entity", "pools": pools}
    essence = {"type": "minecraft:item", "name": "csm:" + essence_item(d)}
    if d["boss"]:
        pools.append({"rolls": 1, "entries": [essence], "conditions": [{"condition": "minecraft:killed_by_player"}]})
    else:
        pools.append({"rolls": 1, "entries": [essence], "conditions": [
            {"condition": "minecraft:killed_by_player"},
            {"condition": "minecraft:random_chance_with_looting", "chance": 0.12, "looting_multiplier": 0.04}]})
    pools.append({"rolls": {"type": "minecraft:uniform", "min": 0, "max": 2},
                  "entries": [{"type": "minecraft:item", "name": "csm:blood_vial"}]})
    return {"type": "minecraft:entity", "pools": pools}
