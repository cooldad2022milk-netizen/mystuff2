package com.csm.hybrids.ability.gun;

import com.csm.hybrids.ability.Ability;
import com.csm.hybrids.ability.AbilityRun;
import com.csm.hybrids.ability.AbilityUtil;
import com.csm.hybrids.fx.Fx;
import com.csm.hybrids.hybrid.HybridData;
import com.csm.hybrids.hybrid.HybridType;
import com.csm.hybrids.registry.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * The Gun Fiend: the Gun Devil wearing Aki's body. The barrel of an M1911 juts out between his eyes, and his left forearm
 * is an M4 carbine. Letting more of the Gun Devil out sprouts barrels all over the body - the Gun Devil once killed
 * over a million people in minutes.
 */
public final class GunAbilities {

    /** Muzzle of the M4 that replaced the left forearm. */
    static Vec3 carbine(ServerPlayer player) {
        return AbilityUtil.handPos(player, false, 1.1).add(0, 0.05, 0);
    }

    /** Muzzle of the pistol barrel between his eyes. */
    static Vec3 faceBarrel(ServerPlayer player) {
        return player.getEyePosition().add(player.getLookAngle().scale(0.45)).add(0, 0.08, 0);
    }

    /** What the Gun Devil is aiming at: the target under the crosshair, else where the look ray lands. */
    static Vec3 aimPoint(ServerPlayer player, double range) {
        net.minecraft.world.phys.EntityHitResult e = AbilityUtil.raycastEntity(player, range);
        if (e != null) {
            return e.getEntity().getBoundingBox().getCenter();
        }
        HitResult b = AbilityUtil.raycastBlock(player, range);
        return b.getType() == HitResult.Type.MISS ? player.getEyePosition().add(player.getLookAngle().scale(range))
                : b.getLocation();
    }

    static Vec3 spread(ServerLevel level, Vec3 dir, double amount) {
        return dir.normalize().add(level.random.nextGaussian() * amount, level.random.nextGaussian() * amount,
                level.random.nextGaussian() * amount).normalize();
    }

    /** Fire one bullet; returns the target it hit, if any. */
    static LivingEntity fire(ServerPlayer player, Vec3 muzzle, Vec3 dir, double range, float dmg) {
        ServerLevel level = player.serverLevel();
        AbilityUtil.Shot shot = AbilityUtil.shoot(player, muzzle, dir, range);
        Fx.bullet(level, muzzle, shot.end());
        if (shot.target() != null) {
            AbilityUtil.hurtIgnoringIFrames(player, shot.target(), dmg);
            AbilityUtil.blood(level, shot.end(), 10, 0.1);
            Fx.bloodSpray(level, shot.end(), dir, 6, 0.3);
        } else {
            level.sendParticles(com.csm.hybrids.registry.ModParticles.SPARK.get(), shot.end().x, shot.end().y, shot.end().z,
                    4, 0.05, 0.05, 0.05, 0.15);
        }
        return shot.target();
    }

    /** Three-round bursts from the carbine forearm. */
    public static class CarbineBurst extends Ability {
        public CarbineBurst() {
            super(HybridType.GUN, "carbine_burst");
            anyForm();
            timing(24, 30);
            cost(2);
            anim("gun_burst", "burst");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            int t = run.tick;
            boolean shot = (t >= 4 && t <= 6) || (t >= 12 && t <= 14) || (t >= 20 && t <= 22);
            if (!shot) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 muzzle = carbine(player);
            fire(player, muzzle, spread(level, aimPoint(player, 48).subtract(muzzle), 0.02), 48, data.isTransformed() ? 6f : 4.5f);
            AbilityUtil.sound(player, ModSounds.GUN_SHOT.get(), 1.1f, 1.1f + level.random.nextFloat() * 0.1f);
            level.sendParticles(com.csm.hybrids.registry.ModParticles.SHARD.get(), carbine(player).x, carbine(player).y,
                    carbine(player).z, 1, 0.02, 0.02, 0.02, 0.1);
        }
    }

