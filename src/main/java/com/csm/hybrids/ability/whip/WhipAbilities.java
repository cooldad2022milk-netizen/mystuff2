package com.csm.hybrids.ability.whip;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** The Whip Hybrid's moves: her hands are bundles of whips strong enough to cut a person in half. */
public final class WhipAbilities {

    /** Three alternating lashes that reach far past sword range. */
    public static class Lash extends Ability {
        public Lash() {
            super(HybridType.WHIP, "whip_lash");
            timing(16, 16);
            anim("whip_lash", "lash");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 4 && run.tick != 8 && run.tick != 12) {
                return;
            }
            ServerLevel level = player.serverLevel();
            boolean right = run.tick != 8;
            Vec3 look = player.getLookAngle();
            Vec3 hand = AbilityUtil.handPos(player, right, 0.3);
            Fx.whipArc(level, hand, look, AbilityUtil.right(player).scale(right ? -1 : 1).add(0, 0.5, 0), 6.2, 0.9);
            boolean any = false;
            for (LivingEntity e : AbilityUtil.inCone(player, 6.8, 22)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 7.5f)) {
                    any = true;
                    AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 22, 0.3);
                    Fx.bloodSpray(level, e.getBoundingBox().getCenter(), AbilityUtil.right(player).scale(right ? -1 : 1), 12, 0.45);
                    AbilityUtil.push(e, player.position(), 0.3, 0.1);
                }
            }
            AbilityUtil.sound(player, any ? ModSounds.WHIP_CRACK.get() : ModSounds.WHIP_LASH.get(), 1.1f,
                    0.9f + level.random.nextFloat() * 0.25f);
        }
    }

    /** Spin with every whip flailing out - a storm that shreds everything around her. */
    public static class Storm extends Ability {
        public Storm() {
            super(HybridType.WHIP, "whip_storm");
            timing(26, 120);
            cost(6);
            anim("whip_storm", "storm");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 4 || run.tick > 22) {
                return;
            }
            ServerLevel level = player.serverLevel();
            double a = run.tick * 0.9;
            for (int k = 0; k < 2; k++) {
                double b = a + k * Math.PI;
                Vec3 dir = new Vec3(Math.cos(b), 0, Math.sin(b));
                Fx.whipArc(level, player.position().add(0, 1.0, 0), dir, new Vec3(0, 1, 0), 4.8, 0.6);
            }
            if (run.tick % 4 == 0) {
                AbilityUtil.sound(player, ModSounds.WHIP_LASH.get(), 1f, 1.2f);
                for (LivingEntity e : AbilityUtil.inRadius(player, player.position().add(0, 1, 0), 5.2)) {
                    if (AbilityUtil.hurtIgnoringIFrames(player, e, 4.5f)) {
                        AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 12, 0.25);
                        AbilityUtil.push(e, player.position(), 0.35, 0.12);
                    }
                }
            }
        }
    }

    /** Lash a target from far away, wrap it and yank it right to her feet. */
    public static class Snare extends Ability {
        public Snare() {
            super(HybridType.WHIP, "whip_snare");
            timing(14, 60);
            cost(3);
            anim("whip_snare", "snare");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                EntityHitResult hit = AbilityUtil.raycastEntity(player, 14);
                Vec3 hand = AbilityUtil.handPos(player, true, 0.3);
                if (hit != null && hit.getEntity() instanceof LivingEntity target) {
                    run.target = target;
                    Fx.whipArc(level, hand, target.getBoundingBox().getCenter().subtract(hand), new Vec3(0, 1, 0),
                            hand.distanceTo(target.getBoundingBox().getCenter()), 0.4);
                    AbilityUtil.hurtIgnoringIFrames(player, target, 4f);
                    target.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 3)));
                    AbilityUtil.sound(player, ModSounds.WHIP_CRACK.get(), 1.2f, 0.8f);
                } else {
                    Fx.whipArc(level, hand, player.getLookAngle(), new Vec3(0, 1, 0), 12, 0.6);
                    AbilityUtil.sound(player, ModSounds.WHIP_LASH.get(), 1f, 0.9f);
                }
            }
            if (run.tick == 8 && run.target instanceof LivingEntity target && target.isAlive()) {
                Vec3 to = player.position().subtract(target.position());
                Vec3 v = to.normalize().scale(Math.min(2.2, to.length() * 0.28));
                target.setDeltaMovement(v.x, 0.45, v.z);
                target.hurtMarked = true;
                AbilityUtil.blood(level, target.getBoundingBox().getCenter(), 10, 0.2);
            }
        }
    }

    /** Crack a whip onto terrain and fling herself through the air. */
    public static class Swing extends Ability {
        public Swing() {
            super(HybridType.WHIP, "whip_swing");
            timing(14, 50);
            cost(2);
            anim("whip_swing", "swing");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick != 3) {
                return;
            }
            BlockHitResult hit = AbilityUtil.raycastBlock(player, 24);
            Vec3 hand = AbilityUtil.handPos(player, true, 0.3);
            Vec3 target = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : hand.add(player.getLookAngle().scale(10));
            Fx.whipArc(level, hand, target.subtract(hand), new Vec3(0, 1, 0), hand.distanceTo(target), 0.7);
            Vec3 d = target.subtract(player.position());
            Vec3 v = d.normalize().scale(Math.min(2.4, 0.9 + d.length() * 0.08));
            player.setDeltaMovement(v.x, Math.max(v.y, 0) + 0.55, v.z);
            player.hurtMarked = true;
            player.fallDistance = 0;
            AbilityUtil.sound(player, ModSounds.WHIP_CRACK.get(), 1.2f, 1.1f);
        }

        @Override
        public void end(ServerPlayer player, HybridData data, AbilityRun run) {
            player.fallDistance = 0;
        }
    }

    /** Both whips overhead, then one supersonic crack that blasts everything in front away. */
    public static class SonicCrack extends Ability {
        public SonicCrack() {
            super(HybridType.WHIP, "sonic_crack");
            timing(20, 160);
            cost(8);
            anim("whip_crack", "crack");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 10) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 tip = player.getEyePosition().add(look.scale(7));
            for (boolean right : new boolean[]{true, false}) {
                Fx.whipArc(level, AbilityUtil.handPos(player, right, 0.2), look, new Vec3(0, 1, 0), 7, 1.2);
            }
            Fx.impact(level, tip, 3.0);
            Fx.shockwave(level, player.position().add(look.scale(4)), 4.5, Fx.STEEL_RING);
            for (int i = 0; i < 10; i++) {
                Vec3 o = player.getEyePosition().add(look.scale(1.5)).add(level.random.nextGaussian() * 0.8,
                        level.random.nextGaussian() * 0.6, level.random.nextGaussian() * 0.8);
                Fx.speedLine(level, o, o.add(look.scale(6)));
            }
            AbilityUtil.sound(player, ModSounds.WHIP_CRACK.get(), 2.0f, 0.6f);
            for (LivingEntity e : AbilityUtil.inCone(player, 9, 35)) {
                AbilityUtil.hurtIgnoringIFrames(player, e, 9f);
                AbilityUtil.push(e, player.position(), 2.0, 0.5);
                AbilityUtil.blood(level, e.getBoundingBox().getCenter(), 14, 0.3);
            }
        }
    }

    private WhipAbilities() {
    }
}
