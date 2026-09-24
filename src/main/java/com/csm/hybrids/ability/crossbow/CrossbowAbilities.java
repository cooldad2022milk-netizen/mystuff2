package com.csm.hybrids.ability.crossbow;

import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.entity.CrossbowBoltEntity;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Quanxi's moves: forearm crossbows and inhuman speed. */
public final class CrossbowAbilities {

    static void fire(ServerPlayer player, boolean right, Vec3 dir, float speed, float damage, int pierce, boolean piercing) {
        CrossbowBoltEntity bolt = new CrossbowBoltEntity(player.level(), player, damage, pierce, piercing);
        Vec3 from = AbilityUtil.handPos(player, right, 0.7);
        bolt.setPos(from.x, from.y, from.z);
        bolt.shoot(dir.x, dir.y, dir.z, speed, 0f);
        player.level().addFreshEntity(bolt);
    }

    static Vec3 spread(ServerPlayer player, float yawDeg, float pitchDeg) {
        float yaw = (player.getYRot() + yawDeg) * Mth.DEG_TO_RAD;
        float pitch = (player.getXRot() + pitchDeg) * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(yaw) * Mth.cos(pitch), -Mth.sin(pitch), Mth.cos(yaw) * Mth.cos(pitch));
    }

    /** Both forearm crossbows fire a fan of bolts, right arm then left. */
    public static class Volley extends Ability {
        public Volley() {
            super(HybridType.CROSSBOW, "crossbow_volley");
            timing(13, 22);
            cost(2);
            anim("crossbow_volley", "volley");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick == 3 || run.tick == 7) {
                boolean right = run.tick == 3;
                for (int i = -1; i <= 1; i++) {
                    fire(player, right, spread(player, i * 4.5f, (i == 0 ? -1f : 0.5f)), 3.4f, 7f, 1, false);
                }
                AbilityUtil.sound(player, ModSounds.CROSSBOW_FIRE.get(), 1f, right ? 1f : 1.12f);
            }
        }
    }

    /** Overdraws the right crossbow and looses a bolt that punches a perfectly round hole through everything. */
    public static class PiercingBolt extends Ability {
        public PiercingBolt() {
            super(HybridType.CROSSBOW, "piercing_bolt");
            timing(27, 160);
            cost(10);
            anim("crossbow_piercing", "charge");
            fx("charge");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 0) {
                AbilityUtil.sound(player, ModSounds.CROSSBOW_CHARGE.get(), 1f, 1f);
            }
            if (run.tick < 18) {
                player.addEffect(AbilityUtil.quiet(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 3, 2, false, false, false)));
                if (run.tick % 3 == 0) {
                    Vec3 h = AbilityUtil.handPos(player, true, 0.9);
                    Fx.charge(level, h, 4, 0.6 + run.tick * 0.02);
                }
            }
            if (run.tick == 18) {
                fire(player, true, player.getLookAngle(), 5.5f, 22f, 127, true);
                Vec3 muzzle = AbilityUtil.handPos(player, true, 1.0);
                Fx.impact(level, muzzle, 1.4);
                Fx.shards(level, muzzle, 8, 0.3);
                AbilityUtil.sound(player, ModSounds.CROSSBOW_PIERCE.get(), 1.4f, 1f);
                Vec3 back = player.getLookAngle().scale(-0.35);
                player.setDeltaMovement(player.getDeltaMovement().add(back.x, 0.05, back.z));
                player.hurtMarked = true;
            }
        }
    }

    /** Quanxi's speed: blink up to 12 blocks, cutting down everything along the line. */
    public static class FlashStep extends Ability {
        public FlashStep() {
            super(HybridType.CROSSBOW, "flash_step");
            timing(9, 45);
            cost(4);
            anim("crossbow_flash_step", "flash");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick != 2) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 look = player.getLookAngle();
            Vec3 dir = new Vec3(look.x, Mth.clamp(look.y, -0.35, 0.35), look.z).normalize();
            Vec3 start = player.position();
            double max = 12.0;
            Vec3 eyeOff = new Vec3(0, player.getEyeHeight() * 0.5, 0);
            BlockHitResult clip = level.clip(new ClipContext(start.add(eyeOff), start.add(eyeOff).add(dir.scale(max)),
                    ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
            double dist = clip.getType() == HitResult.Type.MISS ? max : Math.max(0, clip.getLocation().subtract(start.add(eyeOff)).length() - 0.7);
            Vec3 end = start;
            for (double d = dist; d > 0.5; d -= 0.5) {
                Vec3 cand = start.add(dir.scale(d));
                AABB box = player.getBoundingBox().move(cand.subtract(start));
                if (level.noCollision(player, box)) {
                    end = cand;
                    break;
                }
            }
            // slice everything along the path
            AABB path = player.getBoundingBox().expandTowards(end.subtract(start)).inflate(1.2);
            for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, path, e -> AbilityUtil.canHit(player, e))) {
                Vec3 c = e.getBoundingBox().getCenter();
                Vec3 seg = end.subtract(start);
                double t = seg.lengthSqr() < 1e-4 ? 0 : Mth.clamp(c.subtract(start).dot(seg) / seg.lengthSqr(), 0, 1);
                Vec3 closest = start.add(seg.scale(t)).add(0, 1, 0);
                if (closest.distanceTo(c) < 1.8) {
                    AbilityUtil.hurtIgnoringIFrames(player, e, 10f);
                    AbilityUtil.blood(level, c, 24, 0.3);
                    Fx.slash(level, c, dir, 1.6);
                    Fx.shards(level, c, 4, 0.2);
                }
            }
            // afterimage trail
            int steps = (int) Math.ceil(start.distanceTo(end) * 2);
            for (int i = 0; i <= steps; i++) {
                Vec3 p = start.lerp(end, i / (double) Math.max(steps, 1)).add(0, 1.0, 0);
                if (i % 2 == 0) {
                    Vec3 j = new Vec3(level.random.nextGaussian() * 0.25, level.random.nextGaussian() * 0.45,
                            level.random.nextGaussian() * 0.25);
                    Fx.speedLine(level, p.add(j), p.add(j).add(dir.scale(-1.6)));
                }
            }
            AbilityUtil.soundAt(level, start, ModSounds.FLASH_STEP.get(), 1f, 1f);
            player.connection.teleport(end.x, end.y, end.z, player.getYRot(), player.getXRot());
            player.fallDistance = 0;
            AbilityUtil.soundAt(level, end, ModSounds.FLASH_STEP.get(), 0.7f, 1.3f);
        }
    }

    /** Looses bolts into the sky that come down as a storm around the aimed point. */
    public static class ArrowStorm extends Ability {
        public ArrowStorm() {
            super(HybridType.CROSSBOW, "arrow_storm");
            timing(34, 240);
            cost(12);
            anim("crossbow_storm", "storm");
        }

        @Override
        public void start(ServerPlayer player, HybridData data, AbilityRun run) {
            HitResult hit = AbilityUtil.raycastBlock(player, 36);
            run.vec = hit.getLocation();
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick >= 4 && run.tick <= 10 && run.tick % 2 == 0) {
                boolean right = (run.tick / 2) % 2 == 0;
                fire(player, right, spread(player, level.random.nextFloat() * 10 - 5, -70), 3.5f, 2f, 0, false);
                AbilityUtil.sound(player, ModSounds.CROSSBOW_FIRE.get(), 0.8f, 1.2f + level.random.nextFloat() * 0.2f);
            }
            if (run.tick >= 13 && run.tick % 2 == 1) {
                Vec3 c = run.vec;
                for (int i = 0; i < 4; i++) {
                    double a = level.random.nextDouble() * Math.PI * 2;
                    double r = Math.sqrt(level.random.nextDouble()) * 5.5;
                    Vec3 top = c.add(Math.cos(a) * r, 16, Math.sin(a) * r);
                    CrossbowBoltEntity bolt = new CrossbowBoltEntity(level, player, 7f, 0, false);
                    bolt.setPos(top.x, top.y, top.z);
                    bolt.shoot(level.random.nextGaussian() * 0.05, -1, level.random.nextGaussian() * 0.05, 2.8f, 0);
                    level.addFreshEntity(bolt);
                }
            }
        }
    }

    private CrossbowAbilities() {
    }
}
