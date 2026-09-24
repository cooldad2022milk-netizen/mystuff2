package com.csm.hybrids.ability.longsword;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Sword Man (the Longsword Hybrid). Longswords run out of both arms (with cross-guards at the elbows); strong
 * enough to trade blows with Katana Man and Chainsaw Man.
 */
public final class LongswordAbilities {

    /** Both arm-swords brought down together in one heavy overhead cut. */
    public static class Cleave extends Ability {
        public Cleave() {
            super(HybridType.LONGSWORD, "longsword_cleave");
            timing(16, 22);
            anim("longsword_cleave", "cleave");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 3) {
                AbilityUtil.sound(player, ModSounds.LONGSWORD_DRAW.get(), 0.6f, 1.4f);
            }
            if (run.tick != 8) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 c = player.getEyePosition().add(look.scale(2.0)).add(0, -0.4, 0);
            Fx.slash(level, c, new Vec3(0, -1, 0).add(look.scale(0.3)), 2.6);
            Fx.impact(level, player.position().add(look.x * 2.4, 0.2, look.z * 2.4), 1.4);
            Fx.shockwave(level, player.position().add(look.x * 2.4, 0.02, look.z * 2.4), 2.4, Fx.STEEL_RING);
            Fx.sparks(level, player.position().add(look.x * 2.4, 0.1, look.z * 2.4), new Vec3(0, 1, 0), 14, 0.4);
            AbilityUtil.sound(player, ModSounds.LONGSWORD_CLEAVE.get(), 1.3f, 0.9f);
            for (LivingEntity e : AbilityUtil.inCone(player, 5.2, 28)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 14f)) {
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 36, 0.3);
                    AbilityUtil.push(e, player.position(), 0.6, 0.1);
                }
            }
        }
    }

    /** Spin with both arm-swords held out, cutting everything around. */
    public static class BladeWhirl extends Ability {
        public BladeWhirl() {
            super(HybridType.LONGSWORD, "blade_whirl");
            timing(24, 70);
            cost(4);
            anim("longsword_whirl", "whirl");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 4 || run.tick > 20 || run.tick % 4 != 0) {
                return;
            }
            ServerLevel level = player.serverLevel();
            double a = run.tick * 0.8;
            for (int k = 0; k < 2; k++) {
                Vec3 dir = new Vec3(Math.cos(a + k * Math.PI), 0, Math.sin(a + k * Math.PI));
                Fx.slash(level, player.position().add(0, 1.0, 0).add(dir.scale(1.8)),
                        dir.cross(new Vec3(0, 1, 0)), 2.0);
            }
            AbilityUtil.sound(player, ModSounds.KATANA_SLASH.get(), 0.9f, 0.8f);
            for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 3.8)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 6f)) {
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 16, 0.25);
                    AbilityUtil.push(e, player.position(), 0.35, 0.1);
                }
            }
        }
    }

    /** Drive forward sword-first and run through whatever is in the way. */
    public static class Lunge extends Ability {
        public Lunge() {
            super(HybridType.LONGSWORD, "longsword_lunge");
            timing(14, 45);
            cost(2);
            anim("longsword_lunge", "lunge");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            if (run.tick == 3) {
                player.setDeltaMovement(look.x * 1.7, 0.1, look.z * 1.7);
                player.hurtMarked = true;
                AbilityUtil.sound(player, ModSounds.LONGSWORD_DRAW.get(), 1f, 1.1f);
            }
            if (run.tick >= 3 && run.tick <= 9) {
                Vec3 tip = AbilityUtil.handPos(player, true, 2.0);
                Fx.speedLine(level, tip.subtract(look.scale(1.5)), tip);
                for (LivingEntity e : AbilityUtil.inRadius(player, tip, 1.8)) {
                    if (run.hit.add(e.getId()) && AbilityUtil.hurtIgnoringIFrames(player, e, 11f)) {
                        AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 30, 0.25);
                        Fx.bloodSpray(level, e.getBoundingBox().getCenter(), look, 14, 0.5);
                        AbilityUtil.sound(player, ModSounds.SPEAR_IMPACT.get(), 1f, 1.2f);
                    }
                }
            }
        }
    }

    /**
     * Cross the arm-swords and catch blows on the elbow cross-guards: 80% less damage and melee attackers get
     * the force thrown back at them (see HybridEvents).
     */
    public static class CrossGuard extends Ability {
        public CrossGuard() {
            super(HybridType.LONGSWORD, "cross_guard");
            timing(40, 80);
            cost(2);
            anim("longsword_guard", "guard");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            player.setDeltaMovement(player.getDeltaMovement().multiply(0.4, 1, 0.4));
        }

        /** @return the damage that still gets through */
        public static float block(ServerPlayer player, float amount, Entity attacker) {
            ServerLevel level = player.serverLevel();
            Vec3 guard = player.getEyePosition().add(player.getLookAngle().scale(0.6)).add(0, -0.3, 0);
            Fx.sparks(level, guard, player.getLookAngle(), 12, 0.45);
            Fx.impact(level, guard, 0.8);
            AbilityUtil.sound(player, ModSounds.LONGSWORD_CLANG.get(), 1.2f, 0.9f + level.random.nextFloat() * 0.2f);
            if (attacker instanceof LivingEntity l && l.distanceTo(player) < 5 && AbilityUtil.canHit(player, l)) {
                AbilityUtil.hurtIgnoringIFrames(player, l, Math.min(amount * 1.5f, 20f));
                AbilityUtil.push(l, player.position(), 0.9, 0.2);
            }
            return amount * 0.2f;
        }
    }

    private LongswordAbilities() {
    }
}
