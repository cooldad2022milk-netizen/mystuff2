"""Writes the language file and the loot-modifier data (devil hearts in structure chests)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "src", "main", "resources")

LANG = {
    "itemGroup.csm": "Chainsaw Man: Hybrids",
    "item.csm.chainsaw_devil_heart": "Chainsaw Devil's Heart",
    "item.csm.crossbow_devil_heart": "Crossbow Devil's Heart",
    "item.csm.flamethrower_devil_heart": "Flamethrower Devil's Heart",
    "item.csm.whip_devil_heart": "Whip Devil's Heart",
    "item.csm.bomb_devil_heart": "Bomb Devil's Heart",
    "item.csm.spear_devil_heart": "Spear Devil's Heart",
    "item.csm.katana_devil_heart": "Katana Devil's Heart",
    "item.csm.longsword_devil_heart": "Longsword Devil's Heart",
    "item.csm.blood_devil_remains": "Blood Devil's Remains",
    "item.csm.shark_devil_remains": "Shark Devil's Remains",
    "item.csm.violence_devil_remains": "Violence Devil's Remains",
    "item.csm.cosmos_devil_remains": "Cosmos Devil's Remains",
    "item.csm.gun_devil_flesh": "Gun Devil's Flesh",
    "effect.csm.halloween": "Halloween",
    "item.csm.human_heart": "Human Heart",
    "item.csm.blood_vial": "Blood Vial",
    "entity.csm.chain_hook": "Chain",
    "entity.csm.crossbow_bolt": "Crossbow Bolt",
    "entity.csm.napalm": "Burning Fuel",
    "entity.csm.spear": "Spear",
    "entity.csm.spark_bomb": "Explosive Spark",
    "entity.csm.head_bomb": "Bomb Devil's Head",
    "hybrid.csm.none": "Human",
    "hybrid.csm.chainsaw": "Chainsaw Hybrid",
    "hybrid.csm.crossbow": "Crossbow Hybrid",
    "hybrid.csm.flamethrower": "Flamethrower Hybrid",
    "hybrid.csm.whip": "Whip Hybrid",
    "hybrid.csm.bomb": "Bomb Hybrid",
    "hybrid.csm.spear": "Spear Hybrid",
    "hybrid.csm.katana": "Katana Hybrid",
    "hybrid.csm.longsword": "Longsword Hybrid",
    "hybrid.csm.blood": "Blood Fiend",
    "hybrid.csm.shark": "Shark Fiend",
    "hybrid.csm.violence": "Violence Fiend",
    "hybrid.csm.cosmos": "Cosmos Fiend",
    "hybrid.csm.gun": "Gun Fiend",

    "ability.csm.revert": "Put the Devil Away",
    "ability.csm.pull_cord": "Pull the Starter Cord",
    "ability.csm.pull_cord.desc": "Grab the cord hanging from your chest and yank it. The engine roars and chainsaws burst out of your forehead and forearms. Needs blood, or it only sputters.",
    "ability.csm.chainsaw_slash": "Chainsaw Slash",
    "ability.csm.chainsaw_slash.desc": "Two brutal cuts with your forearm chainsaws.",
    "ability.csm.headsaw_charge": "Headsaw Charge",
    "ability.csm.headsaw_charge.desc": "Charge headfirst, sawing through everything in your path with the chainsaw on your forehead.",
    "ability.csm.chain_grapple": "Chain",
    "ability.csm.chain_grapple.desc": "Fire a chain from your arm. It hooks a wall to reel you in, or wraps a target and drags it to you.",
    "ability.csm.rip_and_tear": "Rip and Tear",
    "ability.csm.rip_and_tear.desc": "Grab whatever is in front of you and saw straight through it, drenching yourself in blood.",
    "ability.csm.leg_saw_spin": "Leg Saw Spin",
    "ability.csm.leg_saw_spin.desc": "Chainsaws erupt from your shins for a full spinning kick.",
    "ability.csm.chain_bind": "Chain Bind",
    "ability.csm.chain_bind.desc": "The chains come off your saws and wrap round the target - and round you - so neither of you gets away. It is held against you and can barely fight back. In water it drowns (it's how Denji beat Reze).",
    "ability.csm.hero_of_hell": "Hero of Hell",
    "ability.csm.hero_of_hell.desc": "Stop holding Pochita back. The Chainsaw Devil's true form tears out of you - black, huge, a saw from its head and two from each split forearm, guts round its neck like a scarf - and takes you over for 30 seconds with its own moves. Costs 50 blood. It also comes out on its own when you die with blood in you.",
    "ability.csm.blood_drink": "Drink Blood",
    "ability.csm.blood_drink.desc": "Bite into whatever is in front of you to steal its blood, or burn your stored blood to heal. Works in human form too.",
    "ability.csm.pull_arrow": "Pull the Arrow",
    "ability.csm.pull_arrow.desc": "Reach under your eyepatch and draw the arrow out of your right eye socket to become the Crossbow Devil hybrid.",
    "ability.csm.crossbow_volley": "Volley",
    "ability.csm.crossbow_volley.desc": "Both forearm crossbows fire a fan of bolts.",
    "ability.csm.piercing_bolt": "Piercing Bolt",
    "ability.csm.piercing_bolt.desc": "Overdraw your crossbow and loose a bolt that tears a perfectly round hole through everything it hits.",
    "ability.csm.flash_step": "Flash Step",
    "ability.csm.flash_step.desc": "Move faster than the eye can follow, cutting down everything along the way.",
    "ability.csm.arrow_storm": "Arrow Storm",
    "ability.csm.arrow_storm.desc": "Fire bolts into the sky that rain down around the spot you are looking at.",
    "ability.csm.bite_molar": "Bite the Molar",
    "ability.csm.bite_molar.desc": "Bite down on your trigger molar. Fuel tanks burst from your head, your arms become flamethrowers, and your body is restored to peak condition.",
    "ability.csm.flame_stream": "Flame Stream",
    "ability.csm.flame_stream.desc": "Both flamethrowers pour out a roaring stream of fire.",
    "ability.csm.napalm_shot": "Napalm Shot",
    "ability.csm.napalm_shot.desc": "Lob a glob of burning fuel that explodes and keeps the ground on fire.",
    "ability.csm.inferno_burst": "Inferno Burst",
    "ability.csm.inferno_burst.desc": "Slam your flamethrowers down and blast a ring of fire outward.",
    "ability.csm.conflagration": "Conflagration",
    "ability.csm.conflagration.desc": "Spin with both flamethrowers roaring and set the whole area ablaze.",
    "ability.csm.molar_regeneration": "Molar Regeneration",
    "ability.csm.molar_regeneration.desc": "Press the molar again to restore your body to peak condition.",

    "ability.csm.snap_fingers": "Snap Your Fingers",
    "ability.csm.snap_fingers.desc": "Snap your fingers like the crack of a whip. Whips tear out of both hands and the nape of your neck.",
    "ability.csm.whip_lash": "Lash",
    "ability.csm.whip_lash.desc": "Three whip strikes that reach far past sword range and slice through flesh.",
    "ability.csm.whip_storm": "Whip Storm",
    "ability.csm.whip_storm.desc": "Fling your arms out and spin, shredding everything around you with every whip.",
    "ability.csm.whip_snare": "Snare",
    "ability.csm.whip_snare.desc": "Lash a distant target, coil the whips round it and yank it to your feet.",
    "ability.csm.whip_swing": "Whip Swing",
    "ability.csm.whip_swing.desc": "Crack a whip onto the terrain you are looking at and fling yourself through the air.",
    "ability.csm.sonic_crack": "Sonic Crack",
    "ability.csm.sonic_crack.desc": "Raise every whip overhead and crack them faster than sound. The shockwave blasts everything in front of you away.",

    "ability.csm.pull_pin": "Pull the Pin",
    "ability.csm.pull_pin.desc": "Hook a finger through the grenade pin under your choker and pull it. You explode on the spot and step out of the fireball as the Bomb Devil. Will not light while you are wet.",
    "ability.csm.explosive_combo": "Explosive Combo",
    "ability.csm.explosive_combo.desc": "Punch, punch, kick. Every blow detonates on contact.",
    "ability.csm.spark_flick": "Spark Flick",
    "ability.csm.spark_flick.desc": "Flick your fingers to send out a spark that explodes on whatever it touches.",
    "ability.csm.blast_propulsion": "Blast Propulsion",
    "ability.csm.blast_propulsion.desc": "Explosions out of your palms and feet send you rocketing through the air.",
    "ability.csm.torpedo": "Torpedo",
    "ability.csm.torpedo.desc": "Your forearm becomes a torpedo. Ride it forward and detonate on whatever it hits.",
    "ability.csm.head_bomb": "Head Bomb",
    "ability.csm.head_bomb.desc": "Tear off your own bomb head and throw it for your biggest explosion. A new one grows back.",

    "ability.csm.pull_spear": "Draw the Spear",
    "ability.csm.pull_spear.desc": "Reach over your shoulder and draw a spear out of the nape of your neck. A spearhead bursts from your head and your arms harden into armour.",
    "ability.csm.spear_thrust": "Thrust",
    "ability.csm.spear_thrust.desc": "Three lightning-fast thrusts with the spear growing from your fist.",
    "ability.csm.spear_throw": "Javelin",
    "ability.csm.spear_throw.desc": "Hurl a spear that flies dead straight at whatever you are looking at, pierces through and sticks.",
    "ability.csm.spear_volley": "Spear Volley",
    "ability.csm.spear_volley.desc": "Spears form in the air behind you, then all fire at once at your target.",
    "ability.csm.spear_impale": "Impale",
    "ability.csm.spear_impale.desc": "Vanish and reappear behind your target, driving your spear straight through its back.",
    "ability.csm.spear_eruption": "Spear Eruption",
    "ability.csm.spear_eruption.desc": "Stab the ground: a line of spears bursts out of the earth ahead of you.",

    "ability.csm.pull_left_hand": "Pull Off Your Hand",
    "ability.csm.pull_left_hand.desc": "Tear off your left hand and a katana rises out of the stump. Katana blades push out of both arms and a blade runs through your skull. Putting the sword away leaves you spent for a while.",
    "ability.csm.sword_draw_dash": "Sword-Draw Dash",
    "ability.csm.sword_draw_dash.desc": "Crouch as if to draw, then move faster than the eye can see. You're already past them when every cut opens.",
    "ability.csm.twin_slash": "Twin Slash",
    "ability.csm.twin_slash.desc": "Both forearm katanas cross in an X.",
    "ability.csm.blade_flurry": "Blade Flurry",
    "ability.csm.blade_flurry.desc": "A storm of quick cuts and thrusts.",
    "ability.csm.iai_counter": "Iai Stance",
    "ability.csm.iai_counter.desc": "Wait with a hand on the hilt. The first attack that comes at you is cut down before it lands.",

    "ability.csm.pull_right_hand": "Pull Off Your Hand",
    "ability.csm.pull_right_hand.desc": "Tear off your right hand to bare the blade inside your arm. Your head becomes a pointed visor with longswords for ears. Putting the swords away leaves you spent for a while.",
    "ability.csm.longsword_cleave": "Cleave",
    "ability.csm.longsword_cleave.desc": "Both arm-swords come down together in one heavy overhead cut.",
    "ability.csm.blade_whirl": "Blade Whirl",
    "ability.csm.blade_whirl.desc": "Spin with both arm-swords held out, cutting everything around you.",
    "ability.csm.longsword_lunge": "Lunge",
    "ability.csm.longsword_lunge.desc": "Drive forward sword-first and run through whatever is in the way.",
    "ability.csm.cross_guard": "Cross Guard",
    "ability.csm.cross_guard.desc": "Catch blows on the cross-guards at your elbows: 80% less damage, and melee attackers get it thrown back at them.",

    "ability.csm.blood_awakening": "Gorge on Blood",
    "ability.csm.blood_awakening.desc": "Drink deep. Your horns grow longer and more curved, fresh pairs burst out along the sides of your head, and every blood weapon hits harder.",
    "ability.csm.blood_hammer": "Blood Hammer",
    "ability.csm.blood_hammer.desc": "Shape your blood into a giant hammer and slam it down.",
    "ability.csm.blood_spear": "Blood Spear",
    "ability.csm.blood_spear.desc": "Hurl a spear of blood. It bursts back into blood where it lands.",
    "ability.csm.blood_scythe": "Blood Scythe",
    "ability.csm.blood_scythe.desc": "A wide sweep of a blood scythe. The wounds keep bleeding.",
    "ability.csm.blood_control": "Blood Control",
    "ability.csm.blood_control.desc": "Touch a target and seize the blood inside it. It is torn out of them and into you.",
    "ability.csm.blood_rain": "Thousand Tera Blood Rain",
    "ability.csm.blood_rain.desc": "Blades of blood rain down on the spot you are looking at. Needs you gorged on blood.",

    "ability.csm.shark_devil": "Shark Devil",
    "ability.csm.shark_devil.desc": "Your head swells into a giant shark's skull with three pairs of eyes, and your bite gets stronger.",
    "ability.csm.ground_swim": "Ground Swim",
    "ability.csm.ground_swim.desc": "Dive into the ground and swim through it like water, through walls too. Only your fin shows, and nothing can touch you down there.",
    "ability.csm.shark_bite": "Bite",
    "ability.csm.shark_bite.desc": "Lunge and bite down.",
    "ability.csm.shark_ambush": "Ambush",
    "ability.csm.shark_ambush.desc": "Dive, swim under your target and burst out of the ground beneath it, jaws first.",
    "ability.csm.shark_form": "Shark Form",
    "ability.csm.shark_form.desc": "Turn your whole body into a shark on long fin-legs for 10 seconds: much faster, and anything you run into gets rammed and bitten.",
    "ability.csm.blood_scent": "Blood Scent",
    "ability.csm.blood_scent.desc": "A shark smells blood. Every wounded creature, hybrid and fiend within 48 blocks lights up.",

    "ability.csm.remove_mask": "Take Off the Mask",
    "ability.csm.remove_mask.desc": "The plague-doctor mask pumps poison into you to hold you back. Take it off and you become huge: four hollow eyes and enormous strength.",
    "ability.csm.violent_punch": "Violent Punch",
    "ability.csm.violent_punch.desc": "Your arm swells with muscle for one haymaker. Devastating with the mask off.",
    "ability.csm.crushing_kick": "Crushing Kick",
    "ability.csm.crushing_kick.desc": "Your leg swells and you stamp. The ground fractures and everything nearby is thrown.",
    "ability.csm.mouth_arm": "Mouth Arm",
    "ability.csm.mouth_arm.desc": "An arm bursts out of your mouth, grabs whatever is in front of you and punches it. Mask off only.",
    "ability.csm.rampage": "Rampage",
    "ability.csm.rampage.desc": "Unrestrained violence: a flurry of punches while you push forward. Mask off only.",

    "ability.csm.open_cosmos": "Open the Cosmos",
    "ability.csm.open_cosmos.desc": "Let the universe pour out of your open skull. Halloweens last longer and burn the mind, and All-Out Halloween opens up.",
    "ability.csm.halloween": "Halloween",
    "ability.csm.halloween.desc": "\"Halloween.\" One mind is shown the whole universe at once and can think of nothing but Halloween.",
    "ability.csm.all_out_halloween": "All-Out Halloween",
    "ability.csm.all_out_halloween.desc": "Drag every mind around you into the endless library inside your head. Needs the cosmos opened.",
    "ability.csm.infinite_knowledge": "Infinite Knowledge",
    "ability.csm.infinite_knowledge.desc": "Know everything: every living thing within 48 blocks is revealed, even through walls.",
    "ability.csm.mind_collapse": "Mind Collapse",
    "ability.csm.mind_collapse.desc": "Minds already drowning in the universe give way. Every Halloween-struck target you look at takes damage for the time it had left.",

    "ability.csm.gun_devil": "Gun Devil",
    "ability.csm.gun_devil.desc": "Let more of the Gun Devil out. Barrels burst out all over your body.",
    "ability.csm.carbine_burst": "Carbine Burst",
    "ability.csm.carbine_burst.desc": "Three-round bursts from the M4 that replaced your left forearm.",
    "ability.csm.gun_headshot": "Headshot",
    "ability.csm.gun_headshot.desc": "The pistol barrel between your eyes fires one enormous round that punches through everything in line.",
    "ability.csm.bullet_storm": "Bullet Storm",
    "ability.csm.bullet_storm.desc": "Every barrel on your body fires in every direction. Gun Devil only.",
    "ability.csm.massacre": "Massacre",
    "ability.csm.massacre.desc": "The Gun Devil's massacre: a hail of aimed shots at every living thing you can see within 40 blocks. Gun Devil only.",

    "msg.csm.cooldown": "%s is recharging (%ss)",
    "msg.csm.need_form": "%s needs your devil form. Use your trigger first.",
    "msg.csm.no_blood": "Not enough blood for %s.",
    "msg.csm.no_blood_to_drink": "There is no blood to drink.",
    "msg.csm.trigger_failed.chainsaw": "The engine sputters. You need blood to start the chainsaw.",
    "msg.csm.trigger_failed.crossbow": "The arrow will not come out. You need blood.",
    "msg.csm.trigger_failed.flamethrower": "The molar clicks, but nothing happens. You need blood.",
    "msg.csm.trigger_failed.whip": "Your fingers snap, but nothing comes out. You need blood.",
    "msg.csm.trigger_failed.bomb": "The pin comes out, but nothing happens. You need blood.",
    "msg.csm.trigger_failed.spear": "The spear will not come out of your neck. You need blood.",
    "msg.csm.trigger_failed.katana": "The hand won't come off. You need blood.",
    "msg.csm.trigger_failed.longsword": "The hand won't come off. You need blood.",
    "msg.csm.trigger_failed.blood": "There's not enough blood in you to gorge on.",
    "msg.csm.trigger_failed.shark": "The devil stirs, then settles. You need blood.",
    "msg.csm.trigger_failed.violence": "The mask won't come off. You need blood.",
    "msg.csm.trigger_failed.cosmos": "Halloween... nothing. You need blood.",
    "msg.csm.trigger_failed.gun": "Click. Empty. You need blood.",
    "msg.csm.scent": "You smell blood: %s",
    "msg.csm.too_wet": "You're soaked. The Bomb Devil can't go off while you're wet.",
    "msg.csm.revived.chainsaw": "Your heart revs back to life...",
    "msg.csm.pochita_wakes": "Denji is dead. Pochita gets up.",
    "msg.csm.takeover_end.chainsaw": "Pochita goes back to sleep in your chest. You're yourself again - and exhausted.",
    "msg.csm.erased": "It ate the %s. That devil is gone from Hell and Earth for good.",
    "msg.csm.revived.crossbow": "The devil's heart refuses to let you die...",
    "msg.csm.revived.flamethrower": "The molar clicks. You are back.",
    "msg.csm.revived.whip": "Your heart cracks like a whip. You are back.",
    "msg.csm.revived.bomb": "Your heart ticks like a fuse. You are back.",
    "msg.csm.revived.katana": "Your left hand is pulled free. You are back.",
    "msg.csm.revived.longsword": "Your right hand is pulled free. You are back.",
    "msg.csm.revived.blood": "Your corpse is still full of blood. The Blood Devil gets back up.",
    "msg.csm.revived.shark": "The Shark Devil drags the body back up.",
    "msg.csm.revived.violence": "Violence doesn't stay down.",
    "msg.csm.revived.cosmos": "Halloween.",
    "msg.csm.revived.gun": "The Gun Devil isn't done with this body.",
    "msg.csm.revived.spear": "The devil's heart refuses to let you die...",
    "msg.csm.already_human": "Your own heart is already beating in your chest.",
    "msg.csm.same_heart": "This devil's heart is already in your chest.",
    "msg.csm.heart_replaced.chainsaw": "You tore out your heart and replaced it with the Chainsaw Devil's. Press V for the ability wheel, G to pull the cord.",
    "msg.csm.heart_replaced.crossbow": "You tore out your heart and replaced it with the Crossbow Devil's. Press V for the ability wheel, G to pull the arrow.",
    "msg.csm.heart_replaced.flamethrower": "You tore out your heart and replaced it with the Flamethrower Devil's. Press V for the ability wheel, G to bite down on the molar.",
    "msg.csm.heart_replaced.whip": "You tore out your heart and replaced it with the Whip Devil's. Press V for the ability wheel, G to snap your fingers.",
    "msg.csm.heart_replaced.bomb": "You tore out your heart and replaced it with the Bomb Devil's. Press V for the ability wheel, G to pull the pin.",
    "msg.csm.heart_replaced.spear": "You tore out your heart and replaced it with the Spear Devil's. Press V for the ability wheel, G to draw the spear from your neck.",
    "msg.csm.heart_replaced.katana": "You tore out your heart and replaced it with the Katana Devil's. Press V for the ability wheel, G to pull off your left hand.",
    "msg.csm.heart_replaced.longsword": "You tore out your heart and replaced it with the Longsword Devil's. Press V for the ability wheel, G to pull off your right hand.",
    "msg.csm.possessed.blood": "You died. The Blood Devil wears your corpse now. Press V for the ability wheel, G to gorge on blood.",
    "msg.csm.possessed.shark": "You died. The Shark Devil wears your corpse now. Press V for the ability wheel, G to let the shark out.",
    "msg.csm.possessed.violence": "You died. The Violence Devil wears your corpse now, held back by a poison mask. Press V for the ability wheel, G to take it off.",
    "msg.csm.possessed.cosmos": "You died. Halloween. Press V for the ability wheel, G to open the cosmos.",
    "msg.csm.possessed.gun": "You died. The Gun Devil wears your corpse now. Press V for the ability wheel, G to let it out.",
    "msg.csm.heart_replaced.none": "Your own heart beats in your chest again. You are human.",
    "msg.csm.not_hybrid": "Only hybrids, fiends and devils have an ability wheel. Replace your heart with a devil's heart first.",
    "msg.csm.blood_gross": "...that was just blood. You feel sick.",

    "tooltip.csm.devil_heart.chainsaw": "Still twitching. A starter cord hangs out of it.",
    "tooltip.csm.devil_heart.crossbow": "Skewered by an arrow that never comes out.",
    "tooltip.csm.devil_heart.flamethrower": "Warm to the touch. It smells of fuel.",
    "tooltip.csm.devil_heart.whip": "It twitches like a coiled whip.",
    "tooltip.csm.devil_heart.bomb": "It ticks. There is a pin in it.",
    "tooltip.csm.devil_heart.spear": "Heavy as iron. A spearhead juts out of it.",
    "tooltip.csm.devil_heart.katana": "A katana blade runs clean through it.",
    "tooltip.csm.devil_heart.longsword": "Cold and heavy, with a cross-guard growing out of it.",
    "tooltip.csm.remains.blood": "It is still bleeding. Two small red horns.",
    "tooltip.csm.remains.shark": "It smells of the sea and of blood.",
    "tooltip.csm.remains.violence": "A shard of a parrot-green gas mask is stuck in it.",
    "tooltip.csm.remains.cosmos": "Halloween.",
    "tooltip.csm.remains.gun": "It is bristling with gun barrels. It's warm.",
    "tooltip.csm.remains_use": "Hold Use to let the devil in. You will die, and it will wear your body",
    "tooltip.csm.heart_use": "Hold Use to rip out your heart and replace it with this one",
    "tooltip.csm.human_heart": "Hold Use to put your human heart back",
    "tooltip.csm.blood_vial": "Hybrids drink this to restore blood",

    "key.categories.csm": "Chainsaw Man: Hybrids",
    "key.csm.ability_wheel": "Ability Wheel",
    "key.csm.use_ability": "Use Selected Ability",
    "key.csm.trigger": "Trigger (Transform)",
    "screen.csm.ability_wheel": "Ability Wheel",
    "screen.csm.blood": "Blood: %s",
    "screen.csm.cost": "Costs %s blood",
    "screen.csm.cooldown": "Cooldown %ss",
    "screen.csm.needs_form": "Needs devil form",
    "screen.csm.hint_hold": "Release to select  -  1-9 to pick  -  use with [%s]",
    "screen.csm.hint_click": "Click to select  -  1-9 to pick  -  use with [%s]",
    "hud.csm.blood": "Blood %s",
    "hud.csm.keys": "[%s] use  [%s] wheel",
    "commands.csm.hybrid": "%s is now a %s",
    "commands.csm.blood": "Set %s's blood to %s",
}

LOOT = {
    "chainsaw": ["minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft",
                 "minecraft:chests/woodland_mansion", "minecraft:chests/ancient_city", "minecraft:chests/shipwreck_supply"],
    "crossbow": ["minecraft:chests/stronghold_corridor", "minecraft:chests/pillager_outpost",
                 "minecraft:chests/woodland_mansion", "minecraft:chests/ancient_city", "minecraft:chests/end_city_treasure"],
    "flamethrower": ["minecraft:chests/bastion_treasure", "minecraft:chests/nether_bridge", "minecraft:chests/ruined_portal",
                     "minecraft:chests/desert_pyramid", "minecraft:chests/bastion_other"],
    "whip": ["minecraft:chests/simple_dungeon", "minecraft:chests/jungle_temple", "minecraft:chests/igloo_chest",
             "minecraft:chests/village/village_weaponsmith", "minecraft:chests/ancient_city"],
    "bomb": ["minecraft:chests/desert_pyramid", "minecraft:chests/buried_treasure", "minecraft:chests/shipwreck_treasure",
             "minecraft:chests/abandoned_mineshaft", "minecraft:chests/end_city_treasure"],
    "spear": ["minecraft:chests/stronghold_crossing", "minecraft:chests/pillager_outpost",
              "minecraft:chests/underwater_ruin_big", "minecraft:chests/bastion_hoglin_stable",
              "minecraft:chests/woodland_mansion"],
    "katana": ["minecraft:chests/pillager_outpost", "minecraft:chests/woodland_mansion", "minecraft:chests/stronghold_corridor",
               "minecraft:chests/village/village_weaponsmith", "minecraft:chests/ancient_city"],
    "longsword": ["minecraft:chests/bastion_treasure", "minecraft:chests/end_city_treasure", "minecraft:chests/ancient_city",
                  "minecraft:chests/stronghold_crossing", "minecraft:chests/simple_dungeon"],
}

FIEND_LOOT = {
    "blood_devil_remains": ["minecraft:chests/nether_bridge", "minecraft:chests/bastion_other", "minecraft:chests/simple_dungeon",
                            "minecraft:chests/ruined_portal"],
    "shark_devil_remains": ["minecraft:chests/shipwreck_treasure", "minecraft:chests/underwater_ruin_big",
                            "minecraft:chests/buried_treasure", "minecraft:chests/shipwreck_supply"],
    "violence_devil_remains": ["minecraft:chests/simple_dungeon", "minecraft:chests/abandoned_mineshaft",
                               "minecraft:chests/pillager_outpost", "minecraft:chests/bastion_hoglin_stable"],
    "cosmos_devil_remains": ["minecraft:chests/end_city_treasure", "minecraft:chests/stronghold_library",
                             "minecraft:chests/ancient_city", "minecraft:chests/woodland_mansion"],
    "gun_devil_flesh": ["minecraft:chests/pillager_outpost", "minecraft:chests/desert_pyramid",
                        "minecraft:chests/woodland_mansion", "minecraft:chests/ancient_city_ice_box"],
}


# Contracts in survival: a devil's contract is paper sealed in blood (a blood vial - use a glass bottle on a mob)
# around something of the devil's. Pattern keys: P paper, B blood vial, X/Y the devil's part.
CONTRACT_RECIPES = {
    "fox_devil_contract_paw": ([" X ", "PBP", " P "], {"X": "minecraft:sweet_berries"}),
    # the Fox Devil lends its head to few: gold for the handsome
    "fox_devil_contract_head": (["YXY", "PBP", " P "], {"X": "minecraft:sweet_berries", "Y": "minecraft:gold_ingot"}),
    "curse_devil_contract": (["YXY", "PBP", " P "], {"X": "minecraft:bone", "Y": "minecraft:iron_nugget"}),
    "future_devil_contract": ([" X ", "PBP", " P "], {"X": "minecraft:ender_eye"}),
    "ghost_devil_contract": ([" X ", "PBP", " P "], {"X": "minecraft:phantom_membrane"}),
    "snake_devil_contract": ([" X ", "PBP", " P "], {"X": "minecraft:scute"}),
    "octopus_devil_contract": ([" X ", "PBP", " P "], {"X": "minecraft:ink_sac"}),
    "doll_devil_contract": ([" X ", "PBP", " P "], {"X": "minecraft:armor_stand"}),
    "hell_devil_contract": (["YXY", "PBP", " P "], {"X": "minecraft:blaze_powder", "Y": "minecraft:netherrack"}),
}


def contract_recipe(item, pattern, extra):
    key = {"P": {"item": "minecraft:paper"}, "B": {"item": "csm:blood_vial"}}
    key.update({k: {"item": v} for k, v in extra.items()})
    return {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": pattern, "key": key,
            "result": {"item": "csm:" + item, "count": 1}}


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    import devil_data
    lang = dict(LANG)
    lang.update(devil_data.lang())
    subs = os.path.join(HERE, "subtitles.json")
    if os.path.exists(subs):
        with open(subs, encoding="utf-8") as f:
            lang.update(json.load(f))
    for d in devil_data.DEVILS:
        write(os.path.join(RES, "data", "csm", "loot_tables", "entities", d["entity"] + ".json"),
              devil_data.loot_table(d))
    write(os.path.join(RES, "assets", "csm", "lang", "en_us.json"), lang)
    entries = []
    for t, tables in LOOT.items():
        name = "%s_heart" % t
        entries.append("csm:" + name)
        write(os.path.join(RES, "data", "csm", "loot_modifiers", name + ".json"),
              {"type": "csm:devil_heart_loot", "conditions": [], "item": "csm:%s_devil_heart" % t,
               "tables": tables, "chance": 0.06})
    for item, tables in FIEND_LOOT.items():
        entries.append("csm:" + item)
        write(os.path.join(RES, "data", "csm", "loot_modifiers", item + ".json"),
              {"type": "csm:devil_heart_loot", "conditions": [], "item": "csm:" + item, "tables": tables, "chance": 0.05})
    for item, (tables, chance) in devil_data.CONTRACT_LOOT.items():
        entries.append("csm:" + item)
        write(os.path.join(RES, "data", "csm", "loot_modifiers", item + ".json"),
              {"type": "csm:devil_heart_loot", "conditions": [], "item": "csm:" + item, "tables": tables,
               "chance": chance})
    for item, (pattern, extra) in CONTRACT_RECIPES.items():
        write(os.path.join(RES, "data", "csm", "recipes", item + ".json"), contract_recipe(item, pattern, extra))
    write(os.path.join(RES, "data", "forge", "loot_modifiers", "global_loot_modifiers.json"),
          {"replace": False, "entries": entries})
    print(len(lang), "lang keys,", len(entries), "loot modifiers,", len(CONTRACT_RECIPES), "recipes")


if __name__ == "__main__":
    main()
