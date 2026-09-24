package com.csm.hybrids.config;

import net.minecraftforge.common.ForgeConfigSpec;

public final class CsmConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.DoubleValue DAMAGE_MULTIPLIER;
    public static final ForgeConfigSpec.BooleanValue ABILITY_GRIEFING;
    public static final ForgeConfigSpec.DoubleValue BLOOD_GAIN_MULTIPLIER;
    public static final ForgeConfigSpec.DoubleValue REVIVE_BLOOD_COST;
    public static final ForgeConfigSpec.DoubleValue STARTING_BLOOD;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.push("hybrids");
        DAMAGE_MULTIPLIER = b.comment("Multiplier applied to every hybrid ability's damage.")
                .defineInRange("damageMultiplier", 1.0, 0.0, 100.0);
        ABILITY_GRIEFING = b.comment("Allow abilities to break/ignite blocks (Piercing Bolt holes, flames). "
                        + "The mobGriefing gamerule must also be on.")
                .define("abilityGriefing", true);
        BLOOD_GAIN_MULTIPLIER = b.comment("Multiplier for blood gained from hurting and drinking.")
                .defineInRange("bloodGainMultiplier", 1.0, 0.0, 100.0);
        REVIVE_BLOOD_COST = b.comment("Blood consumed when a hybrid's devil heart revives them from a lethal hit. "
                        + "Set above 100 to disable revival.")
                .defineInRange("reviveBloodCost", 40.0, 0.0, 1000.0);
        STARTING_BLOOD = b.comment("Blood a player has right after the heart replacement.")
                .defineInRange("startingBlood", 60.0, 0.0, 100.0);
        b.pop();
        SPEC = b.build();
    }

    private CsmConfig() {
    }
}
