package com.csm.hybrids.ability;

import com.csm.hybrids.ability.blood.BloodAbilities;
import com.csm.hybrids.ability.bomb.BombAbilities;
import com.csm.hybrids.ability.cosmos.CosmosAbilities;
import com.csm.hybrids.ability.gun.GunAbilities;
import com.csm.hybrids.ability.katana.KatanaAbilities;
import com.csm.hybrids.ability.longsword.LongswordAbilities;
import com.csm.hybrids.ability.shark.SharkAbilities;
import com.csm.hybrids.ability.violence.ViolenceAbilities;
import com.csm.hybrids.ability.chainsaw.ChainsawAbilities;
import com.csm.hybrids.ability.crossbow.CrossbowAbilities;
import com.csm.hybrids.ability.flamethrower.FlamethrowerAbilities;
import com.csm.hybrids.ability.spear.SpearAbilities;
import com.csm.hybrids.ability.whip.WhipAbilities;
import com.csm.hybrids.hybrid.HybridType;

import java.util.List;

/**
 * The ability wheel of every hybrid, in wheel order. Slot 0 is always the manga trigger.
 */
public final class Abilities {
    public static final List<Ability> CHAINSAW = List.of(
            new TriggerAbility(HybridType.CHAINSAW, "pull_cord"),
            new ChainsawAbilities.Slash(),
            new ChainsawAbilities.HeadsawCharge(),
            new ChainsawAbilities.ChainGrapple(),
            new ChainsawAbilities.RipAndTear(),
            new ChainsawAbilities.LegSawSpin(),
            new ChainsawAbilities.ChainBind(),
            new ChainsawAbilities.HeroOfHell(),
            new BloodDrinkAbility(HybridType.CHAINSAW));

    public static final List<Ability> CROSSBOW = List.of(
            new TriggerAbility(HybridType.CROSSBOW, "pull_arrow"),
            new CrossbowAbilities.Volley(),
            new CrossbowAbilities.PiercingBolt(),
            new CrossbowAbilities.FlashStep(),
            new CrossbowAbilities.ArrowStorm(),
            new BloodDrinkAbility(HybridType.CROSSBOW));

    public static final List<Ability> FLAMETHROWER = List.of(
            new TriggerAbility(HybridType.FLAMETHROWER, "bite_molar"),
            new FlamethrowerAbilities.FlameStream(),
            new FlamethrowerAbilities.NapalmShot(),
            new FlamethrowerAbilities.InfernoBurst(),
            new FlamethrowerAbilities.Conflagration(),
            new FlamethrowerAbilities.MolarRegeneration(),
            new BloodDrinkAbility(HybridType.FLAMETHROWER));

    public static final List<Ability> WHIP = List.of(
            new TriggerAbility(HybridType.WHIP, "snap_fingers"),
            new WhipAbilities.Lash(),
            new WhipAbilities.Storm(),
            new WhipAbilities.Snare(),
            new WhipAbilities.Swing(),
            new WhipAbilities.SonicCrack(),
            new BloodDrinkAbility(HybridType.WHIP));

    public static final List<Ability> BOMB = List.of(
            new TriggerAbility(HybridType.BOMB, "pull_pin"),
            new BombAbilities.ExplosiveCombo(),
            new BombAbilities.SparkFlick(),
            new BombAbilities.BlastPropulsion(),
            new BombAbilities.Torpedo(),
            new BombAbilities.HeadBomb(),
            new BloodDrinkAbility(HybridType.BOMB));

    public static final List<Ability> SPEAR = List.of(
            new TriggerAbility(HybridType.SPEAR, "pull_spear"),
            new SpearAbilities.Thrust(),
            new SpearAbilities.Throw(),
            new SpearAbilities.Volley(),
            new SpearAbilities.Impale(),
            new SpearAbilities.Eruption(),
            new BloodDrinkAbility(HybridType.SPEAR));

    public static final List<Ability> KATANA = List.of(
            new TriggerAbility(HybridType.KATANA, "pull_left_hand"),
            new KatanaAbilities.SwordDrawDash(),
            new KatanaAbilities.TwinSlash(),
            new KatanaAbilities.BladeFlurry(),
            new KatanaAbilities.IaiCounter(),
            new BloodDrinkAbility(HybridType.KATANA));

    public static final List<Ability> LONGSWORD = List.of(
            new TriggerAbility(HybridType.LONGSWORD, "pull_right_hand"),
            new LongswordAbilities.Cleave(),
            new LongswordAbilities.BladeWhirl(),
            new LongswordAbilities.Lunge(),
            new LongswordAbilities.CrossGuard(),
            new BloodDrinkAbility(HybridType.LONGSWORD));

    // ------------------------------------------------------------------ fiends (slot 0 unleashes the devil side)
    public static final List<Ability> BLOOD = List.of(
            new TriggerAbility(HybridType.BLOOD, "blood_awakening"),
            new BloodAbilities.BloodHammer(),
            new BloodAbilities.BloodSpear(),
            new BloodAbilities.BloodScythe(),
            new BloodAbilities.BloodControl(),
            new BloodAbilities.BloodRain(),
            new BloodDrinkAbility(HybridType.BLOOD));

    public static final List<Ability> SHARK = List.of(
            new TriggerAbility(HybridType.SHARK, "shark_devil"),
            new SharkAbilities.GroundSwim(),
            new SharkAbilities.Bite(),
            new SharkAbilities.Ambush(),
            new SharkAbilities.SharkForm(),
            new SharkAbilities.BloodScent(),
            new BloodDrinkAbility(HybridType.SHARK));

    public static final List<Ability> VIOLENCE = List.of(
            new TriggerAbility(HybridType.VIOLENCE, "remove_mask"),
            new ViolenceAbilities.ViolentPunch(),
            new ViolenceAbilities.CrushingKick(),
            new ViolenceAbilities.MouthArm(),
            new ViolenceAbilities.Rampage(),
            new BloodDrinkAbility(HybridType.VIOLENCE));

    public static final List<Ability> COSMOS = List.of(
            new TriggerAbility(HybridType.COSMOS, "open_cosmos"),
            new CosmosAbilities.Halloween(),
            new CosmosAbilities.AllOutHalloween(),
            new CosmosAbilities.InfiniteKnowledge(),
            new CosmosAbilities.MindCollapse(),
            new BloodDrinkAbility(HybridType.COSMOS));

    public static final List<Ability> GUN = List.of(
            new TriggerAbility(HybridType.GUN, "gun_devil"),
            new GunAbilities.CarbineBurst(),
            new GunAbilities.Headshot(),
            new GunAbilities.BulletStorm(),
            new GunAbilities.Massacre(),
            new BloodDrinkAbility(HybridType.GUN));

    public static List<Ability> forType(HybridType type) {
        return switch (type) {
            case CHAINSAW -> CHAINSAW;
            case CROSSBOW -> CROSSBOW;
            case FLAMETHROWER -> FLAMETHROWER;
            case WHIP -> WHIP;
            case BOMB -> BOMB;
            case SPEAR -> SPEAR;
            case KATANA -> KATANA;
            case LONGSWORD -> LONGSWORD;
            case BLOOD -> BLOOD;
            case SHARK -> SHARK;
            case VIOLENCE -> VIOLENCE;
            case COSMOS -> COSMOS;
            case GUN -> GUN;
            case NONE -> List.of();
            default -> com.csm.hybrids.ability.devil.DevilMoves.forType(type);
        };
    }

    private Abilities() {
    }
}
