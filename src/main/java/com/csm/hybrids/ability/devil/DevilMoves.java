package com.csm.hybrids.ability.devil;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.BloodDrinkAbility;
import com.csm.hybrids.ability.TriggerAbility;
import com.csm.hybrids.hybrid.HybridType;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * The ability wheel of every full devil: slot 0 lets the devil out (a monster devil manifests its true form, a
 * humanoid devil lets the devil take over), then its moves, then drinking blood. The mob version fights with the same
 * moves (minus slot 0 and drinking).
 */
public final class DevilMoves {
    private static final Map<HybridType, List<Ability>> CACHE = new EnumMap<>(HybridType.class);

    public static synchronized List<Ability> forType(HybridType type) {
        return CACHE.computeIfAbsent(type, DevilMoves::build);
    }

    private static List<Ability> build(HybridType type) {
        List<Ability> list = new ArrayList<>();
        list.add(new TriggerAbility(type, triggerId(type)));
        list.addAll(moves(type));
        list.add(new BloodDrinkAbility(type));
        return List.copyOf(list);
    }

    /** Slot 0's id (lang key, icon): monster devils all "manifest"; humanoid devils each have their own. */
    public static String triggerId(HybridType type) {
        return switch (type) {
            case CONTROL -> "control_devil";
            case ANGEL -> "angel_wings";
            case WAR -> "yoru_takes_over";
            case FAMINE -> "famine_hunger";
            default -> "manifest";
        };
    }

    private static List<Ability> moves(HybridType type) {
        return switch (type) {
            case CONTROL -> ControlMoves.all();
            case BAT -> BatMoves.all();
            case LEECH -> LeechMoves.all();
            case ZOMBIE -> EarlyDevilMoves.zombie();
            case TOMATO -> EarlyDevilMoves.tomato();
            case SEA_CUCUMBER -> EarlyDevilMoves.seaCucumber();
            case ETERNITY -> PrimalMoves.eternity();
            case DARKNESS -> PrimalMoves.darkness();
            case GUN_DEVIL -> CalamityMoves.gunDevil();
            case TYPHOON -> CalamityMoves.typhoon();
            case FOX -> ContractMoves.fox();
            case CURSE -> ContractMoves.curse();
            case FUTURE -> ContractMoves.future();
            case GHOST -> ContractMoves.ghost();
            case ANGEL -> HumanDevilMoves.angel();
            case WAR -> HumanDevilMoves.war();
            case FAMINE -> HumanDevilMoves.famine();
            case FALLING -> PartTwoMoves.falling();
            case JUSTICE -> PartTwoMoves.justice();
            default -> List.of();
        };
    }

    /** The moment the devil comes out (slot 0 finishing): blood, a shockwave and the devil's own entrance. */
    public static void onManifest(net.minecraft.server.level.ServerPlayer player, HybridType type) {
        net.minecraft.server.level.ServerLevel level = player.serverLevel();
        net.minecraft.world.phys.Vec3 c = player.position().add(0, player.getBbHeight() * 0.55, 0);
        com.csm.hybrids.ability.AbilityUtil.sound(player, com.csm.hybrids.registry.ModSounds.TRANSFORM.get(), 1.3f,
                type.monster() ? 0.55f : 0.8f);
        com.csm.hybrids.fx.Fx.shockwave(level, player.position(), type.monster() ? 4.0 : 2.8,
                com.csm.hybrids.fx.Fx.BLOOD_RING);
        if (type.monster()) {
            // the human shell bursts open
            com.csm.hybrids.ability.AbilityUtil.blood(level, c, 60, 0.6);
            com.csm.hybrids.fx.Fx.impact(level, c, 2.6);
            com.csm.hybrids.fx.Fx.smoke(level, c, 12, 0.6);
            for (net.minecraft.world.entity.LivingEntity e : com.csm.hybrids.ability.AbilityUtil.inRadius(player, c, 3.0)) {
                com.csm.hybrids.ability.AbilityUtil.push(e, player.position(), 0.9, 0.3);
            }
        } else {
            com.csm.hybrids.fx.Fx.impact(level, c, 1.6);
        }
    }

    private DevilMoves() {
    }
}