    /** The pistol barrel in his face fires one enormous round that punches through everything in line. */
    public static class Headshot extends Ability {
        public Headshot() {
            super(HybridType.GUN, "gun_headshot");
            anyForm();
            timing(20, 90);
            cost(5);
            anim("gun_headshot", "headshot");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                AbilityUtil.sound(player, ModSounds.GUN_COCK.get(), 1f, 0.9f);
            }
            if (run.tick != 12) {
                return;
            }
            Vec3 from = faceBarrel(player);
            Vec3 dir = aimPoint(player, 80).subtract(from).normalize();
            Vec3 end = from.add(dir.scale(80));
            BlockHitResult block = level.clip(new ClipContext(from, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
            Vec3 limit = block.getType() == HitResult.Type.MISS ? end : block.getLocation();
            for (LivingEntity e : AbilityUtil.alongLine(player, from, limit, 0.4)) {
                AbilityUtil.hurtIgnoringIFrames(player, e, data.isTransformed() ? 32f : 24f);
                Vec3 c = e.getBoundingBox().getCenter();
                AbilityUtil.blood(level, c, 40, 0.3);
                Fx.bloodSpray(level, c, dir, 20, 0.6);
                AbilityUtil.push(e, from, 0.9, 0.2);
            }
            for (int i = 0; i < 3; i++) {
                Fx.bullet(level, from.add(0, (i - 1) * 0.03, 0), limit);
            }
            Fx.impact(level, from.add(dir.scale(0.6)), 1.6);
            Fx.impact(level, limit, 1.6);
            Fx.shockwave(level, player.position().add(0, 0.02, 0), 2.2, Fx.STEEL_RING);
            AbilityUtil.sound(player, ModSounds.GUN_CANNON.get(), 2f, 0.9f);
            player.setDeltaMovement(player.getDeltaMovement().add(dir.scale(-0.7)));
            player.hurtMarked = true;
        }
    }

    /** Barrels erupt all over the body and fire in every direction. Gun Devil unleashed only. */
    public static class BulletStorm extends Ability {
        public BulletStorm() {
            super(HybridType.GUN, "bullet_storm");
            timing(40, 160);
            cost(10);
            anim("gun_storm", "storm");
            fx("storm");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            if (run.tick < 6 || run.tick > 34 || run.tick % 2 != 0) {
                return;
            }
            ServerLevel level = player.serverLevel();
            Vec3 body = player.position().add(0, 1.2, 0);
            for (int k = 0; k < 5; k++) {
                double a = level.random.nextDouble() * Math.PI * 2;
                Vec3 dir = new Vec3(Math.cos(a), level.random.nextGaussian() * 0.12, Math.sin(a));
                fire(player, body.add(dir.scale(0.5)).add(0, level.random.nextGaussian() * 0.3, 0), dir, 24, 3.5f);
            }
            // anyone in reach gets aimed at
            for (LivingEntity e : AbilityUtil.inRadius(player, body, 16)) {
                if (level.random.nextFloat() < 0.35f) {
                    fire(player, body, e.getBoundingBox().getCenter().subtract(body), 20, 3.5f);
                }
            }
            AbilityUtil.sound(player, ModSounds.GUN_SHOT.get(), 1.4f, 0.8f + level.random.nextFloat() * 0.5f);
        }
    }

    /**
     * The Gun Devil's massacre: in a heartbeat, one shot for every living thing he can see within 40 blocks.
     * Gun Devil unleashed only.
     */
    public static class Massacre extends Ability {
        public Massacre() {
            super(HybridType.GUN, "massacre");
            timing(40, 400);
            cost(20);
            anim("gun_massacre", "massacre");
            fx("storm");
        }

        @Override
        public void tick(ServerPlayer player, HybridData data, AbilityRun run) {
            ServerLevel level = player.serverLevel();
            if (run.tick == 4) {
                AbilityUtil.sound(player, ModSounds.GUN_COCK.get(), 1.5f, 0.6f);
                List<LivingEntity> targets = new ArrayList<>();
                for (LivingEntity e : AbilityUtil.inRadius(player, player.getEyePosition(), 40)) {
                    if (player.hasLineOfSight(e)) {
                        targets.add(e);
                    }
                }
                targets.forEach(e -> run.hit.add(e.getId()));
            }
            if (run.tick < 12 || run.tick > 30) {
                return;
            }
            // every living thing in sight gets one aimed shot per tick while it lasts
            Vec3 body = player.position().add(0, 1.3, 0);
            for (int id : run.hit) {
                if (level.getEntity(id) instanceof LivingEntity e && e.isAlive() && (run.tick + id) % 3 == 0) {
                    Vec3 muzzle = body.add(level.random.nextGaussian() * 0.3, level.random.nextGaussian() * 0.3,
                            level.random.nextGaussian() * 0.3);
                    fire(player, muzzle, e.getBoundingBox().getCenter().subtract(muzzle), 44, 6f);
                }
            }
            AbilityUtil.sound(player, ModSounds.GUN_SHOT.get(), 1.8f, 0.6f + level.random.nextFloat() * 0.6f);
        }
    }

    private GunAbilities() {
    }
}
