package com.csm.hybrids.devil;

import com.csm.hybrids.hybrid.HybridType;
import net.minecraft.world.BossEvent.BossBarColor;

import java.util.EnumMap;
import java.util.Map;

/** Stats of every full devil, as a mob and as a player's form. */
public final class DevilSpecs {
    private static final Map<HybridType, DevilSpec> SPECS = new EnumMap<>(HybridType.class);

    static {
        // ---------------------------------------------------------------- Makima and the humanoid devils
        put(HybridType.CONTROL).stats(420, 8, 0.3, 10).size(0.6f, 1.8f).fight(0.5f, 10, 250).boss(BossBarColor.RED)
                .egg(0xE8E4DC, 0xB8322A).humanForm(20, 5, 0.1, 6);
        put(HybridType.ANGEL).stats(200, 9, 0.3, 6).size(0.6f, 1.8f).fight(0.4f, 4, 80).flying(0.55)
                .egg(0xF4F0E6, 0xC8402A).humanForm(10, 4, 0.1, 4);
        put(HybridType.WAR).stats(360, 10, 0.3, 10).size(0.6f, 1.8f).fight(0.45f, 6, 180).boss(BossBarColor.RED)
                .egg(0x2A2A38, 0x8A2020).humanForm(14, 6, 0.1, 6);
        put(HybridType.FAMINE).stats(330, 8, 0.3, 8).size(0.6f, 1.8f).fight(0.4f, 8, 180).boss(BossBarColor.PINK)
                .egg(0x2A2A38, 0xE890B0).humanForm(12, 4, 0.12, 5);

        // ---------------------------------------------------------------- early part 1
        put(HybridType.BAT).stats(60, 7, 0.28, 4).size(1.6f, 2.6f).fight(0.35f, 3, 20).flying(0.6)
                .egg(0x3A2A44, 0x9A6AB0).form(2.3f, 10, 5, 0.1, 4);
        put(HybridType.LEECH).stats(80, 8, 0.24, 6).size(2.2f, 2.8f).fight(0.35f, 4, 25)
                .egg(0x2A2226, 0x8A5A66).form(2.3f, 14, 5, 0.05, 5);
        put(HybridType.ZOMBIE).stats(160, 8, 0.18, 6).size(2.8f, 4.2f).fight(0.35f, 8, 60).flying(0.3)
                .egg(0x5A6A40, 0xA88A7A).form(2.8f, 20, 5, 0.0, 6);
        put(HybridType.TOMATO).stats(70, 7, 0.22, 3).size(2.2f, 2.4f).fight(0.35f, 3, 20)
                .egg(0xC8281E, 0xF0D0B0).form(2.1f, 12, 5, 0.05, 3);
        put(HybridType.SEA_CUCUMBER).stats(45, 5, 0.2, 2).size(1.2f, 1.8f).fight(0.3f, 3, 12)
                .egg(0x6A4A3A, 0xE0C0A8).form(1.8f, 8, 3, 0.0, 2);

        // ---------------------------------------------------------------- the big threats
        put(HybridType.ETERNITY).stats(320, 10, 0.2, 8).size(3.0f, 3.6f).fight(0.4f, 5, 150).boss(BossBarColor.PINK)
                .egg(0xC89A8A, 0x6A2A2A).form(2.8f, 30, 6, 0.0, 8);
        put(HybridType.DARKNESS).stats(820, 16, 0.25, 16).size(1.8f, 5.6f).fight(0.5f, 10, 400)
                .boss(BossBarColor.PURPLE).egg(0x101014, 0x4A4A5A).form(3.2f, 40, 10, 0.1, 12).fpHidden("head", "mantle");
        put(HybridType.GUN_DEVIL).stats(900, 14, 0.25, 14).size(3.0f, 7.5f).fight(0.45f, 16, 400).flying(0.45)
                .boss(BossBarColor.WHITE).egg(0x3A3E46, 0xC8B070).form(3.2f, 40, 8, 0.05, 12);
        put(HybridType.TYPHOON).stats(620, 18, 0.3, 12).size(3.4f, 7.0f).fight(0.5f, 6, 300).boss(BossBarColor.BLUE)
                .fpHidden("head", "gale3", "gale4")
                .egg(0xB8A0A8, 0x6A8AB0).form(3.2f, 36, 10, 0.1, 10);

        // ---------------------------------------------------------------- contract devils (mobs only: players make
        // contracts with them instead of becoming them, so their form stats are never used)
        put(HybridType.FOX).stats(150, 12, 0.34, 6).size(3.0f, 3.6f).fight(0.4f, 3, 50)
                .egg(0xE8A060, 0xF4F0E6).form(2.4f, 16, 7, 0.2, 5);
        put(HybridType.CURSE).stats(230, 14, 0.22, 8).size(2.0f, 4.4f).fight(0.4f, 4, 90).boss(BossBarColor.WHITE)
                .egg(0xD8D0B8, 0x3A3A3A).form(3.0f, 24, 8, 0.05, 8).eye(0.95f);
        put(HybridType.FUTURE).stats(170, 8, 0.0, 6).size(1.6f, 3.2f).fight(0.35f, 8, 60).stationary()
                .egg(0x8A7050, 0xE8D8A0).form(2.8f, 16, 4, 0.0, 6).eye(0.98f);
        put(HybridType.GHOST).stats(120, 8, 0.25, 2).size(1.6f, 3.4f).fight(0.35f, 3, 40).flying(0.4).translucent()
                .egg(0xE8E0F0, 0xF4C8D8).form(2.8f, 12, 5, 0.05, 2);

        // ---------------------------------------------------------------- part 2
        put(HybridType.FALLING).stats(720, 14, 0.26, 12).size(2.4f, 5.0f).fight(0.5f, 8, 350).boss(BossBarColor.WHITE)
                .egg(0xF0F0F0, 0x1A1A1A).form(3.2f, 36, 8, 0.05, 10);
        put(HybridType.JUSTICE).stats(520, 14, 0.36, 10).size(3.0f, 3.0f).fight(0.45f, 4, 250)
                .boss(BossBarColor.GREEN).egg(0x5A6A3A, 0xC8C0A0).form(2.4f, 30, 9, 0.2, 10);
    }

    private static DevilSpec put(HybridType type) {
        DevilSpec s = new DevilSpec(type);
        SPECS.put(type, s);
        return s;
    }

    public static DevilSpec of(HybridType type) {
        DevilSpec s = SPECS.get(type);
        if (s == null) {
            throw new IllegalArgumentException("not a full devil: " + type);
        }
        return s;
    }

    public static Iterable<DevilSpec> all() {
        return SPECS.values();
    }

    private DevilSpecs() {
    }
}
