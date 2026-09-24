package com.csm.hybrids.ability.spear;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.SpearEntity;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The Spear Hybrid's moves. He makes spears out of his own body and never misses: thrown spears fly dead
 * straight and home in on whatever he is looking at.
 */
public final class SpearAbilities {

    /** Where the hybrid is aiming: the entity under the crosshair, else the block, else far ahead. */
    static Vec3 aimPoint(ServerPlayer player, double range) {
        EntityHitResult e = AbilityUtil.raycastEntity(player, range);
        if (e != null) {
            return e.getEntity().getBoundingBox().getCenter();
        }
        HitResult b = AbilityUtil.raycastBlock(player, range);
        return b.getType() == HitResult.Type.BLOCK ? b.getLocation() : player.getEyePosition().add(player.getLookAngle().scale(range));
    }

    static void launch(ServerPlayer player, Vec3 from, Vec3 to, float speed, float damage, int pierce, float scale) {
        SpearEntity spear = new SpearEntity(player.level(), player, SpearEntity.THROWN, damage, pierce, scale);
        spear.setPos(from.x, from.y, from.z);
        Vec3 d = to.subtract(from);
        spear.shoot(d.x, d.y, d.z, speed, 0f);
        player.level().addFreshEntity(spear);
    }

    /** Three quick thrusts with the spear-arm that reach well past sword range. */
    public static class Thrust extends Ability {
        public Thrust() {
            super(HybridType.SPEAR, "spear_thrust");
            timing(14, 16);
            anim("spear_thrust", "thrust");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 3 && run.tick != 7 && run.tick != 11) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 hand = AbilityUtil.handPos(player, true, 0.4);
            Vec3 tip = hand.add(look.scale(4.6));
            Fx.speedLine(level, hand, tip);
            Fx.speedLine(level, hand.add(0, 0.08, 0), tip.add(0, 0.08, 0));
            boolean any = false;
            for (LivingEntity e : AbilityUtil.inCone(player, 5.6, 14)) {
                if (AbilityUtil.hurtIgnoringIFrames(player, e, 8f)) {
                    any = true;
                    Vec3 c = e.getBoundingBox().getCenter();
                    AbilityUtil.blood(level, c, 24, 0.2);
                    Fx.bloodSpray(level, c, look, 14, 0.5);
                    AbilityUtil.push(e, player.position(), 0.45, 0.08);
                }
            }
            if (!any) {
                Fx.impact(level, tip, 0.8);
            }
            AbilityUtil.sound(player, any ? ModSounds.SPEAR_IMPACT.get() : ModSounds.SPEAR_THROW.get(), 0.9f,
                    1.3f + level.random.nextFloat() * 0.2f);
        }
    }

    /** Wind up and hurl the spear-arm's spear. It flies dead straight, pierces and sticks. */
    public static class Throw extends Ability {
        public Throw() {
            super(HybridType.SPEAR, "spear_throw");
            timing(14, 40);
            cost(3);
            anim("spear_throw", "throw");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 6) {
                return;
            }
            Vec3 from = AbilityUtil.handPos(player, true, 0.9).add(0, 0.25, 0);
            launch(player, from, aimPoint(player, 96), 4.2f, 22f, 3, 1.2f);
            Fx.speedLine(player.serverLevel(), from, from.add(player.getLookAngle().scale(3)));
            Fx.impact(player.serverLevel(), from.add(player.getLookAngle().scale(0.8)), 1.1);
            AbilityUtil.sound(player, ModSounds.SPEAR_THROW.get(), 1.3f, 0.9f);
        }
    }

    /** Spears grow out of his back and shoulders, hang in the air, then all fire at once. */
    public static class Volley extends Ability {
        public Volley() {
            super(HybridType.SPEAR, "spear_volley");
            timing(24, 140);
            cost(8);
            anim("spear_volley", "volley");
        }

        static Vec3 slot(ServerPlayer player, int i) {
            Vec3 right = AbilityUtil.right(player);
            double s = (i - 2.5) / 2.5;
            return player.position().add(0, 2.2 + (1 - s * s) * 0.6, 0).add(right.scale(s * 1.8))
                    .subtract(player.getLookAngle().multiply(1, 0, 1).scale(0.5));
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick >= 3 && run.tick <= 12 && run.tick % 2 == 1) {
                for (int i = 0; i < 6; i++) {
                    Fx.charge(level, slot(player, i), 2, 0.4);
                }
                if (run.tick == 3) {
                    AbilityUtil.sound(player, ModSounds.SPEAR_PULL.get(), 1.0f, 0.8f);
                    AbilityUtil.blood(level, player.position().add(0, 1.4, 0), 14, 0.3);
                }
            }
            if (run.tick == 14) {
                Vec3 target = aimPoint(player, 80);
                for (int i = 0; i < 6; i++) {
                    Vec3 from = slot(player, i);
                    Vec3 spread = new Vec3(level.random.nextGaussian(), level.random.nextGaussian() * 0.5,
                            level.random.nextGaussian()).scale(0.35);
                    launch(player, from, target.add(spread), 3.6f, 10f, 1, 1.0f);
                    Fx.shards(level, from, 3, 0.1);
                }
                AbilityUtil.sound(player, ModSounds.SPEAR_THROW.get(), 1.6f, 0.75f);
            }
        }
    }

    /** Vanish and reappear behind the target, driving the spear through its back. */
    public static class Impale extends Ability {
        public Impale() {
            super(HybridType.SPEAR, "spear_impale");
            timing(16, 120);
            cost(6);
            anim("spear_impale", "impale");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 2) {
                EntityHitResult hit = AbilityUtil.raycastEntity(player, 18);
                if (hit == null || !(hit.getEntity() instanceof LivingEntity target)) {
                    return;
                }
                Vec3 from = player.position();
                Vec3 facing = target.getLookAngle().multiply(1, 0, 1);
                if (facing.lengthSqr() < 1e-4) {
                    facing = target.position().subtract(from).multiply(1, 0, 1);
                }
                Vec3 behind = target.position().subtract(facing.normalize().scale(target.getBbWidth() * 0.5 + 1.1));
                if (!level.noCollision(player, player.getBoundingBox().move(behind.subtract(from)))) {
                    behind = target.position().add(from.subtract(target.position()).normalize().scale(1.4));
                }
                for (int i = 0; i < 6; i++) {
                    Vec3 a = from.add(0, 0.2 + i * 0.3, 0);
                    Fx.speedLine(level, a, behind.add(0, 0.2 + i * 0.3, 0));
                }
                Vec3 to = target.getBoundingBox().getCenter().subtract(player.getEyePosition());
                float yaw = (float) (Math.atan2(to.z, to.x) * 180 / Math.PI) - 90;
                float pitch = (float) (-Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)) * 180 / Math.PI);
                player.connection.teleport(behind.x, behind.y, behind.z, yaw, pitch);
                run.target = target;
            }
            if (run.tick == 5 && run.target instanceof LivingEntity target && target.isAlive()) {
                Vec3 c = target.getBoundingBox().getCenter();
                Vec3 dir = c.subtract(player.getEyePosition()).normalize();
                AbilityUtil.hurtIgnoringIFrames(player, target, 18f);
                target.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 4)));
                AbilityUtil.blood(level, c, 40, 0.3);
                Fx.bloodSpray(level, c.add(dir.scale(0.4)), dir, 26, 0.6);
                Fx.impact(level, c.add(dir.scale(0.6)), 1.8);
                Fx.shockwave(level, c, 2.0, Fx.BLOOD_RING);
                AbilityUtil.sound(player, ModSounds.SPEAR_IMPACT.get(), 1.4f, 0.7f);
            }
        }
    }

    /** Stab the ground: a line of spears erupts forward, skewering anything along it. */
    public static class Eruption extends Ability {
        public Eruption() {
            super(HybridType.SPEAR, "spear_eruption");
            timing(22, 160);
            cost(9);
            anim("spear_eruption", "eruption");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 5) {
                run.vec = player.position();
                run.vec2 = player.getLookAngle().multiply(1, 0, 1).normalize();
                Fx.shockwave(level, player.position().add(run.vec2.scale(0.8)), 2.0, Fx.STEEL_RING);
                AbilityUtil.sound(player, ModSounds.SPEAR_IMPACT.get(), 1.2f, 0.6f);
            }
            if (run.vec == null || run.tick < 6 || run.tick > 16) {
                return;
            }
            int step = run.tick - 5;
            Vec3 side = new Vec3(-run.vec2.z, 0, run.vec2.x);
            for (int k = -1; k <= 1; k += 2) {
                if (step % 2 == 0 && k == -1) {
                    continue;
                }
                Vec3 p = run.vec.add(run.vec2.scale(1.2 + step * 1.25)).add(side.scale(k * 0.45 * (step % 2)));
                Vec3 ground = ground(level, p);
                if (ground == null) {
                    continue;
                }
                SpearEntity spear = new SpearEntity(level, player, SpearEntity.ERUPT, 10f, 0, 1.1f + step * 0.05f);
                spear.setPos(ground.x, ground.y, ground.z);
                spear.setYRot(level.random.nextFloat() * 360f);
                spear.setXRot((level.random.nextFloat() - 0.5f) * 30f);
                level.addFreshEntity(spear);
            }
            if (step % 2 == 1) {
                AbilityUtil.soundAt(level, run.vec.add(run.vec2.scale(1.2 + step * 1.25)), ModSounds.SPEAR_ERUPT.get(), 1f,
                        0.9f + level.random.nextFloat() * 0.3f);
            }
        }

        private static Vec3 ground(ServerLevel level, Vec3 p) {
            BlockPos pos = BlockPos.containing(p.x, p.y + 1.5, p.z);
            for (int i = 0; i < 5; i++) {
                BlockPos below = pos.below();
                if (!level.getBlockState(below).getCollisionShape(level, below).isEmpty()
                        && level.getBlockState(pos).getCollisionShape(level, pos).isEmpty()) {
                    return new Vec3(p.x, pos.getY(), p.z);
                }
                pos = below;
            }
            return null;
        }
    }

    private SpearAbilities() {
    }
}
